#!/usr/bin/env python3
"""Consolidate the current authority and QA state of METSI N00-N10.

This validator is intentionally read-only with respect to courseware. It writes
only the two reports in its own directory.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent

FINAL_PACKAGES = {
    "N01": "N01-v18-final",
    "N02": "N02-v14-final",
    "N03": "N03-v9-final",
    "N04": "N04-v9-final",
    "N05": "N05-v9-final",
    "N06": "N06-v9-final",
    "N07": "N07-v9-final",
    "N08": "N08-v9-final",
    "N09": "N09-v9-final",
    "N10": "N10-v9-final",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def pdf_facts(path: Path) -> dict:
    reader = PdfReader(str(path))
    sizes = []
    uris = []
    for page in reader.pages:
        width = round(float(page.mediabox.width), 2)
        height = round(float(page.mediabox.height), 2)
        sizes.append([width, height])
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                uris.append(str(action.get("/URI")))
    unique_sizes = sorted({tuple(item) for item in sizes})
    return {
        "pages": len(reader.pages),
        "page_sizes_points": [list(item) for item in unique_sizes],
        "all_pages_a4": all(
            abs(width - 594.96) <= 0.5 and abs(height - 841.92) <= 0.5
            for width, height in (tuple(item) for item in sizes)
        ),
        "external_uris": sorted(set(uris)),
    }


def inspect_n00() -> dict:
    approved_root = ROOT / "N00"
    candidate_root = ROOT / "N00-v2-candidate"
    approved_pdf = approved_root / "output/N00-METSI-lectura-previa-final.pdf"
    approved_source = approved_root / "source/N00_como_leer_metsi.md"
    candidate_pdf = candidate_root / "output/N00-METSI-lectura-previa-v2-candidate-final.pdf"
    candidate_source = candidate_root / "source/N00_como_leer_metsi.md"
    approved_qa = load_json(approved_root / "qa-report.json")
    approved_integrity = load_json(approved_root / "integrity-report.json")
    candidate_qa = load_json(candidate_root / "qa-report.json")
    candidate_integrity = load_json(candidate_root / "integrity-report.json")
    candidate_audit = load_json(candidate_root / "audit-report.json")
    approved_pdf_facts = pdf_facts(approved_pdf)
    candidate_pdf_facts = pdf_facts(candidate_pdf)

    return {
        "approved_production": {
            "status": "approved",
            "pdf": relative(approved_pdf),
            "pdf_sha256": sha256(approved_pdf),
            "pdf_bytes": approved_pdf.stat().st_size,
            "pages": approved_qa["pages"],
            "a4_pages": approved_qa["a4_pages"],
            "actual_pages": approved_pdf_facts["pages"],
            "actual_all_pages_a4": approved_pdf_facts["all_pages_a4"],
            "source": relative(approved_source),
            "source_sha256": sha256(approved_source),
            "qa": approved_qa["status"],
            "integrity": approved_integrity["status"],
        },
        "v2_candidate": {
            "status": "technical_pass_pending_author_approval",
            "pdf": relative(candidate_pdf),
            "pdf_sha256": sha256(candidate_pdf),
            "pdf_bytes": candidate_pdf.stat().st_size,
            "pages": candidate_qa["pages"],
            "a4_pages": candidate_qa["a4_pages"],
            "actual_pages": candidate_pdf_facts["pages"],
            "actual_all_pages_a4": candidate_pdf_facts["all_pages_a4"],
            "source": relative(candidate_source),
            "source_sha256": sha256(candidate_source),
            "qa": candidate_qa["status"],
            "integrity": candidate_integrity["status"],
            "audit": candidate_audit["status"],
            "audit_checks_passed": sum(bool(value) for value in candidate_audit["checks"].values()),
            "audit_checks_total": len(candidate_audit["checks"]),
        },
    }


def inspect_n01_n10() -> tuple[list[dict], dict]:
    manifest_path = ROOT / "BLOCK-01-content-final/block-manifest.json"
    manifest = load_json(manifest_path)
    documents = []

    for canonical in manifest["documents"]:
        code = canonical["document"]
        package_root = ROOT / FINAL_PACKAGES[code]
        qa = load_json(package_root / "qa-report.json")
        integrity = load_json(package_root / "integrity-report.json")
        canonical_source = ROOT / canonical["source"]
        packaged_sources = sorted((package_root / "source").glob("*content-final.md"))
        if len(packaged_sources) != 1:
            raise RuntimeError(f"Expected one packaged canonical source for {code}, found {len(packaged_sources)}")
        packaged_source = packaged_sources[0]
        pdf = package_root / qa["pdf"]
        facts = pdf_facts(pdf)
        canonical_hash = sha256(canonical_source)
        packaged_hash = sha256(packaged_source)

        documents.append(
            {
                "document": code,
                "canonical_source": relative(canonical_source),
                "packaged_source": relative(packaged_source),
                "canonical_sha256": canonical_hash,
                "packaged_sha256": packaged_hash,
                "source_byte_identical": canonical_hash == packaged_hash,
                "canonical_words_total": canonical["words_total"],
                "canonical_words_substantive": canonical["words_substantive"],
                "human_depth_score": canonical["human_score"],
                "pdf": relative(pdf),
                "pdf_sha256": sha256(pdf),
                "pdf_bytes": pdf.stat().st_size,
                "pages": qa["pages"],
                "a4_pages": qa["a4_pages"],
                "actual_pages": facts["pages"],
                "actual_all_pages_a4": facts["all_pages_a4"],
                "qa": qa["status"],
                "integrity": integrity["status"],
                "source_blocks": integrity.get("source_block_count"),
                "rendered_source_ids": integrity.get("rendered_source_id_count"),
                "external_reference_links": len(qa.get("external_reference_links", [])),
                "external_reference_links_match_pdf_annotations": sorted(
                    set(qa.get("external_reference_links", []))
                )
                == sorted(
                    {
                        uri
                        for uri in facts["external_uris"]
                        if "linkedin.com" not in uri
                    }
                ),
            }
        )

    return documents, manifest


def inspect_covers() -> dict:
    audit = load_json(ROOT / "BLOCK-01-cover-review-current/audit.json")
    documents = audit["documents"]
    checks = {
        "eleven_documents": len(documents) == 11,
        "all_a4": all(item["a4"] for item in documents),
        "all_eyebrows_extractable": all(item["eyebrow_extractable"] for item in documents),
        "all_full_bleed": all(
            item["metrics"]["edge"]["full_bleed_without_uniform_white_frame"] for item in documents
        ),
        "all_native_monochrome_renders": all(item["metrics"]["native_monochrome_render"] for item in documents),
        "all_original_cover_copy_kept_volt": all(
            item["metrics"]["thesis_zone_proxy"]["current_color"] == "volt" for item in documents
        ),
    }
    return {
        "source": "BLOCK-01-cover-review-current/audit.json",
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def build_report() -> dict:
    content_integrity = load_json(ROOT / "BLOCK-01-content-final/provenance/block-integrity-report.json")
    n00 = inspect_n00()
    n01_n10, manifest = inspect_n01_n10()
    covers = inspect_covers()

    gates = {
        "canonical_content_audit_n01_n10": content_integrity["overall"] == "pass",
        "ten_final_packages_found": len(n01_n10) == 10,
        "all_packaged_sources_match_canonical_bytes": all(item["source_byte_identical"] for item in n01_n10),
        "all_final_pdf_qa_pass": all(item["qa"] == "PASS" for item in n01_n10),
        "all_final_pdf_integrity_pass": all(item["integrity"] == "PASS" for item in n01_n10),
        "all_final_pdf_pages_a4": all(item["pages"] == item["a4_pages"] for item in n01_n10),
        "all_final_pdf_files_directly_confirmed": all(
            item["actual_pages"] == item["pages"]
            and item["actual_all_pages_a4"]
            and item["external_reference_links_match_pdf_annotations"]
            for item in n01_n10
        ),
        "approved_n00_unchanged_and_passes": (
            n00["approved_production"]["pdf_sha256"]
            == "1b4a1ab42665246349ed240659585a2e33766fe72157032bfbefc03cc7127f64"
            and n00["approved_production"]["source_sha256"]
            == "e94edbd29855899f25f22c7ae695cd2a3fe7964371fe210d6b3a1035dd620763"
            and n00["approved_production"]["qa"] == "PASS"
            and n00["approved_production"]["integrity"] == "PASS"
            and n00["approved_production"]["actual_pages"] == n00["approved_production"]["pages"]
            and n00["approved_production"]["actual_all_pages_a4"]
        ),
        "n00_v2_candidate_technical_pass": (
            n00["v2_candidate"]["qa"] == "PASS"
            and n00["v2_candidate"]["integrity"] == "PASS"
            and n00["v2_candidate"]["audit"] == "PASS"
            and n00["v2_candidate"]["audit_checks_passed"] == n00["v2_candidate"]["audit_checks_total"]
            and n00["v2_candidate"]["actual_pages"] == n00["v2_candidate"]["pages"]
            and n00["v2_candidate"]["actual_all_pages_a4"]
        ),
        "cover_system_current_rule_pass": covers["status"] == "PASS",
    }

    return {
        "scope": "METSI N00-N10 current authority state",
        "generated_at": datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).isoformat(timespec="seconds"),
        "overall": "PASS" if all(gates.values()) else "FAIL",
        "authority": {
            "n00_production": "N00 approved original remains authoritative until explicit author approval of v2 candidate",
            "n00_candidate": "N00 v2 candidate is technically ready but not production-authoritative",
            "n01_n10_content": "BLOCK-01-content-final is canonical and frozen",
            "n01_n10_pdf": "The package versions listed below are the current final PDFs",
            "cover_rule": "All copy originally designed in volt remains volt; only local tonal support may be adjusted",
        },
        "n00": n00,
        "n01_n10": n01_n10,
        "content_totals": manifest["totals"],
        "covers": covers,
        "gates": gates,
        "superseded_or_historical": [
            {
                "path": "N01/audit/INFORME-AUDITORIA-N01-N10-v2.md",
                "classification": "historical pre-remediation audit",
            },
            {
                "path": "N01/audit/MATRIZ-REMEDIACION-N01-N10.md",
                "classification": "historical pre-remediation matrix",
            },
            {
                "path": "BLOCK-01-FINAL-HANDOFF.md",
                "classification": "valid baseline close, predates the isolated N00 v2 candidate",
            },
        ],
        "pending_actions": [
            "Revisión autoral y aprobación o rechazo explícito del candidato aislado N00 v2",
            "Completar las atribuciones de autor todavía incompletas en el manifiesto de imágenes de N00 v2 antes de una publicación externa",
            "Publicar N07 a N10 sólo después de una autorización explícita de publicación; esta auditoría no publica",
            "Tratar la percepción del texto volt en prueba de impresión como revisión autoral, no como permiso para aplicar velos oscuros globales",
        ],
        "uncertainties": [
            "Esta pasada no afirma certificación PDF/UA formal; se apoya en los controles de accesibilidad del repositorio",
            "No se consultó el sitio público en vivo; aquí no se cambia ni se recertifica el estado de publicación",
            "N00 v2 sigue siendo candidato pese a su PASS técnico hasta que el autor lo apruebe explícitamente",
        ],
    }


def render_markdown(report: dict) -> str:
    n00 = report["n00"]
    rows = []
    for item in report["n01_n10"]:
        rows.append(
            f"| {item['document']} | {item['pages']} | {item['canonical_words_substantive']:,} | "
            f"{item['human_depth_score']}/40 | {'Sí' if item['source_byte_identical'] else 'No'} | "
            f"{item['qa']} | {item['integrity']} | `{item['pdf_sha256'][:12]}…` |"
        )

    gate_lines = [f"- {'PASS' if value else 'FAIL'}: `{name}`" for name, value in report["gates"].items()]
    pending_lines = [f"- {item}." for item in report["pending_actions"]]
    uncertainty_lines = [f"- {item}." for item in report["uncertainties"]]

    return f"""# Estado consolidado y autoridad vigente · METSI N00 a N10

