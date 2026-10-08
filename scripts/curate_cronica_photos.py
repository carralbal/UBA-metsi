#!/usr/bin/env python3
"""Discover and proof *new* licensed editorial photos for METSI crónicas.

All output from discover mode is provisional. A human selects one distinct image
per chronicle after reviewing the contact sheets. The final asset is then used
both inside its PDF and in its website card.
"""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "pedagogy/cronicas-20261008"
SCRATCH = Path("/private/tmp/metsi-cronicas-photos-20261008")
LICENCE = "https://unsplash.com/license"

# Editorial ideas, not literal depictions of the named people or events.
QUERIES = {
    "N00": ("empty public waiting room chairs", "hospital reception waiting chairs"),
    "N01": ("greenhouse irrigation water lines", "greenhouse plants sunlight irrigation"),
    "N02": ("post office envelopes mail sorting", "letters postal counter"),
    "N03": ("bus ticket validator interior", "bus passenger city transit"),
    "N04": ("archive files documents evidence", "public records documents desk"),
    "N05": ("public service counter window", "office help desk empty"),
    "N06": ("laboratory scientist microscope", "virology laboratory research"),
    "N07": ("interview conversation notebook", "person listening interview"),
    "N08": ("dairy farm milking cows", "dairy barn robotic milking"),
    "N09": ("pharmacy counter medication", "older person healthcare consultation"),
    "N10": ("broken sidewalk city street", "cracked pavement urban pedestrian"),
    "N11": ("statistical chart newspaper desk", "paper charts statistics economy"),
    "N12": ("medical prescription pharmacy", "medicine pharmacy hand"),
    "N13": ("payment card receipt detail", "two paths crossing lines abstract"),
    "N14": ("appointment calendar waiting room", "people waiting government office"),
    "N15": ("grain silo wheat field", "grain storage agricultural silos"),
    "N16": ("hospital records desk", "two hospital corridors connection"),
    "N17": ("ticket queue number service", "paper ticket appointment desk"),
    "N18": ("landline telephone elderly home", "old telephone cord emergency"),
    "N19": ("bank documents desk", "open banking phone paper"),
    "N20": ("call center operator city", "urban service phone desk"),
    "N21": ("telephone headset healthcare worker", "empty call center office"),
    "N22": ("laboratory virus test equipment", "scientist laboratory sample"),
    "N23": ("empty classroom teacher desk", "teacher classroom preparation"),
    "N24": ("water reservoir drought", "water dam low level"),
    "N25": ("empty hospital bed corridor", "hospital discharge wheelchair"),
    "N26": ("border crossing passport document", "border checkpoint architecture"),
    "N27": ("medical records paper chart", "healthcare team information exchange"),
    "N28": ("hospital entrance patient walking", "clinic corridor person"),
    "N29": ("train turnstile transport card", "subway passenger ticket"),
    "N30": ("server room empty dark", "network operations center monitor"),
    "N31": ("government paperwork computer", "public administration form desk"),
    "N32": ("testing notes evaluation desk", "researcher reviewing documents"),
    "N33": ("monitoring control room", "abstract data monitoring screen"),
    "N34": ("rural clinic India healthcare", "community healthcare clinic"),
    "N35": ("identity card document hands", "older person paperwork service"),
    "N36": ("teacher classroom students Latin America", "school classroom teaching Uruguay"),
}


def fetch(url: str) -> bytes:
    return subprocess.check_output([
        "curl", "-fsSL", "--retry", "3", "--retry-delay", "2", "--max-time", "30", url,
    ], stderr=subprocess.DEVNULL)


def search(number: str, query: str) -> tuple[str, list[dict]]:
    params = urllib.parse.urlencode({"query": query, "per_page": 24, "orientation": "landscape"})
    data = json.loads(fetch(f"https://unsplash.com/napi/search/photos?{params}"))
    out = []
    for photo in data.get("results", []):
        if photo.get("premium") or photo.get("plus") or photo.get("asset_type") != "photo":
            continue
        if photo.get("width", 0) < 1600 or photo.get("height", 0) < 1000:
            continue
        out.append({
            "section_id": number,
            "concept": query,
            "provider": "Unsplash",
            "provider_asset_id": photo["id"],
            "source_page": photo["links"]["html"],
            "creator": photo["user"]["name"],
            "license_name": "Unsplash License",
            "license_url": LICENCE,
            "width": photo["width"],
            "height": photo["height"],
            "alt": photo.get("alt_description") or photo.get("description") or query,
            "thumbnail_url": photo["urls"]["small"],
            "download_url": photo["urls"]["raw"],
            "search_query": query,
            "saturation_review": "pending visual review",
            "treatment": "grayscale native derivative for this all-B&W series",
            "approved": False,
        })
    return number, out


def thumbnail(candidate: dict) -> Path:
    path = SCRATCH / "thumbs" / f"{candidate['section_id']}-{candidate['provider_asset_id']}.jpg"
    if not path.exists():
        image = Image.open(io.BytesIO(fetch(candidate["thumbnail_url"]))).convert("RGB")
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, "JPEG", quality=85)
    return path


