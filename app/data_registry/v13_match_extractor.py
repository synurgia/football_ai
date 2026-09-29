import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


INPUT = Path("data/v13_match_discovery_candidates.json")
OUTPUT = Path("data/v13_extracted_match_candidates.json")


DATE_PATTERNS = [
    re.compile(r"\b(2026[-/]\d{1,2}[-/]\d{1,2})\b"),
    re.compile(r"\b(\d{1,2}[-/]\d{1,2}[-/]2026)\b"),
]

TIME_PATTERN = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")

VS_PATTERN = re.compile(
    r"\b([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9 .'\-&()]{1,60}?)\s+"
    r"(?:vs\.?|v\.?|–|-)\s+"
    r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9 .'\-&()]{1,60})\b",
    re.IGNORECASE,
)

HOME_AWAY_PATTERN = re.compile(
    r"(?:home|host)\s*[:\-]\s*([A-Za-zÀ-ÿ0-9 .'\-&()]{2,60}).*?"
    r"(?:away|visitor)\s*[:\-]\s*([A-Za-zÀ-ÿ0-9 .'\-&()]{2,60})",
    re.IGNORECASE | re.DOTALL,
)


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -–—|:;,.")


def extract_date(text: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue

        raw = match.group(1).replace("/", "-")

        parts = raw.split("-")
        if len(parts) != 3:
            continue

        if len(parts[0]) == 4:
            year, month, day = parts
        else:
            day, month, year = parts

        try:
            return datetime(
                int(year), int(month), int(day)
            ).date().isoformat()
        except ValueError:
            pass

    return None


def extract_time(text: str) -> str | None:
    match = TIME_PATTERN.search(text)
    return match.group(0) if match else None


def extract_teams(text: str) -> tuple[str | None, str | None]:
    match = VS_PATTERN.search(text)
    if match:
        home = clean(match.group(1))
        away = clean(match.group(2))

        if home and away and home.lower() != away.lower():
            return home, away

    match = HOME_AWAY_PATTERN.search(text)
    if match:
        home = clean(match.group(1))
        away = clean(match.group(2))

        if home and away and home.lower() != away.lower():
            return home, away

    return None, None


def extract_from_snippet(
    competition_id: str,
    competition_name: str,
    source_id: str,
    source_name: str,
    source_url: str,
    candidate: Dict[str, Any],
) -> Dict[str, Any]:

    snippet = candidate.get("evidence_snippet", "")
    text = clean(snippet)

    # Preserve the existing snippet-based extraction path.
    home_team, away_team = extract_teams(text)
    match_date = extract_date(text)
    match_time = extract_time(text)

    # Structured bridge candidates already contain canonical fixture fields.
    # Use them directly when available, without creating a provider-specific path.
    if not home_team:
        home_team = candidate.get("home_team")
    if not away_team:
        away_team = candidate.get("away_team")

    scheduled = candidate.get("scheduled")
    if scheduled:
        scheduled_text = str(scheduled)
        if not match_date:
            match_date = scheduled_text[:10] if len(scheduled_text) >= 10 else None
        if not match_time and "T" in scheduled_text:
            match_time = scheduled_text[11:16] if len(scheduled_text) >= 16 else None

    identity_complete = bool(
        home_team
        and away_team
        and match_date
    )

    return {
        "competition_id": competition_id,
        "competition_name": competition_name,
        "source_id": source_id,
        "source_name": source_name,
        "source_url": source_url,
        "home_team": home_team,
        "away_team": away_team,
        "date": match_date,
        "time": match_time,
        "identity_status": (
            "STRUCTURED_CANDIDATE"
            if identity_complete
            else "UNRESOLVED_EVIDENCE"
        ),
        "evidence_snippet": snippet[:1500],
    }
def main() -> None:
    data = json.loads(INPUT.read_text(encoding="utf-8"))

    records: List[Dict[str, Any]] = []

    for result in data.get("source_results", []):
        for candidate in result.get("candidates", []):
            records.append(
                extract_from_snippet(
                    competition_id=result.get("competition_id", ""),
                    competition_name=result.get("competition_name", ""),
                    source_id=result.get("source_id", ""),
                    source_name=result.get("source_name", ""),
                    source_url=(
                        candidate.get("source_url")
                        or result.get("url")
                        or ""
                    ),
                    candidate=candidate,
                )
            )

    structured = [
        r for r in records
        if r["identity_status"] == "STRUCTURED_CANDIDATE"
    ]

    unresolved = [
        r for r in records
        if r["identity_status"] == "UNRESOLVED_EVIDENCE"
    ]

    output = {
        "phase": "V1.3_MATCH_EXTRACTION",
        "source_file": str(INPUT),
        "total_evidence_candidates": len(records),
        "structured_candidates": len(structured),
        "unresolved_evidence": len(unresolved),
        "records": records,
    }

    OUTPUT.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=== V1.3 MATCH EXTRACTION ===")
    print("TOTAL EVIDENCE CANDIDATES:", len(records))
    print("STRUCTURED CANDIDATES:", len(structured))
    print("UNRESOLVED EVIDENCE:", len(unresolved))
    print("SAVED:", OUTPUT)


if __name__ == "__main__":
    main()
