import json
import re
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx


COMPETITIONS = Path("app/data_registry/v1_3_competition_catalogue.py")
SOURCE_FILE = Path("data/v13_phase2_source_coverage_candidates.json")
OUTPUT = Path("data/v13_competition_specific_coverage_verification.json")


def load_competitions():
    from app.data_registry.v1_3_competition_catalogue import V13_COMPETITION_CATALOGUE
    return V13_COMPETITION_CATALOGUE


def norm(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def aliases(name):
    n = norm(name)
    vals = {n}

    replacements = {
        "premier league": ["premier", "league"],
        "ligue": ["ligue"],
        "serie a": ["serie a"],
        "bundesliga": ["bundesliga"],
        "liga": ["liga"],
        "championship": ["championship"],
    }

    for key, extra in replacements.items():
        if key in n:
            vals.add(norm(" ".join(extra)))

    return {x for x in vals if len(x) >= 4}


def verify(item):
    competition = item["competition"]
    source = item["source"]

    url = source.get("final_url") or source.get("base_url")

    result = {
        "competition_id": competition["competition_id"],
        "competition_name": competition["name"],
        "source_id": source["source_id"],
        "source_name": source["name"],
        "url": url,
        "status": "UNUSABLE",
        "identity_match": False,
        "fixtures_signal": False,
        "results_signal": False,
        "standings_signal": False,
        "match_data_signal": False,
        "evidence": [],
        "error": None,
    }

    try:
        with httpx.Client(
            timeout=15,
            follow_redirects=True,
            headers={
                "User-Agent":
                "Mozilla/5.0 V1.3-FootballAI-Coverage-Verification"
            },
        ) as client:
            r = client.get(url)

        text = r.text[:150000]
        low = norm(text)

        if r.status_code >= 400:
            result["status"] = "FAILED"
            result["error"] = f"HTTP {r.status_code}"
            return result

        # Actual competition identity check.
        for a in aliases(competition["name"]):
            if a in low:
                result["identity_match"] = True
                result["evidence"].append(
                    f"Competition name found: {competition['name']}"
                )
                break

        fixture_terms = [
            "fixtures", "fixture", "matches", "match schedule",
            "upcoming matches", "games"
        ]
        result_terms = [
            "results", "result", "scores", "full time"
        ]
        table_terms = [
            "standings", "league table", "table", "rankings"
        ]
        match_terms = [
            "lineup", "line-ups", "squad", "match centre",
            "match center", "goal", "minute"
        ]

        result["fixtures_signal"] = any(x in low for x in fixture_terms)
        result["results_signal"] = any(x in low for x in result_terms)
        result["standings_signal"] = any(x in low for x in table_terms)
        result["match_data_signal"] = any(x in low for x in match_terms)

        if result["identity_match"] and (
            result["fixtures_signal"]
            or result["results_signal"]
            or result["standings_signal"]
            or result["match_data_signal"]
        ):
            result["status"] = "VERIFIED"

        elif result["identity_match"]:
            result["status"] = "PARTIAL"

        else:
            result["status"] = "UNUSABLE"

        return result

    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = str(e)[:300]
        return result


def main():
    competitions = load_competitions()
    sources = json.loads(SOURCE_FILE.read_text())

    # Country-exact and explicit international applicability.
    country_scope = {
        "ago":"ANGOLA","civ":"COTE_DIVOIRE","cod":"DR_CONGO",
        "dza":"ALGERIA","egy":"EGYPT","gha":"GHANA","ken":"KENYA",
        "mar":"MOROCCO","nga":"NIGERIA","sen":"SENEGAL","tza":"TANZANIA",
        "tun":"TUNISIA","uga":"UGANDA","zaf":"SOUTH_AFRICA","zmb":"ZAMBIA",
        "arg":"ARGENTINA","bol":"BOLIVIA","bra":"BRAZIL","chi":"CHILE",
        "col":"COLOMBIA","crc":"COSTA_RICA","dom":"DOMINICAN_REPUBLIC",
        "ecu":"ECUADOR","hon":"HONDURAS","mex":"MEXICO","pan":"PANAMA",
        "par":"PARAGUAY","per":"PERU","uru":"URUGUAY","usa":"USA",
        "are":"UNITED_ARAB_EMIRATES","chn":"CHINA","idn":"INDONESIA",
        "ind":"INDIA","irn":"IRAN","irq":"IRAQ","isr":"ISRAEL",
        "jor":"JORDAN","jpn":"JAPAN","kaz":"KAZAKHSTAN",
        "kor":"KOREA_REPUBLIC","mys":"MALAYSIA","qat":"QATAR",
        "sau":"SAUDI_ARABIA","tha":"THAILAND","uzb":"UZBEKISTAN",
        "vnm":"VIETNAM","arm":"ARMENIA","aut":"AUSTRIA","aze":"AZERBAIJAN",
        "bih":"BOSNIA_AND_HERZEGOVINA","bul":"BULGARIA","cro":"CROATIA",
        "cyp":"CYPRUS","cze":"CZECHIA","den":"DENMARK","de":"GERMANY",
        "eng":"ENGLAND","fin":"FINLAND","fr":"FRANCE","fro":"FAROE_ISLANDS",
        "geo":"GEORGIA","gre":"GREECE","hun":"HUNGARY","isl":"ICELAND",
        "irl":"REPUBLIC_OF_IRELAND","ita":"ITALY","nor":"NORWAY",
        "nir":"NORTHERN_IRELAND","nl":"NETHERLANDS","pol":"POLAND",
        "por":"PORTUGAL","rou":"ROMANIA","sco":"SCOTLAND","srb":"SERBIA",
        "sui":"SWITZERLAND","svk":"SLOVAKIA","svn":"SLOVENIA",
        "swe":"SWEDEN","tur":"TURKIYE","ukr":"UKRAINE","aus":"AUSTRALIA",
    }

    international = {
        "uefa": {"EUROPE_CLUB_COMPETITIONS","EUROPE_MENS_CLUB"},
        "conmebol": {"SOUTH_AMERICA"},
        "concacaf": {"NORTH_CENTRAL_AMERICA_CARIBBEAN"},
        "afc": {"ASIA"},
        "caf": {"AFRICA"},
        "ofc": {"OCEANIA","OCEANIA_PROFESSIONAL"},
        "fifa": {"GLOBAL_WHERE_AVAILABLE"},
    }

    jobs = []

    for c in competitions:
        prefix = c["competition_id"].split(".", 1)[0]

        for s in sources:
            scope = (s.get("coverage_scope") or "").upper()

            applicable = False

            if prefix in country_scope and scope == country_scope[prefix]:
                applicable = True

            if prefix in international and scope in international[prefix]:
                applicable = True

            if not applicable:
                continue

            jobs.append({
                "competition": c,
                "source": s,
            })

    print("=== V1.3 COMPETITION-SPECIFIC COVERAGE VERIFICATION ===")
    print("ACTIVE COMPETITIONS:", len(competitions))
    print("REACHABLE SOURCES:", len(sources))
    print("VERIFICATION PAIRS:", len(jobs))
    print("Starting network verification...")

    results = []

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(verify, x) for x in jobs]

        for i, future in enumerate(as_completed(futures), 1):
            results.append(future.result())

            if i % 25 == 0:
                print(f"PROCESSED: {i}/{len(jobs)}")

    summary = {
        "active_competitions": len(competitions),
        "reachable_sources": len(sources),
        "verification_pairs": len(jobs),
        "verified": sum(x["status"] == "VERIFIED" for x in results),
        "partial": sum(x["status"] == "PARTIAL" for x in results),
        "unusable": sum(x["status"] == "UNUSABLE" for x in results),
        "failed": sum(x["status"] == "FAILED" for x in results),
    }

    OUTPUT.write_text(json.dumps({
        "summary": summary,
        "results": results,
    }, indent=2, ensure_ascii=False))

    print("\n=== RESULT ===")
    for k, v in summary.items():
        print(f"{k.upper()}: {v}")

    print("SAVED:", OUTPUT)


if __name__ == "__main__":
    main()
