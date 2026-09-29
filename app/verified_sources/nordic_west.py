"""Chunk 1: NORDIC & NORTHERN EUROPE (8) + WESTERN & CENTRAL EUROPE (11)."""

NORDIC_WEST: dict = {

    # ---------------- NORDIC ----------------
    "isl.1": {
        "name": "Besta deild karla",
        "federation": "https://www.ksi.is/",
        "sources": {"apif": 164, "espn": "isl.1"},
    },
    "nor.1": {
        "name": "Eliteserien",
        "federation": "https://www.fotball.no/",
        "sources": {"apif": 103, "espn": "nor.1", "tsdb": 4358},
    },
    "fin.1": {
        "name": "Veikkausliiga",
        "federation": "https://www.palloliitto.fi/",
        "sources": {"apif": 244, "espn": "fin.1"},
    },
    "swe.1": {
        "name": "Allsvenskan",
        "federation": "https://www.svenskfotboll.se/",
        "sources": {"apif": 113, "espn": "swe.1", "tsdb": 4347},
    },
    "den.1": {
        "name": "Superliga",
        "federation": "https://www.dbu.dk/",
        "sources": {"apif": 119, "espn": "den.1", "tsdb": 4340},
    },
    "fro.1": {
        "name": "Faroe Islands Premier League",
        "federation": "https://www.fsf.fo/",
        "sources": {"apif": 367, "espn": "fro.1"},
    },
    "irl.1": {
        "name": "League of Ireland Premier Division",
        "federation": "https://www.fai.ie/",
        "sources": {"apif": 357, "espn": "irl.1"},
    },
    "nir.1": {
        "name": "NIFL Premiership",
        "federation": "https://www.irishfa.com/",
        "sources": {"apif": 408, "espn": "nir.1"},
    },

    # ---------------- WESTERN & CENTRAL EUROPE ----------------
    "eng.1": {
        "name": "Premier League",
        "federation": "https://www.thefa.com/",
        "sources": {
            "apif": 39, "espn": "eng.1", "tsdb": 4328,
            "fd": "PL", "ofb": "en.1",
        },
    },
    "eng.2": {
        "name": "Championship",
        "federation": "https://www.efl.com/",
        "sources": {
            "apif": 40, "espn": "eng.2", "tsdb": 4329,
            "fd": "ELC", "ofb": "en.2",
        },
    },
    "sco.1": {
        "name": "Scottish Premiership",
        "federation": "https://www.scottishfa.co.uk/",
        "sources": {"apif": 179, "espn": "sco.1", "tsdb": 4330, "ofb": "sc.1"},
    },
    "nl.1": {
        "name": "Eredivisie",
        "federation": "https://www.knvb.nl/",
        "sources": {
            "apif": 88, "espn": "ned.1", "tsdb": 4337,
            "fd": "DED", "ofb": "nl.1",
        },
    },
    "de.1": {
        "name": "Bundesliga",
        "federation": "https://www.dfb.de/",
        "sources": {
            "apif": 78, "espn": "ger.1", "tsdb": 4331,
            "fd": "BL1", "oldb": "bl1", "ofb": "de.1",
        },
    },
    "fr.1": {
        "name": "Ligue 1",
        "federation": "https://www.fff.fr/",
        "sources": {
            "apif": 61, "espn": "fra.1", "tsdb": 4334,
            "fd": "FL1", "ofb": "fr.1",
        },
    },
    "bel.1": {
        "name": "Belgian Pro League",
        "federation": "https://www.rbfa.be/",
        "sources": {"apif": 144, "espn": "bel.1", "tsdb": 4338},
    },
    "aut.1": {
        "name": "Austrian Bundesliga",
        "federation": "https://www.oefb.at/",
        "sources": {"apif": 218, "espn": "aut.1", "ofb": "at.1"},
    },
    "sui.1": {
        "name": "Swiss Super League",
        "federation": "https://www.football.ch/",
        "sources": {"apif": 207, "espn": "sui.1"},
    },
    "por.1": {
        "name": "Primeira Liga",
        "federation": "https://www.fpf.pt/",
        "sources": {
            "apif": 94, "espn": "por.1", "tsdb": 4344,
            "fd": "PPL", "ofb": "pt.1",
        },
    },
    "esp.1": {
        "name": "LaLiga",
        "federation": "https://www.rfef.es/",
        "sources": {
            "apif": 140, "espn": "esp.1", "tsdb": 4335,
            "fd": "PD", "ofb": "es.1",
        },
    },
}
