from typing import Dict, List


# ============================================================================
# GERMANY V1.3 QUESTION-SOURCE REGISTRY
# ============================================================================
# Purpose:
#   Question-specific evidence-source policy for German competitions.
#
# Architecture:
#   COMPETITION
#       -> QUESTION
#           -> AUTHORIZED SOURCES
#
# Rules:
#   - 37 active questions
#   - Q20-Q23 intentionally absent
#   - minimum 5 sources per question
#   - sources are filtered by competition
#   - no generic fallback
#   - no invented match URLs
#   - source authorization != evidence verification
#   - OpenFoot/ESPN are additive only
# ============================================================================


MIN_SOURCES_PER_QUESTION = 5


# ============================================================================
# GERMAN COMPETITIONS
# ============================================================================

COMPETITIONS = {
    "de.1": {
        "name": "Bundesliga",
        "country": "Germany",
        "gender": "men",
        "level": "top",
    },
    "de.2": {
        "name": "2. Bundesliga",
        "country": "Germany",
        "gender": "men",
        "level": "second",
    },
    "de.3": {
        "name": "3. Liga",
        "country": "Germany",
        "gender": "men",
        "level": "third",
    },
    "de.4": {
        "name": "Regionalliga",
        "country": "Germany",
        "gender": "men",
        "level": "regional",
    },
}


GERMANY_COMPETITIONS = list(COMPETITIONS.keys())


# ============================================================================
# EXACT 37-QUESTION SET
# ============================================================================

ACTIVE_QUESTIONS = list(range(1, 20)) + list(range(24, 42))


# ============================================================================
# SOURCE CATALOGUE
# ============================================================================
#
# coverage:
#   competition IDs for which this source is authorized.
#
# verification_status:
#   VERIFIED means the source itself is an accepted source endpoint.
#   It does NOT mean the particular match/question has been verified.
#
# free:
#   Source can be accessed without requiring a paid subscription/API.
#
# layers:
#   V1.3 evidence architecture layers.
# ============================================================================

