#!/usr/bin/env python3
"""Verify every METSI crónica PDF, source photo, card crop, and link."""

from __future__ import annotations

import importlib.util
import io
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "site/covers/cronicas"
DATA = ROOT / "pedagogy/cronicas-20261008"
PROOF = Path("/private/tmp/metsi-cronicas-final-qa")
PYTHON = Path(__import__("sys").executable)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized(value: str) -> str:
    return re.sub(r"\s+", "", value).replace("–", "-").replace("’", "'")


def main() -> None:
    articles = load_module(DATA / "articles.py", "articles").ARTICLES
    narratives = load_module(DATA / "narratives.py", "narratives")
    images = json.loads((DATA / "image-manifest.json").read_text(encoding="utf-8"))["images"]
    assert len(articles) == len(narratives.STORIES) == len(images) == 37
    assert len({item["provider_asset_id"] for item in images}) == 37
    assert len({item["sha256_original"] for item in images}) == 37
    assert sum(a["region"] in {"Argentina", "América Latina"} for a in articles) >= 26
    by_id = {item["section_id"]: item for item in images}
    index = (SERIES / "index.html").read_text(encoding="utf-8")
    homepage = (ROOT / "site/index.html").read_text(encoding="utf-8")
    home_cards = homepage.split("<!-- BEGIN home chronicles cards -->", 1)[1].split(
        "<!-- END home chronicles cards -->", 1)[0]
    failures = []
    report = []
    if homepage.count('id="cronicas"') != 1 or homepage.count('id="lecturas"') != 1:
        failures.append("Homepage is missing distinct chronicles/readings anchors")
    if homepage.index('id="cronicas"') > homepage.index('id="lecturas"'):
        failures.append("Chronicles do not precede N readings on homepage")
    if home_cards.count('<article class="card') != 37:
        failures.append("Homepage does not expose exactly 37 chronicle cards")
    if 'chronicles-entry' in homepage:
        failures.append("Old off-page chronicles entry remains on homepage")
    for article in articles:
        number = article["id"]
        pdf = SERIES / "pdf" / f"{number}.pdf"
        image_path = SERIES / "images/story" / f"{number}.jpg"
        card_path = SERIES / "images/cards" / f"{number}.webp"
        reader = PdfReader(str(pdf))
        if len(reader.pages) != 2:
            failures.append(f"{number}: expected two pages")
        if any(abs(float(p.mediabox.width) - 595.276) > 1 or
               abs(float(p.mediabox.height) - 841.89) > 1 for p in reader.pages):
            failures.append(f"{number}: not A4")
        full_text = normalized(" ".join(page.extract_text() or "" for page in reader.pages))
        paragraphs = narratives.paragraphs(number)
        for i, item in enumerate(paragraphs):
            if normalized(item) not in full_text:
                failures.append(f"{number}: paragraph {i+1} missing or clipped")
        if normalized(article["title"]) not in full_text:
            failures.append(f"{number}: title missing")
        if "HotelHorizonte" in full_text:
            failures.append(f"{number}: forbidden case reference")
        embedded = reader.pages[0].images
        if len(embedded) != 1:
            failures.append(f"{number}: expected one embedded editorial photo, got {len(embedded)}")
        else:
            with Image.open(io.BytesIO(embedded[0].data)) as im, Image.open(image_path) as source:
                if im.size != source.size:
                    failures.append(f"{number}: PDF photo dimensions differ from source")
                elif max(ImageStat.Stat(ImageChops.difference(
                        im.convert("RGB"), source.convert("RGB"))).mean) > 1:
                    failures.append(f"{number}: PDF photo differs from selected story image")
        with Image.open(image_path) as source, Image.open(card_path) as card:
            expected = ImageOps.fit(source.convert("L"), (840, 525),
                                    method=Image.Resampling.LANCZOS,
                                    centering=(.5, .47)).convert("RGB")
            delta = max(ImageStat.Stat(ImageChops.difference(expected, card.convert("RGB"))).mean)
            if delta > 4:
                failures.append(f"{number}: website card is not the same photograph ({delta:.2f})")
            if max(ImageStat.Stat(source.convert("RGB")).mean) - min(
                    ImageStat.Stat(source.convert("RGB")).mean) > .1:
                failures.append(f"{number}: story photo is not neutral B&W")
        if f"images/cards/{number}.webp" not in index or f"pdf/{number}.pdf" not in index:
            failures.append(f"{number}: index link missing")
        if (f"covers/cronicas/images/cards/{number}.webp" not in home_cards or
                f"covers/cronicas/pdf/{number}.pdf" not in home_cards):
            failures.append(f"{number}: homepage card image or PDF link missing")
        if by_id[number]["license_url"] != "https://unsplash.com/license":
            failures.append(f"{number}: missing photo license provenance")
        annotations = [a.get_object().get("/A", {}).get("/URI", "") for page in reader.pages
                       for a in (page.get("/Annots") or [])]
        if (article["source_url"] not in annotations or
                not any("carralbal.github.io/UBA-metsi" in url for url in annotations)):
            failures.append(f"{number}: source/reading link missing in PDF")
        report.append({"id": number, "pages": len(reader.pages),
                       "words": len(narratives.STORIES[number].split()),
                       "photo": by_id[number]["provider_asset_id"],
                       "photo_creator": by_id[number]["creator"]})

    PROOF.mkdir(parents=True, exist_ok=True)
    for start in range(0, 37, 6):
        numbers = [f"N{i:02d}" for i in range(start, min(start+6, 37))]
        sheet = Image.new("RGB", (1080, 6 * 690), "#E8E7E1")
        draw = ImageDraw.Draw(sheet)
        for row, number in enumerate(numbers):
            pdf = SERIES / "pdf" / f"{number}.pdf"
            prefix = PROOF / f"{number}"
            subprocess.run(["pdftoppm", "-f", "1", "-l", "2", "-scale-to", "630",
                            "-jpeg", "-jpegopt", "quality=80", str(pdf), str(prefix)],
                           check=True, stdout=subprocess.DEVNULL)
            for page in (1, 2):
                with Image.open(PROOF / f"{number}-{page}.jpg") as original:
                    render = ImageOps.contain(original.convert("RGB"), (515, 635))
                    x = (page-1)*540 + (540-render.width)//2
                    sheet.paste(render, (x, row*690+28))
                draw.text(((page-1)*540+20, row*690+8), f"{number} / {page}", fill="#171716")
        sheet.save(PROOF / f"contact-{start//6+1:02d}.jpg", "JPEG", quality=86)
    result = {"count": len(report), "failures": failures, "articles": report}
    (PROOF / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Verified {len(report)} articles, 74 pages, 37 embedded/card photo pairs; "
          f"{len(failures)} failures. Proofs: {PROOF}")
    for failure in failures:
        print("FAIL", failure)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
