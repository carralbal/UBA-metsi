#!/usr/bin/env python3
"""Stage current prose with the approved magazine CSS, without touching live PDFs.

This is a recovery *candidate* generator. It does not mark any PDF publishable.
Every candidate still requires source-integrity and page-by-page visual QA.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from lxml import html as lxml_html

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_collection  # noqa: E402


PLAN = ROOT / "pedagogy/plain-language-edition/release-plan.json"
RECOVERY_CSS = ROOT / "pedagogy/editorial-recovery-20260929/recovery.css"
PACKAGE_BY_NUMBER = {
    int(entry["code"][1:]): ROOT / entry["package"]
    for entry in json.loads(PLAN.read_text())
}
PACKAGE_BY_NUMBER[25] = ROOT / "N25-v14-editorial"


def restore_section_classes(number: int, source: str) -> tuple[str, int]:
    """Recover the page families erased by the readability generator."""

    pattern = re.compile(
        r'(<section class=")([^"]*\breading-section\b[^"]*)("[^>]*\bdata-section="(\d+)"[^>]*>)'
    )
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        nearby = source[match.end() : match.end() + 1800]
        heading = re.search(r"<h2\b[^>]*>(.*?)</h2>", nearby, re.S)
        if not heading:
            raise ValueError(f"N{number:02d}: heading missing at section {match[4]}")
        title = html.unescape(re.sub(r"<[^>]+>", "", heading[1])).strip()
        original = build_collection.section_classes(number, int(match[4]), title)
        # Keep special roles added by the later builder; the indiscriminate
        # two-column class must still be replaced by the editorial family.
        generic = {"reading-section", "edition-section", "two-column"}
        preserved = [name for name in match[2].split() if name not in generic]
        merged = list(dict.fromkeys(original + preserved))
        count += 1
        return match[1] + " ".join(merged) + match[3]

    return pattern.sub(replace, source), count


def restore_hotel_spreads(number: int, source: str, package: Path) -> tuple[str, int]:
    """Recompose omitted HH spreads with their established visual apparatus.

    Only imagery and structural wrappers are borrowed from the earlier edition.
    Every paragraph and its source ID comes from the readable current edition.
    """

    if number < 11:
        return source, 0
    old_html = ROOT / f"N{number:02d}-v10-editorial/index.html"
    if not old_html.is_file():
        raise FileNotFoundError(old_html)
    original = lxml_html.parse(str(old_html))
    previous = [
        section
        for section in original.xpath("//section[@data-section]")
        if "hotel-case" in section.get("class", "").split()
    ]
    restored = 0

    def splice(match: re.Match[str]) -> str:
        nonlocal restored
        section = lxml_html.fromstring(match[0])
        title = section.xpath("./div[@class='section-heading']/h2")[0].text_content()
        old = next(
            (candidate for candidate in previous if candidate.xpath("./div[@class='section-heading']/h2")[0].text_content() == title),
            None,
        )
        if old is None and title.startswith(f"Instrumento HH-{number:02d}:"):
            old = next(
                (candidate for candidate in previous if candidate.xpath("./div[@class='section-heading']/h2")[0].text_content().startswith(f"Instrumento HH-{number:02d}:")),
                None,
            )
        if old is None or section.xpath(".//figure[contains(@class,'hotel-primary-photo')]"):
            return match[0]
        if not section.xpath("./div[@class='section-body']"):
            return match[0]
        photo = old.xpath("./figure[contains(@class,'hotel-primary-photo')]")
        voices = old.xpath("./div[@class='hotel-continuation']/aside[contains(@class,'hotel-voices')]")
        icon = old.xpath("./div[@class='section-heading']/svg[contains(@class,'case-application-icon')]")
        if not photo or not voices or not icon:
            return match[0]
        for image in [*photo[0].xpath(".//img"), *voices[0].xpath(".//img")]:
            image_path = package / image.get("src")
            if not image_path.is_file():
                raise FileNotFoundError(image_path)
        heading = section.xpath("./div[@class='section-heading']")[0]
        heading.insert(1, icon[0])
        body = section.xpath("./div[@class='section-body']")[0]
        elements = list(body)
        if len(elements) < 3:
            return match[0]
        section.remove(body)
        lead = lxml_html.Element("div", {"class": "section-body section-lead"})
        lead.append(elements[0])
        section.append(lead)
        section.append(photo[0])
        bridge = lxml_html.Element("div", {"class": "section-body hotel-bridge"})
        bridge.append(elements[1])
        section.append(bridge)
        continuation = lxml_html.Element("div", {"class": "hotel-continuation"})
        continuation.append(voices[0])
        later = lxml_html.Element("div", {"class": "section-body hotel-continuation-body"})
        for element in elements[2:]:
            column = lxml_html.Element("div", {"class": "hotel-text-column"})
            column.append(element)
            later.append(column)
        continuation.append(later)
        section.append(continuation)
        restored += 1
        return lxml_html.tostring(section, encoding="unicode", method="html")

    source = re.sub(
        r'<section class="[^"]*\bhotel-case\b[^"]*"[^>]*data-section="\d+"[^>]*>.*?</section>',
        splice,
        source,
        flags=re.S,
    )
    return source, restored


def restore_mid_argument_visual(number: int, source: str, package: Path) -> tuple[str, int]:
    """Give the longest arguments one source-relevant visual breathing point.

    These assets already belong to the approved document packages. The
    intervention changes only placement, never a source paragraph or its ID.
    """

    choices = {
        3: ("06", "assets/editorial-02.jpg", "La frontera organiza lo visible; un efecto puede reaparecer del otro lado.", "photo"),
        4: ("06", "assets/editorial-02.jpg", "Antes de aceptar una afirmación, conviene mirar qué estructura la sostiene.", "photo"),
    }
    if number not in choices:
        return source, 0
    section_id, image_path, caption, kind = choices[number]
    if not (package / image_path).is_file():
        raise FileNotFoundError(package / image_path)
    pattern = re.compile(
        rf'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="{section_id}"[^>]*>.*?</section>',
        re.S,
    )

    def insert(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        body = section.xpath("./div[contains(@class,'section-body')]")[0]
        paragraphs = body.xpath("./p")
        if len(paragraphs) < 12:
            raise ValueError(f"N{number:02d}: section {section_id} is too short for a visual pause")
        anchor = paragraphs[len(paragraphs) // 2]
        figure = lxml_html.Element("figure", {"class": f"editorial-argument-pause {kind}"})
        image = lxml_html.Element("img", {"src": image_path, "alt": caption or "Mapa de la evidencia y las decisiones que puede cambiar"})
        figure.append(image)
        if caption:
            label = lxml_html.Element("figcaption")
            label.text = caption
            figure.append(label)
        anchor.addnext(figure)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    return pattern.subn(insert, source, count=1)


def prepare(number: int, destination: Path) -> dict:
    package = PACKAGE_BY_NUMBER[number]
    if not package.is_dir():
        raise FileNotFoundError(package)
    source = (package / "index.html").read_text()
    if 'href="edition.css"' not in source or 'id="plain-edition"' not in source:
        raise ValueError(f"N{number:02d}: unexpected source edition")

    source = source.replace('<link rel="stylesheet" href="edition.css">', "", 1)
    source = source.replace(
        "</head>", '<link rel="stylesheet" href="recovery.css"></head>', 1
    )
    source, body_count = re.subn(
        r'<body id="plain-edition" class="([^"]*)">',
        lambda match: '<body class="'
        + " ".join(
            dict.fromkeys(
                [
                    "premium-magazine",
                    f"document-n{number:02d}",
                    *[
                        name
                        for name in match[1].split()
                        if name not in {"premium-magazine", "plain-edition"}
                    ],
                ]
            )
        )
        + '">',
        source,
        count=1,
    )
    if body_count != 1:
        raise ValueError(f"N{number:02d}: body was not recovered")
    source, restored_sections = restore_section_classes(number, source)
    source, restored_hotel_spreads = restore_hotel_spreads(number, source, package)
    source, restored_mid_visuals = restore_mid_argument_visual(number, source, package)
    if number in (3, 4) and restored_mid_visuals != 1:
        raise ValueError(f"N{number:02d}: editorial visual pause was not inserted")
    if number == 3:
        # The closing interpretation belongs to the immediately preceding
        # evidence table. Keep its exact wording and source ID, but move it
        # inside that table's page-spanning editorial unit; otherwise Chrome
        # leaves the 39-word paragraph alone on a new sheet.
        source, closing_count = re.subn(
            r'(</tbody></table>)</div>(<p data-source-id="N03-s06-b071">.*?</p>)',
            r'\1\2</div>',
            source,
            count=1,
            flags=re.S,
        )
        if closing_count != 1:
            raise ValueError("N03: could not reunite the closing note and table")

    target = destination / f"N{number:02d}"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("assets", "diagrams", "magazine.css"):
        original = package / name
        if original.exists():
            link = target / name
            if not link.exists() and not link.is_symlink():
                link.symlink_to(original)
    recovery_link = target / "recovery.css"
    if not recovery_link.exists() and not recovery_link.is_symlink():
        recovery_link.symlink_to(RECOVERY_CSS)
    (target / "index.html").write_text(source)
    result = {
        "number": number,
        "original_package": str(package),
        "candidate_html": str(target / "index.html"),
        "restored_section_classes": restored_sections,
        "restored_hotel_spreads": restored_hotel_spreads,
        "restored_mid_visuals": restored_mid_visuals,
        "source_blocks": len(re.findall(r'data-source-id="[^"]+"', source)),
        "status": "candidate_not_approved",
    }
    (target / "recovery.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    options = parser.parse_args()
    for number in options.numbers or range(1, 37):
        print(json.dumps(prepare(number, options.destination), ensure_ascii=False))
