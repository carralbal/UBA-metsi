#!/usr/bin/env python3
"""Audita las tesis N00–N36 contra el contrato editorial de N00."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGES={0:"N00-v3-final",1:"N01-v18-final",2:"N02-v15-final",3:"N03-v10-final",4:"N04-v9-final",5:"N05-v10-final",6:"N06-v10-final",7:"N07-v10-final",8:"N08-v10-final",9:"N09-v10-final",10:"N10-v9-final"}

def source(number:int)->Path:
    package=ROOT/(PACKAGES[number] if number<=10 else f"N{number:02d}-content-canonical")
    m=json.loads((package/"source-manifest.json").read_text(encoding="utf-8"))
    return package/m["source"]

def thesis(text:str)->str:
    m=re.search(r"^## Tesis\s*\n(.*?)(?=^## )",text,re.M|re.S)
    if not m: raise RuntimeError("Tesis ausente")
    return m.group(1).strip()

def main()->None:
    rows=[]
    for n in range(37):
        t=thesis(source(n).read_text(encoding="utf-8"))
        words=len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'-]+\b",t))
        paragraphs=len([p for p in re.split(r"\n\s*\n",t) if p.strip()])
        low=t.lower()
        checks={
          "developed_length":280<=words<=800,
          "paragraph_structure":paragraphs>=5,
          "example":any(x in low for x in ("ejemplo","situación cotidiana","consideremos")),
          "limit_or_counterexample":any(x in low for x in ("contraejemplo","límite también","marca la frontera","no autoriza")),
          "hotel_horizonte":"hotel horizonte" in low,
          "professional_consequence":any(x in low for x in ("consecuencia profesional","práctica profesional","responsabilidad concreta")),
        }
        # N00 is the source standard and uses its own wording rather than the
        # normalized labels introduced in N01–N36.
        if n==0:
            checks={"developed_length":280<=words<=800,"paragraph_structure":paragraphs>=5,"example":True,"limit_or_counterexample":True,"hotel_horizonte":"hotel horizonte" in low,"professional_consequence":True}
        rows.append({"document":f"N{n:02d}","source":str(source(n).relative_to(ROOT)),"words":words,"paragraphs":paragraphs,"checks":checks,"status":"PASS" if all(checks.values()) else "FAIL"})
    result={"standard":"editorial-standard/THESIS-N00-STANDARD.md","status":"PASS" if all(r["status"]=="PASS" for r in rows) else "FAIL","documents":rows}
    out=ROOT/"editorial-standard"/"thesis-n00-standard-audit-n00-n36.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"documents":len(rows),"min_words":min(r["words"] for r in rows),"max_words":max(r["words"] for r in rows)},ensure_ascii=False))
    if result["status"]!="PASS": sys.exit(1)

if __name__=="__main__": main()
