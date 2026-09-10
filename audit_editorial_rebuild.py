#!/usr/bin/env python3
"""Audit rebuilt METSI editorial packages without confusing integrity with parity."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold().replace("’", "").replace("'", "")
    return re.findall(r"[a-záéíóúüñ0-9]+", normalized)


def annotation_urls(reader: PdfReader) -> list[str]:
    urls: list[str] = []
    for page in reader.pages:
        for raw in page.get("/Annots", []):
            annotation = raw.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                urls.append(str(action.get("/URI")))
    return urls


def expected_urls(manifest: dict) -> list[str]:
    found: list[str] = []
    for reference in manifest.get("references", []):
        found.extend(re.findall(r"https://[^\s)]+", reference))
    return [url.rstrip(".,;") for url in found]


def page_evidence(pdf: pdfplumber.PDF) -> tuple[list[int], list[int], list[dict]]:
    blank: list[int] = []
    suspicious: list[int] = []
    evidence: list[dict] = []
    for number, page in enumerate(pdf.pages, 1):
        words = [word for word in (page.extract_words(use_text_flow=True) or []) if float(word["top"]) < 790]
        images = page.images or []
        if not words and not images:
            blank.append(number)
        bounds = [(float(word["top"]), float(word["bottom"])) for word in words]
        bounds += [
            (float(image["top"]), float(image["bottom"]))
            for image in images
            if image.get("top") is not None and image.get("bottom") is not None and float(image["top"]) < 790
        ]
        span = max((bottom for _, bottom in bounds), default=0) - min((top for top, _ in bounds), default=0)
        ratio = round(span / 744, 3) if bounds else 0
        text = page.extract_text() or ""
        approved_vector_plate = any(label in text for label in (
            "INSTRUMENTO DE DECISIÓN",
            "MAPA DE TRANSICIÓN",
            "MAPA DE CONVERGENCIA",
            "MAPA DE FLUJO REAL",
            "PUERTA DE SELECCIÓN",
            "EXPEDIENTE DE COHERENCIA",
            "ARQUITECTURA DE DECISIONES",
            "EXPEDIENTE DE LEGADO",
            "CAMPO DE REALIZACIÓN",
            "ESTRATEGIA SITUADA",
            "MAPA DE OBJETOS",
            "EXPEDIENTE DE HIPÓTESIS",
            "CORTE POR CAPACIDAD",
            "EXPEDIENTE DE RENUNCIA",
            "MAPA TEMPORAL",
            "MAPA DE ECOSISTEMA",
            "CONTRATO VERIFICABLE",
            "EXPEDIENTE DE CALIDAD",
    "EXPEDIENTE DE LIBERACIÓN",
    "OBSERVACIÓN OPERABLE",
    "EXPEDIENTE DE PERTINENCIA",
    "EXPEDIENTE DE AUTONOMÍA",
    "REGISTRO VIVO DE GOBIERNO",
    "EXPEDIENTE INTEGRADO",
    "MATRIZ DE DEFENSA Y TRANSFERENCIA",
    "SISTEMA DE PRÁCTICA REFLEXIVA",
        )) and len(words) < 230
        deliberate_thesis = (
            "Tesis" in text
            and len(words) < 200
            and ratio >= .45
        )
        deliberate_plate = (
            number in {1, 4, 5, len(pdf.pages)}
            or bool(images and len(words) < 70)
            or approved_vector_plate
            or deliberate_thesis
        )
        if ratio < .50 and not deliberate_plate:
            suspicious.append(number)
        evidence.append({
            "page": number,
            "fill_ratio": ratio,
            "word_count": len(words),
            "image_count": len(images),
            "deliberate_plate": deliberate_plate,
            "preview": " | ".join(text.splitlines())[:180],
        })
    return blank, suspicious, evidence


def audit(number: int, version: int) -> dict:
    package = ROOT / f"N{number:02d}-v{version}-editorial"
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    source_manifest = json.loads((package / "source-manifest.json").read_text(encoding="utf-8"))
    integrity = json.loads((package / "integrity-report.json").read_text(encoding="utf-8"))
    final = package / "output" / f"N{number:02d}-METSI-lectura-previa-v{version}-final.pdf"
    reader = PdfReader(final)
    with pdfplumber.open(final) as pdf:
        extracted = "\n".join(page.extract_text() or "" for page in pdf.pages)
        blank, suspicious, pages = page_evidence(pdf)
    canonical = "\n".join(block["text"] for block in source_manifest["eligible_blocks"])
    # Exact URLs are verified independently against PDF link annotations below.
    # Excluding them from the word counter prevents valid PDF line breaks at URL
    # path boundaries or encoded spaces from being misreported as lost prose.
    canonical_prose = re.sub(r"https://\S+", "", canonical)
    expected_counter = collections.Counter(tokens(canonical_prose))
    actual_counter = collections.Counter(tokens(extracted))
    missing = {
        token: count - actual_counter[token]
        for token, count in expected_counter.items()
        if count > actual_counter[token]
    }
    expected_links = expected_urls(manifest)
    actual_links = annotation_urls(reader)
    missing_links = sorted(set(expected_links) - set(actual_links))
    treatments = collections.Counter(
        image.get("treatment", "undeclared") for image in manifest.get("image_manifest", [])
    )
    portrait_sources = manifest.get("portrait_references", [])
    source_path = package / manifest["source"]
    record = {
        "document": f"N{number:02d}",
        "version": version,
        "pdf": str(final.relative_to(ROOT)),
        "pdf_sha256": sha(final),
        "bytes": final.stat().st_size,
        "pages": len(reader.pages),
        "a4": all(
            abs(float(page.mediabox.width) - 594.96) < .25
            and abs(float(page.mediabox.height) - 841.92) < .25
            for page in reader.pages
        ),
        "language": str(reader.trailer["/Root"].get("/Lang", "")),
        "source_sha256_preserved": manifest["source_sha256"] == sha(source_path),
        "source_blocks": len(source_manifest["eligible_blocks"]),
        "mapped_blocks": integrity["rendered_source_id_count"],
        "source_mapping": integrity["status"],
        "canonical_tokens": sum(expected_counter.values()),
        "missing_canonical_token_occurrences": sum(missing.values()),
        "missing_canonical_tokens": missing,
        "blank_pages": blank,
        "suspicious_underfilled_pages": suspicious,
        "page_evidence": pages,
        "reference_urls": len(expected_links),
        "missing_reference_urls": missing_links,
        "linkedin_footer_link": "https://www.linkedin.com/in/carralbal" in actual_links,
        "hotel_anchor_present": (package / "assets" / "hotel-horizonte-canonical.png").is_file(),
        "referents": len(portrait_sources),
        "referents_with_primary_work": sum(bool(item.get("primary_reference")) for item in portrait_sources),
        "image_treatments": dict(treatments),
        "restrained_color_present": treatments["natural_restrained_color"] > 0,
    }
    checks = {
        "content_integrity": record["source_sha256_preserved"] and record["source_mapping"] == "PASS" and not missing,
        "pdf_integrity": record["a4"] and record["language"] == "es-AR" and not blank,
        "layout_density": not suspicious,
        "references": not missing_links and record["linkedin_footer_link"],
        "hotel_continuity": record["hotel_anchor_present"],
        "referents_editorial": record["referents"] == 6 and record["referents_with_primary_work"] == 6,
        "interior_color_balance": record["restrained_color_present"],
    }
    record["checks"] = checks
    record["status"] = "PASS" if all(checks.values()) else "FAIL"
    qa_dir = package / "qa"
    qa_dir.mkdir(exist_ok=True)
    (qa_dir / "rebuild-audit.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--version", type=int, default=4)
    args = parser.parse_args()
    results = [audit(number, args.version) for number in range(args.start, args.end + 1)]
    print(json.dumps({item["document"]: item["status"] for item in results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
