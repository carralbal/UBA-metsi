#!/usr/bin/env python3
"""Run and persist the read-only publication gate for METSI N11-N36 v8."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import validate_n11_n36_v6 as gate  # noqa: E402


REPORT_ROOT = ROOT / "qa-reports" / "n11-n36-v8"


def write_report(number: int) -> dict:
    try:
        report = gate.audit(number)
    except Exception as error:
        report = {
            "document": f"N{number:02d}",
            "package": f"N{number:02d}-v8-editorial",
            "version": "v8-editorial",
            "validator": Path(gate.__file__).name,
            "mode": "read-only",
            "status": "ERROR",
            "error": f"{type(error).__name__}: {error}",
        }
    target = REPORT_ROOT / f"N{number:02d}-validation-v8.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    failures = ",".join(report.get("failed_checks", [])) or report.get("error", "") or "none"
    print(f"{report['document']}\t{report['status']}\t{report.get('metrics', {}).get('pages', '?')}\t{failures}", flush=True)
    return report


def aggregate() -> int:
    reports = []
    for number in range(11, 37):
        path = REPORT_ROOT / f"N{number:02d}-validation-v8.json"
        if path.is_file():
            reports.append(json.loads(path.read_text(encoding="utf-8")))
    summary = {
        "schema": "metsi-n11-n36-v8-publication-gate/v1",
        "documents_expected": 26,
        "documents_found": len(reports),
        "pass": sum(item.get("status") == "PASS" for item in reports),
        "fail": sum(item.get("status") == "FAIL" for item in reports),
        "error": sum(item.get("status") == "ERROR" for item in reports),
        "status": "PASS" if len(reports) == 26 and all(item.get("status") == "PASS" for item in reports) else "FAIL",
        "documents": [
            {
                "document": item.get("document"),
                "status": item.get("status"),
                "pages": item.get("metrics", {}).get("pages"),
                "minimum_ordinary_vertical_density": item.get("metrics", {}).get("minimum_ordinary_vertical_density"),
                "failed_checks": item.get("failed_checks", []),
                "error": item.get("error"),
            }
            for item in reports
        ],
    }
    target = REPORT_ROOT / "PUBLICATION-GATE-SUMMARY.json"
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=36)
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    if not 11 <= args.start <= args.end <= 36:
        parser.error("se requiere 11 <= --start <= --end <= 36")
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    gate.PACKAGE_VERSION = 8
    if args.aggregate_only:
        return aggregate()
    results = [write_report(number) for number in range(args.start, args.end + 1)]
    aggregate_status = aggregate()
    return 1 if aggregate_status or any(item.get("status") != "PASS" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
