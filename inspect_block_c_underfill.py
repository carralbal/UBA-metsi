#!/usr/bin/env python3
"""Identify the semantic unit occupying every underfilled Block C page."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "qa-reports" / "block-c-v3"


for report_path in sorted(REPORTS.glob("N*-validation-v3.json")):
    report = json.loads(report_path.read_text(encoding="utf-8"))
    density = next(
        check for check in report["checks"]
        if check["check"] == "ordinary_raster_pages_reach_55_percent_vertical_density"
    )["evidence"]["underfilled"]
    if not density:
        continue
    number = int(report["document"][1:])
    pdf = ROOT / f"N{number:02d}-v3-editorial" / "output" / f"N{number:02d}-METSI-lectura-previa-v3-final.pdf"
    with pdfplumber.open(pdf) as document:
        for page_value, ratio in density.items():
            page_number = int(page_value)
            text = document.pages[page_number - 1].extract_text() or ""
            lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]
            preview = " | ".join(lines[:8])
            print(f"N{number:02d} p{page_number:02d} {ratio:.4f} :: {preview}")
