#!/usr/bin/env python3
"""Deterministic validation for the METSI narrative course site."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

PDF_FILES = {
    "N00": "N00-METSI-lectura-previa-v2-final.pdf",
    "N01": "N01-METSI-lectura-previa-v18-final.pdf",
    "N02": "N02-METSI-lectura-previa-v14-final.pdf",
    "N03": "N03-METSI-lectura-previa-v9-final.pdf",
    "N04": "N04-METSI-lectura-previa-v9-final.pdf",
    "N05": "N05-METSI-lectura-previa-v9-final.pdf",
    "N06": "N06-METSI-lectura-previa-v9-final.pdf",
    "N07": "N07-METSI-lectura-previa-v9-final.pdf",
    "N08": "N08-METSI-lectura-previa-v9-final.pdf",
    "N09": "N09-METSI-lectura-previa-v9-final.pdf",
    "N10": "N10-METSI-lectura-previa-v9-final.pdf",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.images: list[dict[str, str]] = []
        self.ids: list[str] = []
        self.controls: list[str] = []
        self.download_links: list[str] = []
        self.meta: dict[tuple[str, str], str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        if values.get("aria-controls"):
            self.controls.append(values["aria-controls"])
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
            if "download" in values:
                self.download_links.append(values["href"])
        if tag == "img":
            self.images.append(values)
        if tag == "meta":
            key = values.get("property") or values.get("name")
            if key:
                self.meta[("meta", key)] = values.get("content", "")


def local_target(link: str) -> Path | None:
    parsed = urlparse(link)
    if parsed.scheme or parsed.netloc or link.startswith("#") or link.startswith("mailto:"):
        return None
    return ROOT / parsed.path


def main() -> int:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "metsi.css").read_text(encoding="utf-8")
    script = (ROOT / "metsi.js").read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)

    approval = json.loads((REPO / "BLOCK-01-cover-review-current/approval.json").read_text(encoding="utf-8"))
    cover_audit = json.loads((REPO / "BLOCK-01-cover-review-current/audit.json").read_text(encoding="utf-8"))
    expected_cover_hashes = {item["code"]: item["metrics"]["sha256"] for item in cover_audit["documents"]}

    local_links = [target for link in parser.links if (target := local_target(link))]
    actual_pdf_hashes = {code: sha256(ROOT / "pdf" / file) for code, file in PDF_FILES.items()}
    page_counts = {code: len(PdfReader(str(ROOT / "pdf" / file)).pages) for code, file in PDF_FILES.items()}
    actual_cover_hashes = {code: sha256(ROOT / "covers" / f"{code}.png") for code in PDF_FILES}
    pdf_downloads = {Path(urlparse(link).path).name for link in parser.download_links if link.startswith("pdf/")}
    mapped_codes = {f"N{number:02d}" for number in range(1, 37)}
    visible_codes = set(re.findall(r"\bN(?:0[1-9]|[12][0-9]|3[0-6])\b", html))

    checks = {
        "semantic_language_and_landmarks": '<html lang="es-AR">' in html and "<main" in html and "<nav" in html and "<footer" in html,
        "all_local_links_resolve": all(path.is_file() for path in local_links),
        "unique_ids": len(parser.ids) == len(set(parser.ids)),
        "aria_controls_resolve": set(parser.controls).issubset(set(parser.ids)),
        "all_images_have_alt": bool(parser.images) and all("alt" in image and image["alt"].strip() for image in parser.images),
        "eleven_exact_pdf_downloads": pdf_downloads == set(PDF_FILES.values()) and len(list((ROOT / "pdf").glob("*.pdf"))) == 11,
        "pdfs_match_closed_approvals": actual_pdf_hashes == approval["pdf_sha256"],
        "pdf_page_counts_expected": page_counts == {"N00":43,"N01":29,"N02":29,"N03":30,"N04":32,"N05":28,"N06":28,"N07":31,"N08":28,"N09":28,"N10":31},
        "covers_match_closed_review_assets": actual_cover_hashes == expected_cover_hashes,
        "all_36_nuclei_present": visible_codes.issuperset(mapped_codes),
        "future_nuclei_not_fake_downloads": not any(re.search(r"N(?:1[1-9]|2[0-9]|3[0-6])", link) for link in parser.links),
        "eight_curricular_blocks": html.count('class="block"') == 8,
        "audience_tabs_complete": html.count('role="tab"') == 4 and html.count('role="tabpanel"') == 4,
        "responsive_and_reduced_motion_css": "@media(max-width:650px)" in css and "prefers-reduced-motion" in css,
        "keyboard_tabs_implemented": "ArrowLeft" in script and "ArrowRight" in script and "tabIndex" in script,
        "social_metadata_complete": all(parser.meta.get(("meta", key), "") for key in ("og:title", "og:description", "og:image", "twitter:card", "twitter:image")),
        "no_placeholders": not re.search(r"\b(?:TBD|TODO|Lorem|XXX)\b", html, flags=re.I),
    }

    report = {
        "scope": "METSI narrative course site",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "facts": {
            "pdf_downloads": len(pdf_downloads),
            "pdf_pages": page_counts,
            "cover_images": len(actual_cover_hashes),
            "curricular_nuclei_visible": len(mapped_codes & visible_codes),
            "curricular_blocks": html.count('class="block"'),
            "local_links_checked": len(local_links),
        },
    }
    (ROOT / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
