#!/usr/bin/env python3
"""Auditoría reproducible del candidato integral N00 v2.

La auditoría nunca modifica el N00 aprobado. Verifica el candidato separado,
la preservación de los hashes canónicos y los criterios editoriales que
resultan de las rondas N00 y N01.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
BASELINE_PDF = ROOT / "N00/output/N00-METSI-lectura-previa-final.pdf"
BASELINE_SOURCE = ROOT / "N00/source/N00_como_leer_metsi.md"
CANDIDATE = ROOT / "N00-v2-candidate"
SOURCE = CANDIDATE / "source/N00_como_leer_metsi.md"
PDF = CANDIDATE / "output/N00-METSI-lectura-previa-v2-candidate-final.pdf"
QA = CANDIDATE / "qa-report.json"
PAGES = CANDIDATE / "qa-pages-final-v2"
OUTPUT = CANDIDATE / "audit-report.json"

EXPECTED_BASELINE_PDF_SHA256 = "1b4a1ab42665246349ed240659585a2e33766fe72157032bfbefc03cc7127f64"
EXPECTED_BASELINE_SOURCE_SHA256 = "e94edbd29855899f25f22c7ae695cd2a3fe7964371fe210d6b3a1035dd620763"

EXPECTED_VOSEO = {
    "N01": "Situá", "N02": "Mostrá", "N03": "Convertí", "N04": "Separá",
    "N05": "Reemplazá", "N06": "Diseñá", "N07": "Transformá", "N08": "Observá",
    "N09": "Estudiá", "N10": "Integrá", "N11": "Examiná", "N12": "Distinguí",
    "N13": "Trabajá", "N14": "Recorré", "N15": "Seleccioná", "N16": "Buscá",
    "N17": "Separá", "N18": "Tratá", "N19": "Ampliá", "N20": "Componé",
    "N21": "Distinguí", "N22": "Convertí", "N23": "Cortá", "N24": "Entendé",
    "N25": "Estudiá", "N26": "Ampliá", "N27": "Diseñá", "N28": "Construí",
    "N29": "Goberná", "N30": "Conectá", "N31": "Distinguí", "N32": "Evaluá",
    "N33": "Diseñá", "N34": "Reconstruí", "N35": "Comunicá", "N36": "Cerrá",
}

REFERENCE_ANCHORS = {
    "Schön (1983)": ("Schön",),
    "Norman (2013)": ("Norman",),
    "Suchman (2007)": ("Suchman", "2007"),
    "Costanza-Chock (2020)": ("Costanza-Chock",),
    "Argyris y Schön (1996)": ("Argyris", "Schön"),
    "Chi y Wylie (2014)": ("Chi", "Wylie"),
    "UNESCO (2024)": ("AI Competency Framework for Students", "UNESCO", "2024"),
    "CAST (2024)": ("CAST", "2024"),
    "Kapur (2024)": ("Kapur",),
    "NIST (2024)": ("NIST", "2024"),
    "Freeman et al. (2014)": ("Freeman",),
    "Deslauriers et al. (2019)": ("Deslauriers",),
    "Roediger y Karpicke (2006)": ("Roediger", "Karpicke"),
    "Valentini y Blancas (2025)": ("UNESCO IESALC", "2025"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dereference(value):
    try:
        return value.get_object()
    except AttributeError:
        return value


def count_outline_items(items) -> int:
    count = 0
    for item in items:
        if isinstance(item, list):
            count += count_outline_items(item)
        else:
            count += 1
    return count


def count_image_alt_metadata(reader: PdfReader) -> tuple[int, int]:
    total = 0
    with_alt = 0
    seen: set[tuple[int, int] | int] = set()

    def walk_resources(resources) -> None:
        nonlocal total, with_alt
        resources = dereference(resources)
        if not resources:
            return
        xobjects = dereference(resources.get("/XObject"))
        if not xobjects:
            return
        for reference in xobjects.values():
            identity = (
                (int(reference.idnum), int(reference.generation))
                if hasattr(reference, "idnum") else id(reference)
            )
            if identity in seen:
                continue
            seen.add(identity)
            obj = dereference(reference)
            if obj.get("/Subtype") == "/Image":
                total += 1
                with_alt += bool(str(obj.get("/Alt", "")).strip())
            elif obj.get("/Subtype") == "/Form":
                walk_resources(obj.get("/Resources"))

    for page in reader.pages:
        walk_resources(page.get("/Resources"))
    return total, with_alt


def structured_figures(reader: PdfReader) -> list[str]:
    root = reader.trailer["/Root"]
    structure = root.get("/StructTreeRoot")
    if not structure:
        return []
    found: list[str] = []
    seen: set[int] = set()

    def walk(value) -> None:
        obj = dereference(value)
        identity = id(obj)
        if identity in seen:
            return
        seen.add(identity)
        if isinstance(obj, dict):
            if obj.get("/S") == "/Figure":
                found.append(str(obj.get("/Alt", "")))
            for key, child in obj.items():
                if key not in ("/P", "/Pg"):
                    walk(child)
        elif isinstance(obj, list):
            for child in obj:
                walk(child)

    walk(structure)
    return found


def page_fill_ratios() -> dict[str, float]:
    """Estimate visual content span, excluding dedicated full-page visual pages."""
    special = {1, 4, 5, 23, 24, 36, 43}
    ratios: dict[str, float] = {}
    for path in sorted(PAGES.glob("page-*.png")):
        number = int(path.stem.split("-")[-1])
        if number in special:
            continue
        image = np.asarray(Image.open(path).convert("RGB"))
        height, width, _ = image.shape
        crop = image[int(.035 * height):int(.90 * height), int(.06 * width):int(.94 * width)]
        samples = np.concatenate((image[:30, :30].reshape(-1, 3), image[:30, -30:].reshape(-1, 3)))
        background = np.median(samples, axis=0)
        difference = np.max(np.abs(crop.astype(int) - background.astype(int)), axis=2)
        active_rows = (difference > 18).mean(axis=1) > .004
        rows = np.flatnonzero(active_rows)
        ratio = 0.0 if not len(rows) else float((rows[-1] - rows[0] + 1) / crop.shape[0])
        ratios[str(number)] = round(ratio, 3)
    return ratios


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    body, references = re.split(r"(?m)^## Referencias base\s*$", source, maxsplit=1)
    reader = PdfReader(str(PDF))
    qa_payload = json.loads(QA.read_text(encoding="utf-8"))
    qa = qa_payload[0] if isinstance(qa_payload, list) else qa_payload
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)

    baseline_hashes = {
        "pdf": sha256(BASELINE_PDF),
        "source": sha256(BASELINE_SOURCE),
    }
    baseline_untouched = (
        baseline_hashes["pdf"] == EXPECTED_BASELINE_PDF_SHA256
        and baseline_hashes["source"] == EXPECTED_BASELINE_SOURCE_SHA256
    )

    entries = {
        match.group(1): match.group(2)
        for match in re.finditer(r"^- \*\*(N\d{2})\.\*\*\s+(\S+)", source, flags=re.MULTILINE)
    }
    voseo_mismatches = {
        key: {"expected": value, "found": entries.get(key)}
        for key, value in EXPECTED_VOSEO.items() if entries.get(key) != value
    }

    hh_identifiers = sorted(set(re.findall(r"\bHH-(?:0\d|10)\b", source)))
    anchors = {
        name: all(token in body for token in tokens)
        for name, tokens in REFERENCE_ANCHORS.items()
    }
    source_urls = sorted(set(re.findall(r"https://[^\s)]+", references)))
    pdf_urls = sorted(qa["external_reference_links"])

    link_annotations = 0
    internal_links = 0
    for page in reader.pages:
        for annotation in page.get("/Annots") or []:
            obj = dereference(annotation)
            if obj.get("/Subtype") != "/Link":
                continue
            link_annotations += 1
            if obj.get("/Dest") is not None or dereference(obj.get("/A") or {}).get("/S") == "/GoTo":
                internal_links += 1

    total_images, images_with_alt = count_image_alt_metadata(reader)
    figures = structured_figures(reader)
    fills = page_fill_ratios()
    minimum_page = min(fills, key=fills.get)

    checks = {
        "baseline_approved_files_untouched": baseline_untouched,
        "qa_status_pass": qa["status"] == "PASS",
        "page_count_43": len(reader.pages) == 43,
        "all_pages_a4": qa["a4_pages"] == 43,
        "all_36_nuclei_present": sorted(entries) == sorted(EXPECTED_VOSEO),
        "all_36_index_verbs_rioplatense": not voseo_mismatches,
        "eight_curricular_blocks_present": all(f"Bloque {letter}." in source for letter in "ABCDEFGH"),
        "production_block_clarified": "Bloque 1" in source and "N01 a N10" in source,
        "hh_00_through_hh_10_present": hh_identifiers == [f"HH-{number:02d}" for number in range(11)],
        "problem_frame_anglicism_removed": "problem frame" not in source.lower(),
        "task_specific_ai_rule_present": "indicación específica prevalece" in source,
        "conditional_modality_present": all(token in source for token in ("programa", "cronograma", "modalidad aprobada para la comisión")),
        "all_reference_entries_anchored": all(anchors.values()),
        "reference_urls_match_pdf_annotations": source_urls == pdf_urls,
        "all_images_have_alt_metadata": total_images == images_with_alt == 21,
        "closing_page_structure_complete": all((qa["closing_caption_present"], qa["closing_folio_present"], qa["closing_alt_present"])),
        "tagged_and_language_declared": qa["struct_tree_present"] and qa["marked_pdf"] and qa["document_language"] == "es-AR",
        "outline_complete": count_outline_items(reader.outline) == 35 and not qa["outline_missing"],
        "internal_navigation_complete": internal_links == 35,
        "no_text_page_below_half_fill": fills[minimum_page] >= .50,
        "no_forbidden_fonts": not qa["forbidden_fonts"],
        "linkedin_footer_on_every_page": qa["linkedin_pages"] == len(reader.pages),
        "closing_quote_absent": qa["closing_quote_absent"],
        "no_placeholder_tokens": not re.search(r"\b(?:TBD|lorem|XXX)\b", source, flags=re.IGNORECASE),
        "pdf_contains_all_source_headings": not qa["missing_headings"],
        "cover_eyebrow_extracts_as_complete_lines": "LECTURA PREVIA" in (reader.pages[0].extract_text() or "") and "EDICIÓN 2026" in (reader.pages[0].extract_text() or ""),
        "index_voseo_visible_in_pdf": all(f"{code}. {verb}" in pdf_text for code, verb in EXPECTED_VOSEO.items()),
    }

    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "candidate": {
            "pdf": str(PDF.relative_to(ROOT)),
            "sha256": sha256(PDF),
            "bytes": PDF.stat().st_size,
            "modified_at": datetime.fromtimestamp(PDF.stat().st_mtime).astimezone().isoformat(timespec="seconds"),
            "pages": len(reader.pages),
            "source_words": qa["source_words"],
            "pdf_words_including_running_matter": qa["pdf_words"],
        },
        "baseline": {**baseline_hashes, "untouched": baseline_untouched},
        "content": {
            "voseo_mismatches": voseo_mismatches,
            "hh_identifiers": hh_identifiers,
            "reference_anchors": anchors,
            "source_reference_urls": source_urls,
        },
        "layout": {
            "ordinary_page_fill_ratios": fills,
            "minimum_ordinary_page": int(minimum_page),
            "minimum_ordinary_page_fill": fills[minimum_page],
            "full_contact_sheet": str((CANDIDATE / "N00-v2-candidate-final-contact-sheet.jpg").relative_to(ROOT)),
        },
        "navigation_accessibility": {
            "outline_items": count_outline_items(reader.outline),
            "link_annotations": link_annotations,
            "internal_links": internal_links,
            "image_xobjects": total_images,
            "image_xobjects_with_alt_metadata": images_with_alt,
            "structured_figure_alts": figures,
            "pdf_ua_conformance_claimed": False,
            "note": "El PDF está etiquetado, declara es-AR y todas las imágenes raster tienen descripción. La conformidad formal PDF/UA no fue certificada; el árbol exportado por Chrome expone tres figuras de forma nativa.",
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failed": [key for key, value in checks.items() if not value], "output": str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
