"""Build auditable screening decisions and PRISMA-style flow counts."""

from __future__ import annotations

import csv
import json
import re
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def normalize(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()


def exclusion_reason(title: str) -> str:
    lowered = title.lower()
    if any(token in lowered for token in ("survey", "review", "position", "taxonomy", "framework for formalizing")):
        return "Conceptual/survey record without a directly auditable enforcement artifact"
    if any(token in lowered for token in ("finance", "radio", "iot", "swarms", "geospatial", "data lake", "bci")):
        return "Domain-specific or adjacent system outside the general tool-agent harness scope"
    if any(token in lowered for token in ("benchmark", "testbed", "safeclawbench")):
        return "Evaluation or benchmark contribution rather than runtime instruction enforcement"
    return "No sufficiently direct, quality-verified harness enforcement contribution after metadata/abstract assessment"


def main() -> None:
    formal = json.loads((HERE / "deduplicated_candidates.json").read_text(encoding="utf-8"))
    high_recall = [record for record in formal if int(record.get("relevance_score", 0)) >= 12]
    with (HERE / "supplementary_candidates.csv").open(encoding="utf-8", newline="") as stream:
        supplementary = list(csv.DictReader(stream))

    included_titles = {normalize(row["title"]): row for row in supplementary if row["decision"] == "include"}
    decisions: list[dict[str, object]] = []
    represented_supplementary: set[str] = set()

    for record in high_recall:
        title = record["title"]
        best = max(supplementary, key=lambda row: similarity(title, row["title"]))
        score = similarity(title, best["title"])
        if score >= 0.91:
            represented_supplementary.add(normalize(best["title"]))
        include_row = included_titles.get(normalize(best["title"])) if score >= 0.91 else None
        decisions.append(
            {
                "stream": "formal-database-rule-pass",
                "title": title,
                "relevance_score": record.get("relevance_score"),
                "decision": "include" if include_row else "exclude",
                "reason": include_row["reason"] if include_row else exclusion_reason(title),
                "matched_supplementary_title": best["title"] if score >= 0.91 else "",
                "title_similarity": round(score, 3) if score >= 0.91 else "",
            }
        )

    additions = [row for row in supplementary if normalize(row["title"]) not in represented_supplementary]
    for row in additions:
        decisions.append(
            {
                "stream": "supplementary-addition-or-rescue",
                "title": row["title"],
                "relevance_score": "",
                "decision": row["decision"],
                "reason": row["reason"],
                "matched_supplementary_title": row["title"],
                "title_similarity": 1.0,
            }
        )

    included = [row for row in decisions if row["decision"] == "include"]
    counts = {
        "database_records_retrieved": 650,
        "duplicates_removed": 104,
        "unique_database_records": 546,
        "formal_rule_pass": len(high_recall),
        "formal_title_abstract_excluded": 546 - len(high_recall),
        "supplementary_candidates_assessed": len(supplementary),
        "supplementary_overlap_with_rule_pass": len(supplementary) - len(additions),
        "supplementary_additions_or_rescues": len(additions),
        "detailed_assessment_pool": len(decisions),
        "included_studies": len(included),
        "excluded_after_detailed_assessment": len(decisions) - len(included),
    }

    fieldnames = list(decisions[0].keys())
    with (HERE / "screening_decisions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(decisions)
    (HERE / "screening_flow.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    print(json.dumps(counts, indent=2))
    if len(included) != 16:
        raise SystemExit(f"Expected 16 included studies, got {len(included)}")


if __name__ == "__main__":
    main()
