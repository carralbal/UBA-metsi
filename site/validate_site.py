#!/usr/bin/env python3
"""Deterministic validation for the METSI narrative course site.

N00-N10 are locked by the integrated Block 01 audit. N11-N36 are checked
against the content-addressed publication contract written by
``sync_site_n11_n36.py``. With ``--check-only`` this program is read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
FIRST_DYNAMIC = 11
LAST_DYNAMIC = 36
DYNAMIC_SOURCE_VERSION = "v9-editorial"
DYNAMIC_SOURCE_VERSION_SHORT = "v9"
DYNAMIC_QA_ROOT = "qa-reports/n11-n36-v9"
DYNAMIC_QA_VALIDATOR = "validate_n11_n36_v6.py"

PDF_FILES = {
    "N00": "N00-METSI-lectura-previa-v3-final.pdf",
    "N01": "N01-METSI-lectura-previa-v18-final.pdf",
    "N02": "N02-METSI-lectura-previa-v15-final.pdf",
    "N03": "N03-METSI-lectura-previa-v10-final.pdf",
    "N04": "N04-METSI-lectura-previa-v9-final.pdf",
    "N05": "N05-METSI-lectura-previa-v10-final.pdf",
    "N06": "N06-METSI-lectura-previa-v10-final.pdf",
    "N07": "N07-METSI-lectura-previa-v10-final.pdf",
    "N08": "N08-METSI-lectura-previa-v10-final.pdf",
    "N09": "N09-METSI-lectura-previa-v10-final.pdf",
    "N10": "N10-METSI-lectura-previa-v9-final.pdf",
    **{
        f"N{number:02d}": f"publicados/N{number:02d}-METSI-lectura-previa-v1-final.pdf"
        for number in range(FIRST_DYNAMIC, LAST_DYNAMIC + 1)
    },
}

COVER_FILES = {
    **{f"N{number:02d}": f"N{number:02d}.png" for number in range(0, 11)},
    **{f"N{number:02d}": f"N{number:02d}.jpg" for number in range(FIRST_DYNAMIC, LAST_DYNAMIC + 1)},
}

LOCKED_PAGES = {
    "N00": 44,
    "N01": 29,
    "N02": 30,
    "N03": 30,
    "N04": 32,
    "N05": 28,
    "N06": 28,
    "N07": 31,
    "N08": 29,
    "N09": 30,
    "N10": 31,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def publication_digest(records: list[dict[str, Any]]) -> str:
    fields = (
        "code",
        "title",
        "canonical_source",
        "canonical_sha256",
        "package_source",
        "package_source_sha256",
        "package_sha256",
        "package_files",
        "source_pdf",
        "public_pdf",
        "cover",
        "pages",
        "bytes",
        "sha256",
        "cover_sha256",
        "qa_validator",
        "qa_validator_sha256",
        "qa_report",
        "qa_status",
        "qa_checks",
        "qa_report_sha256",
        "cover_renderer",
        "cover_dpi",
    )
    canonical = [{key: record.get(key) for key in fields} for record in records]
    return json_digest(canonical)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.resources: list[tuple[str, str, str]] = []
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
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.resources.append((tag, attribute, values[attribute]))
        if values.get("srcset"):
            for candidate in values["srcset"].split(","):
                url = candidate.strip().split()[0] if candidate.strip() else ""
                if url:
                    self.resources.append((tag, "srcset", url))
        if tag == "a" and values.get("href") and "download" in values:
            self.download_links.append(values["href"])
        if tag == "img":
            self.images.append(values)
        if tag == "meta":
            key = values.get("property") or values.get("name")
            if key:
                self.meta[("meta", key)] = values.get("content", "")


def local_reference_problems(parser: SiteParser, css: str) -> tuple[int, list[dict[str, str]]]:
    resources = list(parser.resources)
    resources.extend(("css", "url", match.strip(" \t\"'")) for match in re.findall(r"url\(([^)]+)\)", css))
    problems: list[dict[str, str]] = []
    checked = 0
    root_resolved = ROOT.resolve()
    known_ids = set(parser.ids)
    for _tag, _attribute, value in resources:
        parsed = urlparse(value)
        if parsed.scheme or parsed.netloc or value.startswith("//"):
            continue
        checked += 1
        if not parsed.path:
            if parsed.fragment and unquote(parsed.fragment) not in known_ids:
                problems.append({"reference": value, "reason": "missing local fragment"})
            continue
        candidate = (ROOT / unquote(parsed.path)).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError:
            problems.append({"reference": value, "reason": "path escapes site root"})
            continue
        if not candidate.is_file():
            problems.append({"reference": value, "reason": "missing local file"})
        elif parsed.fragment and candidate == (ROOT / "index.html").resolve() and unquote(parsed.fragment) not in known_ids:
            problems.append({"reference": value, "reason": "missing local fragment"})
    return checked, problems


def safe_hash(path: Path) -> str | None:
    try:
        return sha256(path) if path.is_file() else None
    except OSError:
        return None


def safe_pages(path: Path) -> tuple[int | None, str | None]:
    if not path.is_file():
        return None, "missing"
    try:
        return len(PdfReader(str(path)).pages), None
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"


def load_json(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise TypeError("top-level JSON value is not an object")
        return value, None
    except Exception as error:
        return {}, f"{path.relative_to(REPO)}: {type(error).__name__}: {error}"


def package_file_problems(code: str, record: dict[str, Any]) -> list[str]:
    """Lightweight clone/CI proof that the lean v9 package is complete."""
    number = int(code[1:])
    package = REPO / f"{code}-{DYNAMIC_SOURCE_VERSION}"
    canonical_name = Path(str(record.get("canonical_source", ""))).name
    expected_package_source = package / "source" / canonical_name
    expected_source_pdf = package / "output" / f"{code}-METSI-lectura-previa-{DYNAMIC_SOURCE_VERSION_SHORT}-final.pdf"
    required = [
        package / "document.json",
        package / "manifest.json",
        package / "source-manifest.json",
        package / "integrity-report.json",
        package / "index.html",
        package / "magazine.css",
        expected_package_source,
        expected_source_pdf,
    ]
    problems = [f"{code}.missing.{path.name}" for path in required if not path.is_file() or path.is_symlink()]
    if problems:
        return problems

    lean_files: set[Path] = set()
    for candidate in package.iterdir():
        if candidate.is_file() and candidate.suffix.casefold() in {".json", ".html", ".css", ".md"}:
            lean_files.add(candidate)
    for folder_name in ("assets", "diagrams", "source"):
        folder = package / folder_name
        lean_files.update(candidate for candidate in folder.rglob("*") if candidate.is_file())
    lean_files.add(expected_source_pdf)
    if any(path.is_symlink() for path in lean_files):
        problems.append(f"{code}.lean_package.symlink")
    lean_map = {path.relative_to(package).as_posix(): sha256(path) for path in sorted(lean_files)}
    if len(lean_map) != record.get("package_files") or json_digest(lean_map) != record.get("package_sha256"):
        problems.append(f"{code}.lean_package.digest")

    document, document_error = load_json(package / "document.json")
    manifest, manifest_error = load_json(package / "manifest.json")
    integrity, integrity_error = load_json(package / "integrity-report.json")
    expected_source_inside = f"source/{canonical_name}"
    if (
        document_error
        or manifest_error
        or document != manifest
        or document.get("number") != number
        or document.get("title") != record.get("title")
        or document.get("source") != expected_source_inside
        or document.get("source_sha256") != record.get("package_source_sha256")
    ):
        problems.append(f"{code}.document_manifest_identity")
    if (
        integrity_error
        or integrity.get("status") != "PASS"
        or integrity.get("missing_source_ids")
        or integrity.get("unexpected_source_ids")
    ):
        problems.append(f"{code}.integrity_report")

    media: list[tuple[str, str | None]] = []
    cover = document.get("cover", {})
    if isinstance(cover, dict):
        media.append((str(cover.get("source", "")), str(cover.get("sha256", "")) or None))
    for collection in ("image_manifest", "portrait_references", "diagrams"):
        items = document.get(collection, [])
        if not isinstance(items, list):
            problems.append(f"{code}.{collection}.schema")
            continue
        for item in items:
            if isinstance(item, dict):
                media.append((str(item.get("file", "")), str(item.get("sha256", "")) or None))
    package_resolved = package.resolve()
    for relative, expected_hash in media:
        candidate = (package / relative).resolve()
        try:
            candidate.relative_to(package_resolved)
        except ValueError:
            problems.append(f"{code}.media.escapes_package")
            continue
        if not relative or not candidate.is_file() or candidate.is_symlink():
            problems.append(f"{code}.media.missing.{relative or '<empty>'}")
        elif expected_hash and safe_hash(candidate) != expected_hash:
            problems.append(f"{code}.media.hash.{relative}")

    package_html = (package / "index.html").read_text(encoding="utf-8")
    package_css = (package / "magazine.css").read_text(encoding="utf-8")
    inventory = SiteParser()
    inventory.feed(package_html)
    references = [value for _tag, _attribute, value in inventory.resources]
    references.extend(match.strip(" \t\"'") for match in re.findall(r"url\(([^)]+)\)", package_css))
    for reference in references:
        parsed = urlparse(reference)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        candidate = (package / unquote(parsed.path)).resolve()
        try:
            candidate.relative_to(package_resolved)
        except ValueError:
            problems.append(f"{code}.html_ref.escapes_package")
            continue
        if not candidate.is_file():
            problems.append(f"{code}.html_ref.missing.{parsed.path}")
    return sorted(set(problems))


def build_report(require_sources: bool = False) -> dict[str, Any]:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    program_html = (ROOT / "programa.html").read_text(encoding="utf-8")
    css = (ROOT / "metsi.css").read_text(encoding="utf-8")
    script = (ROOT / "metsi.js").read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)
    program_parser = SiteParser()
    program_parser.feed(program_html)
    program_pdf = ROOT / "programa" / "programa-metsi-2026.pdf"
    deployed_program_pdf = ROOT / "covers" / "programa" / "programa-metsi-2026.pdf"
    program_source = REPO / "programa" / "programa-metsi-2026.md"
    program_pages, program_pdf_error = safe_pages(program_pdf)

    site_manifest, site_manifest_error = load_json(ROOT / "course-manifest.json")
    root_manifest, root_manifest_error = load_json(REPO / "course-manifest.json")
    approval, approval_error = load_json(REPO / "BLOCK-01-integrated-release-current" / "approval.json")
    cover_audit, cover_audit_error = load_json(REPO / "BLOCK-01-cover-review-current" / "audit.json")

    publication = site_manifest.get("publication", {}) if isinstance(site_manifest.get("publication"), dict) else {}
    raw_records = publication.get("readings", []) if isinstance(publication, dict) else []
    records = [item for item in raw_records if isinstance(item, dict)] if isinstance(raw_records, list) else []
    record_by_code = {str(item.get("code")): item for item in records if item.get("code")}
    dynamic_codes = [f"N{number:02d}" for number in range(FIRST_DYNAMIC, LAST_DYNAMIC + 1)]
    records_complete = (
        len(records) == len(dynamic_codes)
        and set(record_by_code) == set(dynamic_codes)
        and len(record_by_code) == len(records)
    )

    expected_pages = dict(LOCKED_PAGES)
    if records_complete:
        expected_pages.update({code: record_by_code[code].get("pages") for code in dynamic_codes})

    actual_pdf_hashes = {code: safe_hash(ROOT / "pdf" / relative) for code, relative in PDF_FILES.items()}
    actual_pdf_bytes = {
        code: (ROOT / "pdf" / relative).stat().st_size if (ROOT / "pdf" / relative).is_file() else None
        for code, relative in PDF_FILES.items()
    }
    page_results = {code: safe_pages(ROOT / "pdf" / relative) for code, relative in PDF_FILES.items()}
    page_counts = {code: result[0] for code, result in page_results.items()}
    pdf_errors = {code: result[1] for code, result in page_results.items() if result[1]}
    actual_cover_hashes = {code: safe_hash(ROOT / "covers" / COVER_FILES[code]) for code in PDF_FILES}

    expected_cover_hashes = {
        item.get("code"): item.get("metrics", {}).get("sha256")
        for item in cover_audit.get("documents", [])
        if isinstance(item, dict) and isinstance(item.get("metrics"), dict)
    }
    source_hashes: dict[str, str | None] = {}
    source_exists: dict[str, bool] = {}
    source_contract_problems: list[str] = []
    source_file_problems: list[str] = []
    for code in dynamic_codes:
        record = record_by_code.get(code, {})
        number = int(code[1:])
        expected_source = (
            f"{code}-{DYNAMIC_SOURCE_VERSION}/output/"
            f"{code}-METSI-lectura-previa-{DYNAMIC_SOURCE_VERSION_SHORT}-final.pdf"
        )
        expected_package_source = (
            f"{code}-{DYNAMIC_SOURCE_VERSION}/source/"
            f"{Path(str(record.get('canonical_source', ''))).name}"
        )
        expected_canonical_parent = f"{code}-content-canonical/source"
        source_value = record.get("source_pdf", "")
        source = (REPO / source_value).resolve() if isinstance(source_value, str) and source_value else REPO / "__missing__"
        canonical_value = record.get("canonical_source", "")
        canonical = (REPO / canonical_value).resolve() if isinstance(canonical_value, str) and canonical_value else REPO / "__missing__"
        package_value = record.get("package_source", "")
        package_source = (REPO / package_value).resolve() if isinstance(package_value, str) and package_value else REPO / "__missing__"
        confined: dict[str, bool] = {}
        for label, candidate in (("source_pdf", source), ("canonical_source", canonical), ("package_source", package_source)):
            try:
                candidate.relative_to(REPO.resolve())
                confined[label] = True
            except ValueError:
                confined[label] = False
                source_contract_problems.append(f"{code}.{label}.escapes_repo")
        if source_value != expected_source:
            source_contract_problems.append(f"{code}.source_pdf.route")
        if package_value != expected_package_source:
            source_contract_problems.append(f"{code}.package_source.route")
        try:
            if confined["canonical_source"] and canonical.parent.relative_to(REPO.resolve()).as_posix() != expected_canonical_parent:
                source_contract_problems.append(f"{code}.canonical_source.route")
        except ValueError:
            pass
        source_exists[code] = confined["source_pdf"] and source.is_file()
        source_hashes[code] = safe_hash(source) if require_sources and confined["source_pdf"] else None
        canonical_hash = safe_hash(canonical) if require_sources and confined["canonical_source"] else None
        package_hash = safe_hash(package_source) if require_sources and confined["package_source"] else None
        for hash_field in ("canonical_sha256", "package_source_sha256", "package_sha256", "qa_validator_sha256", "qa_report_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(record.get(hash_field, ""))):
                source_contract_problems.append(f"{code}.{hash_field}")
        if not isinstance(record.get("package_files"), int) or record.get("package_files", 0) <= 0:
            source_contract_problems.append(f"{code}.package_files")
        if require_sources:
            if not confined["source_pdf"] or not source.is_file():
                source_file_problems.append(f"{code}.source_pdf")
            if not confined["canonical_source"] or not canonical.is_file() or canonical_hash != record.get("canonical_sha256"):
                source_file_problems.append(f"{code}.canonical_sha256")
            if not confined["package_source"] or not package_source.is_file() or package_hash != record.get("package_source_sha256"):
                source_file_problems.append(f"{code}.package_source_sha256")
            if canonical_hash != package_hash:
                source_file_problems.append(f"{code}.canonical_package_identity")
            source_file_problems.extend(package_file_problems(code, record))
        if not str(record.get("title", "")).startswith(f"{code} · "):
            source_contract_problems.append(f"{code}.title")
        if record.get("qa_status") != "PASS" or not isinstance(record.get("qa_checks"), int) or record.get("qa_checks", 0) <= 0:
            source_contract_problems.append(f"{code}.qa")
        if record.get("qa_validator") != DYNAMIC_QA_VALIDATOR:
            source_contract_problems.append(f"{code}.qa_validator")
        expected_qa_report = f"{DYNAMIC_QA_ROOT}/{code}-validation-{DYNAMIC_SOURCE_VERSION_SHORT}.json"
        if record.get("qa_report") != expected_qa_report:
            source_contract_problems.append(f"{code}.qa_report.route")
        qa_report_path = REPO / expected_qa_report
        qa_report_hash = safe_hash(qa_report_path)
        if not qa_report_path.is_file() or qa_report_hash != record.get("qa_report_sha256"):
            source_contract_problems.append(f"{code}.qa_report_sha256")
        else:
            qa_report, qa_report_error = load_json(qa_report_path)
            qa_metrics = qa_report.get("metrics", {}) if isinstance(qa_report.get("metrics"), dict) else {}
            if (
                qa_report_error
                or qa_report.get("document") != code
                or qa_report.get("status") != "PASS"
                or qa_report.get("validator") != record.get("qa_validator")
                or qa_report.get("total_checks") != record.get("qa_checks")
                or qa_metrics.get("pages") != record.get("pages")
                or qa_metrics.get("pdf_bytes") != record.get("bytes")
                or qa_metrics.get("pdf_sha256") != record.get("sha256")
            ):
                source_contract_problems.append(f"{code}.qa_report.content")
        if require_sources:
            validator_path = REPO / DYNAMIC_QA_VALIDATOR
            if not validator_path.is_file() or safe_hash(validator_path) != record.get("qa_validator_sha256"):
                source_file_problems.append(f"{code}.qa_validator_sha256")

    root_documents = root_manifest.get("documents", [])
    root_records = {
        str(item.get("code")): item
        for item in root_documents
        if isinstance(root_documents, list) and isinstance(item, dict) and item.get("code")
    }
    manifest_mismatches: list[str] = []
    for code in dynamic_codes:
        site_record = record_by_code.get(code, {})
        root_record = root_records.get(code, {})
        expected_root = {
            "pdf": site_record.get("source_pdf"),
            "public_pdf": f"site/{site_record.get('public_pdf', '')}",
            "cover": f"site/{site_record.get('cover', '')}",
            "pages": site_record.get("pages"),
            "bytes": site_record.get("bytes"),
            "sha256": site_record.get("sha256"),
            "cover_sha256": site_record.get("cover_sha256"),
            "canonical_source": site_record.get("canonical_source"),
            "canonical_sha256": site_record.get("canonical_sha256"),
            "package_sha256": site_record.get("package_sha256"),
            "package_files": site_record.get("package_files"),
            "qa_report": site_record.get("qa_report"),
            "qa_report_sha256": site_record.get("qa_report_sha256"),
            "qa_validator": site_record.get("qa_validator"),
            "qa_validator_sha256": site_record.get("qa_validator_sha256"),
            "source_version": publication.get("source_version"),
        }
        for key, expected in expected_root.items():
            if root_record.get(key) != expected:
                manifest_mismatches.append(f"{code}.{key}")
        if root_record.get("status") != "closed":
            manifest_mismatches.append(f"{code}.status")

    local_checked, local_problems = local_reference_problems(parser, css)
    pdf_downloads = {
        urlparse(link).path.removeprefix("pdf/")
        for link in parser.download_links
        if urlparse(link).path.startswith("pdf/")
    }
    mapped_codes = {f"N{number:02d}" for number in range(1, 37)}
    visible_codes = set(re.findall(r"\bN(?:0[1-9]|[12][0-9]|3[0-6])\b", html))
    declared_hashes_match = records_complete and all(
        record_by_code[code].get("sha256") == actual_pdf_hashes[code]
        and record_by_code[code].get("bytes") == actual_pdf_bytes[code]
        and record_by_code[code].get("cover_sha256") == actual_cover_hashes[code]
        for code in dynamic_codes
    )
    source_hashes_match = require_sources and records_complete and all(
        source_exists[code]
        and source_hashes[code] == actual_pdf_hashes[code] == record_by_code[code].get("sha256")
        for code in dynamic_codes
    )
    page_labels_match = records_complete and all(
        len(re.findall(rf"<p>N{number:02d}\s*·\s*{record_by_code[f'N{number:02d}'].get('pages')}\s+páginas</p>", html)) == 1
        for number in range(FIRST_DYNAMIC, LAST_DYNAMIC + 1)
    )
    library_titles_match = records_complete and all(
        html.count(
            f'<p>{code} · {record_by_code[code].get("pages")} páginas</p>'
            f'<h3>{html_lib.escape(str(record_by_code[code].get("title", "")).removeprefix(f"{code} · "))}</h3>'
        ) == 1
        for code in dynamic_codes
    )
    stable_routes_match = records_complete and all(
        record_by_code[code].get("public_pdf") == f"pdf/{PDF_FILES[code]}"
        and html.count(f'href="{record_by_code[code].get("public_pdf")}"') == 3
        and record_by_code[code].get("cover") == f"covers/{COVER_FILES[code]}"
        for code in dynamic_codes
    )
    expected_release_digest = publication_digest(records) if records_complete else None
    release_metadata_match = (
        records_complete
        and publication.get("range") == "N11-N36"
        and publication.get("source_version") == DYNAMIC_SOURCE_VERSION
        and publication.get("public_route_contract") == "stable-v1-filename"
        and publication.get("release_sha256") == expected_release_digest
        and root_manifest.get("site_publication") == {
            "range": "N11-N36",
            "source_version": DYNAMIC_SOURCE_VERSION,
            "public_route_contract": "stable-v1-filename",
            "release_sha256": expected_release_digest,
        }
    )

    approved_pdf_hashes = approval.get("pdf_sha256", {}) if isinstance(approval.get("pdf_sha256"), dict) else {}
    checks = {
        "manifests_parse": not any((site_manifest_error, root_manifest_error, approval_error, cover_audit_error)),
        "n11_n36_publication_contract_complete": records_complete,
        "n11_n36_source_contract_well_formed": records_complete and not source_contract_problems,
        "n11_n36_sources_match_current_canonicals": not require_sources or (records_complete and not source_file_problems),
        "root_and_site_manifests_agree": records_complete and not manifest_mismatches,
        "publication_release_digest_matches": release_metadata_match,
        "semantic_language_and_landmarks": '<html lang="es-AR">' in html and "<main" in html and "<nav" in html and "<footer" in html,
        "all_local_links_resolve": not local_problems,
        "unique_ids": len(parser.ids) == len(set(parser.ids)),
        "aria_controls_resolve": set(parser.controls).issubset(set(parser.ids)),
        "all_images_have_alt": bool(parser.images) and all("alt" in image and image["alt"].strip() for image in parser.images),
        "thirty_seven_exact_pdf_downloads": pdf_downloads == set(PDF_FILES.values()) and len(list((ROOT / "pdf").rglob("*.pdf"))) == 37,
        "approved_pdfs_remain_unchanged": bool(approved_pdf_hashes) and {code: actual_pdf_hashes.get(code) for code in approved_pdf_hashes} == approved_pdf_hashes,
        "n11_n36_pdfs_match_v9_sources_and_manifest": declared_hashes_match and (not require_sources or source_hashes_match),
        "pdf_page_counts_match_manifests": len(expected_pages) == 37 and page_counts == expected_pages and not pdf_errors,
        "approved_covers_remain_unchanged": bool(expected_cover_hashes) and {code: actual_cover_hashes.get(code) for code in expected_cover_hashes} == expected_cover_hashes,
        "n11_n36_covers_match_manifest": records_complete and all(
            record_by_code[code].get("cover_sha256") == actual_cover_hashes[code]
            and record_by_code[code].get("cover_dpi") == 120
            and str(record_by_code[code].get("cover_renderer", "")).startswith("pdftoppm version ")
            for code in dynamic_codes
        ),
        "all_published_covers_present": (
            len(actual_cover_hashes) == 37
            and all(actual_cover_hashes.values())
            and {path.name for path in (ROOT / "covers").glob("N[0-9][0-9].*")} == set(COVER_FILES.values())
        ),
        "stable_n11_n36_routes_titles_and_page_labels": stable_routes_match and page_labels_match and library_titles_match,
        "all_36_nuclei_present": visible_codes.issuperset(mapped_codes),
        "all_nuclei_downloadable": all(any(f"N{number:02d}-METSI-lectura-previa" in link for link in parser.download_links) for number in range(1, 37)),
        "eight_curricular_blocks": html.count('class="block"') == 8,
        "audience_tabs_complete": html.count('role="tab"') == 4 and html.count('role="tabpanel"') == 4,
        "responsive_and_reduced_motion_css": "@media(max-width:650px)" in css and "prefers-reduced-motion" in css,
        "keyboard_tabs_implemented": "ArrowLeft" in script and "ArrowRight" in script and "tabIndex" in script,
        "social_metadata_complete": all(parser.meta.get(("meta", key), "") for key in ("og:title", "og:description", "og:image", "twitter:card", "twitter:image")),
        "no_placeholders": not re.search(r"\b(?:TBD|TODO|Lorem|XXX)\b", html, flags=re.I),
        "identity_and_author_visible": (
            "Metodología del Estudio de Sistemas de Información" in html
            and html.count("Diego Carralbal") >= 2
            and html.count("https://www.linkedin.com/in/carralbal/") >= 2
        ),
        "program_source_and_pdf_present": (
            program_source.is_file()
            and program_pdf.is_file()
            and deployed_program_pdf.is_file()
            and safe_hash(deployed_program_pdf) == safe_hash(program_pdf)
            and program_pages == 7
            and not program_pdf_error
        ),
        "public_program_integrated": (
            'id="programa"' in html
            and "Ocho unidades curriculares" in html
            and "covers/programa/programa-metsi-2026.pdf" in html
        ),
        "program_page_complete": all(
            token in program_html
            for token in (
                "Metodología de los Sistemas de Información",
                "Resultados de aprendizaje",
                "Ocho unidades",
                "Hotel Horizonte",
                "Instancias sumativas propuestas",
                "Bibliografía y revisión",
            )
        ),
        "program_navigation_accessible": (
            len(program_parser.ids) == len(set(program_parser.ids))
            and set(program_parser.controls).issubset(set(program_parser.ids))
            and 'aria-current="page"' in program_html
        ),
        "hamburger_menu_implemented": (
            html.count("data-menu-toggle") == 1
            and program_html.count("data-menu-toggle") == 1
            and "aria-expanded" in html
            and "Escape" in script
            and "menu-open" in script
            and ".site-header.menu-open nav" in css
        ),
        "hero_background_asset_and_breakpoints": (
            (ROOT / "covers" / "hero-metsi-bw-v1.webp").is_file()
            and 'url("covers/hero-metsi-bw-v1.webp?v=20260914-2")' in css
            and "background-position:56% center" in css
            and "background-position:62% center" in css
        ),
    }

    return {
        "scope": "METSI narrative course site",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "facts": {
            "manifest_errors": [error for error in (site_manifest_error, root_manifest_error, approval_error, cover_audit_error) if error],
            "manifest_mismatches": sorted(manifest_mismatches),
            "source_contract_problems": sorted(set(source_contract_problems)),
            "source_files_required": require_sources,
            "source_file_problems": sorted(set(source_file_problems)),
            "release_sha256": expected_release_digest,
            "pdf_downloads": len(pdf_downloads),
            "pdf_pages": page_counts,
            "pdf_bytes": actual_pdf_bytes,
            "pdf_sha256": actual_pdf_hashes,
            "pdf_errors": pdf_errors,
            "cover_images": sum(value is not None for value in actual_cover_hashes.values()),
            "cover_sha256": actual_cover_hashes,
            "curricular_nuclei_visible": len(mapped_codes & visible_codes),
            "curricular_blocks": html.count('class="block"'),
            "local_references_checked": local_checked,
            "local_reference_problems": local_problems,
            "program_pdf_pages": program_pages,
            "program_pdf_bytes": program_pdf.stat().st_size if program_pdf.is_file() else None,
            "program_pdf_sha256": safe_hash(program_pdf),
            "program_source_sha256": safe_hash(program_source),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Validate and print JSON without writing site/audit.json.")
    parser.add_argument(
        "--require-sources",
        action="store_true",
        help="Also rehash generated v3 PDFs and canonical/package sources; intended for local release sealing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(require_sources=args.require_sources)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if not args.check_only:
        (ROOT / "audit.json").write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
