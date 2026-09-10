from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ExternalEvidenceContract:
    capability: str
    required_evidence: Tuple[str, ...]
    acceptable_source_types: Tuple[str, ...]
    verification_rule: str


EXTERNAL_EVIDENCE_CONTRACTS: Dict[str, ExternalEvidenceContract] = {
    "competition_context": ExternalEvidenceContract(
        "competition_context",
        ("competition identity", "season", "competition status"),
        ("official_competition", "official_federation", "football_data_provider"),
        "Competition identity and season must be explicitly supported by the source.",
    ),
    "competition_rules": ExternalEvidenceContract(
        "competition_rules",
        ("competition rules", "draw/penalty rules"),
        ("official_competition", "official_federation"),
        "Rule claims must come from an authoritative competition or federation source.",
    ),
    "financial_context": ExternalEvidenceContract(
        "financial_context",
        ("verified financial or ownership information",),
        ("official_club", "official_federation", "reputable_public_reporting"),
        "Financial claims require identifiable source evidence; absence of reporting is not evidence of absence.",
    ),
    "geopolitical_context": ExternalEvidenceContract(
        "geopolitical_context",
        ("verified relevant geopolitical or security context",),
        ("official_authority", "reputable_public_reporting"),
        "Only directly relevant, source-supported events may be recorded.",
    ),
    "market_context": ExternalEvidenceContract(
        "market_context",
        ("legitimate market or public outcome information",),
        ("legitimate_data_provider", "reputable_public_reporting"),
        "Market information must be explicitly sourced and must not be treated as a prediction by itself.",
    ),
    "match_status": ExternalEvidenceContract(
        "match_status",
        ("fixture identity", "kickoff/status information"),
        ("official_competition", "official_federation", "football_data_provider"),
        "The specific fixture must be matched by identifiable teams and competition/date context.",
    ),
    "motivation": ExternalEvidenceContract(
        "motivation",
        ("verified competition position or stated objective",),
        ("official_competition", "official_club", "official_federation", "reputable_public_reporting"),
        "Motivation must be supported by observable competitive circumstances or explicit statements.",
    ),
    "pitch_conditions": ExternalEvidenceContract(
        "pitch_conditions",
        ("venue", "surface or pitch condition"),
        ("official_venue", "official_competition", "official_club", "reputable_public_reporting"),
        "Pitch claims require fixture-specific venue or surface evidence.",
    ),
    "public_context": ExternalEvidenceContract(
        "public_context",
        ("verified public reputation, expectation, or coverage context",),
        ("official_club", "reputable_public_reporting"),
        "Public-context evidence must be attributable to an identifiable source.",
    ),
    "results": ExternalEvidenceContract(
        "results",
        ("completed match result",),
        ("official_competition", "official_federation", "football_data_provider"),
        "A result is verified only when the specific completed fixture is identified and its result is explicitly returned.",
    ),
    "schedule": ExternalEvidenceContract(
        "schedule",
        ("fixture date", "kickoff", "opponent"),
        ("official_competition", "official_federation", "football_data_provider"),
        "Schedule evidence must identify the specific fixture.",
    ),
    "standings": ExternalEvidenceContract(
        "standings",
        ("competition standings", "team position or points"),
        ("official_competition", "official_federation", "football_data_provider"),
        "Standings must identify the competition and relevant season.",
    ),
    "team_changes": ExternalEvidenceContract(
        "team_changes",
        ("verified squad, manager, tactical, or major organizational change",),
        ("official_club", "official_federation", "reputable_public_reporting"),
        "A change is verified only when the source explicitly reports the change.",
    ),
    "team_identity": ExternalEvidenceContract(
        "team_identity",
        ("team identity", "men's/women's designation", "competition participation"),
        ("official_club", "official_competition", "official_federation", "football_data_provider"),
        "Team identity must be explicitly attributable and match the requested fixture.",
    ),
    "weather_venue": ExternalEvidenceContract(
        "weather_venue",
        ("fixture venue", "weather conditions or forecast"),
        ("official_venue", "weather_provider", "official_competition"),
        "Weather evidence must be tied to the fixture venue and relevant match time.",
    ),
}


def get_external_evidence_contracts() -> Dict[str, ExternalEvidenceContract]:
    return dict(EXTERNAL_EVIDENCE_CONTRACTS)


def validate_external_evidence_contracts() -> None:
    expected = {
        "competition_context",
        "competition_rules",
        "financial_context",
        "geopolitical_context",
        "market_context",
        "match_status",
        "motivation",
        "pitch_conditions",
        "public_context",
        "results",
        "schedule",
        "standings",
        "team_changes",
        "team_identity",
        "weather_venue",
    }

    actual = set(EXTERNAL_EVIDENCE_CONTRACTS)

    if actual != expected:
        raise RuntimeError(
            "External evidence contract mismatch: "
            f"missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}"
        )


if __name__ == "__main__":
    validate_external_evidence_contracts()

    print("=== V1.2 EXTERNAL EVIDENCE CONTRACT ===")

    for capability, contract in sorted(EXTERNAL_EVIDENCE_CONTRACTS.items()):
        print(
            f"{capability}: "
            f"{len(contract.required_evidence)} requirement(s) | "
            f"{len(contract.acceptable_source_types)} source type(s)"
        )

    print()
    print("EXTERNAL CAPABILITIES:", len(EXTERNAL_EVIDENCE_CONTRACTS))
    print("RESULT: PASS")
