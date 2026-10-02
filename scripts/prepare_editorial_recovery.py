#!/usr/bin/env python3
"""Stage current prose with the approved magazine CSS, without touching live PDFs.

This is a recovery *candidate* generator. It does not mark any PDF publishable.
Every candidate still requires source-integrity and page-by-page visual QA.
"""

from __future__ import annotations

import argparse
import copy
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


def restore_approved_photography(number: int, source: str, package: Path) -> tuple[str, int]:
    """Recover photographs omitted by the plain-language rebuild.

    The figure is copied from the last editorial edition, while all current
    headings and source-bearing prose remain untouched. When a section was
    retitled or divided, the target follows its *subject*, not its old number.
    """

    approved = {
        1: ("N01-v19-final", [("21", "21", "hotel-photo", "after-heading")]),
        2: ("N02-v16-final", [("15", "15", "hotel-photo", "after-heading")]),
        31: ("N31-v10-editorial", [("08", "08", "movement-two-photo", "after-lead")]),
        32: ("N32-v10-editorial", [("08", "10", "movement-two-photo", "after-lead")]),
        33: (
            "N33-v10-editorial",
            [
                ("08", "11", "movement-two-photo", "after-lead"),
                ("09", "15", "movement-three-tail-photo", "after-body"),
            ],
        ),
        34: ("N34-v10-editorial", [("05", "05", "traditions-evidence-photo", "after-body")]),
    }
    if number not in approved:
        return source, 0

    old_package, restorations = approved[number]
    original = lxml_html.parse(str(ROOT / old_package / "index.html"))
    restored = 0
    for old_section, current_section, figure_class, position in restorations:
        previous = original.xpath(
            f'//section[@data-section="{old_section}"]'
            f'//figure[contains(concat(" ", normalize-space(@class), " "), " {figure_class} ")]'
        )
        if len(previous) != 1:
            raise ValueError(f"N{number:02d}: approved {figure_class} is missing or ambiguous")
        for image in previous[0].xpath(".//img"):
            asset = package / image.get("src")
            if not asset.is_file():
                raise FileNotFoundError(asset)

        pattern = re.compile(
            rf'<section class="[^"]*\breading-section\b[^"]*"[^>]*'
            rf'data-section="{current_section}"[^>]*>.*?</section>',
            re.S,
        )

        def insert(match: re.Match[str]) -> str:
            nonlocal restored
            section = lxml_html.fromstring(match[0])
            if section.xpath(
                f'.//figure[contains(concat(" ", normalize-space(@class), " "), " {figure_class} ")]'
            ):
                raise ValueError(f"N{number:02d}: {figure_class} already present")
            figure = copy.deepcopy(previous[0])
            heading = section.xpath("./div[contains(@class,'section-heading')]")
            bodies = section.xpath("./div[contains(@class,'section-body')]")
            if len(heading) != 1 or not bodies:
                raise ValueError(f"N{number:02d}: unexpected section {current_section} structure")
            if position == "after-heading":
                heading[0].addnext(figure)
            elif position == "after-lead":
                body = bodies[0]
                paragraphs = body.xpath("./p")
                if len(paragraphs) < 2:
                    raise ValueError(f"N{number:02d}: no lead to precede {figure_class}")
                lead = lxml_html.Element("div", {"class": "section-body section-lead"})
                body.addprevious(lead)
                lead.append(paragraphs[0])
                lead.addnext(figure)
            else:
                bodies[-1].addnext(figure)
            restored += 1
            return lxml_html.tostring(section, encoding="unicode", method="html")

        source, matches = pattern.subn(insert, source, count=1)
        if matches != 1:
            raise ValueError(f"N{number:02d}: section {current_section} not found")
    if restored != len(restorations):
        raise ValueError(f"N{number:02d}: incomplete photographic recovery")
    return source, restored


