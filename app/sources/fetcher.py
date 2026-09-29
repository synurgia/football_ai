"""Daily fetcher — combines aggregator APIs and cached federation fixtures.

For each competition:
  1. Query every aggregator source in parallel (apif, espn, tsdb, fd, oldb, ofb, zafx)
  2. Load cached federation fixtures (populated once/day by federation job)
  3. Merge + dedupe by team-name tokens
  4. Return today's matches only

Never scrapes HTML at match time. Federation data is read from DB cache.
"""

from __future__ import annotations
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from app.sources.aggregators import fetch_one


# ----------------------------------------------------------------
# Competition → aggregator sources
# ----------------------------------------------------------------

# Reuse the v2 map (aggregator IDs only, no federation URLs here)
def _aggregator_sources_for(competition_id: str) -> List[Tuple[str, Any]]:
    """Return (source_key, arg) pairs for aggregator queries.

    Uses app/competition_source_map.py (v1) which has the full mapping of
    APIF/ESPN/TSDB/FD/OLDB/OFB/ZAFX IDs per competition. The 'reg' fallback
    is filtered out — federation is handled separately via cache.
    """
    try:
        from app.competition_source_map import sources_for_competition
        return [(k, v) for k, v in sources_for_competition(competition_id) if k != "reg"]
    except Exception as e:
        # Never fail silently — log to stderr so we can debug
        import sys
        print(f"[fetcher] aggregator map load failed: {e}", file=sys.stderr)
        return []


# ----------------------------------------------------------------
# Token helpers
# ----------------------------------------------------------------

def _tokens(name: str) -> set:
    if not name:
        return set()
    s = str(name).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    stop = {"fc", "sc", "ac", "cf", "afc", "the", "of", "and", "de"}
    return {w for w in s.split() if w and w not in stop}


def _match_key(m: Dict[str, Any]) -> Tuple[frozenset, frozenset]:
    return (
        frozenset(_tokens(m.get("home_team", ""))),
        frozenset(_tokens(m.get("away_team", ""))),
    )


# ----------------------------------------------------------------
# One competition
# ----------------------------------------------------------------

def fetch_competition_today(
    competition_id: str,
    *,
    timeout: float = 3.0,
    include_federation_cache: bool = True,
) -> Dict[str, Any]:

    aggregator_sources = _aggregator_sources_for(competition_id)
    results: List[Dict[str, Any]] = []

    if aggregator_sources:
        with ThreadPoolExecutor(max_workers=min(6, len(aggregator_sources))) as pool:
            futures = {
                pool.submit(fetch_one, key, competition_id, arg, timeout): (key, arg)
                for key, arg in aggregator_sources
            }
            for fut in as_completed(futures):
                key, arg = futures[fut]
                try:
                    results.append(fut.result())
                except Exception as exc:
                    results.append({
                        "source": key, "status": "FAILED",
                        "matches": [], "error": str(exc),
                    })

    # Cached federation fixtures
    federation_matches: List[Dict[str, Any]] = []
    if include_federation_cache:
        try:
            from app.sources.cache import load_today
            cached = load_today(competition_id)
            for cm in cached:
                cm = dict(cm)
                cm["competition_id"] = competition_id
                cm["sources"] = cm.get("sources") or ["federation_cache"]
                federation_matches.append(cm)
        except Exception:
            pass

    # Merge — dedupe by team tokens, prefer aggregator first
    merged: List[Dict[str, Any]] = []
    seen = set()

    for r in results:
        for m in r.get("matches", []):
            k = _match_key(m)
            if k in seen:
                continue
            seen.add(k)
            m["sources"] = [r["source"]]
            merged.append(m)

    for m in federation_matches:
        k = _match_key(m)
        if k in seen:
            continue
        seen.add(k)
        merged.append(m)

    return {
        "competition_id": competition_id,
        "date": date.today().isoformat(),
        "matches": merged,
        "aggregator_sources": [
            {"source": r["source"], "status": r["status"],
             "count": len(r.get("matches", [])),
             "error": r.get("error")}
            for r in results
        ],
        "federation_cached": len(federation_matches),
        "total": len(merged),
    }


# ----------------------------------------------------------------
# All competitions
# ----------------------------------------------------------------

def fetch_all_today(
    competition_ids: List[str],
    *,
    timeout: float = 3.0,
    max_workers: int = 4,
) -> Dict[str, Any]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    source_status: Dict[str, List[Dict[str, Any]]] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(fetch_competition_today, cid, timeout=timeout): cid
            for cid in competition_ids
        }
        for fut in as_completed(futures):
            cid = futures[fut]
            try:
                r = fut.result()
                out[cid] = r.get("matches", [])
                source_status[cid] = r.get("aggregator_sources", [])
            except Exception:
                out[cid] = []
                source_status[cid] = []

    return {
        "date": date.today().isoformat(),
        "by_competition": out,
        "source_status": source_status,
        "total_matches": sum(len(v) for v in out.values()),
        "competitions_with_matches": sum(1 for v in out.values() if v),
        "competitions_checked": len(competition_ids),
    }


if __name__ == "__main__":
    import time
    t0 = time.time()
    r = fetch_competition_today("usa.1")
    print(f"usa.1 -> {r['total']} matches in {time.time()-t0:.2f}s")
    for s in r["aggregator_sources"]:
        print(f"  {s['source']:<8} {s['status']:<10} {s['count']} matches")
