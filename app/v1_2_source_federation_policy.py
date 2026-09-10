from typing import Dict, Tuple

from app.v1_2_external_evidence_contract import (
    get_external_evidence_contracts,
)


DISCOVERY_ONLY_SOURCES: Tuple[str, ...] = (
    "google_search",
    "bing_search",
    "brave_search",
    "yandex_search",
)


def build_source_federation_policy() -> Dict[str, Dict[str, object]]:
    contracts = get_external_evidence_contracts()

    policy: Dict[str, Dict[str, object]] = {}

    for capability, contract in contracts.items():
        policy[capability] = {
            "acceptable_source_types": contract.acceptable_source_types,
            "discovery_only_sources": DISCOVERY_ONLY_SOURCES,
            "search_results_are_evidence": False,
            "requires_underlying_source": True,
        }

    return policy


def validate_source_federation_policy() -> None:
    contracts = get_external_evidence_contracts()
    policy = build_source_federation_policy()

    if set(policy) != set(contracts):
        raise RuntimeError(
            "Source federation policy does not cover every external capability."
        )

    for capability, entry in policy.items():
        if entry["search_results_are_evidence"] is not False:
            raise RuntimeError(
                f"{capability}: search results cannot be evidence."
            )

        if entry["requires_underlying_source"] is not True:
            raise RuntimeError(
                f"{capability}: underlying source requirement missing."
            )


if __name__ == "__main__":
    validate_source_federation_policy()

    policy = build_source_federation_policy()

    print("=== V1.2 SOURCE FEDERATION POLICY ===")
    print("EXTERNAL CAPABILITIES:", len(policy))
    print(
        "DISCOVERY-ONLY SOURCES:",
        ", ".join(DISCOVERY_ONLY_SOURCES),
    )
    print("SEARCH RESULTS ARE EVIDENCE: False")
    print("UNDERLYING SOURCE REQUIRED: True")
    print("RESULT: PASS")
