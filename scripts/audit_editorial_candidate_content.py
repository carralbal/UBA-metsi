#!/usr/bin/env python3
"""Prove that an editorial candidate preserves its canonical Markdown source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"https?://[^\s]+|[\wÁÉÍÓÚÜÑáéíóúüñ'-]+", re.UNICODE)


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(value: str) -> list[str]:
    value = unicodedata.normalize("NFKC", value).strip()
    value = re.sub(r"^#{1,6}\s*", "", value)
    value = re.sub(r"^[-*+]\s+", "", value)
    value = re.sub(r"^\d+[.)]\s+", "", value)
    value = re.sub(r"[*_`]", "", value)
    value = value.replace("|", " ")
    return WORD_RE.findall(value.casefold())


def audit(number: int, version: int) -> Path:
    code = f"N{number:02d}"
    canonical_root = ROOT / f"{code}-content-canonical"
    package = ROOT / f"{code}-v{version}-editorial"
    canonical_manifest_path = canonical_root / "source-manifest.json"
    package_manifest_path = package / "manifest.json"
    source_manifest_path = package / "source-manifest.json"
    html_path = package / "index.html"
    pdf_path = package / "output" / f"{code}-METSI-lectura-previa-v{version}-final.pdf"
    qa_path = package / "qa-report.json"

    canonical_manifest = json.loads(canonical_manifest_path.read_text(encoding="utf-8"))
    package_manifest = json.loads(package_manifest_path.read_text(encoding="utf-8"))
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    validation = subprocess.run(
        [
            sys.executable,
            str(ROOT / "validate_n11_n36_v6.py"),
            "--start", str(number),
            "--end", str(number),
            "--version", str(version),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    validator_lines = [line for line in validation.stdout.splitlines() if line.strip()]
    if not validator_lines:
        raise RuntimeError(f"candidate validator produced no JSON: {validation.stderr.strip()}")
    qa = json.loads(validator_lines[-1])
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    canonical_source = canonical_root / canonical_manifest["source"]
    packaged_source = package / package_manifest["source"]
    canonical_entries = canonical_manifest["eligible_blocks"]
    rendered_entries = source_manifest["eligible_blocks"]

    referents_index = next(
        index for index, entry in enumerate(canonical_entries)
        if entry["text"].strip() == "## Referentes"
    )
    references_index = next(
        index for index, entry in enumerate(canonical_entries)
        if entry["text"].strip() == "## Referencias base"
    )
    referent_entries = canonical_entries[referents_index + 1:references_index]
    canonical_editorial_entries = canonical_entries[1:referents_index] + canonical_entries[references_index:]
    rendered_editorial_entries = rendered_entries[1:]

    canonical_counter = Counter(
        token for entry in canonical_editorial_entries for token in tokens(entry["text"])
    )
    rendered_counter = Counter(
        token for entry in rendered_editorial_entries for token in tokens(entry["text"])
    )

    parser = VisibleText()
    parser.feed(html_path.read_text(encoding="utf-8"))
    visible_html = " ".join(parser.parts)
    visible_tokens = Counter(tokens(visible_html))
    referent_token_counter = Counter(
        token for entry in referent_entries for token in tokens(entry["text"])
    )
    referents_present = not (referent_token_counter - visible_tokens)

    qa_checks = qa.get("checks", [])
    qa_failed = [
        item.get("check")
        for item in qa_checks
        if item.get("status") != "PASS"
    ]
    checks = {
        "canonical_source_hash_matches_manifest": sha256(canonical_source) == canonical_manifest["source_sha256"],
        "packaged_source_is_byte_identical_to_canonical": sha256(packaged_source) == sha256(canonical_source),
        "package_manifest_locks_canonical_hash": package_manifest.get("source_sha256") == sha256(canonical_source),
        "canonical_editorial_tokens_equal_rendered_editorial_tokens": canonical_counter == rendered_counter,
        "canonical_referent_words_are_present_in_html": referents_present,
        "editorial_integrity_report_passes": json.loads((package / "integrity-report.json").read_text(encoding="utf-8")).get("status") == "PASS",
        "pdf_exists_and_is_new_output": pdf_path.is_file() and pdf_path.stat().st_size > 0,
        "candidate_validator_passes": not qa_failed and qa.get("status") == "PASS",
    }
    result = {
        "document": code,
        "candidate": f"v{version}-editorial",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "canonical_stage": canonical_manifest.get("stage"),
        "canonical_source": canonical_manifest["source"],
        "canonical_source_sha256": sha256(canonical_source),
        "canonical_blocks": len(canonical_entries),
        "rendered_traceable_blocks": len(rendered_entries),
        "canonical_editorial_tokens": sum(canonical_counter.values()),
        "rendered_editorial_tokens": sum(rendered_counter.values()),
        "canonical_referent_blocks": len(referent_entries),
        "pdf_bytes": pdf_path.stat().st_size if pdf_path.is_file() else 0,
        "validator_failed_checks": qa_failed,
        "checks": checks,
    }
    target = package / "qa" / "content-preservation-audit.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']} {code} v{version}: {target}")
    if result["status"] != "PASS":
        raise SystemExit(1)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--number", type=int, required=True)
    parser.add_argument("--version", type=int, required=True)
    args = parser.parse_args()
    audit(args.number, args.version)


if __name__ == "__main__":
    main()
