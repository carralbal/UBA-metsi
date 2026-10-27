#!/usr/bin/env python3
"""Create the public-worded N12 HTML from the traceable private source.

This prepares a candidate only. It does not replace the public PDF.
"""

from pathlib import Path
from io import BytesIO
import re

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "N12-post-cecilia-20261027/index.html"
OUTPUT = ROOT / "N12-post-cecilia-20261027/index-release-v2.html"
PUBLIC = ROOT / "site/pdf/publicados/N12-METSI-lectura-previa-v10-final.pdf"


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    text = SOURCE.read_text(encoding="utf-8")
    ids = re.findall(r'data-source-id="([^"]+)"', text)
    additions = [source_id for source_id in ids if source_id.startswith("N12-add-uc-")]
    if len(ids) != 358 or len(set(ids)) != 358 or len(additions) != 15:
        raise ValueError("N12 source manifest is not the reviewed 343 + 15 blocks")
    if text.count("PRUEBA PRIVADA · 1/2") != 1 or text.count("PRUEBA PRIVADA · 2/2") != 1:
        raise ValueError("Unexpected trial labels")
    text = text.replace("PRUEBA PRIVADA · 1/2", "CASO DE USO · 1/2")
    text = text.replace("PRUEBA PRIVADA · 2/2", "ACEPTACIÓN · 2/2")
    text = text.replace('data-private-trial="true"', 'data-revision="post-cecilia-20261027"')
    if text.count('href="../corrections.css"') != 1:
        raise ValueError("Unexpected N12 shared stylesheet reference")
    text = text.replace('href="../corrections.css"', 'href="corrections.css"')
    # Reuse the exact monochrome images already published in N12. No new
    # desaturation or invented photograph is introduced by this release.
    pdf = PdfReader(PUBLIC)
    monochrome = (
        (6, 0, "hotel-horizonte-canonical.png", "hotel-horizonte-approved-mono.jpg"),
        (16, 0, "registro-minimalista-r3.png", "registro-minimalista-approved-mono.jpg"),
        (19, -1, "pause-02.png", "pause-02-approved-mono.jpg"),
    )
    for page, image_index, old_name, new_name in monochrome:
        if text.count(f"assets/{old_name}") != 1:
            raise ValueError(f"Unexpected reference count: {old_name}")
        embedded = pdf.pages[page].images[image_index]
        with Image.open(BytesIO(embedded.data)) as picture:
            if picture.mode != "L":
                raise ValueError(f"Public asset is not monochrome: {embedded.name}")
        target = OUTPUT.parent / "assets" / new_name
        if target.exists():
            raise FileExistsError(target)
        target.write_bytes(embedded.data)
        text = text.replace(f"assets/{old_name}", f"assets/{new_name}")
    if "PRUEBA PRIVADA" in text:
        raise ValueError("A private-trial label remains")
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Prepared {OUTPUT}; {len(ids)} unique source blocks, including {len(additions)} additions")


if __name__ == "__main__":
    main()
