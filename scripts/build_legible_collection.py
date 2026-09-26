#!/usr/bin/env python3
"""Reproducible, source-grounded map plates; never edits public PDFs."""
from pathlib import Path
import hashlib, html, json, re, shutil, textwrap
from contextlib import contextmanager
from legible_map_content import MAPS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'editorial-standard/approved-infographics/collection-legible-2026-09'
PACKAGES={1:'N01-v19-final',2:'N02-v16-final',3:'N03-v11-final',4:'N04-v10-final',10:'N10-v10-final',**{n:f'N{n:02d}-v11-final' for n in range(5,10)},**{n:f'N{n:02d}-v10-editorial' for n in range(11,37)}}
PAPER,INK,PALE,VOLT='#F7F6F2','#202020','#E5E6E0','#CFFF00'

def write_json(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class Plate:
    def __init__(self,n,data):
        self.n=n; self.title,self.sub,self.family,self.rows,self.endtitle,self.end=data
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1620" viewBox="0 0 1200 1620" role="img" aria-labelledby="title desc"><title id="title">{html.escape(self.title)}</title><desc id="desc">{html.escape(self.sub+" "+self.end)}</desc>', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#777A76"/></marker></defs>',f'<rect width="1200" height="1620" fill="{PAPER}"/>']
        self.labels=[]; self.nodes=[]; self.edges=[]
    @contextmanager
    def group(self,id,label,role='process'):
        self.nodes.append(dict(id=id,label=label,role=role,source=['original'],purpose=label))
        self.parts.append(f'<g id="{id}" aria-label="{html.escape(label,quote=True)}">'); yield; self.parts.append('</g>')
    def text(self,x,y,s,size=28,bold=False,serif=False):
        self.labels.append(s)
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{("Georgia,serif" if serif else "Arial,Helvetica,sans-serif")}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{INK}">{html.escape(s)}</text>')
    def wrap(self,x,y,s,width,size=28,bold=False,serif=False,leading=1.35):
        lines=textwrap.wrap(s,width=width,break_long_words=False,break_on_hyphens=False)
        for i,line in enumerate(lines): self.text(x,y+i*(size*leading),line,size,bold,serif)
        return y+len(lines)*size*leading
    def line(self,d,arrow=False,id=None):
        self.parts.append(f'<path'+(f' id="{id}"' if id else '')+f' d="{d}" fill="none" stroke="#92958F" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def relation(self,a,b,d,meaning):
        id=f'e-{a}-{b}'; self.line(d,True,id)
        self.edges.append(dict(id=id,**{'from':a,'to':b},relation='flow' if self.family in ('flow','loop','timeline') else 'dependency',source=['original'],meaning=meaning))
    def draw(self):
        with self.group('header',self.title,'annotation'):
            self.parts.append(f'<path d="M52 36 H126 L116 52 H42 Z" fill="{VOLT}"/>')
            with self.group('document-label',f'METSI · N{self.n:02d}', 'annotation'):
                self.text(154,53,f'METSI · N{self.n:02d} · MAPA DE DECISIÓN',24,True)
            yy=self.wrap(52,118,self.title,40,50,False,True)
            subtitle_end=self.wrap(52,max(205,yy+10),self.sub,75)
        rule=max(270,subtitle_end+8)
        self.line(f'M52 {rule} H1148')
        start,end=rule+32,1280
        step=(end-start)/len(self.rows)
        sequential=self.family in ('flow','loop','timeline')
        for i,(title,a,b) in enumerate(self.rows):
            y=start+i*step
            if self.family=='nested':
                offset=i*24
                self.parts.append(f'<path d="M{52+offset} {y} V{end+8} H1148" fill="none" stroke="#A5A79F" stroke-width="2"/>')
                tx=100+offset
            else: tx=145 if sequential else 78
            with self.group(f'item-{i}',title):
                self.parts[-1]=self.parts[-1].replace('>',f' data-row-bottom="{y+step-8}">')
                if not sequential and self.family!='nested': self.line(f'M52 {y} H1148')
                if sequential:
                    cy=y+42
                    self.parts.append(f'<circle cx="82" cy="{cy}" r="26" fill="{VOLT if i==0 else PAPER}" stroke="{INK}" stroke-width="2"/>')
                    self.text(66,cy+10,f'{i+1:02d}',28,True)
                if self.family in ('matrix','comparison','taxonomy','converge','branch'):
                    size=34 if len(self.rows)==3 else (30 if len(self.rows)==4 else 28)
                    self.wrap(tx,y+44,title,22,34,True)
                    yy=self.wrap(530,y+42,a,36 if size==34 else 40 if size==30 else 43,size,leading=1.18)
                    self.wrap(530,yy+6,b,36 if size==34 else 40 if size==30 else 43,size,leading=1.18)
                else:
                    self.wrap(tx,y+43,title,55,32,True)
                    yy=self.wrap(tx,y+87,a,66)
                    self.wrap(tx,yy+8,b,66)
            if sequential and i<len(self.rows)-1:
                self.relation(f'item-{i}',f'item-{i+1}',f'M82 {y+72} V{y+step+7}','La consecuencia o evidencia habilita el paso siguiente.')
        if not sequential:
            # A shared gate: these are concurrent conditions, not a fake chronology.
            with self.group('relation-key','Relaciones entre condiciones','annotation'):
                self.text(78,1324,'CONDICIONES QUE SE LEEN EN CONJUNTO',24,True)
            for i in range(len(self.rows)):
                # Connect the actual rows to a shared decision gate, in a gutter.
                y=start+(i+.5)*step
                self.relation(f'item-{i}','decision',f'M1148 {y} H1175 V1348 H1124 V1364','Esta condición contribuye al criterio conjunto de decisión.')
        elif self.family=='loop':
            self.relation(f'item-{len(self.rows)-1}','item-0',f'M1144 1235 H1170 V310 H1134','El efecto vuelve a modificar las condiciones iniciales.')
        with self.group('decision',self.endtitle,'decision'):
            self.parts.append(f'<rect x="52" y="1370" width="1096" height="200" fill="{PALE}"/><rect x="52" y="1370" width="7" height="200" fill="{VOLT}"/>')
            self.text(78,1418,self.endtitle,32,True)
            self.wrap(78,1465,self.end,72)
        # Supporting semantics are separately addressable for accessibility/QA.
        with self.group('reading-key','Lectura del mapa','annotation'):
            self.text(52,1606,'Las relaciones orientan la decisión; no reemplazan la explicación del texto.',24)
        self.parts.append('</svg>')

def original(n):
    pkg=ROOT/PACKAGES[n]
    h=(pkg/'index.html').read_text()
    src=re.search(r'<img[^>]+src="([^"]+\.svg)"',h)
    assert src,n
    return pkg/src[1]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    plans=[]
    for n,data in MAPS.items():
        folder=OUT/f'N{n:02d}'; folder.mkdir(exist_ok=True)
        src=original(n)
        p=Plate(n,data); p.draw()
        svg=folder/f'N{n:02d}-mapa-legible.svg'; svg.write_text('\n'.join(p.parts))
        manifest=dict(title=p.title,claim=p.sub,topology=p.family,source=str(src.relative_to(ROOT)),source_sha256=sha(src),source_sections=[dict(id='original',heading='Mapa de decisión canónico',summary='Relaciones del mapa original, contrastadas con la lectura canónica.')],nodes=p.nodes,edges=p.edges,visible_labels=p.labels,target_width_mm=173,minimum_content_font_pt=11.44,minimum_metadata_font_pt=9.81,status='AUTHORIZED_COLLECTION_REVISION',page_plan=dict(purpose='Mapa de decisión legible',layout='diagram-feature',source_ids=['original'],dominant_mass='Relaciones y explicación gráfica',secondary_mass='Criterio para decidir',reason_full_page='La cantidad de relaciones y el cuerpo mínimo de 11,44 pt requieren una lámina de consulta completa. Se elimina el gran titular externo duplicado.'))
        write_json(folder/'content-manifest.json',manifest)
        (folder/'alt-text.md').write_text(p.sub+' '+ ' '.join(' '.join(r) for r in p.rows)+' '+p.end+'\n')
        plans.append(dict(number=n,svg=str(svg.relative_to(ROOT)),package=PACKAGES[n]))
    for n in (24,25,26,27):
        source=ROOT/(f'pedagogy/readability-pilots/N25/mapa-legible' if n==25 else f'pedagogy/readability-pilots/mapas-tanda-02/N{n}')
        folder=OUT/f'N{n:02d}';folder.mkdir(exist_ok=True)
        for name in ('content-manifest.json','alt-text.md'):
            shutil.copy2(source/name,folder/name)
        svg=folder/f'N{n:02d}-mapa-legible.svg'
        shutil.copy2(source/f'N{n}-mapa-legible.svg',svg)
        manifest=json.loads((folder/'content-manifest.json').read_text());manifest['status']='USER_APPROVED';manifest['approval']='Aprobados. Continuar con los 36 y publicar.'
        write_json(folder/'content-manifest.json',manifest)
        plans.append(dict(number=n,svg=str(svg.relative_to(ROOT)),package=PACKAGES[n]))
    write_json(OUT/'plan.json',sorted(plans,key=lambda p:p['number']))
    print(f'{len(plans)} mapas; N06 y N34 no contienen un mapa SVG visible en la edición publicada.')

if __name__=='__main__':main()
