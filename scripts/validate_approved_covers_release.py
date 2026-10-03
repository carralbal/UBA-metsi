#!/usr/bin/env python3
"""Validate the 37 approved PDFs, their active previews, and public navigation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,hashlib,json,re,sys
from pypdf import PdfReader
REPO=Path(__file__).resolve().parents[1]
SITE=REPO/'site'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.resources=[];self.ids=set();self.pdf_links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.add(a['id'])
  for key in ['href','src']:
   if a.get(key):self.resources.append(a[key])
  if tag=='a' and a.get('href') and '.pdf' in a['href']:self.pdf_links.append(a['href'])
def validate(manifest):
 release=json.loads(manifest.read_text());root=json.loads((REPO/'course-manifest.json').read_text());site=json.loads((SITE/'course-manifest.json').read_text());errors=[];documents=[]
 records=release['documents'];expected={f'N{n:02d}' for n in range(37)}
 if len(records)!=37 or {x['code'] for x in records}!=expected:errors.append('Release does not cover exactly N00–N36')
 roots={x['code']:x for x in root['documents']};sites={x['code']:x for x in site['readings']}
 if set(sites)!=expected:errors.append('Public manifest document set differs')
 for d in records:
  code=d['code'];p=REPO/d['public_pdf'];checks={};checks['pdf_exists']=p.is_file()
  if p.is_file():
   checks['pdf_sha256_exact']=sha(p)==d['sha256'];checks['bytes_exact']=p.stat().st_size==d['bytes'];reader=PdfReader(p);checks['page_count_exact']=len(reader.pages)==d['pages'];checks['pdf_is_complete']=len(reader.pages)>1
  checks['root_manifest_matches']=all(roots.get(code,{}).get(k)==d[k] for k in ['pages','bytes','sha256','public_pdf'])
  row=sites.get(code,{});checks['public_manifest_matches']=row.get('pages')==d['pages'] and 'site/'+urlsplit(row.get('pdf','')).path==d['public_pdf'] and row.get('title')==d['title']
  previews=d['previews'];checks['thumbnail_present']=any(x['path']==f'site/covers/thumbs/{code}.webp' for x in previews)
  checks['preview_hashes_exact']=all((REPO/x['path']).is_file() and sha(REPO/x['path'])==x['sha256'] for x in previews)
  failed=[k for k,v in checks.items() if not v]
  if failed:errors.append(code+': '+', '.join(failed))
  documents.append({'code':code,'checks':checks,'status':'PASS' if not failed else 'FAIL'})
 parser=Links();html=(SITE/'index.html').read_text();parser.feed(html);local=0
 for ref in parser.resources:
  u=urlsplit(ref)
  if u.scheme or u.netloc or ref.startswith('//'):continue
  if not u.path:
   if u.fragment and unquote(u.fragment) not in parser.ids:errors.append('Missing fragment '+ref)
   continue
  local+=1;p=(SITE/unquote(u.path)).resolve()
  if not p.is_relative_to(SITE.resolve()):errors.append('Reference escapes site '+ref)
  elif not (p.is_file() or (p.is_dir() and (p/'index.html').is_file())):errors.append('Missing local reference '+ref)
 publicpaths={d['public_pdf'].removeprefix('site/'):d for d in records}
 linked=set()
 for ref in parser.pdf_links:
  u=urlsplit(ref);p=u.path
  if p not in publicpaths:continue
  d=publicpaths[p];linked.add(d['code']);fragment=re.fullmatch(r'page=(\d+)',u.fragment)
  if fragment and not 1<=int(fragment[1])<=d['pages']:errors.append('Out-of-range PDF page '+ref)
 if linked!=expected:errors.append('Homepage PDF links do not cover37 approved documents')
 for match in re.finditer(r'''(?:["'])(pdf/[^"']+\.pdf(?:\?[^"'#]*)?#page=(\d+))(?:["'])''',(SITE/'covers/atlas-data.js').read_text()):
  u=urlsplit(match[1]);d=publicpaths.get(u.path)
  if d is None or not 1<=int(match[2])<=d['pages']:errors.append('Invalid atlas PDF page '+match[1])
 for mapping in release.get('page_anchor_updates',[]):
  text=(REPO/mapping['source_file']).read_text()
  if mapping['href'] not in text:errors.append('Missing reviewed page anchor '+mapping['href'])
 return {'status':'PASS' if not errors else 'FAIL','documents_checked':len(documents),'pdf_links_cover_37':linked==expected,'active_preview_count':sum(len(x['previews']) for x in records),'local_references_checked':local,'documents':documents,'errors':errors,'limits':['This verifies release bytes and navigation. Structural interior preservation and visual cover comparison are recorded in the release evidence; this is not a fresh academic audit.']}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=REPO/'audits/approved-covers-release-20261003.json');ap.add_argument('--output',type=Path);a=ap.parse_args();report=validate(a.manifest);text=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
 if a.output:a.output.write_text(text)
 print(json.dumps({'status':report['status'],'documents':report['documents_checked'],'preview_count':report['active_preview_count'],'local_references':report['local_references_checked'],'errors':report['errors']},ensure_ascii=False));return int(report['status']!='PASS')
if __name__=='__main__':sys.exit(main())