def restore_editorial_interludes(number: int, source: str, package: Path) -> tuple[str, int]:
    """Keep the visual interludes that disappeared during the prose rewrite.

    N01's six Hotel Horizonte voices are a distinct visual cast, not another
    paragraph of the case. N23 had a photographic pause at consequences; its
    rewritten text combines consequences and limits into one section, so the
    photograph follows that section's heading without importing old prose.
    N24 already repeats that photograph in the adjacent errors section; adding
    the old second occurrence would create a visibly redundant spread.
    """

    if number not in (1, 23):
        return source, 0
    approved = ROOT / ("N01-v19-final" if number == 1 else f"N{number:02d}-v10-editorial")
    original = lxml_html.parse(str(approved / "index.html"))
    if number == 1:
        voices = original.xpath('//aside[contains(@class,"hotel-voices-compact")]')
        if len(voices) != 1:
            raise ValueError("N01: approved Hotel voices missing or ambiguous")
        for image in voices[0].xpath('.//img'):
            if not (package / image.get("src")).is_file():
                raise FileNotFoundError(package / image.get("src"))
        if 'class="hotel-voices-compact"' in source:
            raise ValueError("N01: Hotel voices already present")
        anchor = re.compile(r'(<section class="[^"]*\bhotel-case\b[^"]*"[^>]*data-section="21"[^>]*>.*?</section>)', re.S)
        source, count = anchor.subn(
            lambda match: match[1] + lxml_html.tostring(copy.deepcopy(voices[0]), encoding="unicode", method="html"),
            source,
            count=1,
        )
        if count != 1:
            raise ValueError("N01: Hotel section 21 not found")
        return source, count

    figures = original.xpath('//figure[contains(@class,"consequence-photo")]')
    if len(figures) != 1:
        raise ValueError(f"N{number:02d}: approved consequence image missing or ambiguous")
    figure = copy.deepcopy(figures[0])
    for image in figure.xpath('.//img'):
        if not (package / image.get("src")).is_file():
            raise FileNotFoundError(package / image.get("src"))
    # The approved caption is retained; only its placement changes to suit the
    # newer combined section. The 2026 explanatory prose stays untouched.
    figure.set("class", figure.get("class", "") + " editorial-argument-pause photo")
    target = "17"
    pattern = re.compile(
        rf'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="{target}"[^>]*>.*?</section>',
        re.S,
    )

    def insert(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        heading = section.xpath('./div[contains(@class,"section-heading")]')
        if len(heading) != 1:
            raise ValueError(f"N{number:02d}: unexpected consequence heading")
        heading[0].addnext(figure)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    source, count = pattern.subn(insert, source, count=1)
    if count != 1:
        raise ValueError(f"N{number:02d}: consequence section {target} not found")
    return source, count


def promote_decision_paragraphs(number: int, source: str) -> tuple[str, int]:
    """Turn existing decision pivots into full-width magazine pauses.

    The paragraph itself moves, rather than being quoted a second time. Its
    source ID and exact wording remain in the reading sequence. This gives
    the longest all-text arguments a different visual register without
    inventing a diagram or adding explanatory prose.
    """

    pivots = {
        3: (("06", "N03-s06-b032", "EL INDICADOR", "ink"),),
        6: (
            ("06", "N06-s06-b028", "LA PRUEBA", "paper"),
            ("07", "N06-s07-b026", "LA EXPLICACIÓN", "rule"),
        ),
        8: (("06", "N08-s06-b025", "OBSERVAR Y EXPLICAR", "ink"),),
        10: (("08", "N10-s08-b032", "LA DECISIÓN", "paper"),),
        27: (("07", "N27-s07-b013", "EL CONTRATO", "rule"),),
    }
    if number not in pivots:
        return source, 0
    count = 0
    for section_number, paragraph_id, label, variant in pivots[number]:
        pattern = re.compile(
            rf'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="{section_number}"[^>]*>.*?</section>',
            re.S,
        )

        def promote(match: re.Match[str]) -> str:
            nonlocal count
            section = lxml_html.fromstring(match[0])
            matches = section.xpath(f'.//p[@data-source-id="{paragraph_id}"]')
            if len(matches) != 1:
                raise ValueError(f"N{number:02d}: pivot {paragraph_id} missing or ambiguous")
            paragraph = matches[0]
            body = paragraph.getparent()
            if "section-body" not in body.get("class", "").split():
                raise ValueError(f"N{number:02d}: pivot {paragraph_id} has unexpected parent")
            at = list(body).index(paragraph)
            before = list(body)[:at]
            after = list(body)[at + 1 :]
            if not before or not after:
                raise ValueError(f"N{number:02d}: pivot {paragraph_id} is not mid-argument")
            continuation = lxml_html.Element("div", {"class": body.get("class", "section-body") + " editorial-continuation"})
            for element in after:
                continuation.append(element)
            aside = lxml_html.Element("aside", {"class": f"editorial-decision-pivot {variant}"})
            kicker = lxml_html.Element("span", {"class": "editorial-decision-pivot-label"})
            kicker.text = label
            aside.append(kicker)
            aside.append(paragraph)
            body.addnext(aside)
            aside.addnext(continuation)
            count += 1
            return lxml_html.tostring(section, encoding="unicode", method="html")

        source, matches = pattern.subn(promote, source, count=1)
        if matches != 1:
            raise ValueError(f"N{number:02d}: section {section_number} missing")
    return source, count


def insert_n06_evidence_plate(number: int, source: str) -> tuple[str, int]:
    """Place a source-grounded evidence map at the turn of N06's second movement."""

    if number != 6:
        return source, 0
    pattern = re.compile(
        r'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="06"[^>]*>.*?</section>',
        re.S,
    )

    def insert(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        anchors = section.xpath('.//p[@data-source-id="N06-s06-b013"]')
        if len(anchors) != 1:
            raise ValueError("N06: evidence map anchor missing or ambiguous")
        anchor = anchors[0]
        body = anchor.getparent()
        if "section-body" not in body.get("class", "").split():
            raise ValueError("N06: evidence map anchor has unexpected parent")
        original_children = list(body)
        position = original_children.index(anchor)
        following = original_children[position + 1 :]
        if not following:
            raise ValueError("N06: evidence map has no subsequent argument")
        continuation = lxml_html.Element("div", {"class": body.get("class", "section-body") + " editorial-continuation"})
        for element in following:
            continuation.append(element)
        figure = lxml_html.Element("figure", {"class": "editorial-evidence-plate"})
        image = lxml_html.Element("img", {
            "src": "infographics/N06/cartera-evidencia-inline.svg",
            "alt": "Cuatro fuentes de evidencia llegan a un contraste controlado por independencia y variación de casos; la conclusión declara su alcance.",
        })
        figure.append(image)
        caption = lxml_html.Element("figcaption")
        caption.text = "N06 · La cartera responde dudas prioritarias y no cuenta varias veces una misma fuente."
        figure.append(caption)
        body.addnext(figure)
        figure.addnext(continuation)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    return pattern.subn(insert, source, count=1)


def compose_n06_uncertainty_atlas(number: int, source: str) -> tuple[str, int]:
    """Set the existing six practical doubts as a readable editorial taxonomy.

    The six original paragraphs, their wording, and their source identifiers
    stay in sequence. Only their page-level composition changes.
    """

    if number != 6:
        return source, 0
    pattern = re.compile(
        r'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="05"[^>]*>.*?</section>',
        re.S,
    )

    def compose(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        headings = section.xpath('.//h3[@data-source-id="N06-s05-b016"]')
        paragraphs = [
            section.xpath(f'.//p[@data-source-id="N06-s05-b{index:03d}"]')
            for index in range(17, 24)
        ]
        if len(headings) != 1 or any(len(group) != 1 for group in paragraphs):
            raise ValueError("N06: six-doubt taxonomy is incomplete")
        heading = headings[0]
        lead = paragraphs[0][0]
        entries = [group[0] for group in paragraphs[1:]]
        body = heading.getparent()
        original = list(body)
        positions = [original.index(item) for item in (heading, lead, *entries)]
        if positions != list(range(positions[0], positions[0] + 8)):
            raise ValueError("N06: taxonomy is no longer contiguous")
        atlas = lxml_html.Element("div", {"class": "n06-uncertainty-atlas"})
        body.insert(positions[0], atlas)
        atlas.append(heading)
        atlas.append(lead)
        entries_container = lxml_html.Element("div", {"class": "n06-uncertainty-entries"})
        atlas.append(entries_container)
        for entry in entries:
            entries_container.append(entry)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    return pattern.subn(compose, source, count=1)


def compose_n04_claims(number: int, source: str) -> tuple[str, int]:
    """Compare three Hotel claims without replacing their source prose."""

    if number != 4:
        return source, 0
    pattern = re.compile(
        r'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="05"[^>]*>.*?</section>',
        re.S,
    )

    def compose(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        nodes = []
        for index, tag in [(17, "h3"), (18, "p"), (19, "p"), (20, "p"), (21, "p"), (22, "p")]:
            found = section.xpath(f'.//{tag}[@data-source-id="N04-s05-b{index:03d}"]')
            if len(found) != 1:
                raise ValueError(f"N04: claim component b{index:03d} missing")
            nodes.append(found[0])
        body = nodes[0].getparent()
        original = list(body)
        positions = [original.index(node) for node in nodes]
        if positions != list(range(positions[0], positions[0] + len(nodes))):
            raise ValueError("N04: claims are no longer contiguous")
        following = original[positions[-1] + 1 :]
        continuation = lxml_html.Element("div", {"class": body.get("class", "section-body") + " editorial-continuation"})
        for element in following:
            continuation.append(element)
        feature = lxml_html.Element("div", {"class": "n04-claim-triptych"})
        feature.append(nodes[0])
        feature.append(nodes[1])
        columns = lxml_html.Element("div", {"class": "n04-claim-columns"})
        feature.append(columns)
        for node in nodes[2:5]:
            column = lxml_html.Element("div", {"class": "n04-claim-column"})
            column.append(node)
            columns.append(column)
        feature.append(nodes[5])
        body.addnext(feature)
        feature.addnext(continuation)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    return pattern.subn(compose, source, count=1)


def compose_n30_telemetry(number: int, source: str) -> tuple[str, int]:
    """Turn the existing metric/log/trace explanations into a visual key."""

    if number != 30:
        return source, 0
    pattern = re.compile(
        r'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="07"[^>]*>.*?</section>',
        re.S,
    )

    def compose(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        headings = section.xpath('.//div[contains(@class,"subsection-lead")][.//h3[@data-source-id="N30-s07-b016"]]')
        paragraphs = [section.xpath(f'.//p[@data-source-id="N30-s07-b{index:03d}"]') for index in (18, 19, 20)]
        if len(headings) != 1 or any(len(group) != 1 for group in paragraphs):
            raise ValueError("N30: telemetry comparison is incomplete")
        heading = headings[0]
        entries = [group[0] for group in paragraphs]
        body = heading.getparent()
        original = list(body)
        positions = [original.index(node) for node in (heading, *entries)]
        if positions != list(range(positions[0], positions[0] + 4)):
            raise ValueError("N30: telemetry explanation is no longer contiguous")
        following = original[positions[-1] + 1 :]
        continuation = lxml_html.Element("div", {"class": body.get("class", "section-body") + " editorial-continuation"})
        for element in following:
            continuation.append(element)
        feature = lxml_html.Element("div", {"class": "n30-telemetry-feature"})
        feature.append(heading)
        rows = lxml_html.Element("div", {"class": "n30-telemetry-entries"})
        feature.append(rows)
        for index, entry in enumerate(entries, start=1):
            column = lxml_html.Element("div", {"class": "n30-telemetry-entry", "data-sequence": f"{index:02d}"})
            column.append(entry)
            rows.append(column)
        body.addnext(feature)
        feature.addnext(continuation)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    return pattern.subn(compose, source, count=1)


def compose_n30_alert_pause(number: int, source: str) -> tuple[str, int]:
    """Give the final alert criterion a deliberate ink page, not an orphan leaf.

    The paragraph is moved once, unchanged and with its source identifier.
    """

    if number != 30:
        return source, 0
    pattern = re.compile(
        r'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="09"[^>]*>.*?</section>',
        re.S,
    )

    def compose(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        paragraphs = section.xpath('.//p[@data-source-id="N30-s09-b007"]')
        if len(paragraphs) != 1 or paragraphs[0].getnext() is not None:
            raise ValueError("N30: final alert criterion is not the final paragraph")
        paragraph = paragraphs[0]
        paragraph.getparent().remove(paragraph)
        pause = lxml_html.Element("section", {"class": "full-bleed n30-alert-pause"})
        kicker = lxml_html.Element("span", {"class": "n30-alert-pause-kicker"})
        kicker.text = "METSI · N30 / 09 · ALERTAS"
        pause.append(kicker)
        pause.append(paragraph)
        return (
            lxml_html.tostring(section, encoding="unicode", method="html")
            + lxml_html.tostring(pause, encoding="unicode", method="html")
        )

    return pattern.subn(compose, source, count=1)


def restore_curated_argument_photography(number: int, source: str, package: Path) -> tuple[str, int]:
    """Use existing, unused photographs at individually chosen argument turns.

    These are per-reading placements and captions, not a generated template.
    The photographs remain in their original asset packages.
    """

    choices_by_number = {
        16: (("07", "N16-s07-b002", "assets/editorial-02.png", "Una contradicción del trabajo real obliga a revisar el modelo, no a ocultar la excepción."),),
        18: (("08", "N18-s08-b002", "assets/editorial-02.png", "Las obligaciones se negocian dentro de una operación que ya tiene personas, reglas y tecnología."),),
        32: (
            ("12", "N32-s12-b003", "assets/editorial-04.png", "Desagregar el resultado permite mirar qué casos y personas quedan detrás del promedio."),
            ("17", "N32-s17-b002", "assets/editorial-05.png", "La supervisión sólo existe si una persona puede reconocer, discutir y corregir la salida."),
        ),
    }
    if number not in choices_by_number:
        return source, 0
    restored = 0
    for section_id, anchor_id, image_path, caption in choices_by_number[number]:
        if not (package / image_path).is_file():
            raise FileNotFoundError(package / image_path)
        pattern = re.compile(
            rf'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="{section_id}"[^>]*>.*?</section>',
            re.S,
        )

        def insert(match: re.Match[str]) -> str:
            section = lxml_html.fromstring(match[0])
            anchors = section.xpath(f'.//p[@data-source-id="{anchor_id}"]')
            if len(anchors) != 1:
                raise ValueError(f"N{number:02d}: photographic anchor {anchor_id} missing or ambiguous")
            figure = lxml_html.Element("figure", {"class": "editorial-argument-pause photo curated-short" if number != 32 else "editorial-argument-pause photo"})
            image = lxml_html.Element("img", {"src": image_path, "alt": caption})
            label = lxml_html.Element("figcaption")
            label.text = caption
            figure.append(image)
            figure.append(label)
            # The image belongs *after* the complete section. A full-width
            # figure inside CSS columns left a fragment of the previous page's
            # gray rule at the top of the new sheet in Chromium print output.
            return lxml_html.tostring(section, encoding="unicode", method="html") + lxml_html.tostring(figure, encoding="unicode", method="html")

        source, count = pattern.subn(insert, source, count=1)
        if count != 1:
            raise ValueError(f"N{number:02d}: section {section_id} not found")
        restored += count
    return source, restored


def compose_n17_strategy_pair(number: int, source: str) -> tuple[str, int]:
    """Set N17's two final decisions as one intentional facing-page feature.

    In the current edition they were a short, unheaded continuation before a
    full photographic pause. Moving the two existing subsection groups into a
    paired composition changes neither their sequence nor their source text.
    """

    if number != 17:
        return source, 0
    pattern = re.compile(
        r'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="09"[^>]*>.*?</section>',
        re.S,
    )

    def compose(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        bodies = section.xpath('./div[contains(@class,"section-body") and not(contains(@class,"section-lead"))]')
        if len(bodies) != 1:
            raise ValueError("N17: strategy argument body missing or ambiguous")
        body = bodies[0]
        starts = []
        for prefix in ("Elegir cuántas apuestas", "Cambiar de idea sin borrar"):
            matches = [
                element for element in body
                if "subsection-lead" in element.get("class", "").split()
                and element.text_content().lstrip().startswith(prefix)
            ]
            if len(matches) != 1:
                raise ValueError(f"N17: decision group {prefix!r} missing or ambiguous")
            starts.append(matches[0])
        original_children = list(body)
        start_indices = [original_children.index(element) for element in starts]
        if start_indices[0] >= start_indices[1] or start_indices[1] >= len(body) - 1:
            raise ValueError("N17: final decision pair has unexpected order")
        feature = lxml_html.Element("div", {"class": "n17-strategy-pair"})
        for first, last in ((start_indices[0], start_indices[1]), (start_indices[1], len(original_children))):
            column = lxml_html.Element("div", {"class": "n17-strategy-pair-column"})
            for element in original_children[first:last]:
                column.append(element)
            feature.append(column)
        pivots = body.xpath('./p[@data-source-id="N17-s09-b031"]')
        if len(pivots) != 1:
            raise ValueError("N17: supervision limit pivot missing or ambiguous")
        pivot = pivots[0]
        body.remove(pivot)
        aside = lxml_html.Element("aside", {"class": "n17-supervision-limit"})
        kicker = lxml_html.Element("span", {"class": "n17-supervision-limit-label"})
        kicker.text = "LÍMITE DE AUTOMATIZACIÓN"
        aside.append(kicker)
        aside.append(pivot)
        body.addnext(aside)
        aside.addnext(feature)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    return pattern.subn(compose, source, count=1)


# An individually selected argument in each of the readings that did not
# receive an interior art pass in the previous release.  These are source
# paragraphs, not newly written summaries: the feature moves each paragraph
# once, preserving its identifier, order and exact wording.
EDITORIAL_FIELD_NOTES = {
    2: (7, 2, 6, "Cinco fronteras distintas", "taxonomy"),
    5: (5, 7, 11, "Quién falta en la conversación", "voices"),
    7: (7, 3, 5, "De una frase a una decisión", "sequence"),
    9: (7, 3, 5, "Medir sin esconder a las personas", "measure"),
    11: (6, 9, 13, "Cinco niveles de afirmación", "claims"),
    12: (6, 3, 5, "Qué prueba un evento", "sequence"),
    13: (8, 3, 5, "Antes de corregir: comparar", "sequence"),
    14: (8, 3, 6, "Un traspaso tiene que poder usarse", "handoff"),
    15: (8, 3, 3, "La estructura no explica por sí sola", "architecture"),
    19: (9, 3, 5, "Más allá del precio de entrada", "ledger"),
    20: (7, 3, 3, "La estrategia como hipótesis", "theory"),
    21: (7, 3, 6, "Un proyecto termina; el servicio sigue", "horizons"),
    22: (7, 3, 6, "Del deseo a una prueba", "hypothesis"),
    24: (14, 2, 13, "Doce preguntas antes de decidir", "register"),
    25: (11, 1, 5, "46 días: separar trabajo y espera", "time"),
    26: (18, 2, 13, "Doce preguntas para mirar la red", "register"),
    28: (9, 4, 6, "Tres dimensiones de la experiencia", "taxonomy"),
    29: (7, 4, 7, "Integrar para detectar pronto", "pipeline"),
    31: (6, 6, 7, "Una regla no es un asistente", "contrast"),
    33: (18, 1, 3, "Gobernar es poder revisar", "governance"),
    34: (7, 3, 6, "Una afirmación debe poder rastrearse", "argument"),
    35: (9, 3, 6, "Nombrar la incertidumbre", "uncertainty"),
    36: (10, 3, 4, "Practicar, recibir devolución, revisar", "practice"),
}


def compose_editorial_field_note(number: int, source: str) -> tuple[str, int]:
    """Make one source-grounded visual argument in every previously untouched N.

    The treatment follows the content: ordered reasoning becomes a sequence,
    lists of distinctions become an atlas, and decision questions a register.
    No new academic claim is inserted into the reading.
    """

    if number not in EDITORIAL_FIELD_NOTES:
        return source, 0
    section_number, first, last, title, family = EDITORIAL_FIELD_NOTES[number]
    pattern = re.compile(
        rf'<section class="[^"]*\breading-section\b[^"]*"[^>]*data-section="{section_number:02d}"[^>]*>.*?</section>',
        re.S,
    )

    def compose(match: re.Match[str]) -> str:
        section = lxml_html.fromstring(match[0])
        ids = [f"N{number:02d}-s{section_number:02d}-b{index:03d}" for index in range(first, last + 1)]
        blocks = []
        for identifier in ids:
            matches = section.xpath(f'.//p[@data-source-id="{identifier}"]')
            if len(matches) != 1:
                raise ValueError(f"N{number:02d}: field note block {identifier} missing")
            blocks.append(matches[0])
        body = blocks[0].getparent()
        if any(block.getparent() is not body for block in blocks):
            raise ValueError(f"N{number:02d}: field note spans different editorial bodies")
        positions = [list(body).index(block) for block in blocks]
        if positions != list(range(positions[0], positions[0] + len(blocks))):
            raise ValueError(f"N{number:02d}: field note is not a contiguous argument")
        before, after = list(body)[:positions[0]], list(body)[positions[-1] + 1:]
        if not before and not after:
            raise ValueError(f"N{number:02d}: no surrounding argument")
        def plate(part: list, heading_text: str, continuation: bool = False):
            variant = " register-part-two" if continuation else ""
            feature = lxml_html.Element("div", {"class": f"editorial-field-note field-{family}{variant}"})
            label = lxml_html.Element("span", {"class": "field-note-kicker"})
            label.text = f"METSI · N{number:02d} / LECTURA VISUAL" + (" · CONTINÚA" if continuation else "")
            heading = lxml_html.Element("h3")
            heading.text = heading_text
            feature.extend((label, heading))
            grid = lxml_html.Element("div", {"class": "field-note-grid"})
            feature.append(grid)
            for block in part:
                grid.append(block)
            return feature

        if family == "register":
            features = [plate(blocks[:6], title), plate(blocks[6:], "Preguntas 07–12", True)]
        else:
            features = [plate(blocks, title)]
        continuation = lxml_html.Element("div", {"class": body.get("class", "section-body") + " editorial-continuation"})
        for element in after:
            continuation.append(element)
        anchor = body
        for feature in features:
            anchor.addnext(feature)
            anchor = feature
        if after:
            anchor.addnext(continuation)
        return lxml_html.tostring(section, encoding="unicode", method="html")

    return pattern.subn(compose, source, count=1)


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
    source, restored_approved_photos = restore_approved_photography(number, source, package)
    source, restored_interludes = restore_editorial_interludes(number, source, package)
    source, promoted_decision_pivots = promote_decision_paragraphs(number, source)
    source, n06_evidence_plate = insert_n06_evidence_plate(number, source)
    source, n06_uncertainty_atlas = compose_n06_uncertainty_atlas(number, source)
    source, n04_claim_triptych = compose_n04_claims(number, source)
    source, n30_telemetry_feature = compose_n30_telemetry(number, source)
    source, n30_alert_pause = compose_n30_alert_pause(number, source)
    source, curated_argument_photography = restore_curated_argument_photography(number, source, package)
    source, n17_strategy_pair = compose_n17_strategy_pair(number, source)
    source, editorial_field_note = compose_editorial_field_note(number, source)
    if number in EDITORIAL_FIELD_NOTES and editorial_field_note != 1:
        raise ValueError(f"N{number:02d}: curated editorial field note was not composed")
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
    if number == 6:
        infographic_link = target / "infographics"
        infographic_source = ROOT / "pedagogy/editorial-recovery-20260929/infographics"
        if not infographic_link.exists() and not infographic_link.is_symlink():
            infographic_link.symlink_to(infographic_source)
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
        "restored_approved_photos": restored_approved_photos,
        "restored_interludes": restored_interludes,
        "promoted_decision_pivots": promoted_decision_pivots,
        "n06_evidence_plate": n06_evidence_plate,
        "n06_uncertainty_atlas": n06_uncertainty_atlas,
        "n04_claim_triptych": n04_claim_triptych,
        "n30_telemetry_feature": n30_telemetry_feature,
        "n30_alert_pause": n30_alert_pause,
        "curated_argument_photography": curated_argument_photography,
        "n17_strategy_pair": n17_strategy_pair,
        "editorial_field_note": editorial_field_note,
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