SOURCES = {

    # ------------------------------------------------------------------------
    # GERMAN FOOTBALL / IDENTITY / OFFICIAL
    # ------------------------------------------------------------------------

    "dfb": {
        "name": "Deutscher Fußball-Bund",
        "url": "https://www.dfb.de/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 4],
    },

    "fussball_de": {
        "name": "FUSSBALL.DE",
        "url": "https://www.fussball.de/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3],
    },

    "kicker": {
        "name": "kicker",
        "url": "https://www.kicker.de/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3, 4],
    },

    "transfermarkt": {
        "name": "Transfermarkt",
        "url": "https://www.transfermarkt.com/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3],
    },

    "worldfootball": {
        "name": "WorldFootball",
        "url": "https://www.worldfootball.net/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3],
    },

    "soccerway": {
        "name": "Soccerway",
        "url": "https://int.soccerway.com/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3],
    },

    "flashscore": {
        "name": "Flashscore",
        "url": "https://www.flashscore.com/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3],
    },

    "365scores": {
        "name": "365Scores",
        "url": "https://www.365scores.com/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3],
    },

    # ------------------------------------------------------------------------
    # TOP-TIER ADDITIVE SOURCES
    # ------------------------------------------------------------------------

    "bundesliga": {
        "name": "Bundesliga.com",
        "url": "https://www.bundesliga.com/",
        "coverage": ["de.1"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3, 4],
    },

    "espn": {
        "name": "ESPN Soccer",
        "url": "https://www.espn.com/soccer/",
        "coverage": ["de.1", "de.2"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [1, 2, 3],
    },

    "footystats": {
        "name": "FootyStats",
        "url": "https://footystats.org/",
        "coverage": ["de.1", "de.2", "de.3"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [2, 3],
    },

    # ------------------------------------------------------------------------
    # NEWS / EXTERNAL SIGNAL
    # ------------------------------------------------------------------------

    "reuters": {
        "name": "Reuters",
        "url": "https://www.reuters.com/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [4],
    },

    "bbc_sport": {
        "name": "BBC Sport Football",
        "url": "https://www.bbc.com/sport/football",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [4],
    },

    "dw": {
        "name": "Deutsche Welle",
        "url": "https://www.dw.com/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [4],
    },

    "sky_de": {
        "name": "Sky Sport Germany",
        "url": "https://sport.sky.de/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [3, 4],
    },

    # ------------------------------------------------------------------------
    # WEATHER
    # ------------------------------------------------------------------------

    "dwd": {
        "name": "Deutscher Wetterdienst",
        "url": "https://www.dwd.de/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [4],
    },

    "open_meteo": {
        "name": "Open-Meteo",
        "url": "https://open-meteo.com/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [4],
    },

    "meteostat": {
        "name": "Meteostat",
        "url": "https://meteostat.net/",
        "coverage": ["de.1", "de.2", "de.3", "de.4"],
        "free": True,
        "verification_status": "VERIFIED",
        "layers": [4],
    },
}


# ============================================================================
# QUESTION-SPECIFIC SOURCE POLICY
# ============================================================================
#
# IMPORTANT:
# These are CANDIDATE sources.
#
# bind_for_match_de() filters them against the actual competition.
#
# Therefore:
#   de.1 != de.4
#   if a source does not cover the competition, it is removed.
#
# No fallback source is silently inserted.
# ============================================================================

QUESTION_SOURCES_DE = {

    # ------------------------------------------------------------------------
    # Q1-Q19
    # ------------------------------------------------------------------------

    1: [
        "dfb",
        "fussball_de",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
    ],

    2: [
        "dfb",
        "fussball_de",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "flashscore",
        "365scores",
    ],

    3: [
        "dfb",
        "fussball_de",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
    ],

    4: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    5: [
        "fussball_de",
        "dfb",
        "kicker",
        "flashscore",
        "soccerway",
        "365scores",
        "worldfootball",
    ],

    6: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    7: [
        "reuters",
        "bbc_sport",
        "dw",
        "sky_de",
        "dfb",
        "kicker",
        "fussball_de",
    ],

    8: [
        "bbc_sport",
        "sky_de",
        "dw",
        "reuters",
        "kicker",
        "dfb",
        "fussball_de",
    ],

    9: [
        "fussball_de",
        "dfb",
        "kicker",
        "flashscore",
        "soccerway",
        "365scores",
        "worldfootball",
    ],

    10: [
        "fussball_de",
        "dfb",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "flashscore",
        "365scores",
    ],

    11: [
        "fussball_de",
        "dfb",
        "kicker",
        "flashscore",
        "soccerway",
        "365scores",
        "worldfootball",
    ],

    12: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    13: [
        "footystats",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
    ],

    14: [
        "transfermarkt",
        "kicker",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    15: [
        "kicker",
        "transfermarkt",
        "fussball_de",
        "dfb",
        "worldfootball",
        "flashscore",
        "365scores",
    ],

    16: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    17: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    18: [
        "kicker",
        "fussball_de",
        "dfb",
        "transfermarkt",
        "worldfootball",
        "flashscore",
        "365scores",
    ],

    19: [
        "dfb",
        "fussball_de",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
    ],

    # ------------------------------------------------------------------------
    # Q20-Q23 INTENTIONALLY ABSENT
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Q24-Q41
    # ------------------------------------------------------------------------

    24: [
        "dfb",
        "fussball_de",
        "kicker",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
    ],

    25: [
        "fussball_de",
        "dfb",
        "kicker",
        "flashscore",
        "soccerway",
        "365scores",
        "worldfootball",
    ],

    26: [
        "dwd",
        "open_meteo",
        "meteostat",
        "fussball_de",
        "kicker",
        "dfb",
        "flashscore",
    ],

    27: [
        "transfermarkt",
        "kicker",
        "dfb",
        "fussball_de",
        "worldfootball",
        "flashscore",
        "365scores",
    ],

    28: [
        "kicker",
        "dfb",
        "fussball_de",
        "reuters",
        "bbc_sport",
        "dw",
        "sky_de",
    ],

    29: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    30: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    31: [
        "kicker",
        "transfermarkt",
        "fussball_de",
        "worldfootball",
        "flashscore",
        "365scores",
        "footystats",
    ],

    32: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    33: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    34: [
        "fussball_de",
        "dfb",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "flashscore",
        "soccerway",
    ],

    35: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    36: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    37: [
        "kicker",
        "transfermarkt",
        "worldfootball",
        "soccerway",
        "flashscore",
        "365scores",
        "footystats",
    ],

    38: [
        "dfb",
        "fussball_de",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "flashscore",
        "365scores",
    ],

    39: [
        "fussball_de",
        "dfb",
        "kicker",
        "transfermarkt",
        "worldfootball",
        "flashscore",
        "soccerway",
    ],

    40: [
        "kicker",
        "transfermarkt",
        "fussball_de",
        "dfb",
        "worldfootball",
        "flashscore",
        "365scores",
    ],

    41: [
        "kicker",
        "fussball_de",
        "dfb",
        "transfermarkt",
        "worldfootball",
        "flashscore",
        "365scores",
    ],
}


# ============================================================================
# HELPERS
# ============================================================================

def _competition_is_valid(competition_id: str) -> bool:
    return competition_id in COMPETITIONS


def _authorized_sources_for_question(
    question_id: int,
    competition_id: str,
) -> List[str]:

    if not _competition_is_valid(competition_id):
        return []

    candidate_sources = QUESTION_SOURCES_DE.get(question_id, [])

    authorized = []

    for source_id in candidate_sources:
        source = SOURCES.get(source_id)

        if source is None:
            continue

        if competition_id not in source["coverage"]:
            continue

        if source.get("free") is not True:
            continue

        if source.get("verification_status") != "VERIFIED":
            continue

        authorized.append(source_id)

    return authorized


def _source_payload(
    source_id: str,
    question_id: int,
    competition_id: str,
    match_id: str = "",
    date: str = "",
) -> Dict[str, object]:

    source = SOURCES[source_id]

    return {
        "source_id": source_id,
        "name": source["name"],
        "url": source["url"],

        "competition_id": competition_id,
        "competition_name": COMPETITIONS[competition_id]["name"],

        "question_id": question_id,

        "match_id": match_id,
        "date": date,

        "country": "Germany",
        "gender": "men",

        "free": source["free"],
        "verified_source": True,
        "authorized": True,

        # Important:
        # This is NOT match evidence verification.
        "evidence_status": "UNVERIFIED",

        "layers": source["layers"],

        # Explicitly prevent the old fallback behaviour.
        "fallback": False,

        # URL is the source endpoint only.
        # The resolver must discover/verify the actual match locator.
        "match_url_verified": False,
    }


# ============================================================================
# PUBLIC SOURCE ACCESS
# ============================================================================

def sources_for_question_de(
    question_id: int,
    competition_id: str,
) -> List[Dict[str, object]]:

    source_ids = _authorized_sources_for_question(
        question_id,
        competition_id,
    )

    return [
        _source_payload(
            source_id,
            question_id,
            competition_id,
        )
        for source_id in source_ids
    ]


def coverage_de(
    competition_id: str,
) -> Dict[str, object]:

    if not _competition_is_valid(competition_id):
        return {}

    return {
        "competition_id": competition_id,
        "competition_name": COMPETITIONS[competition_id]["name"],
        "questions": {
            f"Q{question_id}": len(
                _authorized_sources_for_question(
                    question_id,
                    competition_id,
                )
            )
            for question_id in ACTIVE_QUESTIONS
        },
    }


# ============================================================================
# MATCH BINDER
# ============================================================================

def bind_for_match_de(
    competition_id: str,
    competition_name: str = "",
    match_id: str = "",
    date: str = "",
) -> Dict[str, List[Dict[str, object]]]:

    if competition_id not in COMPETITIONS:
        return {}

    result: Dict[str, List[Dict[str, object]]] = {}

    for question_id in ACTIVE_QUESTIONS:

        source_ids = _authorized_sources_for_question(
            question_id,
            competition_id,
        )

        result[f"Q{question_id}"] = [
            _source_payload(
                source_id=source_id,
                question_id=question_id,
                competition_id=competition_id,
                match_id=match_id,
                date=date,
            )
            for source_id in source_ids
        ]

    return result


# ============================================================================
# AUDIT
# ============================================================================

def audit_germany_source_registry() -> None:

    assert len(COMPETITIONS) == 4
    assert set(COMPETITIONS) == {
        "de.1",
        "de.2",
        "de.3",
        "de.4",
    }

    assert len(ACTIVE_QUESTIONS) == 37

    assert set(QUESTION_SOURCES_DE) == set(
        ACTIVE_QUESTIONS
    )

    for question_id in ACTIVE_QUESTIONS:

        candidate_sources = QUESTION_SOURCES_DE[question_id]

        assert len(candidate_sources) >= MIN_SOURCES_PER_QUESTION

        assert len(candidate_sources) == len(
            set(candidate_sources)
        )

        for source_id in candidate_sources:
            assert source_id in SOURCES

    print()
    print("=" * 72)
    print("GERMANY QUESTION-SOURCE REGISTRY AUDIT")
    print("=" * 72)

    print(f"competitions = {len(COMPETITIONS)}")
    print(f"questions = {len(ACTIVE_QUESTIONS)}")
    print(f"minimum_sources = {MIN_SOURCES_PER_QUESTION}")

    print()
    print("COMPETITION COVERAGE")

    for competition_id, competition in COMPETITIONS.items():

        counts = []

        for question_id in ACTIVE_QUESTIONS:

            count = len(
                _authorized_sources_for_question(
                    question_id,
                    competition_id,
                )
            )

            counts.append(count)

        minimum = min(counts)
        maximum = max(counts)

        print(
            f"{competition_id:5} | "
            f"{competition['name']:<18} | "
            f"min={minimum} | "
            f"max={maximum}"
        )

        assert minimum >= MIN_SOURCES_PER_QUESTION

    print()
    print("QUESTION COVERAGE")

    for question_id in ACTIVE_QUESTIONS:

        counts = {
            competition_id: len(
                _authorized_sources_for_question(
                    question_id,
                    competition_id,
                )
            )
            for competition_id in GERMANY_COMPETITIONS
        }

        assert min(counts.values()) >= MIN_SOURCES_PER_QUESTION

        print(
            f"Q{question_id:02d} | "
            + " | ".join(
                f"{competition_id}={count}"
                for competition_id, count in counts.items()
            )
        )

    print()
    print("✓ GERMANY SOURCE REGISTRY READY")
    print("✓ 4 GERMAN COMPETITIONS")
    print("✓ 37 ACTIVE QUESTIONS")
    print("✓ QUESTION-SPECIFIC SOURCE POLICY")
    print("✓ COMPETITION FILTERING")
    print("✓ >=5 AUTHORIZED SOURCES PER QUESTION")
    print("✓ NO GENERIC FALLBACK")
    print("✓ NO INVENTED MATCH URL")
    print("✓ SOURCE AUTHORIZATION SEPARATE FROM EVIDENCE VERIFICATION")
    print("✓ Q20-Q23 INTENTIONALLY ABSENT")
    print("=" * 72)


# ============================================================================
# DIRECT EXECUTION
# ============================================================================

if __name__ == "__main__":
    audit_germany_source_registry()
