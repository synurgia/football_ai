import hashlib
import re
from typing import Any, Dict


class MatchIdentity:
    """
    Creates a provider-independent canonical identity for a football match.

    Provider-specific match IDs remain available as source references,
    but they are not used as the permanent internal match identity.
    """

    @staticmethod
    def canonical_team_name(name: str) -> str:
        value = (name or "").strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")

    @classmethod
    def canonical_key(cls, match: Dict[str, Any]) -> str:
        competition = str(match.get("competition") or "").strip()
        season = str(match.get("season") or "").strip()
        kickoff = str(match.get("kickoff_at") or "").strip()

        home = cls.canonical_team_name(match.get("home_team", ""))
        away = cls.canonical_team_name(match.get("away_team", ""))

        parts = [competition, season, kickoff, home, away]

        if any(not part for part in parts):
            raise ValueError(
                "Cannot create canonical match identity: "
                "competition, season, kickoff_at, home_team and away_team "
                "are all required."
            )

        return "|".join(parts)

    @classmethod
    def match_id(cls, match: Dict[str, Any]) -> str:
        key = cls.canonical_key(match)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        return f"match_{digest}"
