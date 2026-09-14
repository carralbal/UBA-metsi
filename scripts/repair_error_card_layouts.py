#!/usr/bin/env python3
"""Repair and verify the recurring ``Errores frecuentes`` grid in N11–N36.

The operation is deliberately structural: it groups every bold error label
with the explanation that follows, then derives the grid row count from the
number of complete cards.  Source text and ``data-source-id`` values remain
unchanged.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build_block_c_editorial import wrap_error_cards


SECTION_RE = re.compile(
    r'(<section\b(?=[^>]*class="[^"]*\bblock-c-errors\b[^"]*")[^>]*>)'
    r'(.*?)'
    r'(</section>)',
    re.S,
)
STYLE_RE = re.compile(r'--error-rows:\d+')
def repair_html(html: str, code: str) -> tuple[str, int]:
    matches = list(SECTION_RE.finditer(html))
    if len(matches) != 1:
        raise RuntimeError(f"{code}: expected one errors section, found {len(matches)}")

    match = matches[0]
    opening, body, closing = match.groups()
    labels = len(re.findall(r'<h3\b', body)) + len(re.findall(
        r'<p\b[^>]*>\s*<strong\b', body, re.S
    ))
    repaired_body = wrap_error_cards(body)
    cards = repaired_body.count('class="error-card"')
    if cards < 1 or cards != labels:
        raise RuntimeError(f"{code}: labels={labels}, complete cards={cards}")

    rows = (cards + 1) // 2
    if STYLE_RE.search(opening):
        opening = STYLE_RE.sub(f"--error-rows:{rows}", opening)
    elif ' style="' in opening:
        opening = opening.replace(' style="', f' style="--error-rows:{rows};', 1)
    else:
        opening = opening[:-1] + f' style="--error-rows:{rows}">'

    repaired = html[: match.start()] + opening + repaired_body + closing + html[match.end() :]
    return repaired, cards


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=36)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.start < 11 or args.end > 36 or args.start > args.end:
        raise ValueError("range must stay within N11–N36")

    changed = 0
    for number in range(args.start, args.end + 1):
        code = f"N{number:02d}"
        path = ROOT / f"{code}-v9-editorial" / "index.html"
        before = path.read_text(encoding="utf-8")
        after, cards = repair_html(before, code)
        was_changed = after != before
        if was_changed and not args.check:
            path.write_text(after, encoding="utf-8")
        changed += int(was_changed)
        print(f"{code} cards={cards} rows={(cards + 1) // 2} changed={was_changed}")

    if args.check and changed:
        raise SystemExit(f"FAIL: {changed} documents require repair")
    print(f"PASS: repaired={changed if not args.check else 0}")


if __name__ == "__main__":
    main()
