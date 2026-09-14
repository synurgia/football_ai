from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class CompetitionSource:
    """
    Describes one real data source associated with one football competition.

    The registry records source classification and verification state.
    It does NOT itself perform network requests.

    A source must not be considered production-available merely because
    a URL has been discovered. Verification must establish that the source
    actually covers the intended competition and provides usable data.
    """

    # Existing identity fields — preserved for backward compatibility.
    competition_id: str
    competition_name: str
    source_name: str
    source_url: str
    coverage_status: str

    # V1.3 source classification.
    source_role: str = "UNCLASSIFIED"
    authority_level: str = "UNKNOWN"

    # What the source is actually capable of providing.
    capabilities: Tuple[str, ...] = field(default_factory=tuple)

    # Season/scope information established during verification.
    season: str = ""

    # Verification state.
    verification_status: str = "UNVERIFIED"
    verification_notes: str = ""

    # Existing free-form notes remain available.
    notes: str = ""


class CompetitionRegistry:
    """
    Registry of football competitions and their available data sources.

    Multiple sources may be registered for the same competition.
    Legacy get() behavior is preserved for existing consumers.
    Federation-aware consumers should use get_all() so no source is discarded.
    """

    def __init__(self) -> None:
        self._sources: Dict[str, List[CompetitionSource]] = {}

    def register(self, source: CompetitionSource) -> None:
        sources = self._sources.setdefault(source.competition_id, [])

        for index, existing in enumerate(sources):
            if (
                existing.source_name == source.source_name
                and existing.source_url == source.source_url
            ):
                sources[index] = source
                return

        sources.append(source)

    def get(self, competition_id: str) -> Optional[CompetitionSource]:
        """
        Backward-compatible accessor.

        Returns the first registered source for legacy consumers.
        Federation-aware code should use get_all() so no source is discarded.
        """
        sources = self._sources.get(competition_id, [])
        return sources[0] if sources else None

    def get_all(self, competition_id: str) -> List[CompetitionSource]:
        """Return all registered sources for a competition."""
        return list(self._sources.get(competition_id, []))

    def list_competitions(self) -> List[CompetitionSource]:
        """Preserve the legacy flattened competition listing."""
        return [
            source
            for sources in self._sources.values()
            for source in sources
        ]

    def is_available(self, competition_id: str) -> bool:
        """
        A competition is available only when at least one registered source
        explicitly reports available coverage.
        """
        return any(
            source.coverage_status == "available"
            for source in self._sources.get(competition_id, [])
        )


# ============================================================
# V1.3 GLOBAL COMPETITION DISCOVERY CATALOGUE
# Authoritative discovery universe: V1_3_Global_Football_Competition_Map.pdf
# Total PDF entries: 195
#
# IMPORTANT:
# These records establish discovery/registry identity only.
# They do NOT claim that live data is available.
# ============================================================

