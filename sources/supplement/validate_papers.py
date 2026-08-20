"""Validate downloaded paper PDFs and write a reproducible integrity manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT / "papers" / "supplement"
SELECTION = Path(__file__).with_name("selected_papers.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))
    manifest: list[dict[str, object]] = []
    failures: list[str] = []
    for paper in selected:
        path = PAPER_DIR / f"{paper['id']}.pdf"
        record: dict[str, object] = {
            "id": paper["id"],
            "title": paper["title"],
            "doi": paper.get("doi"),
            "source_url": paper["url"],
            "path": path.relative_to(ROOT).as_posix(),
            "exists": path.exists(),
        }
        try:
            if path.read_bytes()[:5] != b"%PDF-":
                raise ValueError("missing %PDF signature")
            reader = PdfReader(str(path))
            sample = "\n".join((page.extract_text() or "") for page in reader.pages[:3])
            record.update(
                {
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "pages": len(reader.pages),
                    "sample_text_characters": len(sample.strip()),
                    "readable": len(sample.strip()) >= 200,
                }
            )
            if not record["readable"]:
                failures.append(f"{paper['id']}: insufficient extractable text")
        except Exception as exc:  # keep a complete manifest even when one PDF is bad
            record.update({"readable": False, "error": str(exc)})
            failures.append(f"{paper['id']}: {exc}")
        manifest.append(record)

    output = PAPER_DIR / "manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"papers": len(manifest), "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
