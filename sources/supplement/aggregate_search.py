from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "search_raw"

KEYWORDS = {
    "agent": 1,
    "harness": 5,
    "guardrail": 4,
    "runtime": 3,
    "enforcement": 4,
    "policy": 3,
    "privilege": 4,
    "authorization": 4,
    "permission": 3,
    "tool": 2,
    "sandbox": 3,
    "isolation": 3,
    "monitor": 2,
    "contract": 3,
    "invariant": 3,
    "compliance": 3,
    "constraint": 2,
    "approval": 3,
    "verification": 2,
    "safety": 1,
}


def norm_title(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def score(title: str, abstract: str) -> int:
    hay = f"{title} {abstract}".lower()
    return sum(weight for term, weight in KEYWORDS.items() if term in hay)


def doi_key(doi: str | None) -> str | None:
    if not doi:
        return None
    return doi.lower().replace("https://doi.org/", "").replace("doi:", "").strip()


records: list[dict] = []
counts: list[dict] = []

for path in sorted(RAW.glob("openalex-q*.json")):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    query_id = path.stem.split("-")[-1]
    counts.append({"database": "openalex", "query_id": query_id, "reported": data.get("meta", {}).get("count"), "retrieved": len(data.get("results", []))})
    for item in data.get("results", []):
        doi = doi_key(item.get("doi"))
        authors = [a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])]
        abstract_index = item.get("abstract_inverted_index") or {}
        positions = {pos: word for word, indices in abstract_index.items() for pos in indices}
        abstract = " ".join(positions[i] for i in sorted(positions))
        records.append({
            "source": "openalex", "query_id": query_id, "title": item.get("title") or "",
            "year": item.get("publication_year"), "doi": doi, "arxiv_id": None,
            "url": item.get("doi") or item.get("id"), "pdf_url": (item.get("best_oa_location") or {}).get("pdf_url"),
            "venue": ((item.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "authors": authors, "abstract": abstract, "citations": item.get("cited_by_count"),
        })

for path in sorted(RAW.glob("crossref-q*.json")):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    query_id = path.stem.split("-")[-1]
    items = data.get("message", {}).get("items", [])
    counts.append({"database": "crossref", "query_id": query_id, "reported": data.get("message", {}).get("total-results"), "retrieved": len(items)})
    for item in items:
        title = (item.get("title") or [""])[0]
        authors = [" ".join(filter(None, [a.get("given"), a.get("family")])) for a in item.get("author", [])]
        date_parts = (item.get("published") or {}).get("date-parts") or [[None]]
        links = item.get("link") or []
        pdf = next((link.get("URL") for link in links if "pdf" in (link.get("content-type") or "").lower()), None)
        records.append({
            "source": "crossref", "query_id": query_id, "title": title,
            "year": date_parts[0][0], "doi": doi_key(item.get("DOI")), "arxiv_id": None,
            "url": item.get("URL"), "pdf_url": pdf,
            "venue": (item.get("container-title") or [None])[0], "authors": authors,
            "abstract": "", "citations": item.get("is-referenced-by-count"),
        })

ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom", "os": "http://a9.com/-/spec/opensearch/1.1/"}
for path in sorted(RAW.glob("arxiv-q*.xml")):
    root = ET.fromstring(path.read_text(encoding="utf-8-sig"))
    query_id = path.stem.split("-")[-1]
    entries = root.findall("a:entry", ns)
    total_node = root.find("os:totalResults", ns)
    counts.append({"database": "arxiv", "query_id": query_id, "reported": int(total_node.text) if total_node is not None else None, "retrieved": len(entries)})
    for item in entries:
        abs_url = (item.findtext("a:id", default="", namespaces=ns) or "").replace("http://", "https://")
        match = re.search(r"/abs/([^v]+)(?:v\d+)?$", abs_url)
        arxiv_id = match.group(1) if match else None
        authors = [a.findtext("a:name", default="", namespaces=ns) for a in item.findall("a:author", ns)]
        published = item.findtext("a:published", default="", namespaces=ns)
        pdf = None
        for link in item.findall("a:link", ns):
            if link.attrib.get("type") == "application/pdf" or link.attrib.get("title") == "pdf":
                pdf = (link.attrib.get("href") or "").replace("http://", "https://")
        doi = item.findtext("arxiv:doi", default=None, namespaces=ns)
        records.append({
            "source": "arxiv", "query_id": query_id,
            "title": " ".join((item.findtext("a:title", default="", namespaces=ns)).split()),
            "year": int(published[:4]) if published[:4].isdigit() else None,
            "doi": doi_key(doi), "arxiv_id": arxiv_id, "url": abs_url, "pdf_url": pdf,
            "venue": item.findtext("arxiv:journal_ref", default=None, namespaces=ns),
            "authors": authors,
            "abstract": " ".join((item.findtext("a:summary", default="", namespaces=ns)).split()),
            "citations": None,
        })

for path in sorted(RAW.glob("semantic-scholar-q*.json")):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    query_id = path.stem.split("-")[-1]
    items = data.get("data", [])
    counts.append({"database": "semantic-scholar", "query_id": query_id, "reported": data.get("total"), "retrieved": len(items)})
    for item in items:
        external = item.get("externalIds") or {}
        records.append({
            "source": "semantic-scholar", "query_id": query_id, "title": item.get("title") or "",
            "year": item.get("year"), "doi": doi_key(external.get("DOI")), "arxiv_id": external.get("ArXiv"),
            "url": item.get("url"), "pdf_url": (item.get("openAccessPdf") or {}).get("url"),
            "venue": item.get("venue"), "authors": [a.get("name", "") for a in item.get("authors", [])],
            "abstract": item.get("abstract") or "", "citations": item.get("citationCount"),
        })

groups: dict[str, list[dict]] = defaultdict(list)
for record in records:
    normalized = norm_title(record["title"])
    key = f"title:{normalized}" if normalized else f"doi:{record['doi']}" if record.get("doi") else f"arxiv:{record['arxiv_id']}"
    groups[key].append(record)

deduped: list[dict] = []
for key, variants in groups.items():
    variants.sort(key=lambda r: (bool(r.get("abstract")), bool(r.get("pdf_url")), r.get("citations") or -1), reverse=True)
    best = dict(variants[0])
    for field in ("doi", "arxiv_id", "url", "pdf_url", "venue", "authors", "abstract", "year"):
        if not best.get(field):
            best[field] = next((v.get(field) for v in variants if v.get(field)), best.get(field))
    citation_values = [v.get("citations") for v in variants if isinstance(v.get("citations"), int)]
    best["citations"] = max(citation_values) if citation_values else None
    best["sources"] = sorted({v["source"] for v in variants})
    best["query_ids"] = sorted({v["query_id"] for v in variants})
    best["record_count"] = len(variants)
    best["relevance_score"] = score(best.get("title", ""), best.get("abstract", ""))
    best["normalized_title"] = norm_title(best.get("title", ""))
    deduped.append(best)

deduped.sort(key=lambda r: (r["relevance_score"], r.get("citations") or -1), reverse=True)

(ROOT / "all_search_records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "deduplicated_candidates.json").write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "search_counts.json").write_text(json.dumps({"counts": counts, "raw_records": len(records), "deduplicated": len(deduped)}, ensure_ascii=False, indent=2), encoding="utf-8")

fields = ["relevance_score", "title", "year", "doi", "arxiv_id", "venue", "citations", "url", "pdf_url", "sources", "query_ids", "record_count"]
with (ROOT / "deduplicated_candidates.csv").open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in deduped:
        writer.writerow({field: ";".join(row[field]) if isinstance(row.get(field), list) else row.get(field) for field in fields})

print(json.dumps({"raw_records": len(records), "deduplicated": len(deduped), "by_source": Counter(r["source"] for r in records)}, ensure_ascii=False, indent=2))
