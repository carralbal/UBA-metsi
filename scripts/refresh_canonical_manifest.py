#!/usr/bin/env python3
"""Refresh a canonical Markdown manifest after an approved wording edit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source_blocks(text: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            value = " ".join(part.strip() for part in buffer).strip()
            if value:
                result.append({"kind": "paragraph", "text": value})
            buffer.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
        elif line.startswith("#"):
            flush()
            result.append({"kind": "heading", "text": line})
        elif re.match(r"^(?:\d+\.|- )", line):
            flush()
            result.append({"kind": "list-item", "text": line})
        else:
            buffer.append(line)
    flush()
    for index, item in enumerate(result, 1):
        item["source_id"] = f"src-{index:04d}"
    return result


def refresh(number: int) -> None:
    package = ROOT / f"N{number:02d}-content-canonical"
    manifest_path = package / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = package / manifest["source"]
    text = source.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    blocks = source_blocks(text)
    manifest["source_sha256"] = digest
    manifest["eligible_blocks"] = blocks
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_path = package / "provenance" / "integrity-report.json"
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["source_sha256"] = digest
        report["block_count"] = len(blocks)
        for value in report.values():
            if isinstance(value, dict) and "source_sha256" in value:
                value["source_sha256"] = digest
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"N{number:02d} {digest} {len(blocks)} blocks")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="+", type=int)
    args = parser.parse_args()
    for number in args.numbers:
        refresh(number)


if __name__ == "__main__":
    main()
