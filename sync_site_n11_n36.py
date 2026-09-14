#!/usr/bin/env python3
"""Stage and, only with --apply, publish rebuilt N11-N36 into ``site``.

The public ``v1-final`` filenames are stable compatibility routes. Their bytes
come from the current v9 editorial packages. The default invocation is a dry
run: it performs every source/gate/staging check but does not mutate ``site`` or
either course manifest. The apply phase is guarded against concurrent changes
and rolls back every replaced file if the final site validator fails.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import html as html_lib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from pypdf import PdfReader


REPO = Path(__file__).resolve().parent
SITE = REPO / "site"
FIRST = 11
LAST = 36
COVER_DPI = 120
SOURCE_VERSION = "v9-editorial"
SOURCE_VERSION_SHORT = "v9"
VALIDATOR_VERSION = 9
PUBLIC_ROUTE_CONTRACT = "stable-v1-filename"
ACADEMIC_REVISION_MANIFEST = REPO / "academic-content-revision-manifest-n11-n36.json"


class PublicationError(RuntimeError):
    """Fail-closed error with an actionable message."""


def code_for(number: int) -> str:
    return f"N{number:02d}"


def source_pdf_relative(number: int) -> Path:
    code = code_for(number)
    return Path(f"{code}-{SOURCE_VERSION}/output/{code}-METSI-lectura-previa-{SOURCE_VERSION_SHORT}-final.pdf")


def public_pdf_relative(number: int) -> Path:
    code = code_for(number)
    return Path(f"site/pdf/publicados/{code}-METSI-lectura-previa-v1-final.pdf")


def cover_relative(number: int) -> Path:
    return Path(f"site/covers/{code_for(number)}.jpg")


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


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        raise PublicationError(f"No se pudo leer {path.relative_to(REPO)}: {error}") from error
    if not isinstance(value, dict):
        raise PublicationError(f"{path.relative_to(REPO)} no contiene un objeto JSON")
    return value


def rendered_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def one_canonical_source(number: int) -> Path:
    manifest = load_json(ACADEMIC_REVISION_MANIFEST)
    documents = manifest.get("documents")
    if not isinstance(documents, list):
        raise PublicationError("El manifiesto académico no contiene documents")
    code = code_for(number)
    matches = [item for item in documents if isinstance(item, dict) and item.get("code") == code]
    if len(matches) != 1:
        raise PublicationError(f"El manifiesto académico debe declarar exactamente una fuente para {code}")
    relative = matches[0].get("source")
    expected_hash = matches[0].get("sha256")
    if not isinstance(relative, str) or not relative or not isinstance(expected_hash, str):
        raise PublicationError(f"La entrada académica de {code} está incompleta")
    source = confined_repo_path(relative, REPO / relative)
    if not source.is_file() or source.is_symlink():
        raise PublicationError(f"La fuente académica de {code} no es un archivo regular")
    actual_hash = sha256(source)
    if actual_hash != expected_hash:
        raise PublicationError(
            f"La fuente académica de {code} cambió: manifiesto={expected_hash}, archivo={actual_hash}"
        )
    return source


def lean_package_fingerprint(number: int) -> dict[Path, str]:
    code = code_for(number)
    package = REPO / f"{code}-{SOURCE_VERSION}"
    files: set[Path] = set()
    for candidate in package.iterdir():
        if candidate.is_file() and candidate.suffix.casefold() in {".json", ".html", ".css", ".md"}:
            files.add(candidate)
    for folder_name in ("assets", "diagrams", "source"):
        folder = package / folder_name
        files.update(candidate for candidate in folder.rglob("*") if candidate.is_file())
    files.add(REPO / source_pdf_relative(number))
    if any(path.is_symlink() for path in files):
        raise PublicationError(f"{code}: el paquete lean contiene enlaces simbólicos")
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise PublicationError(f"{code}: faltan entradas del paquete lean: {missing}")
    return {path: sha256(path) for path in sorted(files)}


def confined_repo_path(relative: str, expected: Path) -> Path:
    candidate = (REPO / relative).resolve()
    try:
        candidate.relative_to(REPO.resolve())
    except ValueError as error:
        raise PublicationError(f"Ruta fuera del repositorio: {relative}") from error
    if candidate != expected.resolve():
        raise PublicationError(
            f"Ruta de paquete inesperada: {relative}; se esperaba {expected.relative_to(REPO)}"
        )
    return candidate


def collect_package_inputs() -> tuple[list[dict[str, Any]], dict[Path, str]]:
    """Reject stale packages before running the expensive exhaustive PDF gate."""
    partial: list[dict[str, Any]] = []
    fingerprints: dict[Path, str] = {}
    stale: list[str] = []
    for number in range(FIRST, LAST + 1):
        code = code_for(number)
        package = REPO / f"{code}-{SOURCE_VERSION}"
        document_path = package / "document.json"
        integrity_path = package / "integrity-report.json"
        source_pdf = REPO / source_pdf_relative(number)
        canonical = one_canonical_source(number)
        for required in (document_path, integrity_path, source_pdf, canonical):
            if not required.is_file() or required.is_symlink():
                raise PublicationError(f"Falta un archivo regular requerido: {required.relative_to(REPO)}")

        document = load_json(document_path)
        integrity = load_json(integrity_path)
        if document.get("number") != number:
            stale.append(f"{code}: document.json declara number={document.get('number')!r}")
        if not str(document.get("title", "")).strip():
            stale.append(f"{code}: document.json no declara un título")
        elif not str(document["title"]).startswith(f"{code} · "):
            stale.append(f"{code}: document.json tiene un título sin identidad canónica '{code} ·'")
        declared_source = document.get("source")
        if not isinstance(declared_source, str) or not declared_source:
            stale.append(f"{code}: document.json no declara source")
            package_source = package / "__missing__"
        else:
            package_source = confined_repo_path(
                f"{code}-{SOURCE_VERSION}/{declared_source}",
                package / "source" / canonical.name,
            )
        if not package_source.is_file() or package_source.is_symlink():
            stale.append(f"{code}: falta la copia de fuente dentro del paquete")
            package_source_hash = None
        else:
            package_source_hash = sha256(package_source)

        canonical_hash = sha256(canonical)
        declared_hash = document.get("source_sha256")
        if package_source_hash != canonical_hash or declared_hash != canonical_hash:
            stale.append(
                f"{code}: fuente {SOURCE_VERSION_SHORT} desincronizada "
                f"(canónica={canonical_hash}, paquete={package_source_hash}, document.json={declared_hash})"
            )
        if integrity.get("status") != "PASS" or integrity.get("missing_source_ids") or integrity.get("unexpected_source_ids"):
            stale.append(f"{code}: integrity-report.json no está en PASS limpio")

        try:
            reader = PdfReader(str(source_pdf))
            pages = len(reader.pages)
        except Exception as error:
            raise PublicationError(f"PDF final inválido en {source_pdf.relative_to(REPO)}: {error}") from error
        if pages <= 0:
            raise PublicationError(f"PDF final sin páginas: {source_pdf.relative_to(REPO)}")
        pdf_hash = sha256(source_pdf)
        package_fingerprint = lean_package_fingerprint(number)
        partial.append(
            {
                "number": number,
                "code": code,
                "title": str(document.get("title", "")).strip(),
                "canonical_source": canonical.relative_to(REPO).as_posix(),
                "canonical_sha256": canonical_hash,
                "package_source": package_source.relative_to(REPO).as_posix(),
                "package_source_sha256": package_source_hash,
                "package_sha256": json_digest(
                    {path.relative_to(package).as_posix(): digest for path, digest in package_fingerprint.items()}
                ),
                "package_files": len(package_fingerprint),
                "source_pdf": source_pdf_relative(number).as_posix(),
                "public_pdf": public_pdf_relative(number).relative_to("site").as_posix(),
                "cover": cover_relative(number).relative_to("site").as_posix(),
                "pages": pages,
                "bytes": source_pdf.stat().st_size,
                "sha256": pdf_hash,
            }
        )
        for path in (document_path, integrity_path, source_pdf, canonical, package_source):
            if path.is_file():
                fingerprints[path] = sha256(path)
        fingerprints.update(package_fingerprint)

    if stale:
        detail = "\n  - ".join(stale)
        raise PublicationError(
            f"Los paquetes {SOURCE_VERSION_SHORT} no corresponden a las fuentes canónicas vigentes. "
            "Hay que reconstruir antes de publicar:\n  - " + detail
        )
    return partial, fingerprints


def run_exhaustive_gate() -> dict[str, dict[str, Any]]:
    validator = REPO / "validate_n11_n36_v6.py"
    if not validator.is_file():
        raise PublicationError("Falta validate_n11_n36_v6.py")
    process = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--start",
            str(FIRST),
            "--end",
            str(LAST),
            "--version",
            str(VALIDATOR_VERSION),
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    reports: dict[str, dict[str, Any]] = {}
    malformed: list[str] = []
    for line_number, line in enumerate(process.stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            report = json.loads(line)
        except json.JSONDecodeError:
            malformed.append(f"línea {line_number}")
            continue
        if isinstance(report, dict) and report.get("document"):
            reports[str(report["document"])] = report
    expected = {code_for(number) for number in range(FIRST, LAST + 1)}
    failures = {
        code: reports.get(code, {}).get("failed_checks") or reports.get(code, {}).get("error") or reports.get(code, {}).get("status")
        for code in sorted(expected)
        if reports.get(code, {}).get("status") != "PASS"
    }
    if process.returncode != 0 or set(reports) != expected or failures or malformed:
        stderr = process.stderr.strip()[-2000:]
        raise PublicationError(
            "El gate exhaustivo N11-N36 no pasó. "
            f"returncode={process.returncode}; faltantes={sorted(expected - set(reports))}; "
            f"extras={sorted(set(reports) - expected)}; fallas={failures}; JSON_inválido={malformed}; "
            f"stderr={stderr!r}"
        )
    return reports


def merge_gate(partial: list[dict[str, Any]], reports: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    validator_hash = sha256(REPO / "validate_n11_n36_v6.py")
    for item in partial:
        code = item["code"]
        report = reports[code]
        metrics = report.get("metrics", {})
        if not isinstance(metrics, dict):
            raise PublicationError(f"{code}: el gate no emitió metrics")
        mismatches = []
        for field, expected in (("pages", item["pages"]), ("pdf_bytes", item["bytes"]), ("pdf_sha256", item["sha256"])):
            if metrics.get(field) != expected:
                mismatches.append(f"{field}={metrics.get(field)!r}, esperado={expected!r}")
        if mismatches:
            raise PublicationError(f"{code}: gate y PDF final no coinciden: {', '.join(mismatches)}")
        record = dict(item)
        record.pop("number", None)
        record.update(
            {
                "qa_validator": str(report.get("validator", "")),
                "qa_validator_sha256": validator_hash,
                "qa_report": f"qa-reports/n11-n36-v9/{code}-validation-v9.json",
                "qa_status": str(report.get("status", "")),
                "qa_checks": int(report.get("total_checks", 0)),
                "qa_report_sha256": hashlib.sha256(rendered_json(report).encode("utf-8")).hexdigest(),
            }
        )
        records.append(record)
    return records


def render_cover(source: Path, target: Path, pdftoppm: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    prefix = target.with_suffix("")
    environment = dict(os.environ)
    environment.update({"LC_ALL": "C", "TZ": "UTC"})
    process = subprocess.run(
        [
            pdftoppm,
            "-f",
            "1",
            "-l",
            "1",
            "-singlefile",
            "-jpeg",
            "-r",
            str(COVER_DPI),
            "-jpegopt",
            "quality=90,progressive=n,optimize=y",
            str(source),
            str(prefix),
        ],
        cwd=REPO,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0 or not target.is_file():
        raise PublicationError(
            f"No se pudo renderizar {target.name}: returncode={process.returncode}; "
            f"stderr={process.stderr.decode('utf-8', errors='replace')[-1000:]!r}"
        )
    payload = target.read_bytes()
    if len(payload) < 10_000 or not payload.startswith(b"\xff\xd8") or not payload.endswith(b"\xff\xd9"):
        raise PublicationError(f"La tapa renderizada no parece un JPEG completo: {target.name}")


def renderer_identity(pdftoppm: str) -> str:
    process = subprocess.run(
        [pdftoppm, "-v"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = (process.stdout + "\n" + process.stderr).strip().splitlines()
    if process.returncode != 0 or not output:
        raise PublicationError("No se pudo identificar la versión de pdftoppm")
    return output[0].strip()


def update_index(original: str, records: list[dict[str, Any]]) -> str:
    updated = original
    for record in records:
        code = record["code"]
        pattern = re.compile(rf"(<p>{code}\s*·\s*)\d+(\s+páginas</p>)")
        updated, substitutions = pattern.subn(rf"\g<1>{record['pages']}\g<2>", updated)
        if substitutions != 1:
            raise PublicationError(f"site/index.html: se esperaba una etiqueta de páginas para {code}; hay {substitutions}")
        display_title = str(record["title"]).removeprefix(f"{code} · ")
        title_pattern = re.compile(rf"(<p>{code}\s*·\s*{record['pages']}\s+páginas</p><h3>).*?(</h3>)")
        updated, title_substitutions = title_pattern.subn(
            rf"\g<1>{html_lib.escape(display_title)}\g<2>", updated
        )
        if title_substitutions != 1:
            raise PublicationError(f"site/index.html: se esperaba un título de biblioteca para {code}; hay {title_substitutions}")
        route = record["public_pdf"]
        if updated.count(f'href="{route}"') != 3:
            raise PublicationError(f"site/index.html: {code} no tiene exactamente tres enlaces a {route}")
        if updated.count(f'src="{record["cover"]}"') != 1:
            raise PublicationError(f"site/index.html: {code} no tiene exactamente una tapa {record['cover']}")
    return updated


def update_manifests(records: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], str]:
    root_manifest = load_json(REPO / "course-manifest.json")
    site_manifest = load_json(SITE / "course-manifest.json")
    release = publication_digest(records)
    contract = {
        "range": "N11-N36",
        "source_version": SOURCE_VERSION,
        "public_route_contract": PUBLIC_ROUTE_CONTRACT,
        "release_sha256": release,
    }

    documents = root_manifest.get("documents")
    if not isinstance(documents, list):
        raise PublicationError("course-manifest.json: documents no es una lista")
    preserved = [item for item in documents if not (isinstance(item, dict) and item.get("code") in {record["code"] for record in records})]
    locked_before = [item for item in documents if isinstance(item, dict) and item.get("code") in {f"N{n:02d}" for n in range(0, 11)}]
    locked_after = [item for item in preserved if isinstance(item, dict) and item.get("code") in {f"N{n:02d}" for n in range(0, 11)}]
    if locked_before != locked_after or len(locked_after) != 11:
        raise PublicationError("La actualización intentaría alterar el contrato N00-N10")
    additions = []
    for record in records:
        additions.append(
            {
                "code": record["code"],
                "status": "closed",
                "pdf": record["source_pdf"],
                "tag": f"{record['code'].casefold()}-{SOURCE_VERSION}-final",
                "public_pdf": f"site/{record['public_pdf']}",
                "cover": f"site/{record['cover']}",
                "pages": record["pages"],
                "bytes": record["bytes"],
                "sha256": record["sha256"],
                "cover_sha256": record["cover_sha256"],
                "canonical_source": record["canonical_source"],
                "canonical_sha256": record["canonical_sha256"],
                "package_sha256": record["package_sha256"],
                "package_files": record["package_files"],
                "qa_report": record["qa_report"],
                "qa_report_sha256": record["qa_report_sha256"],
                "qa_validator": record["qa_validator"],
                "qa_validator_sha256": record["qa_validator_sha256"],
                "source_version": SOURCE_VERSION,
            }
        )
    root_manifest["documents"] = sorted(preserved + additions, key=lambda item: str(item.get("code", "")) if isinstance(item, dict) else "")
    root_manifest["site_publication"] = contract

    published = site_manifest.get("published_readings")
    if published is None:
        readings = site_manifest.get("readings")
        if isinstance(readings, list):
            published = [
                item.get("code")
                for item in readings
                if isinstance(item, dict)
            ]
    expected_published = [f"N{number:02d}" for number in range(0, LAST + 1)]
    if published != expected_published:
        raise PublicationError("site/course-manifest.json no enumera exactamente N00-N36")
    readings = site_manifest.get("readings")
    if isinstance(readings, list):
        public_by_code = {
            str(item.get("code")): item
            for item in readings
            if isinstance(item, dict) and item.get("code")
        }
        for record in records:
            public = public_by_code.get(record["code"])
            if public is None:
                raise PublicationError(f"site/course-manifest.json no contiene {record['code']}")
            public["pages"] = record["pages"]
            public["pdf"] = record["public_pdf"]
    # El manifiesto público sólo conserva datos académicos y rutas de descarga.
    # La procedencia técnica, los hashes y los informes QA quedan en el manifiesto
    # interno de la raíz del repositorio.
    site_manifest.pop("publication", None)
    return root_manifest, site_manifest, release


class CandidateParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.references: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.references.append(values[attribute])
        if values.get("srcset"):
            self.references.extend(
                candidate.strip().split()[0]
                for candidate in values["srcset"].split(",")
                if candidate.strip()
            )


def validate_staged_links(index: str, candidates: dict[Path, Path]) -> int:
    parser = CandidateParser()
    parser.feed(index)
    css = (SITE / "metsi.css").read_text(encoding="utf-8")
    parser.references.extend(match.strip(" \t\"'") for match in re.findall(r"url\(([^)]+)\)", css))
    problems: list[str] = []
    checked = 0
    site_root = SITE.resolve()
    for reference in parser.references:
        parsed = urlparse(reference)
        if parsed.scheme or parsed.netloc or reference.startswith("//"):
            continue
        checked += 1
        if not parsed.path:
            if parsed.fragment and unquote(parsed.fragment) not in parser.ids:
                problems.append(f"{reference}: fragmento inexistente")
            continue
        relative = Path("site") / unquote(parsed.path)
        resolved = (REPO / relative).resolve()
        try:
            resolved.relative_to(site_root)
        except ValueError:
            problems.append(f"{reference}: escapa site/")
            continue
        effective = candidates.get(relative, resolved)
        if not effective.is_file():
            problems.append(f"{reference}: archivo inexistente")
    if problems:
        raise PublicationError("Enlaces locales inválidos en el índice candidato:\n  - " + "\n  - ".join(problems))
    return checked


def snapshot(paths: list[Path]) -> dict[Path, tuple[bool, str | None]]:
    result: dict[Path, tuple[bool, str | None]] = {}
    for path in paths:
        if path.is_symlink():
            raise PublicationError(f"No se permiten destinos simbólicos: {path.relative_to(REPO)}")
        result[path] = (path.is_file(), sha256(path) if path.is_file() else None)
    return result


def assert_snapshot(expected: dict[Path, tuple[bool, str | None]], label: str) -> None:
    actual = snapshot(list(expected))
    changed = [path.relative_to(REPO).as_posix() for path in expected if actual[path] != expected[path]]
    if changed:
        raise PublicationError(f"Cambio concurrente en {label}: {changed}")


def protected_n00_n10_paths() -> list[Path]:
    pdf_names = {
        0: "N00-METSI-lectura-previa-v3-final.pdf",
        1: "N01-METSI-lectura-previa-v18-final.pdf",
        2: "N02-METSI-lectura-previa-v15-final.pdf",
        3: "N03-METSI-lectura-previa-v10-final.pdf",
        4: "N04-METSI-lectura-previa-v9-final.pdf",
        5: "N05-METSI-lectura-previa-v10-final.pdf",
        6: "N06-METSI-lectura-previa-v10-final.pdf",
        7: "N07-METSI-lectura-previa-v10-final.pdf",
        8: "N08-METSI-lectura-previa-v10-final.pdf",
        9: "N09-METSI-lectura-previa-v10-final.pdf",
        10: "N10-METSI-lectura-previa-v9-final.pdf",
    }
    return [SITE / "pdf" / pdf_names[number] for number in range(0, 11)] + [SITE / "covers" / f"N{number:02d}.png" for number in range(0, 11)]


def verify_protected_approval() -> None:
    approval = load_json(REPO / "BLOCK-01-integrated-release-current" / "approval.json")
    cover_audit = load_json(REPO / "BLOCK-01-cover-review-current" / "audit.json")
    approved_pdfs = approval.get("pdf_sha256", {})
    cover_hashes = {
        item.get("code"): item.get("metrics", {}).get("sha256")
        for item in cover_audit.get("documents", [])
        if isinstance(item, dict) and isinstance(item.get("metrics"), dict)
    }
    paths = protected_n00_n10_paths()
    for number, path in enumerate(paths[:11]):
        code = code_for(number)
        if not path.is_file() or sha256(path) != approved_pdfs.get(code):
            raise PublicationError(f"El PDF protegido {code} no coincide con approval.json")
    for number, path in enumerate(paths[11:]):
        code = code_for(number)
        if not path.is_file() or sha256(path) != cover_hashes.get(code):
            raise PublicationError(f"La tapa protegida {code} no coincide con el audit aprobado")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered_json(value), encoding="utf-8")


def run_site_validator() -> dict[str, Any]:
    validator = SITE / "validate_site.py"
    process = subprocess.run(
        [sys.executable, str(validator), "--check-only", "--require-sources"],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise PublicationError(
            f"El validador del sitio no emitió JSON válido; stderr={process.stderr[-2000:]!r}"
        ) from error
    if process.returncode != 0 or report.get("status") != "PASS":
        failed = [key for key, passed in report.get("checks", {}).items() if not passed]
        raise PublicationError(
            f"El sitio candidato no pasó la validación final: returncode={process.returncode}, checks={failed}"
        )
    return report


def transactional_apply(candidates: dict[Path, Path], target_baseline: dict[Path, tuple[bool, str | None]], protected_baseline: dict[Path, tuple[bool, str | None]], stage: Path) -> dict[str, Any]:
    lock_name = hashlib.sha256(str(REPO.resolve()).encode("utf-8")).hexdigest()[:16]
    lock_path = Path(tempfile.gettempdir()) / f"metsi-site-sync-{lock_name}.lock"
    lock_stream = lock_path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise PublicationError("Ya hay otra sincronización del sitio en curso") from error
        assert_snapshot(target_baseline, "los destinos de publicación")
        assert_snapshot(protected_baseline, "N00-N10")
        backup_root = stage / "backup"
        changed: list[Path] = []
        try:
            for relative, candidate in candidates.items():
                target = REPO / relative
                if target.is_file() and sha256(target) == sha256(candidate):
                    continue
                backup = backup_root / relative
                if target.is_file():
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(target, backup)
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(candidate, target)
                changed.append(relative)

            report = run_site_validator()
            audit_relative = Path("site/audit.json")
            audit_target = REPO / audit_relative
            assert_snapshot({audit_target: target_baseline[audit_target]}, "site/audit.json")
            audit_backup = backup_root / audit_relative
            if audit_target.is_file():
                audit_backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit_target, audit_backup)
            audit_candidate = stage / "final-audit.json"
            write_json(audit_candidate, report)
            if not audit_target.is_file() or sha256(audit_target) != sha256(audit_candidate):
                os.replace(audit_candidate, audit_target)
                changed.append(audit_relative)
            assert_snapshot(protected_baseline, "N00-N10 después de aplicar")
            return report
        except Exception:
            for relative in reversed(changed):
                target = REPO / relative
                backup = backup_root / relative
                if backup.is_file():
                    os.replace(backup, target)
                elif target.exists():
                    target.unlink()
            raise
    finally:
        try:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)
        finally:
            lock_stream.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Replace the staged N11-N36 site assets and manifests. Without it, no repository file is changed.",
    )
    parser.add_argument(
        "--expect-release-sha256",
        metavar="SHA256",
        help="Required with --apply; must equal the release SHA printed by a prior dry-run.",
    )
    args = parser.parse_args()
    if args.apply and not args.expect_release_sha256:
        parser.error("--apply requiere --expect-release-sha256 obtenido de un dry-run")
    if args.expect_release_sha256 and not re.fullmatch(r"[0-9a-f]{64}", args.expect_release_sha256):
        parser.error("--expect-release-sha256 debe ser un SHA256 hexadecimal en minúsculas")
    return args


def main() -> int:
    args = parse_args()
    try:
        verify_protected_approval()
        partial, input_fingerprints = collect_package_inputs()
        input_fingerprints[REPO / "validate_n11_n36_v6.py"] = sha256(REPO / "validate_n11_n36_v6.py")
        reports = run_exhaustive_gate()
        assert_snapshot(
            {path: (True, digest) for path, digest in input_fingerprints.items()},
            "los paquetes durante el gate exhaustivo",
        )
        records = merge_gate(partial, reports)
        pdftoppm = shutil.which("pdftoppm")
        if not pdftoppm:
            raise PublicationError("pdftoppm (Poppler) es obligatorio para regenerar las tapas")
        renderer = renderer_identity(pdftoppm)

        protected_paths = protected_n00_n10_paths()
        protected_baseline = snapshot(protected_paths)
        target_relatives = [public_pdf_relative(n) for n in range(FIRST, LAST + 1)]
        target_relatives += [cover_relative(n) for n in range(FIRST, LAST + 1)]
        target_relatives += [Path(f"qa-reports/n11-n36-v9/{code_for(n)}-validation-v9.json") for n in range(FIRST, LAST + 1)]
        target_relatives += [Path("site/index.html"), Path("site/course-manifest.json"), Path("course-manifest.json"), Path("site/audit.json")]
        target_baseline = snapshot([REPO / relative for relative in target_relatives])

        with tempfile.TemporaryDirectory(prefix=".metsi-site-sync-", dir=REPO) as temporary:
            stage = Path(temporary)
            candidates: dict[Path, Path] = {}
            for record in records:
                number = int(record["code"][1:])
                source = REPO / record["source_pdf"]
                public_relative = public_pdf_relative(number)
                public_candidate = stage / public_relative
                public_candidate.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, public_candidate)
                if sha256(public_candidate) != record["sha256"]:
                    raise PublicationError(f"La copia staged de {record['code']} cambió bytes")
                candidates[public_relative] = public_candidate

                cover_rel = cover_relative(number)
                cover_candidate = stage / cover_rel
                render_cover(source, cover_candidate, pdftoppm)
                record["cover_sha256"] = sha256(cover_candidate)
                record["cover_renderer"] = renderer
                record["cover_dpi"] = COVER_DPI
                candidates[cover_rel] = cover_candidate

                qa_relative = Path(record["qa_report"])
                qa_candidate = stage / qa_relative
                write_json(qa_candidate, reports[record["code"]])
                if sha256(qa_candidate) != record["qa_report_sha256"]:
                    raise PublicationError(f"El informe QA staged de {record['code']} cambió bytes")
                candidates[qa_relative] = qa_candidate

            index_candidate_text = update_index((SITE / "index.html").read_text(encoding="utf-8"), records)
            root_manifest, site_manifest, release = update_manifests(records)
            if args.expect_release_sha256 and args.expect_release_sha256 != release:
                raise PublicationError(
                    f"El release cambió desde el dry-run: esperado={args.expect_release_sha256}, actual={release}"
                )
            index_relative = Path("site/index.html")
            site_manifest_relative = Path("site/course-manifest.json")
            root_manifest_relative = Path("course-manifest.json")
            index_candidate = stage / index_relative
            index_candidate.parent.mkdir(parents=True, exist_ok=True)
            index_candidate.write_text(index_candidate_text, encoding="utf-8")
            candidates[index_relative] = index_candidate
            site_manifest_candidate = stage / site_manifest_relative
            root_manifest_candidate = stage / root_manifest_relative
            write_json(site_manifest_candidate, site_manifest)
            write_json(root_manifest_candidate, root_manifest)
            candidates[site_manifest_relative] = site_manifest_candidate
            candidates[root_manifest_relative] = root_manifest_candidate

            links_checked = validate_staged_links(index_candidate_text, candidates)
            assert_snapshot({path: (True, digest) for path, digest in input_fingerprints.items()}, "las entradas reconstruidas")

            summary: dict[str, Any] = {
                "mode": "apply" if args.apply else "dry-run",
                "status": "READY",
                "range": "N11-N36",
                "source_version": SOURCE_VERSION,
                "public_route_contract": PUBLIC_ROUTE_CONTRACT,
                "release_sha256": release,
                "documents": [
                    {
                        "code": record["code"],
                        "pages": record["pages"],
                        "bytes": record["bytes"],
                        "sha256": record["sha256"],
                        "cover_sha256": record["cover_sha256"],
                        "qa_checks": record["qa_checks"],
                    }
                    for record in records
                ],
                "local_references_checked": links_checked,
                "protected_n00_n10_files": len(protected_paths),
            }
            if args.apply:
                report = transactional_apply(candidates, target_baseline, protected_baseline, stage)
                summary["status"] = "PASS"
                summary["site_checks"] = report.get("checks", {})
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0
    except PublicationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