V13_GLOBAL_COMPETITIONS = (

    # ---------------- EUROPE ----------------

    ("isl.1", "Besta deild karla"),
    ("isl.2", "1. deild karla"),

    ("nor.1", "Eliteserien"),
    ("nor.2", "OBOS-ligaen"),
    ("nor.3", "2. divisjon"),

    ("fin.1", "Veikkausliiga"),
    ("fin.2", "Ykkösliiga"),
    ("fin.3", "Ykkönen"),

    ("swe.1", "Allsvenskan"),
    ("swe.2", "Superettan"),
    ("swe.3", "Ettan"),

    ("den.1", "Superliga"),
    ("den.2", "1st Division"),

    ("fro.1", "Faroe Islands Premier League"),
    ("fro.2", "1. Deild"),

    ("irl.1", "League of Ireland Premier Division"),
    ("irl.2", "First Division"),

    ("nir.1", "NIFL Premiership"),
    ("nir.2", "NIFL Championship"),

    ("eng.1", "Premier League"),
    ("eng.2", "Championship"),
    ("eng.3", "League One"),
    ("eng.4", "League Two"),
    ("eng.5", "National League"),

    ("sco.1", "Scottish Premiership"),
    ("sco.2", "Championship"),
    ("sco.3", "League One"),
    ("sco.4", "League Two"),

    ("nl.1", "Eredivisie"),
    ("nl.2", "Eerste Divisie"),

    ("de.1", "Bundesliga"),
    ("de.2", "2. Bundesliga"),
    ("de.3", "3. Liga"),
    ("de.4", "Regionalliga"),

    ("fr.1", "Ligue 1"),
    ("fr.2", "Ligue 2"),
    ("fr.3", "National"),

    ("bel.1", "Belgian Pro League"),
    ("bel.2", "Challenger Pro League"),

    ("aut.1", "Bundesliga"),
    ("aut.2", "2. Liga"),
    ("aut.3", "Regionalliga"),

    ("sui.1", "Swiss Super League"),
    ("sui.2", "Challenge League"),

    ("por.1", "Primeira Liga"),
    ("por.2", "Liga Portugal 2"),

    ("esp.1", "La Liga"),
    ("esp.2", "Segunda División"),

    ("ita.1", "Serie A"),
    ("ita.2", "Serie B"),
    ("ita.3", "Serie C"),

    ("gre.1", "Super League"),
    ("gre.2", "Super League 2"),

    ("tur.1", "Süper Lig"),
    ("tur.2", "1. Lig"),

    ("cro.1", "Croatian Football League"),
    ("cro.2", "Prva NL"),

    ("cze.1", "Czech First League"),
    ("cze.2", "Czech National Football League"),

    ("pol.1", "Ekstraklasa"),
    ("pol.2", "I Liga"),

    ("rou.1", "Liga I"),
    ("rou.2", "Liga II"),

    ("hun.1", "Nemzeti Bajnokság I"),
    ("hun.2", "NB II"),

    ("srb.1", "Serbian SuperLiga"),
    ("srb.2", "Prva Liga"),

    ("ukr.1", "Ukrainian Premier League"),
    ("ukr.2", "Persha Liha"),

    ("bul.1", "First Professional Football League"),
    ("bul.2", "Second League"),

    ("svn.1", "PrvaLiga"),
    ("svn.2", "2. SNL"),

    ("svk.1", "Niké Liga"),
    ("svk.2", "2. Liga"),

    ("bih.1", "Premier League"),
    ("bih.2", "First League"),

    ("cyp.1", "Cypriot First Division"),
    ("cyp.2", "Second Division"),

    ("geo.1", "Erovnuli Liga"),
    ("geo.2", "Erovnuli Liga 2"),

    ("arm.1", "Armenian Premier League"),
    ("arm.2", "First League"),

    ("aze.1", "Azerbaijan Premier League"),
    ("aze.2", "First Division"),

    ("kaz.1", "Kazakhstan Premier League"),
    ("kaz.2", "First Division"),

    # ---------------- AMERICAS ----------------

    ("usa.1", "Major League Soccer"),
    ("usa.2", "Canadian Premier League"),
    ("usa.3", "USL Championship"),
    ("usa.4", "USL League One"),

    ("mex.1", "Liga MX"),
    ("mex.2", "Liga de Expansión MX"),

    ("crc.1", "Liga FPD"),
    ("hon.1", "Liga Nacional"),
    ("pan.1", "Liga Panameña de Fútbol"),
    ("dom.1", "Liga Dominicana de Fútbol"),

    ("arg.1", "Liga Profesional"),
    ("arg.2", "Primera Nacional"),

    ("bra.1", "Série A"),
    ("bra.2", "Série B"),
    ("bra.3", "Série C"),

    ("chi.1", "Primera División"),
    ("chi.2", "Primera B"),

    ("col.1", "Categoría Primera A"),
    ("col.2", "Primera B"),

    ("ecu.1", "LigaPro Serie A"),
    ("ecu.2", "Serie B"),

    ("per.1", "Liga 1"),
    ("per.2", "Liga 2"),

    ("uru.1", "Liga AUF Uruguaya"),
    ("uru.2", "Segunda División"),

    ("par.1", "Primera División"),
    ("par.2", "División Intermedia"),

    ("bol.1", "División de Fútbol Profesional"),

    # ---------------- ASIA & OCEANIA ----------------

    ("jpn.1", "J1 League"),
    ("jpn.2", "J2 League"),
    ("jpn.3", "J3 League"),

    ("kor.1", "K League 1"),
    ("kor.2", "K League 2"),

    ("chn.1", "Chinese Super League"),
    ("chn.2", "China League One"),

    ("ausnz.1", "A-League Men"),

    ("ind.1", "Indian Super League"),
    ("ind.2", "I-League"),

    ("sau.1", "Saudi Pro League"),
    ("sau.2", "Saudi First Division League"),

    ("qat.1", "Qatar Stars League"),
    ("qat.2", "Qatari Second Division"),

    ("are.1", "UAE Pro League"),
    ("are.2", "UAE First Division"),

    ("irn.1", "Persian Gulf Pro League"),
    ("irn.2", "Azadegan League"),

    ("tha.1", "Thai League 1"),
    ("tha.2", "Thai League 2"),

    ("mys.1", "Malaysia Super League"),
    ("mys.2", "Malaysia A1 Semi-Pro League"),

    ("idn.1", "Liga 1"),
    ("idn.2", "Liga 2"),

    ("vnm.1", "V.League 1"),
    ("vnm.2", "V.League 2"),

    ("uzb.1", "Uzbekistan Super League"),
    ("uzb.2", "Uzbekistan Pro League"),

    ("irq.1", "Iraq Stars League"),
    ("irq.2", "Iraq Premier Division"),

    ("jor.1", "Jordanian Pro League"),
    ("jor.2", "Jordan League Division 1"),

    ("isr.1", "Israeli Premier League"),
    ("isr.2", "Liga Leumit"),

    # ---------------- AFRICA ----------------

    ("zaf.1", "Premier Soccer League"),
    ("zaf.2", "Motsepe Foundation Championship"),

    ("egy.1", "Egyptian Premier League"),
    ("egy.2", "Egyptian Second Division"),

    ("mar.1", "Botola Pro"),
    ("mar.2", "Botola 2"),

    ("dza.1", "Ligue Professionnelle 1"),
    ("dza.2", "Ligue 2"),

    ("tun.1", "Tunisian Ligue Professionnelle 1"),
    ("tun.2", "Ligue 2"),

    ("nga.1", "Nigeria Premier Football League"),
    ("nga.2", "Nigeria National League"),

    ("gha.1", "Ghana Premier League"),
    ("gha.2", "Division One League"),

    ("ken.1", "Kenyan Premier League"),
    ("ken.2", "National Super League"),

    ("tza.1", "Tanzania Premier League"),
    ("tza.2", "Championship"),

    ("uga.1", "Uganda Premier League"),
    ("uga.2", "FUFA Big League"),

    ("zmb.1", "Zambia Super League"),
    ("zmb.2", "National Division One"),

    ("ago.1", "Girabola"),
    ("ago.2", "Segundona"),

    ("cod.1", "Linafoot / Ligue 1"),
    ("cod.2", "Ligue 2"),

    ("sen.1", "Senegal Premier League"),
    ("sen.2", "Ligue 2"),

    ("civ.1", "Ligue 1"),
    ("civ.2", "Ligue 2"),

    # ---------------- INTERNATIONAL / CONTINENTAL ----------------

    ("uefa.1", "Champions League"),
    ("uefa.2", "Europa League"),
    ("uefa.3", "Conference League"),

    ("conmebol.1", "Copa Libertadores"),
    ("conmebol.2", "Copa Sudamericana"),

    ("concacaf.1", "Champions Cup"),
    ("concacaf.2", "Leagues Cup"),

    ("afc.1", "AFC Champions League Elite"),
    ("afc.2", "Champions League Two"),

    ("caf.1", "CAF Champions League"),
    ("caf.2", "Confederation Cup"),

    ("ofc.1", "OFC Champions League"),
    ("ofc.2", "OFC Professional League"),

    ("fifa.1", "World Cup"),
    ("fifa.2", "Club World Cup"),
    ("fifa.3", "Intercontinental Cup"),
)


