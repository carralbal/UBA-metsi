#!/usr/bin/env python3
"""Exporta y finaliza N01–N36 luego de la revisión de tesis."""
from __future__ import annotations
import os, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import export_pdfs
import finalize_and_qa
import finalize_block_c_pdfs

PACKAGES={1:("N01-v18-final","v18"),2:("N02-v15-final","v15"),3:("N03-v10-final","v10"),4:("N04-v9-final","v9"),5:("N05-v10-final","v10"),6:("N06-v10-final","v10"),7:("N07-v10-final","v10"),8:("N08-v10-final","v10"),9:("N09-v10-final","v10"),10:("N10-v9-final","v9")}

def main()->None:
    finalize_and_qa.register_fonts()
    for n in range(1,37):
        code=f"N{n:02d}"
        if n<=10:
            package,version=PACKAGES[n]
            os.environ[f"METSI_PACKAGE_ROOT_{code}"]=str(ROOT/package)
            os.environ[f"METSI_PDF_VERSION_{code}"]=version
        export_pdfs.export(n)
        if n<=10:
            finalize_and_qa.finalize(n)
        else:
            finalize_block_c_pdfs.finalize(n)

if __name__=="__main__": main()
