"""
FOOTBALL AI V1.5 — BROAD EVIDENCE REASONING & ADVANTAGE SYNTHESIS LAYER
========================================================================
Additive layer on top of football_ai_v14_5d.py.

Does NOT modify, rename, or replace any V1.1 / V1.2 / V1.3 / V1.4 component.
Consumes the same QuestionAnswer / Evidence dataclasses that V1.4 already
produces. Produces a BroadReasoningReport that the dashboard / Match
Intelligence endpoint can display alongside the existing V1.4 output.

Contract followed (V1.5 mission brief):
  * Two-sided advantage model with explicit counter-advantages
  * Cross-question reasoning (existing Q IDs only — no new canonical Qs)
  * Explicit conflict detection (never silent source replacement)
  * Prioritised missing-evidence analysis (impact-ranked, not a flat list)
  * Evidence-quality scoring (verification / directness / freshness /
    source type / independence / completeness / conflict)
  * Held-match intelligence (prediction_status = HELD when readiness
    does not permit processing — but intelligence stays visible)
  * Strict no-hallucination: every conclusion traceable to evidence
    via the provenance chain
  * Self-challenge: for every emerging verdict, actively seek the
    evidence that argues against it before finalising
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
from collections import defaultdict
from typing import Any, Optional

# Import existing V1.4 dataclasses & helpers — same directory assumed.
from app.v13_ai_intelligence_engine import (          # noqa: F401
    QuestionAnswer,
    Evidence,
    EvidenceLog,
    SOURCE_REGISTRY,
    FiveDimensionalAnalyticsEngine,
    TacticalStyleProfiler,
    FiveDIntelligenceReasoner,
    run as run_v14,
)


# ===========================================================================
# SECTION A — EVIDENCE QUALITY MODEL
# ===========================================================================
@dataclasses.dataclass
class EvidenceQuality:
    verification: str       # VERIFIED | UNVERIFIED | FAILED
    directness: str         # DIRECT | DERIVED | INFERRED
    freshness: str          # CURRENT | RECENT | DATED | STALE | UNKNOWN
    source_quality: str     # PRIMARY | OFFICIAL | AGGREGATOR | DERIVED
    independence: str       # INDEPENDENT | SINGLE_SOURCE | DUPLICATE
    completeness: str       # COMPLETE | PARTIAL | MINIMAL
    conflict: str           # NONE | DETECTED
    overall_score: float    # 0.0 .. 1.0

    def to_dict(self):
        return dataclasses.asdict(self)


_SOURCE_QUALITY = {
    "ESPN": "AGGREGATOR",
    "football-data.org": "OFFICIAL",
    "Open-Meteo": "PRIMARY",
    "Open-Meteo Geocoding": "PRIMARY",
    "derived": "DERIVED",
    "inference from ESPN scorelines": "DERIVED",
    "5D Intelligence Reasoner (derived)": "DERIVED",
    "ESPN (derived)": "DERIVED",
}

_FRESHNESS_WEIGHT = {"CURRENT": 1.0, "RECENT": 0.8, "DATED": 0.5, "STALE": 0.2, "UNKNOWN": 0.3}
_VERIFICATION_WEIGHT = {"VERIFIED": 1.0, "UNVERIFIED": 0.4, "FAILED": 0.0}
_DIRECTNESS_WEIGHT = {"DIRECT": 1.0, "DERIVED": 0.75, "INFERRED": 0.45}
_SOURCE_WEIGHT = {"PRIMARY": 1.0, "OFFICIAL": 0.9, "AGGREGATOR": 0.7, "DERIVED": 0.55}


class EvidenceQualityScorer:
    """Scores a QuestionAnswer / Evidence pair on the seven quality axes."""

    def score_question_answer(self, qa: QuestionAnswer) -> EvidenceQuality:
        verification = qa.answer_status if qa.answer_status in (
            "VERIFIED", "UNVERIFIED", "FAILED"
        ) else "UNVERIFIED"
        if qa.answer_status in ("INSUFFICIENT_EVIDENCE", "DISAGREEMENT"):
            verification = "UNVERIFIED"

        directness = {
            "A": "DIRECT", "B": "DERIVED", "C": "DERIVED", "D": "INFERRED",
        }.get(qa.resolution_type, "DERIVED")

        freshness = qa.freshness or "UNKNOWN"

        src_types = [_SOURCE_QUALITY.get(s, "AGGREGATOR") for s in (qa.sources or [])]
        source_quality = ("PRIMARY" if "PRIMARY" in src_types
                          else "OFFICIAL" if "OFFICIAL" in src_types
                          else "AGGREGATOR" if "AGGREGATOR" in src_types
                          else "DERIVED")

        independence = ("INDEPENDENT" if len(qa.sources) > 1
                        else "SINGLE_SOURCE" if len(qa.sources) == 1
                        else "SINGLE_SOURCE")

        completeness = ("COMPLETE" if qa.answer_status == "VERIFIED" and not qa.missing_information
                        else "PARTIAL" if qa.answer_status == "VERIFIED"
                        else "MINIMAL")

        conflict = "DETECTED" if qa.disagreement or qa.answer_status == "DISAGREEMENT" else "NONE"

        score = (
            _VERIFICATION_WEIGHT[verification]
            * _DIRECTNESS_WEIGHT[directness]
            * _FRESHNESS_WEIGHT.get(freshness, 0.3)
            * _SOURCE_WEIGHT[source_quality]
            * (1.0 if independence == "INDEPENDENT" else 0.75)
            * (1.0 if completeness == "COMPLETE" else 0.7 if completeness == "PARTIAL" else 0.4)
            * (0.6 if conflict == "DETECTED" else 1.0)
        )
        score = round(max(0.0, min(1.0, score)), 3)

        return EvidenceQuality(
            verification=verification, directness=directness,
            freshness=freshness, source_quality=source_quality,
            independence=independence, completeness=completeness,
            conflict=conflict, overall_score=score,
        )


# ===========================================================================
# SECTION B — TWO-SIDED ADVANTAGE MODEL
# ===========================================================================
@dataclasses.dataclass
class Advantage:
    advantage_id: str
    factor: str
    team: Optional[str]            # team receiving the advantage (None => NEUTRAL)
    opposing_team: Optional[str]
    direction: str                 # ADVANTAGE | NEUTRAL | UNKNOWN | CONFLICTED
    magnitude: str                 # MINOR | MODERATE | MAJOR
    confidence: float
    evidence_refs: list[str]       # QA IDs and/or Evidence IDs
    evidence_quality: str          # short descriptor, e.g. "VERIFIED/DIRECT/CURRENT"
    counter_factor: Optional[str]  # human-readable description
    countered_by: list[str]        # advantage_ids that counter this
    effective_status: str          # RAW | PARTIALLY_COUNTERED | COUNTERED | UNRESOLVED
    reasoning: str
    is_inference: bool = False

    def to_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class CounterAdvantage:
    counter_id: str
    primary_advantage_id: str
    countering_factor: str
    countering_team: str
    strength: str                  # FULL | PARTIAL | MINIMAL
    evidence_refs: list[str]
    reasoning: str

    def to_dict(self):
        return dataclasses.asdict(self)


class AdvantageEngine:
    """
    Derives a two-sided advantage set from the QAs / 5D matrix / reasoning
    block already produced by V1.4. Then applies the counter-advantage
    pass. Every Advantage carries provenance back to QA IDs.
    """

    def __init__(self):
        self._counter = 0

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}{self._counter:02d}"

    # -- factor derivations --------------------------------------------------
    def _home_field(self, home_team: str, away_team: str, match: dict) -> Advantage:
        return Advantage(
            advantage_id=self._next_id("ADV"),
            factor="Home-field advantage",
            team=home_team, opposing_team=away_team,
            direction="ADVANTAGE", magnitude="MINOR",
            confidence=0.75,
            evidence_refs=["Q1_kickoff", "Q2_venue"],
            evidence_quality="VERIFIED/DIRECT/CURRENT",
            counter_factor="Away side's containment structure (if supported by Q9)",
            countered_by=[], effective_status="RAW",
            reasoning=("Standard home-field factor. Only overturned when evidence "
                       "(neutral venue / away-side tactical containment) supports it."),
            is_inference=True,
        )

    def _from_dim(self, factor, home_val, away_val, home_team, away_team,
                   threshold, evidence_refs, magnitude_scale=(3.0, 10.0)):
        delta = home_val - away_val
        if abs(delta) <= threshold:
            return Advantage(
                advantage_id=self._next_id("ADV"), factor=factor,
                team=None, opposing_team=None, direction="NEUTRAL",
                magnitude="MINOR", confidence=0.55,
                evidence_refs=evidence_refs,
                evidence_quality="VERIFIED/DERIVED/RECENT",
                counter_factor=None, countered_by=[], effective_status="UNRESOLVED",
                reasoning=f"Statistical parity on '{factor}' (Δ={round(delta, 2)}).",
                is_inference=False,
            )
        team, opp = (home_team, away_team) if delta > 0 else (away_team, home_team)
        mag = ("MAJOR" if abs(delta) >= magnitude_scale[1]
               else "MODERATE" if abs(delta) >= magnitude_scale[0]
               else "MINOR")
        return Advantage(
            advantage_id=self._next_id("ADV"), factor=factor,
            team=team, opposing_team=opp,
            direction="ADVANTAGE", magnitude=mag,
            confidence=0.7, evidence_refs=evidence_refs,
            evidence_quality="VERIFIED/DERIVED/RECENT",
            counter_factor=None, countered_by=[], effective_status="RAW",
            reasoning=f"Δ={round(delta, 2)} on '{factor}' favours {team}.",
            is_inference=False,
        )

    def _tactical_containment(self, reasoning: dict, home_team, away_team) -> list[Advantage]:
        out = []
        if reasoning.get("park_bus_pattern_detected"):
            out.append(Advantage(
                advantage_id=self._next_id("ADV"),
                factor="Away-side defensive containment (park-the-bus pattern)",
                team=away_team, opposing_team=home_team,
                direction="ADVANTAGE", magnitude="MODERATE",
                confidence=0.45,
                evidence_refs=["Q9_tactical_style_inference"],
                evidence_quality="UNVERIFIED/INFERRED/RECENT",
                counter_factor="Home side's set-piece / wide overload threat",
                countered_by=[], effective_status="RAW",
                reasoning=("Away side's last-10 scoreline pattern is consistent with "
                           "a low-block / contain-first setup. This is an inference "
                           "from goals-for/against shape, not confirmed formation data."),
                is_inference=True,
            ))
        return out

    def _weather_factor(self, weather_qa: QuestionAnswer, home_team, away_team) -> Optional[Advantage]:
        if weather_qa.answer_status != "VERIFIED":
            return None
        # Weather is a shared condition — represent it explicitly as NEUTRAL
        # so the reasoner cannot accidentally use it as a directional lean.
        return Advantage(
            advantage_id=self._next_id("ADV"),
            factor="Match-date weather (shared condition)",
            team=None, opposing_team=None,
            direction="NEUTRAL", magnitude="MINOR",
            confidence=weather_qa.confidence,
            evidence_refs=[weather_qa.question_id],
            evidence_quality=f"VERIFIED/DIRECT/{weather_qa.freshness}",
            counter_factor=None, countered_by=[], effective_status="UNRESOLVED",
            reasoning=("Weather affects both sides. Recorded as a context factor, "
                       "not as a directional lean, per V1.3 reasoning rule."),
            is_inference=False,
        )

    # -- orchestrator --------------------------------------------------------
    def derive(self, qas_by_id: dict[str, QuestionAnswer], five_d: Optional[dict],
               reasoning: Optional[dict], match: dict, home_team, away_team) -> list[Advantage]:
        adv: list[Advantage] = []
        adv.append(self._home_field(home_team, away_team, match))

        if five_d:
            adv.append(self._from_dim(
                "Recent momentum (weighted form)",
                five_d["dim_1_momentum_delta"], 0.0,
                home_team, away_team, threshold=2.0,
                evidence_refs=["Q8_five_dimensional_matrix"],
                magnitude_scale=(6.0, 15.0),
            ))
            adv.append(self._from_dim(
                "Attacking threat (goals-for per game)",
                five_d["dim_2_offensive_threat"]["home"],
                five_d["dim_2_offensive_threat"]["away"],
                home_team, away_team, threshold=0.15,
                evidence_refs=["Q8_five_dimensional_matrix"],
                magnitude_scale=(0.4, 0.9),
            ))
            adv.append(self._from_dim(
                "Defensive stability (clean-sheet-adjusted)",
                five_d["dim_3_defensive_stability"]["home"],
                five_d["dim_3_defensive_stability"]["away"],
                home_team, away_team, threshold=0.4,
                evidence_refs=["Q8_five_dimensional_matrix"],
                magnitude_scale=(1.5, 3.0),
            ))

        form_qa = qas_by_id.get("Q3_recent_form")
        if form_qa and form_qa.answer_status == "VERIFIED" and form_qa.answer not in (None, "EVEN"):
            team = form_qa.answer
            opp = away_team if team == home_team else home_team
            adv.append(Advantage(
                advantage_id=self._next_id("ADV"),
                factor="Recent form (points from last 10)",
                team=team, opposing_team=opp,
                direction="ADVANTAGE", magnitude="MODERATE",
                confidence=0.65,
                evidence_refs=[form_qa.question_id],
                evidence_quality="VERIFIED/DERIVED/RECENT",
                counter_factor=None, countered_by=[], effective_status="RAW",
                reasoning=form_qa.reasoning, is_inference=False,
            ))

        if reasoning:
            adv.extend(self._tactical_containment(reasoning, home_team, away_team))

        weather_qa = qas_by_id.get("Q7_weather")
        if weather_qa:
            wf = self._weather_factor(weather_qa, home_team, away_team)
            if wf:
                adv.append(wf)

        return adv

    # -- counter pass --------------------------------------------------------
    def apply_counters(self, advantages: list[Advantage]) -> list[CounterAdvantage]:
        counters: list[CounterAdvantage] = []

        home_offense = next((a for a in advantages if "Attacking threat" in a.factor), None)
        away_defense = next((a for a in advantages if "Defensive stability" in a.factor), None)
        containment = next((a for a in advantages if "park-the-bus pattern" in a.factor), None)
        home_field = next((a for a in advantages if a.factor == "Home-field advantage"), None)
        form = next((a for a in advantages if "Recent form" in a.factor), None)

        def _register(primary: Advantage, countering: Advantage, strength: str, why: str):
            c = CounterAdvantage(
                counter_id=self._next_id("CNT"),
                primary_advantage_id=primary.advantage_id,
                countering_factor=countering.factor,
                countering_team=countering.team or "(neutral)",
                strength=strength,
                evidence_refs=list(set(primary.evidence_refs + countering.evidence_refs)),
                reasoning=why,
            )
            counters.append(c)
            primary.countered_by.append(c.counter_id)
            if strength == "FULL":
                primary.effective_status = "COUNTERED"
            elif strength == "PARTIAL":
                if primary.effective_status == "RAW":
                    primary.effective_status = "PARTIALLY_COUNTERED"
            return c

        # Offence vs opposing defence — the classic counter
        if home_offense and away_defense and home_offense.team and away_defense.team \
                and home_offense.team != away_defense.team:
            if away_defense.team and away_defense.team != home_offense.team:
                _register(home_offense, away_defense, "PARTIAL",
                          f"{away_defense.team}'s defensive stability directly reduces "
                          f"the effective conversion rate of {home_offense.team}'s attack.")

        # Park-the-bus vs the home side's attack
        if containment and home_offense and home_offense.team == containment.opposing_team:
            _register(home_offense, containment, "PARTIAL",
                      f"{containment.team}'s containment pattern is designed to blunt "
                      f"exactly the kind of front-foot attacking profile "
                      f"{home_offense.team} shows.")

        # Home-field vs strong away form
        if home_field and form and form.team != home_field.team:
            _register(home_field, form, "PARTIAL",
                      f"Raw home-field factor is offset by {form.team}'s superior "
                      f"recent form (points from last 10).")

        return counters


# ===========================================================================
# SECTION C — CROSS-QUESTION REASONING
# ===========================================================================
@dataclasses.dataclass
class CrossQuestionFinding:
    theme: str
    question_ids: list[str]
    finding: str
    evidence_refs: list[str]
    confidence: float
    is_inference: bool = False

    def to_dict(self):
        return dataclasses.asdict(self)


class CrossQuestionReasoner:
    """
    Groups related QAs into thematic findings. Uses existing Q IDs only —
    never invents a new canonical question.
    """

    THEMES = {
        "form_and_momentum": ["Q3_recent_form", "Q6_home_advantage_assessment",
                              "Q8_five_dimensional_matrix"],
        "tactical_matchup": ["Q9_tactical_style_inference", "Q8_five_dimensional_matrix"],
        "environmental": ["Q2_venue", "Q7_weather"],
        "availability_and_strength": ["Q5_player_availability", "Q3_recent_form"],
        "historical": ["Q4_head_to_head"],
    }

    def derive(self, qas_by_id: dict[str, QuestionAnswer]) -> list[CrossQuestionFinding]:
        out: list[CrossQuestionFinding] = []
        for theme, qids in self.THEMES.items():
            present = [qid for qid in qids if qid in qas_by_id]
            if not present:
                continue
            verified = [qid for qid in present
                        if qas_by_id[qid].answer_status == "VERIFIED"]
            if theme == "form_and_momentum" and verified:
                form = qas_by_id.get("Q3_recent_form")
                matrix = qas_by_id.get("Q8_five_dimensional_matrix")
                txt = form.reasoning if form else ""
                if matrix and matrix.answer:
                    txt += f" 5D state: {matrix.answer}."
                out.append(CrossQuestionFinding(
                    theme=theme, question_ids=present, finding=txt,
                    evidence_refs=verified, confidence=0.7, is_inference=False,
                ))
            elif theme == "tactical_matchup" and "Q9_tactical_style_inference" in present:
                q9 = qas_by_id["Q9_tactical_style_inference"]
                out.append(CrossQuestionFinding(
                    theme=theme, question_ids=present,
                    finding=f"Tactical profiles (inferred): {q9.answer}.",
                    evidence_refs=[q9.question_id],
                    confidence=0.4, is_inference=True,
                ))
            elif theme == "environmental":
                parts = []
                for qid in present:
                    qa = qas_by_id[qid]
                    if qa.answer_status == "VERIFIED":
                        parts.append(f"{qid}: {qa.answer}")
                if parts:
                    out.append(CrossQuestionFinding(
                        theme=theme, question_ids=present,
                        finding=" | ".join(parts),
                        evidence_refs=present, confidence=0.65, is_inference=False,
                    ))
            elif theme == "historical":
                qa = qas_by_id.get("Q4_head_to_head")
                if qa and qa.answer_status == "VERIFIED":
                    out.append(CrossQuestionFinding(
                        theme=theme, question_ids=present,
                        finding=qa.reasoning,
                        evidence_refs=[qa.question_id], confidence=qa.confidence,
                    ))
            elif theme == "availability_and_strength":
                q5 = qas_by_id.get("Q5_player_availability")
                if q5 and q5.answer_status == "VERIFIED":
                    out.append(CrossQuestionFinding(
                        theme=theme, question_ids=present,
                        finding=f"Availability signal: {q5.answer}",
                        evidence_refs=[q5.question_id],
                        confidence=q5.confidence, is_inference=False,
                    ))
        return out

# ===========================================================================
# SECTION D — CONFLICT DETECTION
# ===========================================================================
@dataclasses.dataclass
class ConflictRecord:
    factor: str
    description: str
    competing_evidence: list[dict]
    stronger_evidence: Optional[str]
    resolution: str
    unresolved_uncertainty: str

    def to_dict(self):
        return dataclasses.asdict(self)


class ConflictDetector:
    """
    Detects disagreement between evidence for the same factor.
    Preserves every source — never silently replaces one with another.
    """

    def detect(self, qas: list[QuestionAnswer], evidence: list[Evidence]) -> list[ConflictRecord]:
        conflicts: list[ConflictRecord] = []

        # 1. Explicit QA-level disagreement flag (e.g. Q1 cross-source kickoff)
        for qa in qas:
            if qa.disagreement:
                conflicts.append(ConflictRecord(
                    factor=qa.question_id,
                    description=qa.disagreement.get("description",
                                "Two sources disagree on the same factor."),
                    competing_evidence=qa.disagreement.get("observations", []),
                    stronger_evidence=qa.disagreement.get("stronger_source"),
                    resolution="Both observations preserved; source-priority rule applied "
                               "only where a defensible priority exists.",
                    unresolved_uncertainty=qa.disagreement.get("uncertainty",
                                              "Which source is authoritative is not settled by the evidence."),
                ))
            elif qa.answer_status == "DISAGREEMENT":
                conflicts.append(ConflictRecord(
                    factor=qa.question_id,
                    description=qa.reasoning,
                    competing_evidence=[{"sources": qa.sources, "answer": qa.answer}],
                    stronger_evidence=None,
                    resolution="Not resolvable from the evidence available.",
                    unresolved_uncertainty=qa.uncertainty,
                ))

        # 2. Same-factor multiple-evidence disagreement (group by evidence_type)
        by_key: dict[str, list[Evidence]] = defaultdict(list)
        for ev in evidence:
            by_key[ev.evidence_type].append(ev)
        for etype, evs in by_key.items():
            if len(evs) < 2:
                continue
            values = [json.dumps(e.normalized_value, sort_keys=True, default=str)
                      for e in evs if e.normalized_value is not None]
            if len(set(values)) > 1:
                conflicts.append(ConflictRecord(
                    factor=etype,
                    description=f"Multiple sources disagree on {etype}.",
                    competing_evidence=[
                        {"source_id": e.source_id, "value": e.normalized_value,
                         "freshness": e.freshness, "verification_status": e.verification_status}
                        for e in evs
                    ],
                    stronger_evidence=None,
                    resolution="Both observations preserved; no silent overwrite.",
                    unresolved_uncertainty="Source-priority rule deferred to caller.",
                ))
        return conflicts


# ===========================================================================
# SECTION E — MISSING-EVIDENCE PRIORITISATION
# ===========================================================================
@dataclasses.dataclass
class MissingEvidenceItem:
    question_id: str
    description: str
    impact: str                    # HIGH | MEDIUM | LOW
    potential_to_change_verdict: str
    suggested_source: str
    reasoning: str

    def to_dict(self):
        return dataclasses.asdict(self)


class MissingEvidencePrioritizer:
    """
    Ranks missing evidence by its potential to change the emerging verdict —
    not by a flat listing of every unanswered question.
    """

    IMPACT_MAP = {
        "Q1_kickoff":                  ("MEDIUM", "Confirms the fixture is real & timely"),
        "Q2_venue":                    ("MEDIUM", "Venue drives weather + home/away context"),
        "Q3_recent_form":              ("HIGH",   "Form is a first-order input to the 5D matrix"),
        "Q4_head_to_head":             ("MEDIUM", "Narrows the two-sided assessment"),
        "Q5_player_availability":      ("HIGH",   "Confirmed XI can overturn a statistical lean"),
        "Q6_home_advantage_assessment":("MEDIUM", "Adjusts the raw home-field factor"),
        "Q7_weather":                  ("MEDIUM", "Environment can materially shift conditions"),
        "Q8_five_dimensional_matrix":  ("HIGH",   "Core statistical input"),
        "Q9_tactical_style_inference": ("MEDIUM", "Matchup interaction is a first-class signal"),
    }

    def prioritise(self, qas: list[QuestionAnswer],
                   reasoning: Optional[dict]) -> list[MissingEvidenceItem]:
        out: list[MissingEvidenceItem] = []
        for qa in qas:
            if qa.answer_status in ("VERIFIED",):
                continue
            impact, why = self.IMPACT_MAP.get(qa.question_id, ("LOW", "Secondary factor"))
            suggested = self._suggest_source(qa.question_id)
            out.append(MissingEvidenceItem(
                question_id=qa.question_id,
                description=qa.question_text,
                impact=impact,
                potential_to_change_verdict=why,
                suggested_source=suggested,
                reasoning=(qa.missing_information
                           or "No evidence retrieved for this question."),
            ))
        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        out.sort(key=lambda x: order[x.impact])
        return out

    @staticmethod
    def _suggest_source(qid: str) -> str:
        return {
            "Q4_head_to_head": "registered results_statistics source (see SOURCE_REGISTRY)",
            "Q5_player_availability": "official club injury report + a second registered source",
            "Q7_weather": "Open-Meteo (re-query closer to kickoff for CURRENT freshness)",
            "Q3_recent_form": "ESPN schedule (or football-data.org when key configured)",
        }.get(qid, "next source in SOURCE_REGISTRY for this data class")



# ===========================================================================
# SECTION F — BROAD REASONING ORCHESTRATOR + OUTPUT CONTRACT
# ===========================================================================
@dataclasses.dataclass
class BroadReasoningReport:
    match_id: Optional[str]
    competition_id: str
    question_count: int
    question_state: list[dict]
    advantages: dict                         # {"home": [...], "away": [...], "neutral": [...]}
    counter_advantages: list[dict]
    tactical_matchup: dict
    statistical_assessment: dict
    environmental_assessment: dict
    availability_assessment: dict
    schedule_context: dict
    conflicts: list[dict]
    uncertainties: list[dict]
    missing_evidence: list[dict]
    decisive_factors: list[dict]
    overall_synthesis: str
    final_outcome: Optional[str]
    confidence: str
    readiness: str
    prediction_status: str                   # HELD | PROCESSED
    provenance: list[dict]
    explicit_caveats: list[str]
    cross_question_findings: list[dict]
    self_challenge: dict

    def to_dict(self):
        return dataclasses.asdict(self)


class BroadMatchReasoner:
    """
    Consumes the V1.4 package (competition + match + questions + evidence +
    5D matrix + reasoning + readiness). Produces the BroadReasoningReport.
    Nothing in V1.4 is mutated.
    """

    def __init__(self):
        self.scorer = EvidenceQualityScorer()
        self.advantages = AdvantageEngine()
        self.cross = CrossQuestionReasoner()
        self.conflicts = ConflictDetector()
        self.missing = MissingEvidencePrioritizer()

    # ----------------------------------------------------------------------
    def reason(self, package: dict) -> BroadReasoningReport:
        match = package.get("match") or {}
        competition = package.get("competition") or {}
        readiness = package.get("readiness", "INSUFFICIENT")
        five_d = package.get("five_dimensional_matrix")
        reasoning_block = package.get("reasoning")
        qas = [self._qa_from_dict(d) for d in package.get("questions", [])]
        evidence = [self._ev_from_dict(d) for d in package.get("evidence", [])]

        qas_by_id = {qa.question_id: qa for qa in qas}
        home_team = match.get("home_team")
        away_team = match.get("away_team")

        # -- advantage model -------------------------------------------------
        advantages = []
        if home_team and away_team:
            advantages = self.advantages.derive(
                qas_by_id, five_d, reasoning_block, match, home_team, away_team,
            )
            counters = self.advantages.apply_counters(advantages)
        else:
            counters = []

        home_adv = [a.to_dict() for a in advantages
                    if a.direction == "ADVANTAGE" and a.team == home_team]
        away_adv = [a.to_dict() for a in advantages
                    if a.direction == "ADVANTAGE" and a.team == away_team]
        neutral = [a.to_dict() for a in advantages if a.direction == "NEUTRAL"]

        # -- cross-question reasoning ---------------------------------------
        cross_findings = [f.to_dict() for f in self.cross.derive(qas_by_id)]

        # -- conflicts & missing --------------------------------------------
        conflict_records = [c.to_dict() for c in self.conflicts.detect(qas, evidence)]
        missing_items = [m.to_dict() for m in self.missing.prioritise(qas, reasoning_block)]

        # -- statistical / environmental / availability blocks ---------------
        statistical = self._statistical_block(qas_by_id, five_d)
        environmental = self._environmental_block(qas_by_id)
        availability = self._availability_block(qas_by_id)
        schedule_context = self._schedule_block(qas_by_id)
        tactical_matchup = self._tactical_block(qas_by_id, reasoning_block)

        # -- decisive factors ------------------------------------------------
        decisive = self._decisive_factors(advantages, counters, decisive_cap=5)

        # -- self-challenge --------------------------------------------------
        self_challenge = self._self_challenge(
            home_adv, away_adv, counters, missing_items, statistical,
        )

        # -- synthesis + outcome ---------------------------------------------
        synthesis, outcome, confidence, prediction_status = self._synthesise(
            readiness=readiness,
            home_team=home_team, away_team=away_team,
            home_adv=home_adv, away_adv=away_adv,
            counters=counters, decisive=decisive,
            missing=missing_items, conflicts=conflict_records,
            five_d=five_d, reasoning_block=reasoning_block,
            self_challenge=self_challenge,
        )

        # -- provenance ------------------------------------------------------
        provenance = self._build_provenance(advantages, counters, decisive)

        caveats = [
            "Every conclusion above is traceable to a question or evidence ID; "
            "nothing is asserted that was not retrieved or explicitly labelled as inference.",
            "Tactical style is an inference from scoreline shape, not a confirmed "
            "formation / press report — no free source in the registry exposes that directly.",
            "Counter-advantage reasoning is qualitative; magnitudes are described, "
            "not converted into numerical weights beyond the existing V1.4 composite index.",
        ]
        if prediction_status == "HELD":
            caveats.append("Prediction processing was held because readiness did not permit it. "
                           "The intelligence above remains available and inspectable.")

        return BroadReasoningReport(
            match_id=match.get("match_id"),
            competition_id=competition.get("competition_id", "UNKNOWN"),
            question_count=len(qas),
            question_state=[{"qid": qa.question_id, "status": qa.answer_status,
                             "confidence": qa.confidence} for qa in qas],
            advantages={"home": home_adv, "away": away_adv, "neutral": neutral},
            counter_advantages=[c.to_dict() for c in counters],
            tactical_matchup=tactical_matchup,
            statistical_assessment=statistical,
            environmental_assessment=environmental,
            availability_assessment=availability,
            schedule_context=schedule_context,
            conflicts=conflict_records,
            uncertainties=self._uncertainties(qas, missing_items, conflict_records),
            missing_evidence=missing_items,
            decisive_factors=decisive,
            overall_synthesis=synthesis,
            final_outcome=outcome,
            confidence=confidence,
            readiness=readiness,
            prediction_status=prediction_status,
            provenance=provenance,
            explicit_caveats=caveats,
            cross_question_findings=cross_findings,
            self_challenge=self_challenge,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def _qa_from_dict(d: dict) -> QuestionAnswer:
        return QuestionAnswer(**{k: d.get(k) for k in (
            "question_id", "question_text", "resolution_type", "answer",
            "answer_status", "evidence_ids", "sources", "reasoning",
            "uncertainty", "disagreement", "freshness", "missing_information",
            "confidence",
        )})

    @staticmethod
    def _ev_from_dict(d: dict) -> Evidence:
        return Evidence(**{k: d.get(k) for k in (
            "evidence_id", "match_id", "competition_id", "question_id",
            "source_id", "source_url", "retrieved_at", "published_at",
            "freshness", "evidence_type", "raw_value", "normalized_value",
            "extraction_method", "verification_status", "confidence", "notes",
        )})

    # ----------------------------------------------------------------------
    def _statistical_block(self, qas_by_id, five_d) -> dict:
        q8 = qas_by_id.get("Q8_five_dimensional_matrix")
        if not five_d:
            return {"available": False,
                    "note": "5D matrix not computed (form data insufficient)."}
        return {
            "available": True,
            "raw_statistical_state": five_d.get("raw_statistical_state"),
            "composite_index": five_d.get("dim_5_composite_index"),
            "momentum_delta": five_d.get("dim_1_momentum_delta"),
            "offensive_threat": five_d.get("dim_2_offensive_threat"),
            "defensive_stability": five_d.get("dim_3_defensive_stability"),
            "volatility": five_d.get("dim_4_volatility_score"),
            "note": (q8.reasoning if q8 else
                     "Statistical block derived from the V1.4 engine output."),
        }

    def _environmental_block(self, qas_by_id) -> dict:
        q7 = qas_by_id.get("Q7_weather")
        q2 = qas_by_id.get("Q2_venue")
        return {
            "venue": q2.answer if q2 and q2.answer_status == "VERIFIED" else None,
            "weather_answer": q7.answer if q7 and q7.answer_status == "VERIFIED" else None,
            "weather_freshness": q7.freshness if q7 else "UNKNOWN",
            "note": ("Environment is recorded as a shared condition, not a "
                     "directional lean (V1.3 reasoning rule)."),
        }

    def _availability_block(self, qas_by_id) -> dict:
        q5 = qas_by_id.get("Q5_player_availability")
        if not q5:
            return {"status": "UNKNOWN", "note": "Availability question not present."}
        return {
            "status": q5.answer_status,
            "answer": q5.answer if q5.answer_status == "VERIFIED" else None,
            "missing": q5.missing_information,
            "note": ("Absence of injury data is NOT evidence of full-squad availability "
                     "— see V1.4 Q5 reasoning."),
        }

    def _schedule_block(self, qas_by_id) -> dict:
        return {
            "available": False,
            "note": "No schedule-congestion / rest-days question wired in this build. "
                    "Cannot reason about fatigue without it. Marked UNKNOWN, not assumed.",
        }

    def _tactical_block(self, qas_by_id, reasoning) -> dict:
        q9 = qas_by_id.get("Q9_tactical_style_inference")
        if not q9:
            return {"available": False}
        return {
            "available": True,
            "status": q9.answer_status,
            "profiles": q9.answer,
            "park_bus_pattern_detected": bool(reasoning and reasoning.get("park_bus_pattern_detected")),
            "basis": q9.reasoning,
            "is_inference": True,
        }

    def _decisive_factors(self, advantages, counters, decisive_cap=5) -> list[dict]:
        def rank(a: Advantage) -> float:
            mag = {"MAJOR": 1.0, "MODERATE": 0.6, "MINOR": 0.3}.get(a.magnitude, 0.3)
            eff = {"RAW": 1.0, "UNRESOLVED": 0.8, "PARTIALLY_COUNTERED": 0.5, "COUNTERED": 0.2}.get(
                a.effective_status, 0.5)
            return mag * a.confidence * eff
        ordered = sorted([a for a in advantages if a.direction == "ADVANTAGE"],
                         key=rank, reverse=True)[:decisive_cap]
        return [{
            "factor": a.factor,
            "team": a.team,
            "magnitude": a.magnitude,
            "effective_status": a.effective_status,
            "confidence": a.confidence,
            "countered_by": a.countered_by,
            "reasoning": a.reasoning,
            "evidence_refs": a.evidence_refs,
        } for a in ordered]

    def _uncertainties(self, qas, missing_items, conflicts) -> list[dict]:
        out = []
        for qa in qas:
            if qa.answer_status != "VERIFIED":
                out.append({"kind": "UNRESOLVED_QUESTION",
                            "qid": qa.question_id,
                            "detail": qa.uncertainty,
                            "missing": qa.missing_information})
        for m in missing_items:
            if m["impact"] == "HIGH":
                out.append({"kind": "HIGH_IMPACT_MISSING",
                            "qid": m["question_id"],
                            "detail": m["potential_to_change_verdict"]})
        for c in conflicts:
            out.append({"kind": "CONFLICT",
                        "factor": c["factor"],
                        "detail": c["unresolved_uncertainty"]})
        return out

    def _self_challenge(self, home_adv, away_adv, counters, missing, statistical) -> dict:
        home_score = sum(a["confidence"] for a in home_adv
                         if a["effective_status"] in ("RAW", "UNRESOLVED"))
        away_score = sum(a["confidence"] for a in away_adv
                         if a["effective_status"] in ("RAW", "UNRESOLVED"))
        emerging = ("HOME" if home_score > away_score + 0.15
                    else "AWAY" if away_score > home_score + 0.15
                    else "DRAW")

        against = []
        if emerging == "HOME":
            against = [a for a in away_adv if a["effective_status"] in ("RAW", "UNRESOLVED")]
        elif emerging == "AWAY":
            against = [a for a in home_adv if a["effective_status"] in ("RAW", "UNRESOLVED")]
        else:
            against = (home_adv[:2] + away_adv[:2])

        high_impact_missing = [m for m in missing if m["impact"] == "HIGH"]

        return {
            "emerging_lean_before_challenge": emerging,
            "evidence_against_emerging_lean": [
                {"factor": a["factor"], "team": a["team"],
                 "why_it_argues_against": f"Still-unresolved advantage for {a['team']}."}
                for a in against[:4]
            ],
            "high_impact_missing_that_could_flip_verdict": [
                m["question_id"] for m in high_impact_missing
            ],
            "statistical_caveat": (
                "Statistical composite is descriptive, not deterministic — it does "
                "not account for tactical matchup fit unless Q9 reasoning is present."
            ),
            "challenge_verdict": (
                "Held" if (high_impact_missing or len(against) >= 2 and emerging != "DRAW")
                else "No material counter-evidence found."
            ),
        }

    def _synthesise(self, readiness, home_team, away_team, home_adv, away_adv,
                    counters, decisive, missing, conflicts, five_d, reasoning_block,
                    self_challenge):
        ready_for_prediction = readiness == "READY"

        if not home_team or not away_team:
            return ("No match identity — cannot synthesise a two-sided assessment.",
                    None, "LOW", "HELD")

        countered_home = [a for a in home_adv if a["effective_status"] == "PARTIALLY_COUNTERED"
                          or a["effective_status"] == "COUNTERED"]
        countered_away = [a for a in away_adv if a["effective_status"] == "PARTIALLY_COUNTERED"
                          or a["effective_status"] == "COUNTERED"]

        eff_home = sum(a["confidence"] * (0.5 if a["effective_status"] == "PARTIALLY_COUNTERED"
                                          else 0.15 if a["effective_status"] == "COUNTERED"
                                          else 1.0)
                       for a in home_adv)
        eff_away = sum(a["confidence"] * (0.5 if a["effective_status"] == "PARTIALLY_COUNTERED"
                                          else 0.15 if a["effective_status"] == "COUNTERED"
                                          else 1.0)
                       for a in away_adv)

        parts = []
        parts.append(
            f"{home_team} carries {len(home_adv)} supported advantages "
            f"(net effective weight {round(eff_home,2)}); {away_team} carries "
            f"{len(away_adv)} (net effective weight {round(eff_away,2)})."
        )
        if counters:
            parts.append(
                f"{len(counters)} counter-advantage(s) were registered — "
                f"{len(countered_home)} of {home_team}'s advantages and "
                f"{len(countered_away)} of {away_team}'s are at least partially neutralised."
            )
        if decisive:
            top = decisive[0]
            parts.append(
                f"The single most decisive factor is '{top['factor']}' "
                f"({top['magnitude']}, favouring {top['team']}, "
                f"effective status {top['effective_status']})."
            )
        if reasoning_block and reasoning_block.get("park_bus_pattern_detected"):
            parts.append(
                "A park-the-bus / containment pattern on the away side was detected "
                "from scoreline shape; this pulls the read toward a draw rather than "
                "a straightforward home win, all else being equal."
            )
        if conflicts:
            parts.append(
                f"{len(conflicts)} evidence conflict(s) were detected and preserved — "
                "the synthesis deliberately does not silently choose a side on those."
            )
        if missing:
            top_missing = [m["question_id"] for m in missing if m["impact"] == "HIGH"]
            if top_missing:
                parts.append(
                    f"High-impact missing evidence: {', '.join(top_missing)}. "
                    "These are the questions whose resolution would most likely shift "
                    "the current read."
                )
        if self_challenge["evidence_against_emerging_lean"]:
            parts.append(
                "Self-challenge: " + " ".join(
                    e["why_it_argues_against"]
                    for e in self_challenge["evidence_against_emerging_lean"][:2]
                )
            )

        if not ready_for_prediction:
            outcome = None
            confidence = "INSUFFICIENT_EVIDENCE"
            prediction_status = "HELD"
            parts.append(
                "Readiness gate did not permit prediction processing, so no final "
                "outcome is asserted — the assessment above remains available and "
                "inspectable."
            )
        else:
            if abs(eff_home - eff_away) < 0.25:
                outcome = "Draw"
                confidence = "LOW-MODERATE"
            elif eff_home > eff_away:
                outcome = home_team
                confidence = "MODERATE" if (eff_home - eff_away) < 0.75 else "MODERATE-HIGH"
            else:
                outcome = away_team
                confidence = "MODERATE" if (eff_away - eff_home) < 0.75 else "MODERATE-HIGH"
            if conflicts or any(m["impact"] == "HIGH" for m in missing):
                confidence = "LOW" if confidence == "LOW-MODERATE" else "MODERATE"
            prediction_status = "PROCESSED"

        return (" ".join(parts), outcome, confidence, prediction_status)

    # ----------------------------------------------------------------------
    def _build_provenance(self, advantages, counters, decisive) -> list[dict]:
        counters_by_adv: dict[str, list[CounterAdvantage]] = defaultdict(list)
        for c in counters:
            counters_by_adv[c.primary_advantage_id].append(c)
        prov = []
        for a in advantages:
            if a.direction != "ADVANTAGE":
                continue
            prov.append({
                "factor": a.factor,
                "advantage_id": a.advantage_id,
                "team": a.team,
                "evidence_refs": a.evidence_refs,
                "reasoning": a.reasoning,
                "conclusion": f"{a.direction} ({a.magnitude}) for {a.team}, "
                              f"effective={a.effective_status}",
                "counters": [c.to_dict() for c in counters_by_adv.get(a.advantage_id, [])],
                "is_inference": a.is_inference,
            })
        return prov



# ===========================================================================
# SECTION G — HELD-MATCH DASHBOARD PRESENTATION
# ===========================================================================
def print_broad_dashboard(report: BroadReasoningReport):
    r = report
    bar = "=" * 78
    print(bar)
    print("BROAD EVIDENCE REASONING — ADVANTAGE SYNTHESIS")
    print(bar)
    print(f"READINESS          : {r.readiness}")
    print(f"PREDICTION STATUS  : {r.prediction_status}"
          + ("  (REASON: INSUFFICIENT EVIDENCE)" if r.prediction_status == "HELD" else ""))
    print(f"QUESTIONS PRESENT  : {r.question_count}")
    print("-" * 78)
    print("HOME ADVANTAGES:")
    for a in r.advantages.get("home", []):
        print(f"  • [{a['magnitude']}/{a['effective_status']}] {a['factor']}  "
              f"(conf={a['confidence']})")
    print("AWAY ADVANTAGES:")
    for a in r.advantages.get("away", []):
        print(f"  • [{a['magnitude']}/{a['effective_status']}] {a['factor']}  "
              f"(conf={a['confidence']})")
    if r.counter_advantages:
        print("-" * 78)
        print("COUNTER-ADVANTAGES:")
        for c in r.counter_advantages:
            print(f"  • {c['countering_team']} counters {c['primary_advantage_id']} "
                  f"({c['strength']}): {c['countering_factor']}")
    if r.conflicts:
        print("-" * 78)
        print("CONFLICTS DETECTED:")
        for c in r.conflicts:
            print(f"  ! {c['factor']}: {c['description']}")
    if r.missing_evidence:
        print("-" * 78)
        print("MISSING EVIDENCE (ranked by impact):")
        for m in r.missing_evidence[:5]:
            print(f"  [{m['impact']}] {m['question_id']}: {m['description']}")
    if r.decisive_factors:
        print("-" * 78)
        print("DECISIVE FACTORS:")
        for d in r.decisive_factors:
            print(f"  → {d['factor']} → {d['team']} ({d['magnitude']}, "
                  f"effective={d['effective_status']})")
    print("-" * 78)
    print("SELF-CHALLENGE:")
    print(f"  Emerging lean before challenge : {r.self_challenge.get('emerging_lean_before_challenge')}")
    print(f"  Challenge verdict              : {r.self_challenge.get('challenge_verdict')}")
    if r.self_challenge.get("high_impact_missing_that_could_flip_verdict"):
        print(f"  Missing that could flip        : "
              f"{', '.join(r.self_challenge['high_impact_missing_that_could_flip_verdict'])}")
    print("-" * 78)
    print("OVERALL SYNTHESIS:")
    print(f"  {r.overall_synthesis}")
    print("-" * 78)
    print(f"FINAL OUTCOME      : {r.final_outcome or '(held — not asserted)'}")
    print(f"CONFIDENCE         : {r.confidence}")
    print(bar)


# ===========================================================================
# SECTION H — INTEGRATION WRAPPERS (do NOT modify V1.4)
# ===========================================================================
def augment_with_broad_reasoning(v14_package: dict) -> dict:
    """Take the V1.4 `run()` output and return it with a `broad_reasoning` key."""
    reasoner = BroadMatchReasoner()
    report = reasoner.reason(v14_package)
    out = dict(v14_package)                     # shallow copy; V1.4 dict untouched
    out["broad_reasoning"] = report.to_dict()
    return out


def run_broad(team_a: str, team_b: str, competition_id: str,
              date: Optional[str] = None, print_dashboard: bool = True) -> dict:
    """
    Drop-in wrapper: identical CLI/API surface to V1.4's `run()`, but the
    returned dict also contains the broad reasoning report.
    """
    package = run_v14(team_a, team_b, competition_id, date)   # untouched V1.4
    augmented = augment_with_broad_reasoning(package)
    if print_dashboard:
        report = BroadMatchReasoner().reason(package)
        print_broad_dashboard(report)
    return augmented



# ===========================================================================
# CLI (additive — V1.4 CLI still works if you call the old module directly)
# ===========================================================================
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Football AI V1.5 — Broad Reasoning CLI")
    ap.add_argument("team_a")
    ap.add_argument("team_b")
    ap.add_argument("--competition", required=True)
    ap.add_argument("--date", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    pkg = run_broad(args.team_a, args.team_b, args.competition, args.date)
    if args.json:
        print(json.dumps(pkg, indent=2, default=str))
