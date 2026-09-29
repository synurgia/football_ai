"""Chunk 5: AFRICA (15 competitions).

Coverage reality — the hardest region for free data:
  - API-Football covers ~14 of 15 (best programmatic source here).
  - ESPN covers ~10 (RSA, EGY, MAR, DZA, TUN, NGA, GHA, KEN, TAN, UGA).
  - TheSportsDB covers ZERO African leagues on free tier.
  - openfootball covers Egypt, Nigeria only.
  - Federation URLs recorded for HTML scraping.

HONEST NOTE: African leagues are the weakest-covered region on free tiers.
For 5 of these, API-Football + ESPN + federation HTML is the entire
available source set. No fourth source exists.
"""

AFRICA: dict = {

    "zaf.1": {
        "name": "Premier Soccer League",
        "federation": "https://www.safa.net/",
        "sources": {
            "apif": 288, "espn": "rsa.1",
        },
    },
    "egy.1": {
        "name": "Egyptian Premier League",
        "federation": "https://www.efa.com.eg/",
        "sources": {
            "apif": 233, "espn": "egy.1", "ofb": "eg.1",
        },
    },
    "mar.1": {
        "name": "Botola Pro",
        "federation": "https://www.frmf.ma/",
        "sources": {
            "apif": 200, "espn": "mar.1",
        },
    },
    "dza.1": {
        "name": "Ligue Professionnelle 1",
        "federation": "https://www.faf.dz/",
        "sources": {
            "apif": 186, "espn": "alg.1",
        },
    },
    "tun.1": {
        "name": "Ligue Professionnelle 1",
        "federation": "https://www.ftf.org.tn/",
        "sources": {
            "apif": 202, "espn": "tun.1",
        },
    },
    "nga.1": {
        "name": "Nigeria Premier Football League",
        "federation": "https://www.thenff.com/",
        "sources": {
            "apif": 399, "espn": "nga.1", "ofb": "ng.1",
        },
    },
    "gha.1": {
        "name": "Ghana Premier League",
        "federation": "https://www.ghanafa.org/",
        "sources": {
            "apif": 570, "espn": "gha.1",
        },
    },
    "ken.1": {
        "name": "Kenya Premier League",
        "federation": "https://footballkenya.org/",
        "sources": {
            "apif": 579, "espn": "ken.1",
        },
    },
    "tza.1": {
        "name": "Tanzania Premier League",
        "federation": "https://www.tff.or.tz/",
        "sources": {
            "apif": 567, "espn": "tan.1",
        },
    },
    "uga.1": {
        "name": "Uganda Premier League",
        "federation": "https://www.fufa.co.ug/",
        "sources": {
            "apif": 586, "espn": "uga.1",
        },
    },
    "zmb.1": {
        "name": "Zambia Super League",
        "federation": "https://www.faz.co.zm/",
        "sources": {
            "apif": 594, "espn": "zam.1",
        },
    },
    "ago.1": {
        "name": "Girabola",
        "federation": "https://www.faf.co.ao/",
        "sources": {
            "apif": 585, "espn": "ang.1",
        },
    },
    "cod.1": {
        "name": "Linafoot / Ligue 1",
        "federation": "https://www.fecofa.cd/",
        "sources": {
            "apif": 585, "espn": "cod.1",
        },
    },
    "sen.1": {
        "name": "Senegal Premier League",
        "federation": "https://www.fsf.sn/",
        "sources": {
            "apif": 401, "espn": "sen.1",
        },
    },
    "civ.1": {
        "name": "Ligue 1",
        "federation": "https://www.fifciv.com/",
        "sources": {
            "apif": 402, "espn": "civ.1",
        },
    },
}
