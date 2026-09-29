"""Strict ESPN scoreboard collector.

Two hard rules that the original _collect_espn violated:
  1. Only query ESPN with TODAY'S date (or ±1 day), never a fixture's stale date.
  2. Only accept an event when BOTH team names appear in the competitors list.

If either rule fails, return INSUFFICIENT — never return a different match.
"""

from __future__ import annotations
import re
from datetime import date, datetime, timezone, timedelta
from typing import Any, Dict, Optional, List

import httpx


def _today_yyyymmdd() -> str:
    return date.today().strftime("%Y%m%d")


def _yesterday_yyyymmdd() -> str:
    return (date.today() - timedelta(days=1)).strftime("%Y%m%d")


def _tomorrow_yyyymmdd() -> str:
    return (date.today() + timedelta(days=1)).strftime("%Y%m%d")


def _normalise(name: str) -> str:
    if not name:
        return ""
    s = str(name).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return " ".join(s.split())


def _tokens(name: str) -> set:
    stop = {"fc", "sc", "ac", "cf", "the", "of", "and", "de", "afc"}
    return {w for w in _normalise(name).split() if w and w not in stop}


def _team_matches(fixture_name: str, competitor: Dict[str, Any]) -> bool:
    """Does this competitor represent fixture_name?"""
    if not fixture_name or not isinstance(competitor, dict):
        return False

    target = _tokens(fixture_name)
    if not target:
        return False

    team = competitor.get("team") or {}
    candidates = [
        team.get("displayName"),
        team.get("shortDisplayName"),
        team.get("name"),
        team.get("location"),
        team.get("abbreviation"),
        competitor.get("displayName"),
    ]
    for c in candidates:
        if not c:
            continue
        ct = _tokens(c)
        if not ct:
            continue
        if target & ct:
            return True
    return False


def _event_matches_fixture(event: Dict[str, Any], home: str, away: str) -> bool:
    """Require BOTH teams to appear among the event's competitors."""
    comps = (event.get("competitions") or [{}])[0].get("competitors") or []
    if len(comps) < 2:
        return False

    home_ok = any(_team_matches(home, c) for c in comps)
    away_ok = any(_team_matches(away, c) for c in comps)
    return home_ok and away_ok


def collect_espn_strict(
    fixture: Dict[str, Any],
    source: Dict[str, Any],
    *,
    timeout: float = 6.0,
    make_failure,
    make_insufficient,
    make_success,
):
    """Strict ESPN collector.

    make_failure(fixture, source, url, error) -> CollectedSourceEvidence
    make_insufficient(fixture, source, reason, url=None) -> CollectedSourceEvidence
    make_success(fixture, source, url, evidence, evidence_types) -> CollectedSourceEvidence
    """

    home = str(fixture.get("home_team") or "").strip()
    away = str(fixture.get("away_team") or "").strip()
    if not home or not away:
        return make_insufficient(
            fixture, source,
            "ESPN requires both home and away team names on the fixture.",
        )

    # Query today, yesterday and tomorrow. Merge all three scoreboards.
    # This handles timezone drift without ever going back 18 days.
    events: List[Dict[str, Any]] = []
    urls_tried: List[str] = []
    last_error: Optional[str] = None

    for date_str in (_yesterday_yyyymmdd(), _today_yyyymmdd(), _tomorrow_yyyymmdd()):
        url = (
            "https://site.api.espn.com/apis/site/v2/"
            f"sports/soccer/all/scoreboard?dates={date_str}"
        )
        urls_tried.append(url)
        try:
            r = httpx.get(url, timeout=timeout)
            r.raise_for_status()
            payload = r.json()
        except Exception as exc:
            last_error = str(exc)
            continue
        for ev in payload.get("events", []) or []:
            events.append(ev)

    if not events:
        if last_error:
            return make_failure(fixture, source, urls_tried[0], last_error)
        return make_insufficient(
            fixture, source,
            "ESPN returned no events for today, yesterday or tomorrow.",
            urls_tried[0],
        )

    # Strict match: both team names must be present.
    matched = None
    for ev in events:
        if _event_matches_fixture(ev, home, away):
            matched = ev
            break

    if matched is None:
        return make_insufficient(
            fixture, source,
            f"ESPN scoreboard has {len(events)} events across 3 days, "
            f"but no event contains both '{home}' and '{away}'.",
            urls_tried[1],
        )

    return make_success(
        fixture, source,
        urls_tried[1],
        {
            "event": matched,
            "response_event_count": len(events),
        },
        source.get("evidence_types", []),
    )
