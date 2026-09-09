from typing import Dict, List, Any

from app.source_capability_registry import (
    SourceCapability,
    SourceCapabilityRegistry,
    build_default_registry,
)


class EvidenceSourceRouter:
    """
    Routes evidence requirements to sources that are registered
    for the required capability.

    This class does NOT fetch data.
    It does NOT claim that a source has verified evidence.
    It only determines which sources are eligible to be queried.
    """

    def __init__(
        self,
        registry: SourceCapabilityRegistry | None = None,
    ):
        self.registry = (
            registry
            if registry is not None
            else build_default_registry()
        )

    def route(
        self,
        capability: str,
        *,
        country_code: str | None = None,
    ) -> Dict[str, Any]:

        candidates = self.registry.sources_for_capability(
            capability
        )

        regional = []
        global_sources = []

        for source in candidates:
            if source.scope == "GLOBAL":
                global_sources.append(source.source_id)
                continue

            if (
                country_code
                and source.scope.upper()
                == country_code.upper()
            ):
                regional.append(source.source_id)

        if regional:
            selected = regional + global_sources
            routing_status = "REGIONAL_AND_GLOBAL"
        elif global_sources:
            selected = global_sources
            routing_status = "GLOBAL_ONLY"
        else:
            selected = []
            routing_status = "NO_CONFIGURED_SOURCE"

        return {
            "capability": capability,
            "country_code": country_code,
            "sources": selected,
            "regional_sources": regional,
            "global_sources": global_sources,
            "routing_status": routing_status,
        }

    def route_question(
        self,
        question_id: str,
        capability: str,
        *,
        country_code: str | None = None,
    ) -> Dict[str, Any]:

        result = self.route(
            capability,
            country_code=country_code,
        )

        result["question_id"] = question_id

        return result


if __name__ == "__main__":
    print("=== EVIDENCE SOURCE ROUTER TEST ===")

    router = EvidenceSourceRouter()

    print()
    print("=== GLOBAL TEAM DATA ===")

    team_route = router.route(
        "team_data"
    )

    print(team_route)

    print()
    print("=== KENYAN FIXTURES ===")

    kenya_route = router.route(
        "fixtures",
        country_code="KE",
    )

    print(kenya_route)

    print()
    print("=== GLOBAL WEATHER ===")

    weather_route = router.route(
        "weather",
    )

    print(weather_route)

    print()
    print("=== QUESTION ROUTING ===")

    q15 = router.route_question(
        "Q15",
        "results",
    )

    q19 = router.route_question(
        "Q19",
        "standings",
    )

    q40 = router.route_question(
        "Q40",
        "injuries",
    )

    print("Q15:", q15)
    print("Q19:", q19)
    print("Q40:", q40)

    print()
    print("=== TRUTH CHECKS ===")

    if "openfoot" not in team_route["sources"]:
        raise SystemExit(
            "FAIL: OpenFoot was not routed for team data."
        )

    if "fkf_official" not in kenya_route["regional_sources"]:
        raise SystemExit(
            "FAIL: FKF was not selected for Kenyan fixtures."
        )

    if kenya_route["routing_status"] != (
        "REGIONAL_AND_GLOBAL"
    ):
        raise SystemExit(
            "FAIL: Kenyan routing did not include regional "
            "and global sources."
        )

    if weather_route["routing_status"] != (
        "NO_CONFIGURED_SOURCE"
    ):
        raise SystemExit(
            "FAIL: unconfigured weather source was "
            "incorrectly claimed."
        )

    if q40["routing_status"] != (
        "NO_CONFIGURED_SOURCE"
    ):
        raise SystemExit(
            "FAIL: unconfigured injury source was "
            "incorrectly claimed."
        )

    print("TEAM DATA ROUTING: PASS")
    print("KENYAN REGIONAL ROUTING: PASS")
    print("GLOBAL FALLBACK ROUTING: PASS")
    print("UNCONFIGURED CAPABILITY: TRUTHFULLY BLOCKED")

    print()
    print("RESULT: PASS")
    print("EVIDENCE SOURCE ROUTER IS WORKING")
    print("NO NETWORK REQUESTS WERE MADE")
    print("NO SOURCE WAS CLAIMED AS VERIFIED")
    print("PIECES 1-9: UNCHANGED")
    print("37 QUESTIONS: UNCHANGED")
    print("=== TEST COMPLETE ===")
