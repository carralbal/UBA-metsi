#!/usr/bin/env python3
"""Rebuild the N00 private proof with the original semantic assembler."""

from pathlib import Path
import json
import subprocess
from baseline import ensure_baseline

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "N00-post-cecilia-stage.pdf"
ASSEMBLER = HERE / "assemble_pdf_patched.py"
FINALIZER = ROOT.parent / "UBA-metsi-publication/output/source-recovery-20261020/private-assembly/scripts/vendor/finalize_and_qa.py"
PYTHON = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
PACKAGE = HERE / "proper-assembly-v4"


def main() -> None:
    baseline = ensure_baseline()
    for path in (SOURCE, baseline, ASSEMBLER, FINALIZER, PYTHON):
        if not path.is_file():
            raise FileNotFoundError(path)
    output = PACKAGE / "assembled"
    final = output / "N00-METSI-revision-privada.pdf"
    if final.exists():
        raise FileExistsError(final)
    stage = PACKAGE / "stage/N00"
    snapshot = PACKAGE / "snapshot"
    stage.mkdir(parents=True, exist_ok=True)
    snapshot.mkdir(parents=True, exist_ok=True)
    for link, target in ((stage / "interior-stage.pdf", SOURCE), (snapshot / "N00.pdf", baseline)):
        if link.is_symlink():
            if link.resolve() != target.resolve():
                raise ValueError(f"Unexpected symlink target: {link}")
        else:
            link.symlink_to(target)
    subprocess.run([str(PYTHON), str(ASSEMBLER), str(PACKAGE / "stage"), "00",
                    "--snapshot", str(snapshot), "--output", str(output),
                    "--finalizer", str(FINALIZER)], check=True)
    report = json.loads((output / "validation/N00-assembly.json").read_text())
    print(json.dumps({"status": report["status"], "pages": report["output_pages"],
                      "removed": report["removed_blank_source_pages"],
                      "navigation_errors": report["navigation"]["errors"]}))


if __name__ == "__main__":
    main()