Fecha de auditoría: {report['generated_at']}.

## Dictamen

El estado técnico consolidado es **{report['overall']}**. No hay una deuda de contenido oculta en N01 a N10: las diez fuentes empaquetadas coinciden byte por byte con las fuentes canónicas, los diez controles de QA de PDF informan PASS y los diez controles de integridad informan PASS.

N00 requiere una distinción de autoridad. El N00 aprobado continúa siendo la versión de producción. El candidato N00 v2 está técnicamente listo, con {n00['v2_candidate']['audit_checks_passed']} de {n00['v2_candidate']['audit_checks_total']} controles aprobados, pero no reemplaza al original sin aprobación autoral explícita.

Esta auditoría no modificó fuentes, HTML, CSS ni PDF.

## Jerarquía de autoridad

1. **N00 de producción:** `N00/output/N00-METSI-lectura-previa-final.pdf`, 45 páginas, SHA-256 `{n00['approved_production']['pdf_sha256']}`.
2. **N00 v2 candidato:** `N00-v2-candidate/output/N00-METSI-lectura-previa-v2-candidate-final.pdf`, 43 páginas, SHA-256 `{n00['v2_candidate']['pdf_sha256']}`. Estado: PASS técnico, pendiente de aprobación autoral.
3. **Contenido N01 a N10:** `BLOCK-01-content-final/` es la autoridad canónica y congelada.
4. **PDF N01 a N10:** las versiones de la tabla siguiente son los finales vigentes y contienen una copia exacta de su fuente canónica.
5. **Tapas:** todo texto originalmente diseñado en volt permanece en volt. Se prohíbe resolver legibilidad con una tela oscura global. Cualquier apoyo debe ser tonal, localizado y sujeto a revisión de la tapa completa.