def register_v13_global_discovery_catalogue(registry: CompetitionRegistry) -> None:
    """
    Register every competition in the authoritative V1.3 PDF catalogue.

    These are discovery records only. They are deliberately NOT marked
    as live/available sources.
    """
    for competition_id, competition_name in V13_GLOBAL_COMPETITIONS:
        registry.register(
            CompetitionSource(
                competition_id=competition_id,
                competition_name=competition_name,
                source_name="V1.3 PDF Discovery Catalogue",
                source_url="",
                coverage_status="not_mapped",
                source_role="DISCOVERY",
                authority_level="PLANNING_CATALOGUE",
                capabilities=(),
                season="",
                verification_status="UNVERIFIED",
                verification_notes=(
                    "Competition discovered in the authoritative "
                    "V1.3 Global Football Competition Map PDF."
                ),
                notes=(
                    "Discovery record only. Live/source coverage must be "
                    "verified separately before activation."
                ),
            )
        )


# Convenience method added without changing legacy get()/get_all() behavior.
_CompetitionRegistry_original_init = CompetitionRegistry.__init__


def _competition_registry_v13_init(self) -> None:
    _CompetitionRegistry_original_init(self)
    register_v13_global_discovery_catalogue(self)


CompetitionRegistry.__init__ = _competition_registry_v13_init
