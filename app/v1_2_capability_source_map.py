from typing import Dict, Tuple

from app.source_capability_registry import build_default_registry
from app.v1_2_external_evidence_contract import get_external_evidence_contracts


CAPABILITY_SOURCE_MAP: Dict[str, Tuple[str, ...]] = {
    "competition_context": ("competition_context",),
    "competition_rules": ("competition_rules",),
    "financial_context": ("financial_context",),
    "geopolitical_context": ("geopolitical_context",),
    "market_context": ("market_context",),
    "match_status": ("match_status", "fixtures"),
    "motivation": ("motivation",),
    "pitch_conditions": ("pitch_conditions",),
    "public_context": ("public_context",),
    "results": ("results",),
    "schedule": ("schedule", "fixtures"),
    "standings": ("standings",),
    "team_changes": ("team_changes",),
    "team_identity": ("team_identity", "team_data"),
    "weather_venue": ("weather_venue",),
}


def resolve_sources_for_capability(
    capability: str,
) -> Tuple[str, ...]:
    registry = build_default_registry()

    required_capabilities = CAPABILITY_SOURCE_MAP.get(
        capability,
        (),
    )

    selected = []

    for provider_capability in required_capabilities:
        for source in registry.sources_for_capability(
            provider_capability
        ):
            if source.source_id not in selected:
                selected.append(source.source_id)

    return tuple(selected)


def resolve_sources_for_capability_and_country(
    capability: str,
    country_code: str | None = None,
) -> Dict[str, object]:
    registry = build_default_registry()

    required_capabilities = CAPABILITY_SOURCE_MAP.get(
        capability,
        (),
    )

    regional = []
    global_sources = []

    for provider_capability in required_capabilities:
        for source in registry.sources_for_capability(
            provider_capability
        ):
            if source.scope == "GLOBAL":
                if source.source_id not in global_sources:
                    global_sources.append(source.source_id)
                continue

            if (
                country_code
                and source.scope.upper()
                == country_code.upper()
                and source.source_id not in regional
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


def validate_capability_source_map() -> None:
    contracts = get_external_evidence_contracts()

    if set(CAPABILITY_SOURCE_MAP) != set(contracts):
        raise RuntimeError(
            "Capability source map does not cover every external capability."
        )


if __name__ == "__main__":
    validate_capability_source_map()

    print("=== V1.2 CAPABILITY → SOURCE MAP ===")

    for capability in sorted(CAPABILITY_SOURCE_MAP):
        sources = resolve_sources_for_capability(capability)
        print(
            f"{capability}: "
            f"{list(sources) if sources else 'NO_CONFIGURED_SOURCE'}"
        )

    print()
    print("EXTERNAL CAPABILITIES:", len(CAPABILITY_SOURCE_MAP))
    print("RESULT: PASS")
