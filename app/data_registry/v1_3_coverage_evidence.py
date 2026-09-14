from dataclasses import dataclass, asdict
from datetime import date
from typing import List, Dict


@dataclass
class V13CoverageEvidence:
    competition_id: str
    competition_name: str
    source_id: str
    evidence_url: str = ""
    evidence_type: str = "UNVERIFIED"
    current_season: str = ""
    fixtures_confirmed: bool = False
    results_confirmed: bool = False
    verified_on: str = ""
    status: str = "UNVERIFIED"
    notes: str = ""


TARGETS = [
    ("bra.1", "Série A"),
    ("bra.2", "Série B"),
    ("bra.3", "Série C"),
    ("cyp.1", "Cyprus First Division"),
    ("cyp.2", "Cyprus Second Division"),
    ("dom.1", "Liga Dominicana"),
    ("dza.1", "Ligue Professionnelle 1"),
    ("dza.2", "Ligue Professionnelle 2"),
    ("cro.1", "Croatian Football League"),
    ("irn.1", "Persian Gulf Pro League"),
    ("irn.2", "Azadegan League"),
    ("per.1", "Liga 1"),
    ("per.2", "Liga 2"),
    ("tur.1", "Süper Lig"),
    ("tur.2", "1. Lig"),
    ("uefa.1", "UEFA Champions League"),
    ("uefa.2", "UEFA Europa League"),
    ("uefa.3", "UEFA Conference League"),
    ("uru.1", "Liga AUF"),
    ("uru.2", "Segunda"),
    ("zmb.1", "Zambia Super League"),
    ("zmb.2", "National Division One"),
]

SOURCE_IDS = [
    "gsa_global_football",
    "espn_football",
]


def build_empty_ledger() -> List[V13CoverageEvidence]:
    return [
        V13CoverageEvidence(
            competition_id=cid,
            competition_name=name,
            source_id=source_id,
            verified_on=str(date.today()),
        )
        for cid, name in TARGETS
        for source_id in SOURCE_IDS
    ]


def get_coverage_ledger() -> List[Dict]:
    return [asdict(x) for x in build_empty_ledger()]


def coverage_count() -> int:
    return len(build_empty_ledger())
