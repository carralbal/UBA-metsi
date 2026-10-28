"""Normalize the p.3 paper background of the remaining canonical readings.

Each input is SHA-guarded and edited in place. The one inherited patterned
background fill is made non-painting; all text, links, page geometry, other
page streams and tagged structure are compared before replacement. No final
PDF clone is retained. Run one N at a time and perform visual/publication QA.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


ROOT = Path(__file__).resolve().parents[1]
BASELINES = {
    "N00": ("53ef97cb0f147b215aaf7c73639e7bde7d7c907720ac00be7e8a844803828336", 55, [0, 2524, 794, 1123]),
    "N01": ("53be797ea45234a654a29dbf445173cbbe23355a2a98948a6c72103cc28f6821", 36, [0, 2336, 794, 1123]),
    "N03": ("fd4606719825cdb63263753b9b4f298a24188577be4348ada95e54d529fd7ae8", 33, [0, 2336, 794, 1123]),
    "N04": ("0c8d87866705690a1110219dabb984b254ed9073f9eed02b48750b438a3bd4d9", 34, [0, 2336, 794, 1123]),
    "N05": ("ac485affa209f66176f92544d39b62646a4d33398fb79d629b8cd55b0a9139e2", 32, [0, 2336, 794, 1123]),
    "N06": ("32f4e9ed7b2e3f7b91d9aadee60c039e0731a682ec12ca714dd436307b91dee9", 34, [0, 2336, 794, 1123]),
    "N07": ("5b7aad77ef7b02e4d5bdd077e56fa90f756a433d808b5e5ccd4e150a3f84b4e6", 35, [0, 2336, 794, 1123]),
    "N08": ("b871223c07c181978b7dda29b23300db75bcd275de15ea157d815a640f0b9322", 34, [0, 2336, 794, 1123]),
    "N09": ("df01487035f846cbb2a03f88dc890de390c36b5db4c3664252a134b8f6c5c24a", 32, [0, 2336, 794, 1123]),
    "N10": ("fba101047ad61b65463db6fc5473ec7614765a733c0e701e0791adbabc508730", 37, [0, 2336, 794, 1123]),
    "N11": ("e2a8f5dc6ddcc59408831143d838f35cc689095df52c5fbbf2acca82c6292ab9", 47, [0, 2336, 794, 1123]),
    "N13": ("ce0fa8333fe7fe2749dd70e0671703f89a8e52678af3be8e0c640c67644f9888", 37, [0, 2336, 794, 1123]),
    "N18": ("9c47c87654d1b34d9a354884e22e51c768c16de7260118073c6392f522b47331", 38, [0, 2336, 794, 1145]),
    "N20": ("39ed5d0b3e1303445348255cbd2fde9e5f82626791d07914ad8cff66accb4bbb", 42, [0, 2246, 794, 1123]),
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def annotations(page) -> list[str]:
    return [str({str(k): v for k, v in item.get_object().items() if k != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_remaining_referentes_20261028.py Nxx")
    number = sys.argv[1]
    baseline, expected_pages, rect = BASELINES[number]
    manifest = json.loads((ROOT / "site/course-manifest.json").read_text())
    entry = next(item for item in manifest["readings"] if item["code"] == number)
    path = ROOT / "site" / urlsplit(entry["pdf"]).path
    if sha(path) != baseline:
        raise ValueError(f"Unexpected {number} input SHA")
    old = PdfReader(str(path))
    if len(old.pages) != expected_pages:
        raise ValueError("Unexpected page count")
    writer = PdfWriter(clone_from=str(path))
    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    paints = [i for i, (args, op) in enumerate(contents.operations)
              if op == b"scn" and len(args) == 1 and str(args[0]).startswith("/P")]
    if len(paints) != 1:
        raise ValueError(f"Unexpected background paints: {paints}")
    index = paints[0]
    if [contents.operations[index + n][1] for n in range(1, 5)] != [b"gs", b"BDC", b"re", b"f"]:
        raise ValueError("Unexpected background paint sequence")
    if [float(x) for x in contents.operations[index + 3][0]] != [float(x) for x in rect]:
        raise ValueError("Unexpected background rectangle")
    contents.operations[index + 4] = (contents.operations[index + 4][0], b"n")
    page.replace_contents(contents)

    transient = path.with_name(f".{path.name}.normalizing")
    if transient.exists():
        raise FileExistsError(transient)
    try:
        writer.write(str(transient))
        result = PdfReader(str(transient))
        if len(result.pages) != expected_pages or not result.trailer["/Root"].get("/StructTreeRoot"):
            raise AssertionError("Tagged structure or page count changed")
        for p in range(expected_pages):
            before, after = old.pages[p], result.pages[p]
            if before.extract_text() != after.extract_text():
                raise AssertionError(f"Text changed on p. {p + 1}")
            if annotations(before) != annotations(after) or before.mediabox != after.mediabox:
                raise AssertionError(f"Links or geometry changed on p. {p + 1}")
            if p != 2 and before.get_contents().get_data() != after.get_contents().get_data():
                raise AssertionError(f"Other page stream changed on p. {p + 1}")
        os.replace(transient, path)
    finally:
        transient.unlink(missing_ok=True)
    print(f"{number}: {expected_pages} pages, uniform paper; all text/links/geometry/tags preserved; SHA-256 {sha(path)}")


if __name__ == "__main__":
    main()
