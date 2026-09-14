#!/usr/bin/env python3
"""Reconstruye N01–N36 con las tesis desarrolladas según N00."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGES={1:"N01-v18-final",2:"N02-v15-final",3:"N03-v10-final",4:"N04-v9-final",5:"N05-v10-final",6:"N06-v10-final",7:"N07-v10-final",8:"N08-v10-final",9:"N09-v10-final",10:"N10-v9-final"}
VERSIONS={1:"v18-final",2:"v15-final",3:"v10-final",4:"v9-final",5:"v10-final",6:"v10-final",7:"v10-final",8:"v10-final",9:"v10-final",10:"v9-final"}

def build_first_block(start:int,end:int)->None:
    sys.path.insert(0,str(ROOT))
    import build_collection as b
    for n,name in PACKAGES.items():
        if not start <= n <= end:
            continue
        package=ROOT/name
        record=json.loads((package/"source-manifest.json").read_text(encoding="utf-8"))
        master=ROOT/f"N{n:02d}-content-final"/"source"/Path(record["source"]).name
        b.SOURCE_PATH_OVERRIDES[n]=master
        b.OUTPUT_ROOT_OVERRIDES[n]=package
        b.PACKAGE_VERSION_LABELS[n]=VERSIONS[n]
        manifest=b.build_document(n)
        print(f"BUILT N{n:02d} {manifest['source_words']} words")

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--start",type=int,default=1)
    parser.add_argument("--end",type=int,default=36)
    args=parser.parse_args()
    if args.start < 1 or args.end > 36 or args.start > args.end:
        raise ValueError("El generador cubre N01–N36")
    build_first_block(args.start,args.end)
    import build_block_c_editorial as c
    for n in range(max(11,args.start),args.end+1):
        manifest=c.build(n)
        print(f"BUILT N{n:02d} {manifest['source_words']} words")

if __name__=="__main__": main()