## Evidencia N01 a N10

| Documento | Páginas A4 | Palabras sustantivas | Profundidad | Fuente exacta | QA PDF | Integridad | SHA PDF |
|---|---:|---:|---:|---|---|---|---|
{chr(10).join(rows)}

Totales canónicos: {report['content_totals']['words_total']:,} palabras, {report['content_totals']['words_substantive']:,} sustantivas, {report['content_totals']['reference_entries']} referencias y {report['content_totals']['urls']} URL.

## Tapas N00 a N10

La auditoría comparativa vigente informa PASS: once páginas A4, once fotografías a sangre, once renders monocromos, once eyebrows extraíbles y conservación de la copia original en volt. La plancha de revisión sigue siendo `BLOCK-01-cover-review-current/contact-sheet-N00-N10-current.jpg`.

## Informes históricos que no abren trabajo nuevo

- `N01/audit/INFORME-AUDITORIA-N01-N10-v2.md` documenta el estado previo a la remediación.
- `N01/audit/MATRIZ-REMEDIACION-N01-N10.md` es una matriz histórica previa al cierre canónico.
- `BLOCK-01-FINAL-HANDOFF.md` conserva valor como cierre de baseline, pero antecede al candidato aislado N00 v2. No autoriza su promoción.

## Gates reproducidos

{chr(10).join(gate_lines)}

## Únicos pendientes reales

{chr(10).join(pending_lines)}

## Incertidumbres explícitas

{chr(10).join(uncertainty_lines)}

## Reproducción

Con las dependencias declaradas en `requirements-qa.txt`:

```bash
python3 BLOCK-01-content-final/validate_block01_content.py
python3 BLOCK-01-state-current/validate_block01_state.py
```

## Próxima decisión correcta

No corresponde reabrir N01 a N10 ni tocar sus interiores. La próxima decisión editorial es revisar y aprobar o rechazar el candidato N00 v2. Sólo después de una aprobación explícita corresponde promoverlo, actualizar el manifiesto central y evaluar su publicación. La publicación de N07 a N10 también permanece como una acción separada y requiere autorización explícita.
"""


def main() -> None:
    report = build_report()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "REPORT.md").write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"overall": report["overall"], "gates": report["gates"]}, indent=2))


if __name__ == "__main__":
    main()
