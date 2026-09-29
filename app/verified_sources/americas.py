"""Chunk 3: AMERICAS (22 competitions).

Coverage reality:
  - API-Football covers ~21 (all major CONMEBOL + CONCACAF leagues).
  - ESPN covers 22 (broadest free coverage of CONMEBOL).
  - TheSportsDB covers 2 (MLS 4346, Brazil Serie A 4351).
  - football-data.org covers 1 (Brasileirao BSA).
  - openfootball covers MLS, Liga MX, Brazil.
  - Federation URLs recorded for HTML scraping fallback.

No source is primary. All are queried in parallel.
"""

AMERICAS: dict = {

    # ---------- USA / CANADA ----------
    "usa.1": {
        "name": "Major League Soccer",
        "federation": "https://www.ussoccer.com/",
        "sources": {
            "apif": 253, "espn": "usa.1", "tsdb": 4346, "ofb": "us.1",
        },
    },
    "usa.2": {
        "name": "Canadian Premier League",
        "federation": "https://canpl.ca/",
        "sources": {
            "apif": 257, "espn": "usa.canadian",
        },
    },
    "usa.3": {
        "name": "USL Championship",
        "federation": "https://www.uslchampionship.com/",
        "sources": {
            "apif": 255, "espn": "usa.usl.1",
        },
    },
    "usa.4": {
        "name": "USL League One",
        "federation": "https://www.uslleagueone.com/",
        "sources": {
            "apif": 256, "espn": "usa.usl.l1",
        },
    },
    "usa.cup": {
        "name": "U.S. Open Cup",
        "federation": "https://www.ussoccer.com/",
        "sources": {
            "espn": "usa.open",
        },
    },
    "usa.w.1": {
        "name": "NWSL",
        "federation": "https://www.nwslsoccer.com/",
        "sources": {
            "apif": 254, "espn": "usa.nwsl",
        },
    },
    "usa.w.2": {
        "name": "USL Super League",
        "federation": "https://www.uslsuperleague.com/",
        "sources": {
            "espn": "usa.usl.w",
        },
    },

    # ---------- MEXICO / CENTRAL AMERICA ----------
    "mex.1": {
        "name": "Liga MX",
        "federation": "https://www.fmf.mx/",
        "sources": {
            "apif": 262, "espn": "mex.1", "tsdb": 4350, "ofb": "mx.1",
        },
    },
    "crc.1": {
        "name": "Liga FPD",
        "federation": "https://www.fcrf.cr/",
        "sources": {
            "apif": 162, "espn": "crc.1",
        },
    },
    "hon.1": {
        "name": "Liga Nacional",
        "federation": "https://fenafuth.org.hn/",
        "sources": {
            "apif": 234, "espn": "hon.1",
        },
    },
    "pan.1": {
        "name": "Liga Panameña de Fútbol",
        "federation": "https://www.fepafut.com/",
        "sources": {
            "apif": 304, "espn": "pan.1",
        },
    },
    "dom.1": {
        "name": "Liga Dominicana",
        "federation": "https://www.fedofutbol.org/",
        "sources": {
            "apif": 559, "espn": "dom.1",
        },
    },

    # ---------- SOUTH AMERICA ----------
    "arg.1": {
        "name": "Liga Profesional",
        "federation": "https://www.afa.com.ar/",
        "sources": {
            "apif": 128, "espn": "arg.1",
        },
    },
    "bra.1": {
        "name": "Série A",
        "federation": "https://www.cbf.com.br/",
        "sources": {
            "apif": 71, "espn": "bra.1", "tsdb": 4351,
            "fd": "BSA", "ofb": "br.1",
        },
    },
    "chi.1": {
        "name": "Primera División",
        "federation": "https://www.anfp.cl/",
        "sources": {
            "apif": 265, "espn": "chi.1",
        },
    },
    "col.1": {
        "name": "Categoría Primera A",
        "federation": "https://fcf.com.co/",
        "sources": {
            "apif": 239, "espn": "col.1",
        },
    },
    "ecu.1": {
        "name": "LigaPro Serie A",
        "federation": "https://www.fef.ec/",
        "sources": {
            "apif": 242, "espn": "ecu.1",
        },
    },
    "per.1": {
        "name": "Liga 1",
        "federation": "https://www.fpf.org.pe/",
        "sources": {
            "apif": 281, "espn": "per.1",
        },
    },
    "uru.1": {
        "name": "Liga AUF Uruguay",
        "federation": "https://www.auf.org.uy/",
        "sources": {
            "apif": 268, "espn": "uru.1",
        },
    },
    "par.1": {
        "name": "Primera División",
        "federation": "https://www.apf.org.py/",
        "sources": {
            "apif": 250, "espn": "par.1",
        },
    },
    "bol.1": {
        "name": "División de Fútbol Profesional",
        "federation": "https://www.fbf.com.bo/",
        "sources": {
            "apif": 344, "espn": "bol.1",
        },
    },
    "ven.1": {
        "name": "Liga FUTVE",
        "federation": "https://www.fvf.com.ve/",
        "sources": {
            "apif": 299, "espn": "ven.1",
        },
    },
}
