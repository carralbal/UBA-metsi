#!/usr/bin/env python3
"""Resolve and package Wikimedia portraits used by METSI Block C.

The script queries the public MediaWiki API for a declared article title,
downloads the lead image thumbnail, and preserves article/image provenance in
a package-local registry. It never changes canonical source text.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import urllib.error
import time
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "portraits-block-c"

PEOPLE = {
    "richard-wang": ("Richard Y. Wang", "Richard_Y._Wang"),
    "luc-moreau": ("Luc Moreau", "Luc_Moreau_(computer_scientist)"),
    "robert-groves": ("Robert Groves", "Robert_Groves"),
    "helen-nissenbaum": ("Helen Nissenbaum", "Helen_Nissenbaum"),
    "elham-tabassi": ("Elham Tabassi", "Elham_Tabassi"),
    "cathy-oneil": ("Cathy O’Neil", "Cathy_O'Neil"),
    "eric-evans": ("Eric Evans", "Eric_Evans_(technologist)"),
    "leslie-lamport": ("Leslie Lamport", "Leslie_Lamport"),
    "martin-fowler": ("Martin Fowler", "Martin_Fowler_(software_engineer)"),
    "david-ferraiolo": ("David Ferraiolo", "David_Ferraiolo"),
    "nancy-leveson": ("Nancy Leveson", "Nancy_Leveson"),
    "jim-gray": ("Jim Gray", "Jim_Gray_(computer_scientist)"),
    "pat-helland": ("Pat Helland", "Pat_Helland"),
    "werner-vogels": ("Werner Vogels", "Werner_Vogels"),
    "martin-kleppmann": ("Martin Kleppmann", "Martin_Kleppmann"),
    "peter-bailis": ("Peter Bailis", "Peter_Bailis"),
    "michael-hammer": ("Michael Hammer", "Michael_Hammer"),
    "thomas-davenport": ("Thomas H. Davenport", "Thomas_H._Davenport"),
    "geary-rummler": ("Geary Rummler", "Geary_Rummler"),
    "wil-van-der-aalst": ("Wil van der Aalst", "Wil_van_der_Aalst"),
    "john-little": ("John D. C. Little", "John_Little_(academic)"),
    "wallace-hopp": ("Wallace Hopp", "Wallace_Hopp"),
    "george-box": ("George Box", "George_E._P._Box"),
    "peter-checkland": ("Peter Checkland", "Peter_Checkland"),
    "john-sterman": ("John Sterman", "John_Sterman"),
    "daniel-moody": ("Daniel Moody", "Daniel_Moody_(information_systems_researcher)"),
    "simon-brown": ("Simon Brown", "Simon_Brown_(software_architect)"),
    "marc-lankhorst": ("Marc Lankhorst", "Marc_Lankhorst"),
    "chris-argyris": ("Chris Argyris", "Chris_Argyris"),
    "michael-jackson": ("Michael A. Jackson", "Michael_A._Jackson"),
    "barry-boehm": ("Barry Boehm", "Barry_Boehm"),
    "winston-royce": ("Winston W. Royce", "Winston_W._Royce"),
}


def api(params: dict[str, str]) -> dict:
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "METSI-courseware/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry: dict[str, dict] = {}
    for key, (name, title) in PEOPLE.items():
        existing = next((path for path in (
            ROOT / "assets" / "portraits" / f"{key}.jpg",
            ROOT / "assets" / "portraits" / f"{key}.png",
        ) if path.is_file()), None)
        if existing is not None:
            target = OUT / existing.name
            shutil.copy2(existing, target)
            registry[key] = {
                "key": key,
                "name": name,
                "article_title": title.replace("_", " "),
                "article_url": "",
                "image_name": existing.name,
                "download_url": "",
                "source": "Audited METSI portrait registry",
                "rights_status": "inherited_from_portrait_registry",
                "local_file": str(target.relative_to(ROOT)),
                "bytes": target.stat().st_size,
            }
            print(key, "REUSED", existing)
            continue
        time.sleep(1.25)
        result = api({
            "action": "query",
            "format": "json",
            "redirects": "1",
            "prop": "pageimages|info",
            "inprop": "url",
            "piprop": "thumbnail|name|original",
            "pithumbsize": "1200",
            "titles": title,
        })
        page = next(iter(result["query"]["pages"].values()))
        source = (page.get("original") or page.get("thumbnail") or {}).get("source", "")
        record = {
            "key": key,
            "name": name,
            "article_title": page.get("title", title),
            "article_url": page.get("fullurl", ""),
            "image_name": page.get("pageimage", ""),
            "download_url": source,
            "source": "Wikimedia / Wikipedia lead image",
            "rights_status": "requires_commons_metadata_review",
        }
        if source:
            suffix = Path(urllib.parse.urlsplit(source).path).suffix.lower()
            if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
                suffix = ".jpg"
            target = OUT / f"{key}{suffix}"
            request = urllib.request.Request(source, headers={"User-Agent": "METSI-courseware/1.0"})
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(request, timeout=60) as response:
                        target.write_bytes(response.read())
                    break
                except urllib.error.HTTPError as exc:
                    if exc.code != 429 or attempt == 3:
                        raise
                    time.sleep(4 * (attempt + 1))
            record["local_file"] = str(target.relative_to(ROOT))
            record["bytes"] = target.stat().st_size
        registry[key] = record
        print(key, "OK" if source else "NO_IMAGE", record["article_url"])
    (OUT / "registry.json").write_text(
        json.dumps({"entries": registry}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
