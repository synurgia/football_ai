from typing import Any, Dict, List

from app.data_registry.v13_ai_routing_adapter import get_ai_routing_context
from app.v13_ai_intelligence_engine import run as run_ai


def analyze_daily_match(match: Dict[str, Any]) -> Dict[str, Any]:
    """
    V1.3 -> AI Intelligence Engine bridge.

    V1.3 remains authoritative for competition identity and source routing.
    The AI engine performs the intelligence/reasoning work.
    Missing information is preserved as insufficient evidence.
    """

    competition_id = match.get("competition_id")
    home_team = match.get("home_team")
    away_team = match.get("away_team")

    if not competition_id or not home_team or not away_team:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "reason": "V1.3 match identity is incomplete.",
            "questions": [],
            "evidence": [],
            "reasoning": None,
            "readiness": {
                "status": "INSUFFICIENT",
                "process": False,
            },
        }

    routing = get_ai_routing_context(competition_id)

    if routing["competition_identity_status"] != "RESOLVED":
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "reason": "V1.3 could not resolve the competition.",
            "routing": routing,
            "questions": [],
            "evidence": [],
            "reasoning": None,
            "readiness": {
                "status": "INSUFFICIENT",
                "process": False,
            },
        }

    try:
        kickoff_at = match.get("kickoff_at")
        match_date = str(kickoff_at)[:10] if kickoff_at else None

        ai_result = run_ai(
            home_team,
            away_team,
            competition_id,
            match_date,
        )

        return {
            "status": "COMPLETED",
            "routing": routing,
            "ai": ai_result,
            "questions": ai_result.get("questions", []),
            "evidence": ai_result.get("evidence", []),
            "reasoning": ai_result.get("reasoning"),
            "readiness": ai_result.get("readiness"),
        }

    except Exception as exc:
        return {
            "status": "FAILED",
            "routing": routing,
            "error": str(exc),
            "questions": [],
            "evidence": [],
            "reasoning": None,
            "readiness": {
                "status": "INSUFFICIENT",
                "process": False,
            },
        }


def analyze_daily_matches(
    matches: List[Dict[str, Any]],
) -> Dict[str, Any]:
    results = []

    for match in matches:
        result = analyze_daily_match(match)

        enriched_match = dict(match)
        enriched_match["v13_ai"] = result

        results.append(enriched_match)

    return {
        "status": "COMPLETED",
        "total": len(results),
        "completed": sum(
            1 for item in results
            if item["v13_ai"]["status"] == "COMPLETED"
        ),
        "insufficient": sum(
            1 for item in results
            if item["v13_ai"]["status"] == "INSUFFICIENT_EVIDENCE"
        ),
        "failed": sum(
            1 for item in results
            if item["v13_ai"]["status"] == "FAILED"
        ),
        "matches": results,
    }
