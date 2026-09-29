"""Layer 2 — Country / competition federation sources.

These are DISTINCT per competition. Every country has its own federation
and its own country-specific football sites. This is what makes each
competition's source set genuinely different.

Structure per competition:
  {
    "federation":  "<official federation URL>",   # always HTML
    "country_sites": [...],                        # national outlets
    "regional":   [...],                           # continental body
  }

These are scraped once per day by app/sources/daily_federation_job.py —
NOT per match. Match pipeline reads cached results from the DB.

No source here is primary. Every URL is a candidate. If one fails,
the others still provide data.
"""


# ================================================================
# AFRICA
# ================================================================

AFRICA = {

    "zaf.1": {
        "name": "Premier Soccer League",
        "federation": "https://www.safa.net/",
        "country_sites": [
            "https://www.psl.co.za/",
            "https://www.kickoff.com/",
            "https://www.soccerladuma.co.za/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "egy.1": {
        "name": "Egyptian Premier League",
        "federation": "https://www.efa.com.eg/",
        "country_sites": [
            "https://www.yallakora.com/",
            "https://www.filgoal.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "mar.1": {
        "name": "Botola Pro",
        "federation": "https://www.frmf.ma/",
        "country_sites": [
            "https://www.le360sport.ma/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "dza.1": {
        "name": "Ligue Professionnelle 1",
        "federation": "https://www.faf.dz/",
        "country_sites": [
            "https://www.dzfoot.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "tun.1": {
        "name": "Ligue Professionnelle 1",
        "federation": "https://www.ftf.org.tn/",
        "country_sites": [
            "https://www.tunisie-foot.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "nga.1": {
        "name": "Nigeria Premier Football League",
        "federation": "https://www.thenff.com/",
        "country_sites": [
            "https://www.completesports.com/",
            "https://www.brila.net/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "gha.1": {
        "name": "Ghana Premier League",
        "federation": "https://www.ghanafa.org/",
        "country_sites": [
            "https://www.ghanasoccernet.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "ken.1": {
        "name": "Kenya Premier League",
        "federation": "https://footballkenya.org/",
        "country_sites": [
            "https://www.futaa.co.ke/",
            "https://michezoafrika.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "tza.1": {
        "name": "Tanzania Premier League",
        "federation": "https://www.tff.or.tz/",
        "country_sites": [
            "https://binzubeiry.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "uga.1": {
        "name": "Uganda Premier League",
        "federation": "https://www.fufa.co.ug/",
        "country_sites": [
            "https://kawowo.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },

    "zmb.1": {
        "name": "Zambia Super League",
        "federation": "https://www.faz.co.zm/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },

    "ago.1": {
        "name": "Girabola",
        "federation": "https://www.faf.co.ao/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },

    "cod.1": {
        "name": "Linafoot / Ligue 1",
        "federation": "https://www.fecofa.cd/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },

    "sen.1": {
        "name": "Senegal Premier League",
        "federation": "https://www.fsf.sn/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },

    "civ.1": {
        "name": "Ligue 1",
        "federation": "https://www.fifciv.com/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
}


# ================================================================
# EUROPE — WESTERN
# ================================================================

EUROPE_WEST = {

    "eng.1": {
        "name": "Premier League",
        "federation": "https://www.thefa.com/",
        "country_sites": [
            "https://www.premierleague.com/",
            "https://www.bbc.co.uk/sport/football",
            "https://www.skysports.com/football",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "sco.1": {
        "name": "Scottish Premiership",
        "federation": "https://www.scottishfa.co.uk/",
        "country_sites": [
            "https://spfl.co.uk/",
            "https://www.bbc.co.uk/sport/scotland",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "nl.1": {
        "name": "Eredivisie",
        "federation": "https://www.knvb.nl/",
        "country_sites": [
            "https://eredivisie.nl/",
            "https://www.vi.nl/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "de.1": {
        "name": "Bundesliga",
        "federation": "https://www.dfb.de/",
        "country_sites": [
            "https://www.bundesliga.com/",
            "https://www.kicker.de/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "fr.1": {
        "name": "Ligue 1",
        "federation": "https://www.fff.fr/",
        "country_sites": [
            "https://www.ligue1.com/",
            "https://www.lequipe.fr/Football/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "bel.1": {
        "name": "Belgian Pro League",
        "federation": "https://www.rbfa.be/",
        "country_sites": [
            "https://www.proleague.be/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "aut.1": {
        "name": "Austrian Bundesliga",
        "federation": "https://www.oefb.at/",
        "country_sites": [
            "https://www.bundesliga.at/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "sui.1": {
        "name": "Swiss Super League",
        "federation": "https://www.football.ch/",
        "country_sites": [
            "https://www.sfl.ch/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "por.1": {
        "name": "Primeira Liga",
        "federation": "https://www.fpf.pt/",
        "country_sites": [
            "https://www.ligaportugal.pt/",
            "https://www.abola.pt/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "esp.1": {
        "name": "LaLiga",
        "federation": "https://www.rfef.es/",
        "country_sites": [
            "https://www.laliga.com/",
            "https://www.marca.com/futbol.html",
            "https://as.com/futbol/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    "ita.1": {
        "name": "Serie A",
        "federation": "https://www.figc.it/",
        "country_sites": [
            "https://www.legaseriea.it/",
            "https://www.gazzetta.it/Calcio/",
        ],
        "regional": ["https://www.uefa.com/"],
    },
}


# ================================================================
# EUROPE — CENTRAL / EASTERN / SE
# ================================================================

EUROPE_EAST = {

    "gre.1": {
        "name": "Super League Greece",
        "federation": "https://www.epo.gr/",
        "country_sites": ["https://www.slgr.gr/"],
        "regional": ["https://www.uefa.com/"],
    },
    "tur.1": {
        "name": "Süper Lig",
        "federation": "https://www.tff.org/",
        "country_sites": ["https://www.tff.org/Default.aspx?pageID=198"],
        "regional": ["https://www.uefa.com/"],
    },
    "cro.1": {
        "name": "Croatian Football League",
        "federation": "https://hns-cff.hr/",
        "country_sites": ["https://hnl.hr/"],
        "regional": ["https://www.uefa.com/"],
    },
    "cze.1": {
        "name": "Czech First League",
        "federation": "https://www.fotbal.cz/",
        "country_sites": ["https://www.fortunaliga.cz/"],
        "regional": ["https://www.uefa.com/"],
    },
    "pol.1": {
        "name": "Ekstraklasa",
        "federation": "https://www.pzpn.pl/",
        "country_sites": ["https://www.ekstraklasa.org/"],
        "regional": ["https://www.uefa.com/"],
    },
    "rou.1": {
        "name": "Liga I",
        "federation": "https://www.frf.ro/",
        "country_sites": ["https://www.lpf.ro/"],
        "regional": ["https://www.uefa.com/"],
    },
    "hun.1": {
        "name": "NB I",
        "federation": "https://www.mlsz.hu/",
        "country_sites": ["https://www.nb1.hu/"],
        "regional": ["https://www.uefa.com/"],
    },
    "srb.1": {
        "name": "Serbia SuperLiga",
        "federation": "https://fss.rs/",
        "country_sites": ["https://www.superliga.rs/"],
        "regional": ["https://www.uefa.com/"],
    },
    "ukr.1": {
        "name": "Ukrainian Premier League",
        "federation": "https://uaf.ua/",
        "country_sites": ["https://upl.ua/"],
        "regional": ["https://www.uefa.com/"],
    },
    "bul.1": {
        "name": "First Professional League",
        "federation": "https://bfunion.bg/",
        "country_sites": ["https://www.efbetleague.com/"],
        "regional": ["https://www.uefa.com/"],
    },
    "svn.1": {
        "name": "PrvaLiga",
        "federation": "https://www.nzs.si/",
        "country_sites": ["https://www.prvaliga.si/"],
        "regional": ["https://www.uefa.com/"],
    },
    "svk.1": {
        "name": "Niké Liga",
        "federation": "https://www.futbalsfz.sk/",
        "country_sites": ["https://www.nikeliga.sk/"],
        "regional": ["https://www.uefa.com/"],
    },
    "bih.1": {
        "name": "Bosnia Premier League",
        "federation": "https://www.nfsbih.ba/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "cyp.1": {
        "name": "Cyprus First Division",
        "federation": "https://www.cfa.com.cy/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "geo.1": {
        "name": "Erovnuli Liga",
        "federation": "https://gff.ge/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "arm.1": {
        "name": "Armenian Premier League",
        "federation": "https://www.ffa.am/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "aze.1": {
        "name": "Azerbaijan Premier League",
        "federation": "https://www.affa.az/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "kaz.1": {
        "name": "Kazakhstan Premier League",
        "federation": "https://kff.kz/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "rus.1": {
        "name": "Russian Premier League",
        "federation": "https://www.rfs.ru/",
        "country_sites": ["https://premierliga.ru/"],
        "regional": ["https://www.uefa.com/"],
    },
}


# ================================================================
# AMERICAS
# ================================================================

AMERICAS = {
    "usa.1": {
        "name": "Major League Soccer",
        "federation": "https://www.ussoccer.com/",
        "country_sites": [
            "https://www.mlssoccer.com/",
            "https://www.espn.com/soccer/",
        ],
        "regional": ["https://www.concacaf.com/"],
    },
    "mex.1": {
        "name": "Liga MX",
        "federation": "https://www.fmf.mx/",
        "country_sites": [
            "https://www.ligamx.net/",
            "https://www.mediotiempo.com/",
        ],
        "regional": ["https://www.concacaf.com/"],
    },
    "crc.1": {
        "name": "Liga FPD",
        "federation": "https://www.fcrf.cr/",
        "country_sites": ["https://www.unafut.com/"],
        "regional": ["https://www.concacaf.com/"],
    },
    "hon.1": {
        "name": "Liga Nacional",
        "federation": "https://fenafuth.org.hn/",
        "country_sites": ["https://www.diez.hn/"],
        "regional": ["https://www.concacaf.com/"],
    },
    "pan.1": {
        "name": "Liga Panameña de Fútbol",
        "federation": "https://www.fepafut.com/",
        "country_sites": [],
        "regional": ["https://www.concacaf.com/"],
    },
    "dom.1": {
        "name": "Liga Dominicana",
        "federation": "https://www.fedofutbol.org/",
        "country_sites": [],
        "regional": ["https://www.concacaf.com/"],
    },
    "arg.1": {
        "name": "Liga Profesional",
        "federation": "https://www.afa.com.ar/",
        "country_sites": [
            "https://www.ole.com.ar/",
            "https://www.tycsports.com/",
        ],
        "regional": ["https://www.conmebol.com/"],
    },
    "bra.1": {
        "name": "Série A",
        "federation": "https://www.cbf.com.br/",
        "country_sites": [
            "https://ge.globo.com/",
            "https://www.lance.com.br/",
        ],
        "regional": ["https://www.conmebol.com/"],
    },
    "chi.1": {
        "name": "Primera División",
        "federation": "https://www.anfp.cl/",
        "country_sites": ["https://www.anfp.cl/noticias"],
        "regional": ["https://www.conmebol.com/"],
    },
    "col.1": {
        "name": "Categoría Primera A",
        "federation": "https://fcf.com.co/",
        "country_sites": ["https://www.dimayor.com.co/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "ecu.1": {
        "name": "LigaPro Serie A",
        "federation": "https://www.fef.ec/",
        "country_sites": ["https://www.ligapro.ec/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "per.1": {
        "name": "Liga 1",
        "federation": "https://www.fpf.org.pe/",
        "country_sites": ["https://www.liga1.pe/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "uru.1": {
        "name": "Liga AUF Uruguay",
        "federation": "https://www.auf.org.uy/",
        "country_sites": ["https://www.auf.org.uy/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "par.1": {
        "name": "Primera División",
        "federation": "https://www.apf.org.py/",
        "country_sites": [],
        "regional": ["https://www.conmebol.com/"],
    },
    "bol.1": {
        "name": "División de Fútbol Profesional",
        "federation": "https://www.fbf.com.bo/",
        "country_sites": [],
        "regional": ["https://www.conmebol.com/"],
    },
    "ven.1": {
        "name": "Liga FUTVE",
        "federation": "https://www.fvf.com.ve/",
        "country_sites": ["https://www.ligafutve.com/"],
        "regional": ["https://www.conmebol.com/"],
    },
}


# ================================================================
# ASIA / OCEANIA
# ================================================================

ASIA_OCEANIA = {
    "jpn.1": {
        "name": "J1 League",
        "federation": "https://www.jfa.jp/",
        "country_sites": ["https://www.jleague.jp/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "kor.1": {
        "name": "K League 1",
        "federation": "https://www.kfa.or.kr/",
        "country_sites": ["https://www.kleague.com/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "chn.1": {
        "name": "Chinese Super League",
        "federation": "https://www.thecfa.cn/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "aus.1": {
        "name": "A-League Men",
        "federation": "https://www.footballaustralia.com.au/",
        "country_sites": ["https://aleagues.com.au/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "ind.1": {
        "name": "Indian Super League",
        "federation": "https://www.the-aiff.com/",
        "country_sites": ["https://www.indiansuperleague.com/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "sau.1": {
        "name": "Saudi Pro League",
        "federation": "https://www.saff.com.sa/",
        "country_sites": ["https://www.spl.com.sa/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "qat.1": {
        "name": "Qatar Stars League",
        "federation": "https://www.qfa.qa/",
        "country_sites": ["https://www.qsl.qa/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "are.1": {
        "name": "UAE Pro League",
        "federation": "https://www.uaefa.ae/",
        "country_sites": ["https://www.uaeproleague.ae/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "irn.1": {
        "name": "Persian Gulf Pro League",
        "federation": "https://www.ffiri.ir/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "tha.1": {
        "name": "Thai League 1",
        "federation": "https://www.fathailand.org/",
        "country_sites": ["https://www.thaileague.co.th/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "mys.1": {
        "name": "Malaysia Super League",
        "federation": "https://www.fam.org.my/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "idn.1": {
        "name": "Liga 1",
        "federation": "https://www.pssi.org/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "vnm.1": {
        "name": "V.League 1",
        "federation": "https://www.vff.org.vn/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "uzb.1": {
        "name": "Uzbekistan Super League",
        "federation": "https://www.ufa.uz/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "irq.1": {
        "name": "Iraq Stars League",
        "federation": "https://ifa.iq/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "jor.1": {
        "name": "Jordan Pro League",
        "federation": "https://www.jfa.jo/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "isr.1": {
        "name": "Israeli Premier League",
        "federation": "https://www.football.org.il/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
}


# ================================================================
# MERGE ALL REGIONS
# ================================================================

FEDERATIONS = {}
for _region in (AFRICA, EUROPE_WEST, EUROPE_EAST, AMERICAS, ASIA_OCEANIA):
    FEDERATIONS.update(_region)


def federation_for(competition_id):
    """Return federation block for a competition, or empty structure."""
    if not competition_id:
        return {"federation": None, "country_sites": [], "regional": []}
    entry = FEDERATIONS.get(str(competition_id).strip().lower())
    if not entry:
        return {"federation": None, "country_sites": [], "regional": []}
    return {
        "federation": entry.get("federation"),
        "country_sites": list(entry.get("country_sites") or []),
        "regional": list(entry.get("regional") or []),
    }


def all_federation_urls(competition_id):
    """Return every federation-related URL for a competition."""
    block = federation_for(competition_id)
    urls = []
    if block["federation"]:
        urls.append(block["federation"])
    urls.extend(block["country_sites"])
    urls.extend(block["regional"])
    return urls


def coverage_report():
    from collections import Counter
    c = Counter()
    for entry in FEDERATIONS.values():
        if entry.get("federation"):
            c["federation"] += 1
        c["country_sites"] += len(entry.get("country_sites") or [])
    return dict(c)


# ================================================================
# NORDIC & NORTHERN EUROPE
# ================================================================

NORDIC = {
    "isl.1": {
        "name": "Besta deild karla",
        "federation": "https://www.ksi.is/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "nor.1": {
        "name": "Eliteserien",
        "federation": "https://www.fotball.no/",
        "country_sites": ["https://www.eliteserien.no/"],
        "regional": ["https://www.uefa.com/"],
    },
    "fin.1": {
        "name": "Veikkausliiga",
        "federation": "https://www.palloliitto.fi/",
        "country_sites": ["https://www.veikkausliiga.com/"],
        "regional": ["https://www.uefa.com/"],
    },
    "swe.1": {
        "name": "Allsvenskan",
        "federation": "https://www.svenskfotboll.se/",
        "country_sites": ["https://www.allsvenskan.se/"],
        "regional": ["https://www.uefa.com/"],
    },
    "den.1": {
        "name": "Superliga",
        "federation": "https://www.dbu.dk/",
        "country_sites": ["https://www.superliga.dk/"],
        "regional": ["https://www.uefa.com/"],
    },
    "fro.1": {
        "name": "Faroe Islands Premier League",
        "federation": "https://www.fsf.fo/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "irl.1": {
        "name": "League of Ireland Premier Division",
        "federation": "https://www.fai.ie/",
        "country_sites": ["https://www.leagueofireland.ie/"],
        "regional": ["https://www.uefa.com/"],
    },
    "nir.1": {
        "name": "NIFL Premiership",
        "federation": "https://www.irishfa.com/",
        "country_sites": ["https://www.nifootballleague.com/"],
        "regional": ["https://www.uefa.com/"],
    },
}


# ================================================================
# INTERNATIONAL / CONTINENTAL
# ================================================================

INTERNATIONAL = {
    "uefa.1": {
        "name": "UEFA Champions League",
        "federation": "https://www.uefa.com/uefachampionsleague/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "uefa.2": {
        "name": "UEFA Europa League",
        "federation": "https://www.uefa.com/uefaeuropaleague/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "uefa.3": {
        "name": "UEFA Conference League",
        "federation": "https://www.uefa.com/uefaconferenceleague/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "uefa.nations": {
        "name": "UEFA Nations League",
        "federation": "https://www.uefa.com/uefanationsleague/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "uefa.u21q": {
        "name": "UEFA U-21 Qualifying",
        "federation": "https://www.uefa.com/under21/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "fifa.1": {
        "name": "FIFA World Cup",
        "federation": "https://www.fifa.com/",
        "country_sites": [],
        "regional": ["https://www.fifa.com/"],
    },
    "fifa.2": {
        "name": "FIFA Club World Cup",
        "federation": "https://www.fifa.com/",
        "country_sites": [],
        "regional": ["https://www.fifa.com/"],
    },
    "fifa.3": {
        "name": "FIFA Intercontinental Cup",
        "federation": "https://www.fifa.com/",
        "country_sites": [],
        "regional": ["https://www.fifa.com/"],
    },
    "caf.1": {
        "name": "CAF Champions League",
        "federation": "https://www.cafonline.com/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "caf.2": {
        "name": "CAF Confederation Cup",
        "federation": "https://www.cafonline.com/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "caf.afconq": {
        "name": "AFCON Qualifying",
        "federation": "https://www.cafonline.com/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "afc.1": {
        "name": "AFC Champions League Elite",
        "federation": "https://www.the-afc.com/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "afc.2": {
        "name": "AFC Champions League Two",
        "federation": "https://www.the-afc.com/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "concacaf.1": {
        "name": "Concacaf Champions Cup",
        "federation": "https://www.concacaf.com/",
        "country_sites": [],
        "regional": ["https://www.concacaf.com/"],
    },
    "concacaf.2": {
        "name": "Leagues Cup",
        "federation": "https://www.concacaf.com/",
        "country_sites": [],
        "regional": ["https://www.concacaf.com/"],
    },
    "concacaf.nations": {
        "name": "Concacaf Nations League",
        "federation": "https://www.concacaf.com/",
        "country_sites": [],
        "regional": ["https://www.concacaf.com/"],
    },
    "conmebol.1": {
        "name": "Copa Libertadores",
        "federation": "https://www.conmebol.com/",
        "country_sites": [],
        "regional": ["https://www.conmebol.com/"],
    },
    "conmebol.2": {
        "name": "Copa Sudamericana",
        "federation": "https://www.conmebol.com/",
        "country_sites": [],
        "regional": ["https://www.conmebol.com/"],
    },
    "ofc.1": {
        "name": "OFC Champions League",
        "federation": "https://www.oceaniafootball.com/",
        "country_sites": [],
        "regional": ["https://www.oceaniafootball.com/"],
    },
    "ofc.2": {
        "name": "OFC Professional League",
        "federation": "https://www.oceaniafootball.com/",
        "country_sites": [],
        "regional": ["https://www.oceaniafootball.com/"],
    },
}


# Merge into FEDERATIONS
for _reg in (NORDIC, INTERNATIONAL):
    FEDERATIONS.update(_reg)


# ================================================================
# EUROPE — 2nd / 3rd TIERS (Western)
# ================================================================

EUROPE_WEST_LOWER = {
    "eng.3": {
        "name": "League One",
        "federation": "https://www.efl.com/",
        "country_sites": ["https://www.efl.com/league-one/"],
        "regional": ["https://www.uefa.com/"],
    },
    "eng.4": {
        "name": "League Two",
        "federation": "https://www.efl.com/",
        "country_sites": ["https://www.efl.com/league-two/"],
        "regional": ["https://www.uefa.com/"],
    },
    "eng.5": {
        "name": "National League",
        "federation": "https://www.thenationalleague.org.uk/",
        "country_sites": ["https://www.thenationalleague.org.uk/"],
        "regional": ["https://www.thefa.com/"],
    },
    "sco.2": {
        "name": "Scottish Championship",
        "federation": "https://spfl.co.uk/",
        "country_sites": ["https://spfl.co.uk/league/championship"],
        "regional": ["https://www.scottishfa.co.uk/"],
    },
    "sco.3": {
        "name": "Scottish League One",
        "federation": "https://spfl.co.uk/",
        "country_sites": ["https://spfl.co.uk/league/league-one"],
        "regional": ["https://www.scottishfa.co.uk/"],
    },
    "sco.4": {
        "name": "Scottish League Two",
        "federation": "https://spfl.co.uk/",
        "country_sites": ["https://spfl.co.uk/league/league-two"],
        "regional": ["https://www.scottishfa.co.uk/"],
    },
    "ita.2": {
        "name": "Serie B",
        "federation": "https://www.figc.it/",
        "country_sites": [
            "https://www.legab.it/",
            "https://www.gazzetta.it/Calcio/Serie-B/",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "ita.3": {
        "name": "Serie C",
        "federation": "https://www.figc.it/",
        "country_sites": ["https://www.lega-pro.com/"],
        "regional": ["https://www.uefa.com/"],
    },
    "esp.2": {
        "name": "LaLiga 2",
        "federation": "https://www.rfef.es/",
        "country_sites": [
            "https://www.laliga.com/laliga-hypermotion",
            "https://www.marca.com/futbol/segunda-division.html",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "de.2": {
        "name": "2. Bundesliga",
        "federation": "https://www.dfb.de/",
        "country_sites": [
            "https://www.bundesliga.com/de/2bundesliga/",
            "https://www.kicker.de/2-bundesliga",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "de.3": {
        "name": "3. Liga",
        "federation": "https://www.dfb.de/",
        "country_sites": ["https://www.dfb.de/3-liga/"],
        "regional": ["https://www.uefa.com/"],
    },
    "de.4": {
        "name": "Regionalliga",
        "federation": "https://www.dfb.de/",
        "country_sites": ["https://www.dfb.de/regionalliga/"],
        "regional": ["https://www.uefa.com/"],
    },
    "fr.2": {
        "name": "Ligue 2",
        "federation": "https://www.fff.fr/",
        "country_sites": [
            "https://www.ligue2.fr/",
            "https://www.lequipe.fr/Football/ligue-2/",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "fr.3": {
        "name": "National",
        "federation": "https://www.fff.fr/",
        "country_sites": ["https://www.fff.fr/championnats/fff/national-1"],
        "regional": ["https://www.uefa.com/"],
    },
    "nl.2": {
        "name": "Eerste Divisie",
        "federation": "https://www.knvb.nl/",
        "country_sites": [
            "https://www.keukenkampioendivisie.nl/",
            "https://www.vi.nl/",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "por.2": {
        "name": "Liga Portugal 2",
        "federation": "https://www.fpf.pt/",
        "country_sites": ["https://www.ligaportugal.pt/pt/liga/liga-portugal-2/"],
        "regional": ["https://www.uefa.com/"],
    },
    "bel.2": {
        "name": "Challenger Pro League",
        "federation": "https://www.rbfa.be/",
        "country_sites": ["https://www.proleague.be/en/cpl"],
        "regional": ["https://www.uefa.com/"],
    },
    "aut.2": {
        "name": "2. Liga",
        "federation": "https://www.oefb.at/",
        "country_sites": ["https://www.2liga.at/"],
        "regional": ["https://www.uefa.com/"],
    },
    "aut.3": {
        "name": "Regionalliga",
        "federation": "https://www.oefb.at/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "sui.2": {
        "name": "Challenge League",
        "federation": "https://www.football.ch/",
        "country_sites": ["https://www.sfl.ch/challenge-league/"],
        "regional": ["https://www.uefa.com/"],
    },
    "gre.2": {
        "name": "Super League 2",
        "federation": "https://www.epo.gr/",
        "country_sites": ["https://www.sl2.gr/"],
        "regional": ["https://www.uefa.com/"],
    },
    "tur.2": {
        "name": "1. Lig",
        "federation": "https://www.tff.org/",
        "country_sites": ["https://www.tff.org/Default.aspx?pageID=198"],
        "regional": ["https://www.uefa.com/"],
    },
}


for _reg in (EUROPE_WEST_LOWER,):
    FEDERATIONS.update(_reg)


# ================================================================
# EUROPE — 2nd TIERS (Central / Eastern / SE)
# ================================================================

EUROPE_EAST_LOWER = {
    "rou.2": {
        "name": "Liga II",
        "federation": "https://www.frf.ro/",
        "country_sites": ["https://www.liga2.ro/"],
        "regional": ["https://www.uefa.com/"],
    },
    "pol.2": {
        "name": "I Liga",
        "federation": "https://www.pzpn.pl/",
        "country_sites": ["https://www.1liga.org/"],
        "regional": ["https://www.uefa.com/"],
    },
    "ukr.2": {
        "name": "Persha Liha",
        "federation": "https://uaf.ua/",
        "country_sites": ["https://pfl.ua/"],
        "regional": ["https://www.uefa.com/"],
    },
    "srb.2": {
        "name": "Prva Liga",
        "federation": "https://fss.rs/",
        "country_sites": ["https://prvaliga.rs/"],
        "regional": ["https://www.uefa.com/"],
    },
    "cro.2": {
        "name": "Prva NL",
        "federation": "https://hns-cff.hr/",
        "country_sites": ["https://www.drugahnl.hr/"],
        "regional": ["https://www.uefa.com/"],
    },
    "cze.2": {
        "name": "Czech National Football League",
        "federation": "https://www.fotbal.cz/",
        "country_sites": ["https://www.fnliga.cz/"],
        "regional": ["https://www.uefa.com/"],
    },
    "hun.2": {
        "name": "NB II",
        "federation": "https://www.mlsz.hu/",
        "country_sites": ["https://www.mlsz.hu/bajnoksagok"],
        "regional": ["https://www.uefa.com/"],
    },
    "svn.2": {
        "name": "2. SNL",
        "federation": "https://www.nzs.si/",
        "country_sites": ["https://www.nzs.si/tekmovanja/2-snl"],
        "regional": ["https://www.uefa.com/"],
    },
    "svk.2": {
        "name": "2. Liga",
        "federation": "https://www.futbalsfz.sk/",
        "country_sites": ["https://www.futbalsfz.sk/2-liga"],
        "regional": ["https://www.uefa.com/"],
    },
    "bul.2": {
        "name": "Second Professional League",
        "federation": "https://bfunion.bg/",
        "country_sites": ["https://bfunion.bg/competitions/2"],
        "regional": ["https://www.uefa.com/"],
    },
    "bih.2": {
        "name": "First League FBiH",
        "federation": "https://www.nfsbih.ba/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "cyp.2": {
        "name": "Cyprus Second Division",
        "federation": "https://www.cfa.com.cy/",
        "country_sites": ["https://www.cfa.com.cy/en/competitions/2"],
        "regional": ["https://www.uefa.com/"],
    },
    "geo.2": {
        "name": "Erovnuli Liga 2",
        "federation": "https://gff.ge/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "arm.2": {
        "name": "Armenian First League",
        "federation": "https://www.ffa.am/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "aze.2": {
        "name": "Azerbaijan First Division",
        "federation": "https://www.affa.az/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "kaz.2": {
        "name": "Kazakhstan First Division",
        "federation": "https://kff.kz/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "blr.1": {
        "name": "Belarusian Premier League",
        "federation": "https://www.bfunion.by/",
        "country_sites": ["https://www.pressball.by/"],
        "regional": ["https://www.uefa.com/"],
    },
    "blr.2": {
        "name": "Belarusian First League",
        "federation": "https://www.bfunion.by/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "est.1": {
        "name": "Premium Liiga",
        "federation": "https://jalgpall.ee/",
        "country_sites": ["https://jalgpall.ee/voistlused/premium-liiga"],
        "regional": ["https://www.uefa.com/"],
    },
    "kos.1": {
        "name": "Superliga",
        "federation": "https://www.ffk-kosova.com/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "fro.2": {
        "name": "1. Deild",
        "federation": "https://www.fsf.fo/",
        "country_sites": ["https://www.fsf.fo/kappingar"],
        "regional": ["https://www.uefa.com/"],
    },
}


for _reg in (EUROPE_EAST_LOWER,):
    FEDERATIONS.update(_reg)


# ================================================================
# AMERICAS — 2nd TIERS
# ================================================================

AMERICAS_LOWER = {
    "arg.2": {
        "name": "Primera Nacional",
        "federation": "https://www.afa.com.ar/",
        "country_sites": [
            "https://www.ole.com.ar/futbol-ascenso/",
            "https://www.tycsports.com/",
        ],
        "regional": ["https://www.conmebol.com/"],
    },
    "arg.3": {
        "name": "Copa Argentina",
        "federation": "https://www.afa.com.ar/",
        "country_sites": ["https://www.ole.com.ar/futbol-ascenso/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "bra.2": {
        "name": "Série B",
        "federation": "https://www.cbf.com.br/",
        "country_sites": [
            "https://ge.globo.com/futebol/brasileirao-serie-b/",
            "https://www.lance.com.br/",
        ],
        "regional": ["https://www.conmebol.com/"],
    },
    "bra.3": {
        "name": "Série C",
        "federation": "https://www.cbf.com.br/",
        "country_sites": ["https://ge.globo.com/futebol/brasileirao-serie-c/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "chi.2": {
        "name": "Primera B",
        "federation": "https://www.anfp.cl/",
        "country_sites": ["https://www.anfp.cl/noticias"],
        "regional": ["https://www.conmebol.com/"],
    },
    "col.2": {
        "name": "Primera B",
        "federation": "https://fcf.com.co/",
        "country_sites": ["https://www.dimayor.com.co/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "ecu.2": {
        "name": "LigaPro Serie B",
        "federation": "https://www.fef.ec/",
        "country_sites": ["https://www.ligapro.ec/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "per.2": {
        "name": "Liga 2",
        "federation": "https://www.fpf.org.pe/",
        "country_sites": ["https://www.liga1.pe/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "uru.2": {
        "name": "Segunda División",
        "federation": "https://www.auf.org.uy/",
        "country_sites": ["https://www.auf.org.uy/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "par.2": {
        "name": "División Intermedia",
        "federation": "https://www.apf.org.py/",
        "country_sites": [],
        "regional": ["https://www.conmebol.com/"],
    },
    "mex.2": {
        "name": "Liga de Expansión MX",
        "federation": "https://www.fmf.mx/",
        "country_sites": [
            "https://www.ligamx.net/",
            "https://www.mediotiempo.com/",
        ],
        "regional": ["https://www.concacaf.com/"],
    },
    "can.w.1": {
        "name": "Northern Super League",
        "federation": "https://canpl.ca/",
        "country_sites": ["https://www.northernsuperleague.ca/"],
        "regional": ["https://www.concacaf.com/"],
    },
}


for _reg in (AMERICAS_LOWER,):
    FEDERATIONS.update(_reg)


# ================================================================
# ASIA & OCEANIA — 2nd TIERS
# ================================================================

ASIA_OCEANIA_LOWER = {
    "jpn.2": {
        "name": "J2 League",
        "federation": "https://www.jfa.jp/",
        "country_sites": ["https://www.jleague.jp/en/j2/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "jpn.3": {
        "name": "J3 League",
        "federation": "https://www.jfa.jp/",
        "country_sites": ["https://www.jleague.jp/en/j3/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "kor.2": {
        "name": "K League 2",
        "federation": "https://www.kfa.or.kr/",
        "country_sites": ["https://www.kleague.com/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "chn.2": {
        "name": "China League One",
        "federation": "https://www.thecfa.cn/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "sau.2": {
        "name": "Saudi First Division",
        "federation": "https://www.saff.com.sa/",
        "country_sites": ["https://www.spl.com.sa/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "qat.2": {
        "name": "Qatar Second Division",
        "federation": "https://www.qfa.qa/",
        "country_sites": ["https://www.qsl.qa/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "are.2": {
        "name": "UAE First Division",
        "federation": "https://www.uaefa.ae/",
        "country_sites": ["https://www.uaeproleague.ae/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "irn.2": {
        "name": "Azadegan League",
        "federation": "https://www.ffiri.ir/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "tha.2": {
        "name": "Thai League 2",
        "federation": "https://www.fathailand.org/",
        "country_sites": ["https://www.thaileague.co.th/"],
        "regional": ["https://www.the-afc.com/"],
    },
    "mys.2": {
        "name": "A1 Semi-Pro League",
        "federation": "https://www.fam.org.my/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "idn.2": {
        "name": "Liga 2",
        "federation": "https://www.pssi.org/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "vnm.2": {
        "name": "V.League 2",
        "federation": "https://www.vff.org.vn/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "uzb.2": {
        "name": "Uzbekistan Pro League",
        "federation": "https://www.ufa.uz/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "irq.2": {
        "name": "Iraq Premier Division",
        "federation": "https://ifa.iq/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "jor.2": {
        "name": "Jordan Division 1",
        "federation": "https://www.jfa.jo/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
    "isr.2": {
        "name": "Liga Leumit",
        "federation": "https://www.football.org.il/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "ind.2": {
        "name": "I-League",
        "federation": "https://www.the-aiff.com/",
        "country_sites": ["https://www.i-league.org/"],
        "regional": ["https://www.the-afc.com/"],
    },
}


for _reg in (ASIA_OCEANIA_LOWER,):
    FEDERATIONS.update(_reg)


# ================================================================
# AFRICA — 2nd TIERS
# ================================================================

AFRICA_LOWER = {
    "egy.2": {
        "name": "Egyptian Second Division",
        "federation": "https://www.efa.com.eg/",
        "country_sites": [
            "https://www.yallakora.com/",
            "https://www.filgoal.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },
    "gha.2": {
        "name": "Division One League",
        "federation": "https://www.ghanafa.org/",
        "country_sites": ["https://www.ghanasoccernet.com/"],
        "regional": ["https://www.cafonline.com/"],
    },
    "ken.2": {
        "name": "National Super League",
        "federation": "https://footballkenya.org/",
        "country_sites": [
            "https://www.futaa.co.ke/",
            "https://michezoafrika.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },
    "tza.2": {
        "name": "Championship",
        "federation": "https://www.tff.or.tz/",
        "country_sites": ["https://binzubeiry.com/"],
        "regional": ["https://www.cafonline.com/"],
    },
    "uga.2": {
        "name": "FUFA Big League",
        "federation": "https://www.fufa.co.ug/",
        "country_sites": ["https://kawowo.com/"],
        "regional": ["https://www.cafonline.com/"],
    },
    "zaf.2": {
        "name": "Motsepe Foundation Championship",
        "federation": "https://www.safa.net/",
        "country_sites": [
            "https://www.psl.co.za/",
            "https://www.kickoff.com/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },
    "zmb.2": {
        "name": "National Division One",
        "federation": "https://www.faz.co.zm/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "ago.2": {
        "name": "Segundona",
        "federation": "https://www.faf.co.ao/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "cod.2": {
        "name": "Ligue 2",
        "federation": "https://www.fecofa.cd/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "sen.2": {
        "name": "Ligue 2",
        "federation": "https://www.fsf.sn/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "civ.2": {
        "name": "Ligue 2",
        "federation": "https://www.fifciv.com/",
        "country_sites": [],
        "regional": ["https://www.cafonline.com/"],
    },
    "dza.2": {
        "name": "Ligue 2",
        "federation": "https://www.faf.dz/",
        "country_sites": ["https://www.dzfoot.com/"],
        "regional": ["https://www.cafonline.com/"],
    },
    "tun.2": {
        "name": "Ligue 2",
        "federation": "https://www.ftf.org.tn/",
        "country_sites": ["https://www.tunisie-foot.com/"],
        "regional": ["https://www.cafonline.com/"],
    },
    "mar.2": {
        "name": "Botola 2",
        "federation": "https://www.frmf.ma/",
        "country_sites": ["https://www.le360sport.ma/"],
        "regional": ["https://www.cafonline.com/"],
    },
    "nga.2": {
        "name": "Nigeria National League",
        "federation": "https://www.thenff.com/",
        "country_sites": [
            "https://www.completesports.com/",
            "https://www.brila.net/",
        ],
        "regional": ["https://www.cafonline.com/"],
    },
}


for _reg in (AFRICA_LOWER,):
    FEDERATIONS.update(_reg)


# ================================================================
# CUPS
# ================================================================

CUPS = {
    "eng.cup": {
        "name": "FA Cup",
        "federation": "https://www.thefa.com/competitions/thefacup",
        "country_sites": [
            "https://www.bbc.co.uk/sport/football/fa-cup",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "eng.trophy": {
        "name": "EFL Trophy",
        "federation": "https://www.efl.com/",
        "country_sites": ["https://www.efl.com/competitions/efl-trophy/"],
        "regional": ["https://www.uefa.com/"],
    },
    "esp.cup": {
        "name": "Copa del Rey",
        "federation": "https://www.rfef.es/",
        "country_sites": [
            "https://www.marca.com/futbol/copa-del-rey.html",
            "https://as.com/futbol/copa_del_rey/",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "esp.w.cup": {
        "name": "Copa de la Reina",
        "federation": "https://www.rfef.es/",
        "country_sites": ["https://www.marca.com/futbol/futbol-femenino.html"],
        "regional": ["https://www.uefa.com/"],
    },
    "por.cup": {
        "name": "Taca de Portugal",
        "federation": "https://www.fpf.pt/",
        "country_sites": ["https://www.fpf.pt/competicoes/taca-de-portugal"],
        "regional": ["https://www.uefa.com/"],
    },
    "ita.cup": {
        "name": "Coppa Italia",
        "federation": "https://www.figc.it/",
        "country_sites": [
            "https://www.legaseriea.it/en/coppa-italia",
            "https://www.gazzetta.it/Calcio/Coppa-Italia/",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "sco.cup": {
        "name": "Scottish Cup",
        "federation": "https://www.scottishfa.co.uk/",
        "country_sites": ["https://www.scottishfa.co.uk/scottish-cup/"],
        "regional": ["https://www.uefa.com/"],
    },
    "sco.cup.q": {
        "name": "Scottish Cup Qualifying",
        "federation": "https://www.scottishfa.co.uk/",
        "country_sites": ["https://www.scottishfa.co.uk/scottish-cup/"],
        "regional": ["https://www.uefa.com/"],
    },
    "sco.challenge": {
        "name": "SPFL Challenge Cup",
        "federation": "https://spfl.co.uk/",
        "country_sites": ["https://spfl.co.uk/league/challenge-cup"],
        "regional": ["https://www.scottishfa.co.uk/"],
    },
    "chi.cup": {
        "name": "Copa Chile",
        "federation": "https://www.anfp.cl/",
        "country_sites": ["https://www.anfp.cl/noticias"],
        "regional": ["https://www.conmebol.com/"],
    },
    "col.cup": {
        "name": "Copa Colombia",
        "federation": "https://fcf.com.co/",
        "country_sites": ["https://www.dimayor.com.co/"],
        "regional": ["https://www.conmebol.com/"],
    },
    "bol.cup": {
        "name": "Copa Bolivia",
        "federation": "https://www.fbf.com.bo/",
        "country_sites": [],
        "regional": ["https://www.conmebol.com/"],
    },
    "gulf.cup": {
        "name": "Arabian Gulf Cup",
        "federation": "https://www.the-afc.com/",
        "country_sites": [],
        "regional": ["https://www.the-afc.com/"],
    },
}


# ================================================================
# WOMEN'S LEAGUES
# ================================================================

WOMENS = {
    "eng.w.1": {
        "name": "Women's Super League",
        "federation": "https://www.thefa.com/",
        "country_sites": [
            "https://womensleagues.thefa.com/",
            "https://www.bbc.co.uk/sport/football/womens",
        ],
        "regional": ["https://www.uefa.com/womenschampionsleague/"],
    },
    "esp.w.1": {
        "name": "Liga F",
        "federation": "https://www.rfef.es/",
        "country_sites": [
            "https://www.ligaf.es/",
            "https://www.marca.com/futbol/futbol-femenino.html",
        ],
        "regional": ["https://www.uefa.com/womenschampionsleague/"],
    },
    "fr.w.1": {
        "name": "Première Ligue",
        "federation": "https://www.fff.fr/",
        "country_sites": [
            "https://www.fff.fr/championnats/fff/d1-arkema",
            "https://www.lequipe.fr/Football/football-feminin/",
        ],
        "regional": ["https://www.uefa.com/womenschampionsleague/"],
    },
    "ned.w.1": {
        "name": "Vrouwen Eredivisie",
        "federation": "https://www.knvb.nl/",
        "country_sites": ["https://www.eredivisievrouwen.nl/"],
        "regional": ["https://www.uefa.com/womenschampionsleague/"],
    },
    "usa.w.1": {
        "name": "NWSL",
        "federation": "https://www.ussoccer.com/",
        "country_sites": ["https://www.nwslsoccer.com/"],
        "regional": ["https://www.concacaf.com/"],
    },
    "usa.w.2": {
        "name": "USL Super League",
        "federation": "https://www.ussoccer.com/",
        "country_sites": ["https://www.uslsuperleague.com/"],
        "regional": ["https://www.concacaf.com/"],
    },
    "usa.ncaaw": {
        "name": "NCAA Women's Soccer",
        "federation": "https://www.ncaa.com/sports/soccer-women",
        "country_sites": ["https://www.ncaa.com/sports/soccer-women/d1"],
        "regional": ["https://www.ussoccer.com/"],
    },
    "uefa.w.cup": {
        "name": "Women's Europa Cup",
        "federation": "https://www.uefa.com/womenschampionsleague/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
}


# ================================================================
# FRIENDLIES
# ================================================================

FRIENDLIES = {
    "friendly.club": {
        "name": "Club Friendly",
        "federation": None,
        "country_sites": [
            "https://www.espn.com/soccer/scoreboard",
            "https://www.flashscore.com/",
        ],
        "regional": [],
    },
    "friendly.intl.men": {
        "name": "Men's International Friendly",
        "federation": "https://www.fifa.com/",
        "country_sites": [
            "https://www.espn.com/soccer/scoreboard",
            "https://www.flashscore.com/",
        ],
        "regional": ["https://www.fifa.com/"],
    },
    "friendly.intl.women": {
        "name": "Women's International Friendly",
        "federation": "https://www.fifa.com/",
        "country_sites": [
            "https://www.espn.com/soccer/scoreboard",
            "https://www.flashscore.com/",
        ],
        "regional": ["https://www.fifa.com/"],
    },
}


for _reg in (CUPS, WOMENS, FRIENDLIES):
    FEDERATIONS.update(_reg)


# ================================================================
# FINAL 20 — closes the 235/235 catalogue
# ================================================================

FINAL_20 = {

    # --- Nordic / Northern Europe lower ---
    "isl.2": {
        "name": "1. deild karla",
        "federation": "https://www.ksi.is/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "nor.2": {
        "name": "OBOS-ligaen",
        "federation": "https://www.fotball.no/",
        "country_sites": ["https://www.obos-ligaen.no/"],
        "regional": ["https://www.uefa.com/"],
    },
    "nor.3": {
        "name": "2. divisjon",
        "federation": "https://www.fotball.no/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "fin.2": {
        "name": "Ykkösliiga",
        "federation": "https://www.palloliitto.fi/",
        "country_sites": ["https://www.ykkosliiga.fi/"],
        "regional": ["https://www.uefa.com/"],
    },
    "fin.3": {
        "name": "Ykkönen",
        "federation": "https://www.palloliitto.fi/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "swe.2": {
        "name": "Superettan",
        "federation": "https://www.svenskfotboll.se/",
        "country_sites": ["https://www.superettan.se/"],
        "regional": ["https://www.uefa.com/"],
    },
    "swe.3": {
        "name": "Ettan",
        "federation": "https://www.svenskfotboll.se/",
        "country_sites": [],
        "regional": ["https://www.uefa.com/"],
    },
    "den.2": {
        "name": "1st Division",
        "federation": "https://www.dbu.dk/",
        "country_sites": ["https://www.divisionsforeningen.dk/"],
        "regional": ["https://www.uefa.com/"],
    },
    "irl.2": {
        "name": "League of Ireland First Division",
        "federation": "https://www.fai.ie/",
        "country_sites": ["https://www.leagueofireland.ie/"],
        "regional": ["https://www.uefa.com/"],
    },
    "nir.2": {
        "name": "NIFL Championship",
        "federation": "https://www.irishfa.com/",
        "country_sites": ["https://www.nifootballleague.com/"],
        "regional": ["https://www.uefa.com/"],
    },

    # --- Western Europe lower ---
    "eng.2": {
        "name": "Championship",
        "federation": "https://www.efl.com/",
        "country_sites": [
            "https://www.efl.com/championship/",
            "https://www.bbc.co.uk/sport/football/championship",
            "https://www.skysports.com/football",
        ],
        "regional": ["https://www.uefa.com/"],
    },
    "eng.fa.cup.q": {
        "name": "FA Cup Qualifying",
        "federation": "https://www.thefa.com/competitions/thefacup/qualifying",
        "country_sites": [],
        "regional": ["https://www.thefa.com/"],
    },
    "ned.2": {
        "name": "Eerste Divisie",
        "federation": "https://www.knvb.nl/",
        "country_sites": [
            "https://www.keukenkampioendivisie.nl/",
            "https://www.vi.nl/",
        ],
        "regional": ["https://www.uefa.com/"],
    },

    # --- Americas ---
    "usa.2": {
        "name": "Canadian Premier League",
        "federation": "https://canpl.ca/",
        "country_sites": ["https://canpl.ca/"],
        "regional": ["https://www.concacaf.com/"],
    },
    "usa.3": {
        "name": "USL Championship",
        "federation": "https://www.uslsoccer.com/",
        "country_sites": [
            "https://www.uslchampionship.com/",
            "https://www.espn.com/soccer/",
        ],
        "regional": ["https://www.concacaf.com/"],
    },
    "usa.4": {
        "name": "USL League One",
        "federation": "https://www.uslsoccer.com/",
        "country_sites": ["https://www.uslleagueone.com/"],
        "regional": ["https://www.concacaf.com/"],
    },
    "usa.5": {
        "name": "NCAA Men's Soccer",
        "federation": "https://www.ncaa.com/sports/soccer-men",
        "country_sites": ["https://www.ncaa.com/sports/soccer-men/d1"],
        "regional": ["https://www.ussoccer.com/"],
    },
    "usa.cup": {
        "name": "U.S. Open Cup",
        "federation": "https://www.ussoccer.com/competitions/us-open-cup",
        "country_sites": ["https://www.ussoccer.com/competitions/us-open-cup"],
        "regional": ["https://www.concacaf.com/"],
    },
    "gtm.1": {
        "name": "Liga Nacional de Guatemala",
        "federation": "https://www.fedefutguate.org/",
        "country_sites": [],
        "regional": ["https://www.concacaf.com/"],
    },
    "slv.1": {
        "name": "Primera División de El Salvador",
        "federation": "https://www.fesfut.org.sv/",
        "country_sites": [],
        "regional": ["https://www.concacaf.com/"],
    },
}


for _reg in (FINAL_20,):
    FEDERATIONS.update(_reg)
