#!/usr/bin/env python3
"""Point METSI's public bibliography links at the recovered PDF folios."""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
STAGE = Path("/private/tmp/metsi-editorial-recovery.LQBs9R")
HTML = ROOT / "site/index.html"
OLD_VERSION = "portadas-velo-gradual-20260928"
NEW_VERSION = "editorial-recuperada-20260929"


def reference_page(number: int) -> int:
    pages = PdfReader(STAGE / f"N{number:02d}" / "candidate.pdf").pages
    matches = [index + 1 for index, page in enumerate(pages)
               if index > 5 and "Referencias base" in (page.extract_text() or "")]
    if len(matches) != 1:
        raise ValueError(f"N{number:02d}: expected one references page, got {matches}")
    return matches[0]


def main() -> None:
    folios = {f"N{number:02d}": reference_page(number) for number in range(1, 37)}
    source = HTML.read_text()

    def replace_href(match: re.Match[str]) -> str:
        code = match.group("code")
        return f'{match.group("prefix")}{folios[code]}{match.group("suffix")}'

    updated, href_count = re.subn(
        r'(?P<prefix>href="[^"]*?(?P<code>N\d{2})-METSI-lectura-previa-[^"]*?#page=)\d+(?P<suffix>[^"]*")',
        replace_href, source,
    )
    if href_count < 100:
        raise ValueError(f"Only {href_count} bibliography links found; refusing partial update")

    updated, aria_count = re.subn(
        r'Bibliografía de (N\d{2}), página \d+',
        lambda match: f'Bibliografía de {match.group(1)}, página {folios[match.group(1)]}',
        updated,
    )
    for code, page in folios.items():
        pattern = re.compile(
            rf'(<li><a href="[^"]*{code}-METSI-lectura-previa-[^"]*"[^>]*>[^<]*</a><small>Referencias base · pág\. )\d+(</small></li>)'
        )
        updated, count = pattern.subn(rf'\g<1>{page}\2', updated)
        if count != 1:
            raise ValueError(f"{code}: expected one bibliography-grid label, found {count}")

    updated, version_count = re.subn(
        rf'(href="[^"]*N\d{{2}}-METSI-lectura-previa-[^"]*?\?v=){OLD_VERSION}',
        rf'\g<1>{NEW_VERSION}', updated,
    )
    if version_count < 200 or aria_count < 100:
        raise ValueError(f"Unexpected update scope: versions={version_count}, aria={aria_count}")
    if updated == source:
        raise ValueError("No changes")
    HTML.write_text(updated)
    print(f"Updated {href_count} reference-page links, {aria_count} labels, "
          f"{version_count} PDF cache keys")
    print("Reference folios:", folios)


if __name__ == "__main__":
    main()
