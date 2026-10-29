"""Remove the redundant editorial echo from N28 p. 35, preserving the prompt.

The PDF is canonical; this is a narrowly guarded, reproducible PDF-level delta.
The faithful HTML source contains the phrase only once. The duplicate arose in
the assembled publication. Git preserves the prior PDF, so no backup copy is
kept on disk.
"""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path
from subprocess import check_output
from tempfile import NamedTemporaryFile

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


PDF = Path("site/pdf/publicados/N28-METSI-lectura-previa-v10-final.pdf")
EXPECTED_SHA = "4bd945eb9ccf76ec8c1f7bbf47d725e1b24791df0547a32dc74b98f1df979b3e"
BASE_COMMIT = "caf826a"
PROMPT = "Para el encuentro, elegí una aﬁrmación de calidad"
ECHO = "Cerrá con una decisión concreta: quépermitirías"


def main() -> None:
    base_pdf = check_output(["git", "show", f"{BASE_COMMIT}:{PDF.as_posix()}"])
    assert sha256(base_pdf).hexdigest() == EXPECTED_SHA, "Unexpected N28 baseline"
    original = PdfReader(BytesIO(base_pdf))
    assert len(original.pages) == 38
    assert original.trailer["/Root"].get("/StructTreeRoot")
    old_text = original.pages[34].extract_text()
    assert PROMPT in old_text and old_text.count("Cerrá con una decisión concreta") == 2
    assert ECHO in old_text

    writer = PdfWriter(clone_from=original)
    page = writer.pages[34]
    content = ContentStream(page.get_contents(), writer)
    operations = content.operations
    assert len(operations) == 2517, "Unexpected p. 35 content layout"
    assert operations[42][1] == b"BDC" and operations[51][1] == b"EMC"
    assert operations[43][1] == b"re" and operations[47][1] == b"re"
    assert operations[2280][1] == b"BT" and operations[2464][1] == b"ET"
    expected_baselines = (36583, 36614, 36646)
    actual_baselines = tuple(int(operations[i][0][5]) for i in (2282, 2357, 2442))
    assert actual_baselines == expected_baselines, actual_baselines

    # The two one-pixel rules and the three enlarged lines constitute the
    # non-semantic echo. The original prompt and its light panel are retained.
    # Keep the surrounding colour-state operations: they also paint the white
    # section number in its black circle. Only the two rules and quote text go.
    content.operations = [op for i, op in enumerate(operations)
                          if i not in (43, 44, 47, 48) and not 2280 <= i <= 2464]
    page.replace_contents(content)

    with NamedTemporaryFile(prefix="n28-editorial-", suffix=".pdf", dir=PDF.parent, delete=False) as f:
        temp = Path(f.name)
        writer.write(f)
    try:
        revised = PdfReader(temp)
        assert len(revised.pages) == len(original.pages)
        assert revised.trailer["/Root"].get("/StructTreeRoot")
        assert revised.pages[34].extract_text().count("Cerrá con una decisión concreta") == 1
        assert PROMPT in revised.pages[34].extract_text()
        assert ECHO not in revised.pages[34].extract_text()
        for i in range(len(original.pages)):
            assert list(revised.pages[i].mediabox) == list(original.pages[i].mediabox), i
            assert len(revised.pages[i].get("/Annots", [])) == len(original.pages[i].get("/Annots", [])), i
            if i != 34:
                assert revised.pages[i].extract_text() == original.pages[i].extract_text(), i
        temp.replace(PDF)
    finally:
        temp.unlink(missing_ok=True)
    print(f"N28 p. 35 corrected: {sha256(PDF.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
