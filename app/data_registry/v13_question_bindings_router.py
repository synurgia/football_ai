"""
V1.3 Question Bindings Router

MAIN SCANNER -> THIS ROUTER -> COMPETITION-SPECIFIC 37Q SOURCE REGISTRY

Routes by resolved competition_id.

eng.*      -> England question bindings
de.*       -> Germany 37-question source registry
usa.ncaaw  -> NCAAW 37-question source registry
usa.5      -> NCAAM question bindings
nor.*      -> Norway question bindings
sco.*      -> Scotland question bindings

Unknown competition -> NOT_BOUND
"""

from __future__ import annotations

from typing import Any, Dict


# ---------------------------------------------------------------------------
# ENGLAND
# ---------------------------------------------------------------------------

from app.data_registry.v13_question_bindings import (
    bind_questions_for_match_england as _bind_england,
)


# ---------------------------------------------------------------------------
# GERMANY
# ---------------------------------------------------------------------------

from app.data_registry.v13_germany_question_sources import (
    bind_for_match_de as _bind_de,
)


# ---------------------------------------------------------------------------
# NCAAW
# ---------------------------------------------------------------------------
#
# IMPORTANT:
# Use the new question-source registry.
# Do NOT import the old v13_ncaaw_bindings implementation here.
#

from app.data_registry.v13_ncaaw_question_sources import (
    bind_for_match_ncaaw as _bind_ncaaw,
)


# ---------------------------------------------------------------------------
# NCAAM
# ---------------------------------------------------------------------------

from app.data_registry.v13_ncaam_question_sources import (
    bind_for_match_ncaam as _bind_ncaam,
)


# ---------------------------------------------------------------------------
# NORWAY
# ---------------------------------------------------------------------------

from app.data_registry.v13_norway_question_sources import (
    bind_for_match_no as _bind_no,
)


# ---------------------------------------------------------------------------
# SCOTLAND
# ---------------------------------------------------------------------------

from app.data_registry.v13_scotland_question_sources import (
    bind_for_match_sco as _bind_sco,
)


# ---------------------------------------------------------------------------
# ROUTING DEFINITIONS
# ---------------------------------------------------------------------------

ENGLAND_PREFIXES = ("eng.",)

GERMANY_PREFIXES = ("de.",)

NCAAW_IDS = {"usa.ncaaw"}

NCAAM_IDS = {"usa.5"}

NORWAY_PREFIXES = ("nor.",)

SCOTLAND_PREFIXES = ("sco.",)


# ---------------------------------------------------------------------------
# INTERNAL ROUTER
# ---------------------------------------------------------------------------

def _route(
    competition_id: str,
    match_id: str,
    date: str,
    competition_name: str = "",
):

    cid = str(competition_id or "").strip().lower()

    if not cid:
        return None, "NO_COMPETITION_ID"


    # =======================================================================
    # ENGLAND
    # =======================================================================

    if cid.startswith(ENGLAND_PREFIXES):

        return (
            _bind_england(
                competition_name=competition_name,
                match_id=match_id,
                date=date,
            ),
            "ENGLAND",
        )


    # =======================================================================
    # GERMANY
    # =======================================================================
    #
    # IMPORTANT:
    # Germany binding is competition-aware.
    #
    # de.1 -> Bundesliga
    # de.2 -> 2. Bundesliga
    # de.3 -> 3. Liga
    # de.4 -> Regionalliga
    #
    # The Germany registry itself filters the 37 questions against
    # the authorized sources for the exact competition.
    #

    if cid.startswith(GERMANY_PREFIXES):

        return (
            _bind_de(
                competition_id=cid,
                competition_name=competition_name,
                match_id=match_id,
                date=date,
            ),
            "GERMANY",
        )


    # =======================================================================
    # NCAAW
    # =======================================================================

    if cid in NCAAW_IDS:

        return (
            _bind_ncaaw(
                competition_name=competition_name,
                match_id=match_id,
                date=date,
            ),
            "NCAAW",
        )


    # =======================================================================
    # NCAAM
    # =======================================================================

    if cid in NCAAM_IDS:

        return (
            _bind_ncaam(
                competition_name=competition_name,
                match_id=match_id,
                date=date,
            ),
            "NCAAM",
        )


    # =======================================================================
    # NORWAY
    # =======================================================================

    if cid.startswith(NORWAY_PREFIXES):

        return (
            _bind_no(
                competition_name=competition_name,
                match_id=match_id,
                date=date,
            ),
            "NORWAY",
        )


    # =======================================================================
    # SCOTLAND
    # =======================================================================

    if cid.startswith(SCOTLAND_PREFIXES):

        return (
            _bind_sco(
                cid,
                match_id,
                date,
            ),
            "SCOTLAND",
        )


    # =======================================================================
    # UNKNOWN
    # =======================================================================

    return {}, "NOT_BOUND"


# ---------------------------------------------------------------------------
# PUBLIC ATTACHMENT FUNCTION
# ---------------------------------------------------------------------------

def attach_bindings_routed(
    match: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Attach competition-specific question bindings to a scanned match.

    Main scanner flow:

        scanned match
            ->
        resolved competition_id
            ->
        correct question registry
            ->
        question_bindings

    Status:

        FULL
            Every returned question has at least one source.

        PARTIAL
            Some returned questions have no sources.

        NOT_BOUND
            Competition is not registered.

    Germany additionally guarantees >=5 authorized sources per question
    through v13_germany_question_sources.py.
    """

    cid = (
        match.get("competition_id")
        or ""
    )

    mid = (
        match.get("match_id")
        or match.get("source_match_id")
        or ""
    )

    date = (
        match.get("match_date")
        or (match.get("kickoff_at") or "")[:10]
    )

    competition_name = (
        match.get("competition_name_canonical")
        or match.get("competition_name")
        or match.get("competition")
        or ""
    )


    bindings, scope = _route(
        cid,
        mid,
        date,
        competition_name,
    )


    match["question_bindings"] = bindings or {}

    match["question_bindings_scope"] = scope


    if scope == "NOT_BOUND":

        match["question_bindings_status"] = "NOT_BOUND"

        return match


    filled = sum(
        1
        for value in (bindings or {}).values()
        if value
    )

    total = (
        len(bindings)
        if bindings
        else 0
    )


    if total and filled == total:

        status = "FULL"

    elif filled > 0:

        status = "PARTIAL"

    else:

        status = "NOT_BOUND"


    match["question_bindings_status"] = status


    # -----------------------------------------------------------------------
    # Germany-specific audit metadata
    # -----------------------------------------------------------------------

    if scope == "GERMANY":

        match["question_bindings_question_count"] = len(
            bindings or {}
        )

        match["question_bindings_min_sources"] = min(
            (
                len(value)
                for value in (bindings or {}).values()
            ),
            default=0,
        )

        match["question_bindings_source_policy"] = (
            "GERMANY_37Q_COMPETITION_FILTERED"
        )


    # -----------------------------------------------------------------------
    # NCAAW-specific audit metadata
    # -----------------------------------------------------------------------

    if scope == "NCAAW":

        match["question_bindings_question_count"] = len(
            bindings or {}
        )

        match["question_bindings_min_sources"] = min(
            (
                len(value)
                for value in (bindings or {}).values()
            ),
            default=0,
        )

        match["question_bindings_source_policy"] = (
            "NCAAW_37Q"
        )


    return match
