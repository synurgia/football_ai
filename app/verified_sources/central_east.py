"""Chunk 2: CENTRAL / EASTERN / SOUTHEASTERN EUROPE (20 competitions).

Honest coverage note: For most of these competitions, the free programmatic
sources are API-Football and ESPN only. TheSportsDB covers 4 of them.
openfootball covers 1-2. The federation HTML site (registered in V1.3)
is the third always-available source — it requires HTML scraping but
is always present.

No source is marked primary. The fetcher queries all of them in parallel
and the reconciler merges results, retaining conflicts.
"""

CENTRAL_EAST: dict = {

    "ita.1": {
        "name": "Serie A",
        "federation": "https://www.figc.it/",
        "sources": {
            "apif": 135, "espn": "ita.1", "tsdb": 4332,
            "fd": "SA", "ofb": "it.1",
        },
    },
    "gre.1": {
        "name": "Super League Greece",
        "federation": "https://www.epo.gr/",
        "sources": {
            "apif": 197, "espn": "gre.1", "tsdb": 4336,
        },
    },
    "tur.1": {
        "name": "Süper Lig",
        "federation": "https://www.tff.org/",
        "sources": {
            "apif": 203, "espn": "tur.1", "tsdb": 4339,
        },
    },
    "cro.1": {
        "name": "Croatian Football League",
        "federation": "https://hns-cff.hr/",
        "sources": {
            "apif": 210, "espn": "cro.1",
        },
    },
    "cze.1": {
        "name": "Czech First League",
        "federation": "https://www.fotbal.cz/",
        "sources": {
            "apif": 345, "espn": "cze.1",
        },
    },
    "pol.1": {
        "name": "Ekstraklasa",
        "federation": "https://www.pzpn.pl/",
        "sources": {
            "apif": 106, "espn": "pol.1",
        },
    },
    "rou.1": {
        "name": "Liga I",
        "federation": "https://www.frf.ro/",
        "sources": {
            "apif": 283, "espn": "rou.1", "ofb": "ro.1",
        },
    },
    "hun.1": {
        "name": "NB I",
        "federation": "https://www.mlsz.hu/",
        "sources": {
            "apif": 271, "espn": "hun.1",
        },
    },
    "srb.1": {
        "name": "Serbia SuperLiga",
        "federation": "https://fss.rs/",
        "sources": {
            "apif": 286, "espn": "srb.1",
        },
    },
    "ukr.1": {
        "name": "Ukrainian Premier League",
        "federation": "https://uaf.ua/",
        "sources": {
            "apif": 333, "espn": "ukr.1", "tsdb": 4354,
        },
    },
    "bul.1": {
        "name": "First Professional League",
        "federation": "https://bfunion.bg/",
        "sources": {
            "apif": 172, "espn": "bul.1",
        },
    },
    "svn.1": {
        "name": "PrvaLiga",
        "federation": "https://www.nzs.si/",
        "sources": {
            "apif": 373, "espn": "svn.1",
        },
    },
    "svk.1": {
        "name": "Niké Liga",
        "federation": "https://www.futbalsfz.sk/",
        "sources": {
            "apif": 332, "espn": "svk.1",
        },
    },
    "bih.1": {
        "name": "Bosnia Premier League",
        "federation": "https://www.nfsbih.ba/",
        "sources": {
            "apif": 315, "espn": "bih.1",
        },
    },
    "cyp.1": {
        "name": "Cyprus First Division",
        "federation": "https://www.cfa.com.cy/",
        "sources": {
            "apif": 318, "espn": "cyp.1",
        },
    },
    "geo.1": {
        "name": "Erovnuli Liga",
        "federation": "https://gff.ge/",
        "sources": {
            "apif": 327, "espn": "geo.1",
        },
    },
    "arm.1": {
        "name": "Armenian Premier League",
        "federation": "https://www.ffa.am/",
        "sources": {
            "apif": 342, "espn": "arm.1",
        },
    },
    "aze.1": {
        "name": "Azerbaijan Premier League",
        "federation": "https://www.affa.az/",
        "sources": {
            "apif": 419, "espn": "aze.1",
        },
    },
    "kaz.1": {
        "name": "Kazakhstan Premier League",
        "federation": "https://kff.kz/",
        "sources": {
            "apif": 389, "espn": "kaz.1",
        },
    },
    "rus.1": {
        "name": "Russian Premier League",
        "federation": "https://www.rfs.ru/",
        "sources": {
            "apif": 235, "espn": "rus.1", "tsdb": 4355,
        },
    },
}
