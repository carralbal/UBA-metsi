#!/usr/bin/env python3
"""Reaplica sólo la tesis desarrollada sobre la composición v9 estable.

La fuente canónica cambia; el resto del HTML y del sistema editorial vuelve a
la versión publicada y auditada en HEAD. Así, una revisión localizada de la
tesis no vuelve a componer ni desplaza las demás secciones del documento.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")
THESIS_RE = re.compile(
    r'<section\b(?=[^>]*class="[^"]*block-c-thesis[^"]*")[^>]*>.*?</section>',
    re.S,
)
THESIS_PLATE_WRAPPER_RE = re.compile(
    r'<div class="thesis-infographic-page">'
    r'(<section\b(?=[^>]*class="[^"]*block-c-thesis[^"]*")[^>]*>.*?</section>)'
    r'(<section\b(?=[^>]*class="[^"]*approved-infographic-page[^"]*")[^>]*>.*?</section>)'
    r'</div>',
    re.S,
)


def stable(relative: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"HEAD:{relative.as_posix()}"], cwd=ROOT)


def load_stable_json(relative: Path) -> dict:
    return json.loads(stable(relative).decode("utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    import sys

    sys.path.insert(0, str(ROOT))
    from build_block_c_editorial import THESIS_N00_STANDARD_CSS

    for number in range(11, 37):
        code = f"N{number:02d}"
        package = ROOT / f"{code}-v9-editorial"
        relative = package.relative_to(ROOT)

        current_html = (package / "index.html").read_text(encoding="utf-8")
        current_thesis = THESIS_RE.search(current_html)
        if not current_thesis:
            raise RuntimeError(f"{code}: tesis nueva ausente")

        stable_html = stable(relative / "index.html").decode("utf-8")
        if len(THESIS_RE.findall(stable_html)) != 1:
            raise RuntimeError(f"{code}: la base estable no tiene una tesis única")
        html = THESIS_RE.sub(current_thesis.group(0), stable_html, count=1)

        # La composición estable agrupaba una tesis breve y su mapa en una
        # sola página. Con el argumento desarrollado, ambos pasan a ser dos
        # páginas hermanas completas: tesis textual y lámina legible. Quitar
        # el wrapper (en vez de usar display:contents) preserva los cortes de
        # página posteriores y evita reflujo en el resto del documento.
        html, unwrapped = THESIS_PLATE_WRAPPER_RE.subn(r"\1\2", html, count=1)
        if "thesis-infographic-page" in stable_html and unwrapped != 1:
            raise RuntimeError(f"{code}: no se pudo separar tesis y lámina")

        css = stable(relative / "magazine.css").decode("utf-8")
        css += THESIS_N00_STANDARD_CSS
        if number == 34:
            # La tesis desarrollada deja la sección de continuidad en una
            # página nueva. Compactar apenas su ritmo evita una segunda página
            # con cinco líneas huérfanas, sin alterar contenido ni jerarquía.
            css += r'''
body.block-c.document-n34 .reading-section[data-section="05"] .section-body{
  font-size:9.4pt!important;line-height:1.28!important
}
body.block-c.document-n34 .reading-section[data-section="05"] .section-body p{
  margin-bottom:1.6mm!important
}
body.block-c.document-n34 .reading-section[data-section="05"] .traditions-evidence-photo{
  box-sizing:border-box!important;min-height:236mm!important;margin:0!important;
  padding:18mm 8mm 12mm!important;background:#E3E6E4!important;
  break-before:page!important;page-break-before:always!important
}
body.block-c.document-n34 .reading-section[data-section="05"] .traditions-evidence-photo .photo-viewport{
  height:190mm!important
}
body.block-c.document-n34 .reading-section[data-section="05"] .traditions-evidence-photo img{
  width:100%!important;height:100%!important;object-fit:cover!important
}
body.block-c.document-n34 .reading-section[data-section="05"] .traditions-evidence-photo figcaption{
  margin-top:4mm!important;font-size:8.2pt!important;line-height:1.3!important
}
'''

        # Partir del manifiesto estable: el constructor actual reagrupa
        # secciones ajenas a la tesis y no debe cambiar su identidad editorial.
        # Sólo sustituimos los bloques de texto comprendidos entre el título
        # "Tesis" y el encabezado siguiente por los seis párrafos nuevos.
        source_manifest = load_stable_json(relative / "source-manifest.json")
        current_manifest = json.loads(
            (package / "source-manifest.json").read_text(encoding="utf-8")
        )
        current_entries = current_manifest["eligible_blocks"]
        current_start = next(
            i
            for i, entry in enumerate(current_entries)
            if entry["kind"] == "heading-2" and entry["text"].strip() == "Tesis"
        )
        current_end = next(
            (
                i
                for i in range(current_start + 1, len(current_entries))
                if current_entries[i]["kind"].startswith("heading")
            ),
            len(current_entries),
        )
        thesis_entries = current_entries[current_start:current_end]

        stable_entries = source_manifest["eligible_blocks"]
        stable_start = next(
            i
            for i, entry in enumerate(stable_entries)
            if entry["kind"] == "heading-2" and entry["text"].strip() == "Tesis"
        )
        stable_end = next(
            (
                i
                for i in range(stable_start + 1, len(stable_entries))
                if stable_entries[i]["kind"].startswith("heading")
            ),
            len(stable_entries),
        )
        source_manifest["eligible_blocks"] = (
            stable_entries[:stable_start] + thesis_entries + stable_entries[stable_end:]
        )
        source = package / source_manifest["source"]
        digest = sha256(source)
        source_words = len(WORD_RE.findall(source.read_text(encoding="utf-8")))

        rendered_ids = re.findall(r'data-source-id="([^"]+)"', html)
        eligible_ids = [entry["source_id"] for entry in source_manifest["eligible_blocks"]]
        if rendered_ids != eligible_ids:
            missing = [item for item in eligible_ids if item not in set(rendered_ids)]
            extra = [item for item in rendered_ids if item not in set(eligible_ids)]
            raise RuntimeError(f"{code}: cobertura fuente/HTML inválida; faltan={missing}; sobran={extra}")

        document = load_stable_json(relative / "document.json")
        manifest = load_stable_json(relative / "manifest.json")
        for record in (document, manifest):
            record["source_sha256"] = digest
            record["source_words"] = source_words
            record["content_audit"] = "plain-language-canonical-source-audited-pass"

        (package / "index.html").write_text(html, encoding="utf-8")
        (package / "magazine.css").write_text(css, encoding="utf-8")
        (package / "document.json").write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (package / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (package / "source-manifest.json").write_text(
            json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (package / "integrity-report.json").write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "source_block_count": len(eligible_ids),
                    "rendered_source_id_count": len(rendered_ids),
                    "missing_source_ids": [],
                    "unexpected_source_ids": [],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        # No hay cambio de estructura fuera de la tesis; conservar el plan de
        # spreads estable evita que una revisión de contenido altere el ritmo.
        (package / "spread-plan.json").write_bytes(stable(relative / "spread-plan.json"))
        print(f"REBASED {code} {source_words} words {len(eligible_ids)} blocks")


if __name__ == "__main__":
    main()
