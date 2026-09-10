#!/usr/bin/env python3
"""Build the approved Block 01 completion editions without mutating baselines."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
PDF_PYTHON = Path(
    os.environ.get(
        "METSI_PDF_PYTHON",
        "/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    )
)

RELEASES = {
    0: ("N00-v2-candidate", "N00-v3-final", "v3", "N00-v2-candidate/source/N00_como_leer_metsi.md"),
    2: ("N02-v14-final", "N02-v15-final", "v15", "N02-content-final/source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final-v2.md"),
    3: ("N03-v9-final", "N03-v10-final", "v10", "N03-content-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final-v2.md"),
    5: ("N05-v9-final", "N05-v10-final", "v10", "N05-content-final/source/N05_actores_afectados_poder_y_perspectivas-content-final-v2.md"),
    6: ("N06-v9-final", "N06-v10-final", "v10", "N06-content-final/source/N06_discovery_como_reduccion_de_incertidumbre-content-final-v2.md"),
    7: ("N07-v9-final", "N07-v10-final", "v10", "N07-content-final/source/N07_entrevistar_no_es_pedir_requisitos-content-final.md"),
    8: ("N08-v9-final", "N08-v10-final", "v10", "N08-content-final/source/N08_observar_el_trabajo_invisible-content-final-v2.md"),
    9: ("N09-v9-final", "N09-v10-final", "v10", "N09-content-final/source/N09_experiencia_accesibilidad_y_adopcion-content-final-v2.md"),
}

INFOGRAPHICS = {
    number: HERE / "editorial-standard" / "infographic-rebuild-candidates-v2" / f"N{number:02d}"
    for number in (0, 7, 8, 9)
}


def prepare_packages(resume: bool) -> None:
    for _, (baseline_name, target_name, _, _) in RELEASES.items():
        baseline = HERE / baseline_name
        target = HERE / target_name
        if target.exists() and not resume:
            raise FileExistsError(f"Ya existe {target}; usar --resume para reconstruirlo")
        shutil.copytree(baseline, target, dirs_exist_ok=True)
        output = target / "output"
        output.mkdir(parents=True, exist_ok=True)
        for pdf in output.glob("*.pdf"):
            pdf.unlink()


def build_html() -> list[dict]:
    sys.path.insert(0, str(HERE))
    import build_collection as builder

    builder.SOURCE_PATH_OVERRIDES.update(
        {number: HERE / values[3] for number, values in RELEASES.items()}
    )
    builder.OUTPUT_ROOT_OVERRIDES.update(
        {number: HERE / values[1] for number, values in RELEASES.items()}
    )
    builder.PACKAGE_VERSION_LABELS.update(
        {number: f"{values[2]}-final" for number, values in RELEASES.items()}
    )
    builder.INFOGRAPHIC_PATH_OVERRIDES.update(INFOGRAPHICS)
    builder.N00_ROOT = HERE / RELEASES[0][1]
    return [builder.build_document(number) for number in RELEASES]


def export_and_finalize() -> None:
    for number, (_, target_name, version, _) in RELEASES.items():
        code = f"N{number:02d}"
        env = dict(os.environ)
        env[f"METSI_PACKAGE_ROOT_{code}"] = str(HERE / target_name)
        env[f"METSI_PDF_VERSION_{code}"] = version
        subprocess.run(
            [str(PDF_PYTHON), str(HERE / "export_pdfs.py"), str(number)],
            cwd=HERE,
            env=env,
            check=True,
        )
        subprocess.run(
            [str(PDF_PYTHON), str(HERE / "finalize_and_qa.py"), str(number)],
            cwd=HERE,
            env=env,
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--html-only", action="store_true")
    args = parser.parse_args()
    prepare_packages(args.resume)
    manifests = build_html()
    if not args.html_only:
        export_and_finalize()
    report = {
        "status": "PASS",
        "documents": [f"N{number:02d}" for number in RELEASES],
        "packages": [values[1] for values in RELEASES.values()],
        "sources": [values[3] for values in RELEASES.values()],
        "infographics": [f"N{number:02d}" for number in INFOGRAPHICS],
        "manifest_count": len(manifests),
    }
    (HERE / "qa-reports" / "block01-completion-build.json").parent.mkdir(parents=True, exist_ok=True)
    (HERE / "qa-reports" / "block01-completion-build.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
