from datetime import date, timedelta
from typing import Any, Dict, Optional

from app.data_registry.v13_match_discovery import extract_match_candidates, extract_fixture_bridge_candidates
from app.data_registry.v13_match_extractor import extract_from_snippet
from app.data_registry.match_identity import MatchIdentity


class V13MatchSourceAdapter:
    """
    V1.3 source-neutral match retrieval seam.

    Uses the already retrieved V1.3 mapped source pool. No source is given
    priority. ESPN/OpenFoot may participate only when present in the supplied
    source pool.

    The adapter normalizes evidence-bearing source content into the existing
    match object expected by the protected AI reasoning engine.
    """

    def _name_matches(self, candidate: str, target: str) -> bool:
        c = (candidate or "").lower().strip()
        t = (target or "").lower().strip()
        if not c or not t:
            return False

        def norm(value: str) -> str:
            import re
            return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

        c_norm = norm(c)
        t_norm = norm(t)

        return (
            c_norm == t_norm
            or t_norm in c_norm
            or c_norm in t_norm
        )

    def _dates_to_check(self, around_date: Optional[str]) -> list[str]:
        if around_date:
            return [around_date]

        today = date.today()
        return [
            (today + timedelta(days=delta)).strftime("%Y-%m-%d")
            for delta in range(-3, 15)
        ]

    def _candidate_matches_teams(
        self,
        candidate: Dict[str, Any],
        team_a: str,
        team_b: str,
    ) -> bool:
        home = candidate.get("home_team") or ""
        away = candidate.get("away_team") or ""

        direct = (
            self._name_matches(home, team_a)
            and self._name_matches(away, team_b)
        )

        reversed_order = (
            self._name_matches(home, team_b)
            and self._name_matches(away, team_a)
        )

        return direct or reversed_order

    def _date_matches(
        self,
        candidate: Dict[str, Any],
        around_date: Optional[str],
    ) -> bool:
        if not around_date:
            return True

        candidate_date = str(candidate.get("date") or "").strip()
        requested = str(around_date).replace("/", "-").strip()

        return candidate_date == requested

    def _build_match(
        self,
        candidate: Dict[str, Any],
        *,
        competition_id: str,
        competition_name: str,
        season: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        home = candidate.get("home_team")
        away = candidate.get("away_team")
        match_date = candidate.get("date")
        match_time = candidate.get("time")

        # Canonical identity requires all five fields. Do not fabricate any.
        if not all((competition_id, season, home, away, match_date, match_time)):
            return None

        kickoff_at = f"{match_date}T{match_time}:00"

        match = {
            "competition": competition_id,
            "competition_name": competition_name,
            "season": str(season),
            "home_team": home,
            "away_team": away,
            "kickoff_at": kickoff_at,
            "match_date": match_date,
            "venue": candidate.get("venue"),
            "source_id": candidate.get("source_id"),
            "source_name": candidate.get("source_name"),
            "source_url": candidate.get("source_url"),
            "evidence_snippet": candidate.get("evidence_snippet"),
            "match_status": "FOUND",
        }

        # The existing canonical identity remains the final promotion gate.
        try:
            match["match_id"] = MatchIdentity.match_id(match)
        except (TypeError, ValueError):
            return None

        return match

    def find_match(
        self,
        *,
        competition_id: str,
        competition_name: str,
        team_a: str,
        team_b: str,
        around_date: Optional[str] = None,
        source_retrieval: Optional[Dict[str, Any]] = None,
        season: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resolve a fixture from the V1.3 mapped/retrieved source pool.

        No source priority is assigned. Every SOURCE_RETRIEVED source is
        treated as applicable evidence and candidates are matched against
        the requested teams/date.

        The returned object preserves the contract expected by V1.4.
        """

        if not source_retrieval:
            return {
                "match_status": "NOT_FOUND",
                "reason": "NO_V13_SOURCE_RETRIEVAL",
            }

        all_candidates: list[Dict[str, Any]] = []

        for source in source_retrieval.get("results", []):
            if source.get("status") != "SOURCE_RETRIEVED":
                continue

            content = source.get("content") or ""
            if not content:
                continue

            discovered = extract_match_candidates(content)
            bridge_candidates = extract_fixture_bridge_candidates(content)
            if bridge_candidates:
                discovered.extend(bridge_candidates)

            for raw_candidate in discovered:
                candidate = extract_from_snippet(
                    competition_id=competition_id,
                    competition_name=competition_name,
                    source_id=source.get("source_id", ""),
                    source_name=source.get("source_name", ""),
                    source_url=(
                        source.get("final_url")
                        or source.get("source_url")
                        or ""
                    ),
                    candidate=raw_candidate,
                )

                if candidate.get("identity_status") != "STRUCTURED_CANDIDATE":
                    continue

                if not self._candidate_matches_teams(
                    candidate,
                    team_a,
                    team_b,
                ):
                    continue

                if not self._date_matches(candidate, around_date):
                    continue

                all_candidates.append(candidate)

        # Promote only a candidate with a complete canonical identity.
        for candidate in all_candidates:
            match = self._build_match(
                candidate,
                competition_id=competition_id,
                competition_name=competition_name,
                season=season,
            )
            if match:
                return match

        return {
            "match_status": "NOT_FOUND",
            "reason": "NO_CANONICAL_MATCH_FROM_MAPPED_SOURCES",
            "source_count": source_retrieval.get("source_count", 0),
            "retrieved_sources": source_retrieval.get("retrieved", 0),
            "candidate_count": len(all_candidates),
        }
