#!/usr/bin/env python3
"""Run and preserve the exhaustive N11–N36 audit with concise console output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_block_c_v2 import audit


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "qa-reports" / "block-c-v3"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=36)
    args = parser.parse_args()
    if not 11 <= args.start <= args.end <= 36:
        parser.error("se requiere 11 <= --start <= --end <= 36")

    REPORTS.mkdir(parents=True, exist_ok=True)
    failed = False
    for number in range(args.start, args.end + 1):
        report = audit(number)
        target = REPORTS / f"N{number:02d}-validation-v3.json"
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        failed_checks = report.get("failed_checks", [])
        metrics = report.get("metrics", {})
        print(
            f"N{number:02d} {report['status']} "
            f"pages={metrics.get('pages')} density={metrics.get('minimum_ordinary_vertical_density')} "
            f"fails={','.join(failed_checks) if failed_checks else '-'}"
        )
        failed = failed or report["status"] != "PASS"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
