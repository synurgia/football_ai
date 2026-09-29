"""Chunk 4: ASIA & OCEANIA (17 competitions).

Coverage reality:
  - API-Football covers ~16 (all major Asian leagues).
  - ESPN covers ~17 (broadest free coverage of Asian football).
  - TheSportsDB covers 3 (Japan, China, Australia).
  - openfootball covers Japan, Australia, China.
  - Federation URLs recorded for HTML scraping fallback.

No source is primary. All queried in parallel.
"""

ASIA_OCEANIA: dict = {

    "jpn.1": {
        "name": "J1 League",
        "federation": "https://www.jfa.jp/",
        "sources": {
            "apif": 98, "espn": "jpn.1", "tsdb": 4353, "ofb": "jp.1",
        },
    },
    "kor.1": {
        "name": "K League 1",
        "federation": "https://www.kfa.or.kr/",
        "sources": {
            "apif": 292, "espn": "kor.1",
        },
    },
    "chn.1": {
        "name": "Chinese Super League",
        "federation": "https://www.thecfa.cn/",
        "sources": {
            "apif": 169, "espn": "chn.1", "tsdb": 4359, "ofb": "cn.1",
        },
    },
    "aus.1": {
        "name": "A-League Men",
        "federation": "https://www.footballaustralia.com.au/",
        "sources": {
            "apif": 188, "espn": "aus.1", "tsdb": 4356, "ofb": "au.1",
        },
    },
    "ind.1": {
        "name": "Indian Super League",
        "federation": "https://www.the-aiff.com/",
        "sources": {
            "apif": 323, "espn": "ind.1",
        },
    },
    "sau.1": {
        "name": "Saudi Pro League",
        "federation": "https://www.saff.com.sa/",
        "sources": {
            "apif": 307, "espn": "sau.1",
        },
    },
    "qat.1": {
        "name": "Qatar Stars League",
        "federation": "https://www.qfa.qa/",
        "sources": {
            "apif": 306, "espn": "qat.1",
        },
    },
    "are.1": {
        "name": "UAE Pro League",
        "federation": "https://www.uaefa.ae/",
        "sources": {
            "apif": 301, "espn": "uae.1",
        },
    },
    "irn.1": {
        "name": "Persian Gulf Pro League",
        "federation": "https://www.ffiri.ir/",
        "sources": {
            "apif": 290, "espn": "irn.1",
        },
    },
    "tha.1": {
        "name": "Thai League 1",
        "federation": "https://www.fathailand.org/",
        "sources": {
            "apif": 296, "espn": "tha.1",
        },
    },
    "mys.1": {
        "name": "Malaysia Super League",
        "federation": "https://www.fam.org.my/",
        "sources": {
            "apif": 278, "espn": "mys.1",
        },
    },
    "idn.1": {
        "name": "Liga 1",
        "federation": "https://www.pssi.org/",
        "sources": {
            "apif": 274, "espn": "idn.1",
        },
    },
    "vnm.1": {
        "name": "V.League 1",
        "federation": "https://www.vff.org.vn/",
        "sources": {
            "apif": 340, "espn": "vnm.1",
        },
    },
    "uzb.1": {
        "name": "Uzbekistan Super League",
        "federation": "https://www.ufa.uz/",
        "sources": {
            "apif": 369, "espn": "uzb.1",
        },
    },
    "irq.1": {
        "name": "Iraq Stars League",
        "federation": "https://ifa.iq/",
        "sources": {
            "apif": 543, "espn": "irq.1",
        },
    },
    "jor.1": {
        "name": "Jordan Pro League",
        "federation": "https://www.jfa.jo/",
        "sources": {
            "apif": 385, "espn": "jor.1",
        },
    },
    "isr.1": {
        "name": "Israeli Premier League",
        "federation": "https://www.football.org.il/",
        "sources": {
            "apif": 383, "espn": "isr.1",
        },
    },
}
