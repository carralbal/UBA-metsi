#!/usr/bin/env python3
"""Rank manually inspected stock-image candidates for the METSI visual system."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

POSITIVE = {
    "concept_match": 0.24,
    "editorial_quality": 0.18,
    "negative_space": 0.12,
    "contrast_match": 0.10,
    "palette_match": 0.13,
    "crop_flexibility": 0.09,
    "series_cohesion": 0.14,
}
PENALTIES = {
    "literalness_penalty": 0.12,
    "stock_cliche_penalty": 0.22,
    "license_risk_penalty": 0.50,
}


def bounded(value: object, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number from 0 to 1") from exc
    if not 0 <= number <= 1:
        raise ValueError(f"{field} must be from 0 to 1")
    return number


def score(candidate: dict) -> float:
    total = sum(bounded(candidate.get(k, 0), k) * w for k, w in POSITIVE.items())
    total -= sum(bounded(candidate.get(k, 0), k) * w for k, w in PENALTIES.items())
    if int(candidate.get("width", 0)) < 1600:
        total -= 0.08
    if not candidate.get("source_page") or not candidate.get("license_url"):
        total -= 0.35
    return round(max(0.0, min(1.0, total)), 4)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    candidates = data["candidates"] if isinstance(data, dict) else data
    ranked = []
    for item in candidates:
        copy = dict(item)
        copy["metsi_score"] = score(copy)
        ranked.append(copy)
    ranked.sort(key=lambda x: x["metsi_score"], reverse=True)
    result = {"candidates": ranked}
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
