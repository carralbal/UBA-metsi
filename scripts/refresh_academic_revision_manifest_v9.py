#!/usr/bin/env python3
"""Refresh the N11-N36 academic manifest from the audited v9 packages."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "academic-content-revision-manifest-n11-n36.json"
WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")


def count_words(value: str) -> int:
    return len(WORD_RE.findall(value))


def segment(text: str, start: str, stop: str) -> str:
    left = text.find(start)
    right = text.find(stop, max(left, 0))
    return text[left if left >= 0 else 0 : right if right >= 0 else None]


def opening_segment(text: str) -> str:
    headings = list(re.finditer(r"^##\s+(.+)$", text, re.MULTILINE))
    start = headings[1].start()
    stops = [
        match.start()
        for match in headings[2:]
        if match.group(1) == "Tesis" or match.group(1).startswith("Hotel Horizonte")
    ]
    return text[start : min(stops)]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = {item["code"]: item for item in manifest["documents"]}
    documents = []
    for number in range(11, 37):
        code = f"N{number:02d}"
        audit_path = ROOT / f"{code}-v9-editorial/qa/content-preservation-audit.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        filename = Path(audit["canonical_source"]).name
        source_rel = Path(f"{code}-content-canonical/source") / filename
        source = ROOT / source_rel
        text = source.read_text(encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != audit["canonical_source_sha256"]:
            raise SystemExit(f"{code}: canonical hash mismatch")
        opening = opening_segment(text)
        substantive = segment(text, opening.splitlines()[0], "## Cinco píldoras para recordar")
        documents.append(
            {
                "code": code,
                "source": str(source_rel),
                "sha256": digest,
                "words_total": count_words(text),
                "words_substantive": count_words(substantive),
                "words_opening": count_words(opening),
                "audit_score": existing[code]["audit_score"],
            }
        )
    manifest.update(
        {
            "created_at": "2026-09-14",
            "scope": "N11-N36 canonical content and v9 editorial packages",
            "status": "content-and-editorial-approved-publication-authorized",
            "publication_policy": "The v9 editorial packages passed content, readability, visual and PDF QA and are authorized for main publication on 2026-09-14.",
            "documents": documents,
        }
    )
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"refreshed {len(documents)} records")


if __name__ == "__main__":
    main()
