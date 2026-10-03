from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.constants import PageLabelStyle

root = Path(__file__).resolve().parent.parent
original = root / "N00-v3-final/output/N00-METSI-lectura-previa-v3-final.pdf"
insert = root / "N00-v4-recorrido/output/N00-recorrido-insert.pdf"
target = root / "N00-v4-recorrido/output/N00-METSI-lectura-previa-v4-recorrido.pdf"
source = PdfReader(original)
addition = PdfReader(insert)
if len(source.pages) != 44 or len(addition.pages) != 6:
    raise SystemExit(f"Conteo inesperado: original={len(source.pages)}, inserto={len(addition.pages)}")
writer = PdfWriter()
for page in source.pages[:12]:
    writer.add_page(page)
for page in addition.pages:
    writer.add_page(page)
for page in source.pages[12:]:
    writer.add_page(page)
writer.set_page_label(0, 11, style=PageLabelStyle.DECIMAL, start=1)
writer.set_page_label(12, 17, style=PageLabelStyle.UPPERCASE_LETTER, prefix="12", start=1)
writer.set_page_label(18, 49, style=PageLabelStyle.DECIMAL, start=13)
# La edición pública conserva la higiene del PDF v3: no incluye DocumentInfo.
writer._info = None
with target.open("wb") as handle:
    writer.write(handle)
print(target)
