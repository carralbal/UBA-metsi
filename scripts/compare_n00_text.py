"""Compare N00's public PDF and regenerated candidate without touching either."""

from __future__ import annotations

import difflib
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "site/pdf/publicados/N00-METSI-lectura-previa-v4-recorrido.pdf"
STAGE = ROOT / "N00-post-cecilia-from-current-20261027/N00-post-cecilia-stage.pdf"


def clean(text: str) -> list[str]:
    text = re.sub(r"Diego Carralbal, 2026\s*·\s*linkedin\.com/in/carralbal", "", text)
    text = re.sub(r"\bMETSI\s*·\s*N00\b", "", text)
    return re.findall(r"[\wÁÉÍÓÚÜÑáéíóúüñ]+", text.lower())


public = clean(" ".join(page.extract_text() or "" for page in PdfReader(PUBLIC).pages))
stage = clean(" ".join(page.extract_text() or "" for page in PdfReader(STAGE).pages))
print("tokens", len(public), len(stage))
matcher = difflib.SequenceMatcher(None, public, stage, autojunk=False)
print("matching ratio", round(matcher.ratio(), 4))
for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == "equal" or max(i2 - i1, j2 - j1) < 18:
        continue
    print("\n", tag, "public", i1, i2, "stage", j1, j2)
    print("BEFORE", " ".join(public[max(0, i1 - 15):i1]))
    print("PUBLIC", " ".join(public[i1:min(i2, i1 + 120)]))
    print("STAGE ", " ".join(stage[j1:min(j2, j1 + 120)]))
    print("AFTER ", " ".join(public[i2:i2 + 15]))
