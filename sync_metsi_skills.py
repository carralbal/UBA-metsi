#!/usr/bin/env python3
"""Sincroniza y verifica los seis skills METSI desde su copia versionada."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parent
SNAPSHOT = REPO / "editorial-standard"
ACTIVE = Path.home() / ".codex" / "skills"
STATE = SNAPSHOT / "SKILLS-SYNC-STATE.json"
SKILLS = (
    "metsi-build-infographics",
    "metsi-build-reference-grade-infographics",
    "metsi-compose-document",
    "metsi-find-images",
    "metsi-generate-courseware",
    "metsi-publish-course",
)
IGNORED_PARTS = {"__pycache__", ".DS_Store"}
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files(root: Path) -> dict[Path, Path]:
    return {
        path.relative_to(root): path
        for path in sorted(root.rglob("*"))
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
    }


def lfs_contract(path: Path) -> tuple[str, int] | None:
    payload = path.read_bytes()
    if not payload.startswith(LFS_HEADER):
        return None
    text = payload.decode("ascii")
    oid = re.search(r"^oid sha256:([0-9a-f]{64})$", text, re.MULTILINE)
    size = re.search(r"^size ([0-9]+)$", text, re.MULTILINE)
    if not oid or not size:
        raise RuntimeError(f"Puntero LFS inválido: {path}")
    return oid.group(1), int(size.group(1))


def synchronize(apply: bool) -> dict[str, object]:
    reports: list[dict[str, object]] = []
    failures: list[str] = []
    for name in SKILLS:
        source_root = SNAPSHOT / name
        active_root = ACTIVE / name
        source_files = files(source_root)
        active_files = files(active_root) if active_root.is_dir() else {}
        copied = 0
        validated_lfs = 0
        for relative, source in source_files.items():
            target = active_root / relative
            contract = lfs_contract(source)
            if contract:
                expected_hash, expected_size = contract
                if not target.is_file() or target.stat().st_size != expected_size or sha256(target) != expected_hash:
                    failures.append(f"{name}/{relative}: el activo no coincide con el objeto LFS versionado")
                else:
                    validated_lfs += 1
                continue
            if apply and (not target.is_file() or source.read_bytes() != target.read_bytes()):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                copied += 1
            if not target.is_file() or source.read_bytes() != target.read_bytes():
                failures.append(f"{name}/{relative}: copia activa desincronizada")
        extras = sorted(set(active_files) - set(source_files))
        if extras:
            failures.extend(f"{name}/{relative}: archivo activo sin respaldo" for relative in extras)
        reports.append(
            {
                "skill": name,
                "files": len(source_files),
                "copied": copied,
                "lfs_objects_validated": validated_lfs,
                "status": "PASS" if not any(item.startswith(f"{name}/") for item in failures) else "FAIL",
            }
        )
    result = {
        "schema": "metsi-skills-sync/v1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if apply else "check",
        "status": "PASS" if not failures else "FAIL",
        "skills": reports,
        "failures": failures,
    }
    if apply:
        STATE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actualiza las copias activas antes de verificarlas.")
    args = parser.parse_args()
    report = synchronize(args.apply)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
