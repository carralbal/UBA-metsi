#!/usr/bin/env python3
"""Prepare versioned source overlays. Approved package assets remain immutable."""
from pathlib import Path
import html,json,re,shutil,hashlib
from build_legible_collection import ROOT,OUT,PACKAGES,write_json,sha
RELEASE=ROOT/'pedagogy/readability-pilots/collection-map-release-2026-09'

def main():
    RELEASE.mkdir(parents=True,exist_ok=True)
    readings=json.loads((ROOT/'site/course-manifest.json').read_text())['readings']
    plan=[]
    for r in readings:
        n=int(r['code'][1:])
        if not n:continue
        folder=RELEASE/r['code'];folder.mkdir(exist_ok=True)
        public=r['pdf'].split('?',1)[0]
        original=ROOT/'site'/public;archive=folder/'previous.pdf'
        if not archive.exists():shutil.copy2(original,archive)
        entry=dict(number=n,code=r['code'],public=public,baseline=str(archive.relative_to(ROOT)),baseline_sha256=sha(archive),output=str((folder/'reading.pdf').relative_to(ROOT)))
        if n in (6,34):entry['mode']='audited-preserved'
        elif n==25:entry.update(mode='approved-full-document',source='N25-v12-editorial/output/N25-METSI-lectura-previa-v12.pdf')
        elif n>=11:entry.update(mode='replace-map-page',plate=str((OUT/r['code']/'plate.pdf').relative_to(ROOT)))
        else:
            entry['mode']='html-reflow'
            pkg=ROOT/PACKAGES[n]; original_html=(pkg/'index.html').read_text()
            figures=list(re.finditer(r'<figure\b[^>]*>.*?</figure>',original_html,re.S))
            matches=[m for m in figures if re.search(r'<img[^>]+src="[^"]+\.svg"',m[0])]
            assert len(matches)==1,(n,len(matches))
            match=matches[0];mapfolder=OUT/r['code'];alt=(mapfolder/'alt-text.md').read_text().strip()
            svg='../'+str((mapfolder/f'{r["code"]}-mapa-legible.svg').relative_to(ROOT))
            figure=f'<figure class="legible-map-release" role="img" aria-label="{html.escape(alt,quote=True)}"><img src="{svg}" alt="{html.escape(alt,quote=True)}"></figure>'
            # Place the full-page figure before its section, so its heading stays
            # attached to the argument rather than stranded on the preceding page.
            openings=list(re.finditer(r'<section\b[^>]*class="[^"]*reading-section[^\"]*"[^>]*>',original_html[:match.start()]))
            assert openings,n
            insert=openings[-1].start()
            result=original_html[:insert]+figure+original_html[insert:match.start()]+original_html[match.end():]
            if n==1:
                # Introduce the distinctions before their full-page map, keeping
                # the heading with prose and the later photograph with its text.
                result=original_html[:match.start()]+original_html[match.end():]
                intro=re.search(r'<p\b[^>]*data-source-id="N01-s07-b003"[^>]*>.*?</p>',result,re.S)
                assert intro
                result=result[:intro.end()]+figure+result[intro.end():]
            result=result.replace('<head>',f'<head><base href="../../../../{PACKAGES[n]}/">',1)
            style='''<style id="map-release-layout">
            @media print {
            body.premium-magazine .legible-map-release{display:block!important;box-sizing:border-box!important;position:static!important;float:none!important;column-span:all!important;clear:both!important;width:100%!important;max-width:173mm!important;height:234mm!important;max-height:none!important;margin:0 auto!important;padding:0!important;border:0!important;background:#F7F6F2!important;break-before:page!important;break-after:page!important;break-inside:avoid!important;page-break-before:always!important;page-break-after:always!important;overflow:visible!important;}
            body.premium-magazine .legible-map-release>img{display:block!important;width:100%!important;height:233.55mm!important;max-height:none!important;max-width:none!important;object-fit:contain!important;margin:0!important;padding:0!important;}
            }
            @media screen {.legible-map-release{column-span:all;width:100%;margin:24px 0}.legible-map-release>img{display:block;width:100%;height:auto}}
            </style>'''
            result=result.replace('</head>',style+'</head>',1)
            # Compare every eligible source node before and after this overlay.
            blocks=lambda s:re.findall(r'<([a-z][\w-]*)\b[^>]*data-source-id="([^"]+)"[^>]*>(.*?)</\1>',s,re.S)
            assert blocks(original_html)==blocks(result),n
            (folder/'index.html').write_text(result)
            write_json(folder/'integrity.json',dict(source_package=PACKAGES[n],source_blocks=len(blocks(result)),normalized_text_equal=True,eligible_word_delta=0,changed_only='Decision-map figure and its scoped layout rules'))
            entry['html']=str((folder/'index.html').relative_to(ROOT))
        plan.append(entry)
    write_json(RELEASE/'release-plan.json',plan)
    print(RELEASE)
if __name__=='__main__':main()