def contact_sheets(candidates: list[dict]) -> None:
    by_number = {number: [c for c in candidates if c["section_id"] == number] for number in QUERIES}
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    try:
        font = ImageFont.truetype(font_path, 16)
    except OSError:
        font = ImageFont.load_default()
    for start in range(0, 37, 6):
        numbers = [f"N{i:02d}" for i in range(start, min(start + 6, 37))]
        sheet = Image.new("RGB", (1360, 6 * 207), "#F4F3EF")
        draw = ImageDraw.Draw(sheet)
        for row, number in enumerate(numbers):
            y = row * 207
            draw.text((12, y + 3), number + "  " + QUERIES[number][0], fill="#171716", font=font)
            for col, item in enumerate(by_number[number][:4]):
                x = 12 + col * 337
                try:
                    with Image.open(thumbnail(item)) as im:
                        photo = ImageOps.fit(im.convert("RGB"), (326, 160), Image.Resampling.LANCZOS)
                    sheet.paste(photo, (x, y + 27))
                    draw.text((x + 4, y + 187), item["provider_asset_id"] + "  " + item["creator"][:24], fill="#171716", font=font)
                except Exception as exc:  # Retain proof of a broken candidate.
                    draw.text((x + 4, y + 70), f"UNAVAILABLE: {exc}", fill="#171716", font=font)
        sheet.save(SCRATCH / f"contact-{start//6+1:02d}.jpg", "JPEG", quality=87)


def discover() -> None:
    jobs = [(number, query) for number, queries in QUERIES.items() for query in queries]
    result = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(search, number, query): (number, query) for number, query in jobs}
        for future in as_completed(futures):
            number, query = futures[future]
            try:
                _, items = future.result()
                result[(number, query)] = items
            except Exception as exc:
                print(f"SEARCH FAILED {number} {query}: {exc}", file=sys.stderr)
                result[(number, query)] = []
    selected = []
    for number, queries in QUERIES.items():
        seen = set()
        for query in queries:
            for item in result[(number, query)]:
                if item["provider_asset_id"] in seen:
                    continue
                seen.add(item["provider_asset_id"])
                selected.append(item)
                if sum(c["section_id"] == number for c in selected) >= 6:
                    break
            if sum(c["section_id"] == number for c in selected) >= 6:
                break
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = DATA_DIR / "image-candidates.json"
    output.write_text(json.dumps({"candidates": selected}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    contact_sheets(selected)
    print(f"Discovered {len(selected)} free-photo candidates across {len(QUERIES)} stories; proofs in {SCRATCH}")


def install() -> None:
    selection = json.loads((DATA_DIR / "image-selection.json").read_text(encoding="utf-8"))
    candidates = json.loads((DATA_DIR / "image-candidates.json").read_text(encoding="utf-8"))["candidates"]
    by_id = {(candidate["section_id"], candidate["provider_asset_id"]): candidate
             for candidate in candidates}
    dest = ROOT / "site/covers/cronicas/images/story"
    dest.mkdir(parents=True, exist_ok=True)
    manifest = []
    used_ids = set()
    used_hashes = set()
    for number in QUERIES:
        identifier = selection[number]
        if identifier in used_ids:
            raise ValueError(f"Repeated photo: {identifier}")
        used_ids.add(identifier)
        if (number, identifier) in by_id:
            candidate = by_id[(number, identifier)]
        else:
            # A few precise editorial searches were added after contact-sheet
            # review (notably the hospital bed and public-service desk).
            photo = json.loads(fetch(f"https://unsplash.com/napi/photos/{identifier}"))
            if photo.get("premium") or photo.get("plus"):
                raise ValueError(f"Selected photo is not under the free license: {identifier}")
            candidate = {
                "section_id": number,
                "concept": "supplemental editorial search",
                "provider": "Unsplash",
                "provider_asset_id": identifier,
                "source_page": photo["links"]["html"],
                "creator": photo["user"]["name"],
                "license_name": "Unsplash License",
                "license_url": LICENCE,
                "width": photo["width"],
                "height": photo["height"],
                "alt": photo.get("alt_description") or photo.get("description") or number,
                "thumbnail_url": photo["urls"]["small"],
                "download_url": photo["urls"]["raw"],
                "search_query": "supplemental search",
            }
        source_html = fetch(candidate["source_page"]).decode("utf-8", "ignore")
        if "Free to use under the Unsplash License" not in source_html and "Unsplash License" not in source_html:
            raise ValueError(f"License status not visible on {candidate['source_page']}")
        url = candidate["download_url"].split("?")[0] + "?w=2200&q=88&fit=max"
        raw = fetch(url)
        digest = hashlib.sha256(raw).hexdigest()
        if digest in used_hashes:
            raise ValueError(f"Repeated image hash: {number} {identifier}")
        used_hashes.add(digest)
        with Image.open(io.BytesIO(raw)) as original:
            if min(original.size) < 1000:
                raise ValueError(f"Insufficient resolution: {number} {original.size}")
            # The approved Crónicas series is strictly black and white.
            mono = ImageOps.grayscale(original)
            mono = ImageOps.autocontrast(mono, cutoff=0.4, preserve_tone=False)
            final = mono.convert("RGB")
            final_path = dest / f"{number}.jpg"
            final.save(final_path, "JPEG", quality=89, optimize=True)
            width, height = final.size
        candidate = dict(candidate)
        candidate.update({
            "section_id": number,
            "local_file": str(final_path.relative_to(ROOT)),
            "sha256_original": digest,
            "sha256_final": hashlib.sha256(final_path.read_bytes()).hexdigest(),
            "width": width,
            "height": height,
            "crop": "centered 3.6:1 PDF panorama; centered 1.6:1 website card",
            "alt": candidate["alt"],
            "saturation_review": "neutral",
            "treatment": "grayscale + restrained autocontrast baked into shared article/card asset",
            "approved": True,
            "selected_at": str(date.today()),
        })
        manifest.append(candidate)
        print(f"INSTALLED {number} {identifier} {width}x{height} {candidate['creator']}")
    (DATA_DIR / "image-manifest.json").write_text(
        json.dumps({"images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    if sys.argv[1:] == ["--discover"]:
        discover()
    elif sys.argv[1:] == ["--install"]:
        install()
    else:
        raise SystemExit("usage: curate_cronica_photos.py --discover|--install")
