#!/usr/bin/env python3
"""Assemble reviewed vector plates while keeping all other published pages intact."""
from pathlib import Path
import json,shutil,re,hashlib
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject as N, NumberObject, TextStringObject, ArrayObject, DictionaryObject, ContentStream, DecodedStreamObject
from build_legible_collection import ROOT,OUT,write_json,sha
RELEASE=ROOT/'pedagogy/readability-pilots/collection-map-release-2026-09'

def replace_plate(writer,index,plate,alt):
    dest=writer.pages[index]; original_page=dest.indirect_reference
    src=PdfReader(plate).pages[0]
    content=ContentStream(src.get_contents(),src.pdf)
    content.operations=[(operands,operator) for operands,operator in content.operations if operator not in (b'BDC',b'BMC',b'EMC')]
    stream=DecodedStreamObject();stream.set_data(b'/Figure <</MCID 0>> BDC\n'+content.get_data()+b'\nEMC')
    dest[N('/Contents')]=writer._add_object(stream)
    dest[N('/Resources')]=src['/Resources'].clone(writer)
    for key in ('/MediaBox','/CropBox','/TrimBox','/BleedBox'):
        dest.pop(N(key),None)
    dest[N('/MediaBox')]=src.mediabox.clone(writer)
    dest.pop(N('/Annots'),None)
    # Remove only the old map page's structural content; retain other page tags.
    structure=writer.root_object.get('/StructTreeRoot')
    if structure:
        structure=structure.get_object()
        fig=DictionaryObject({N('/Type'):N('/StructElem'),N('/S'):N('/Figure'),N('/P'):structure.indirect_reference,N('/Pg'):original_page,N('/K'):NumberObject(0),N('/Alt'):TextStringObject(alt)})
        ref=writer._add_object(fig);inserted=False
        def is_target(pg):
            return getattr(pg,'idnum',None)==original_page.idnum
        def prune(obj,inherited=False,parent=None):
            nonlocal inserted
            obj=obj.get_object()
            if isinstance(obj,(int,float)):return not inherited
            if isinstance(obj,ArrayObject):
                remaining=[]
                for v in obj:
                    if prune(v,inherited,parent):remaining.append(v)
                    elif not inserted:
                        remaining.append(ref);inserted=True
                        if parent is not None and parent.indirect_reference:fig[N('/P')]=parent.indirect_reference
                obj[:]=remaining;return bool(obj)
            if not isinstance(obj,DictionaryObject):return True
            here=is_target(obj.raw_get('/Pg')) if '/Pg' in obj else inherited
            if '/K' in obj:
                child=obj['/K']
                if not prune(child,here,obj):return False
            elif here and ('/MCID' in obj or obj.get('/Type')=='/StructElem'):return False
            if here:obj.pop(N('/Pg'),None)
            return True
        if '/K' in structure:prune(structure['/K'],parent=structure)
        key=int(dest.get('/StructParents',structure.get('/ParentTreeNextKey',0)))
        dest[N('/StructParents')]=NumberObject(key)
        if not inserted:
            kids=structure.get('/K',ArrayObject())
            if not isinstance(kids,ArrayObject):kids=ArrayObject([structure.raw_get('/K')])
            kids.append(ref);structure[N('/K')]=kids
        entries={}
        def collect(node):
            node=node.get_object()
            nums=node.get('/Nums',[])
            for i in range(0,len(nums),2):entries[int(nums[i])]=nums[i+1]
            for kid in node.get('/Kids',[]):collect(kid)
        if '/ParentTree' in structure:collect(structure['/ParentTree'])
        entries[key]=ArrayObject([ref])
        nums=ArrayObject()
        for k,v in sorted(entries.items()):nums.extend([NumberObject(k),v])
        structure[N('/ParentTree')]=writer._add_object(DictionaryObject({N('/Nums'):nums}))
        structure[N('/ParentTreeNextKey')]=NumberObject(max(entries)+1)
    writer.root_object[N('/Lang')]=TextStringObject('es-AR')

def main():
    reports=[]
    for e in json.loads((RELEASE/'release-plan.json').read_text()):
        baseline=ROOT/e['baseline'];assert sha(baseline)==e['baseline_sha256']
        old=PdfReader(baseline);folder=RELEASE/e['code'];output=ROOT/e['output']
        mode=e['mode'];changed=[];removed=[]
        if mode=='audited-preserved':
            shutil.copy2(baseline,output);reports.append(dict(code=e['code'],status='PRESERVED',pages=len(old.pages),sha256=sha(output),reason='No embedded decision-map SVG in published HTML. No unnecessary replacement.'));continue
        if mode=='html-reflow':reader=PdfReader(folder/'rendered.pdf')
        elif mode=='approved-full-document':reader=PdfReader(ROOT/e['source'])
        else:reader=old
        writer=PdfWriter();writer.clone_document_from_reader(reader)
        if mode=='replace-map-page':
            changed=[i for i,p in enumerate(old.pages) if 'MAPA DE DECISIÓN' in (p.extract_text() or '')]
            assert len(changed)==1,e['code']
            replace_plate(writer,changed[0],ROOT/e['plate'],(OUT/e['code']/'alt-text.md').read_text())
            if e['number']==15:
                # Visually confirmed pre-existing overflow-only page: no words,
                # image, exercise prompt or response field; only a spilled rule.
                assert not (old.pages[26].extract_text() or '').strip()
                assert len(old.pages[26].images)==0
                del writer.pages[26];removed=[26]
        writer._info=None;writer._ID=None;writer.root_object.pop(N('/Metadata'),None)
        with output.open('wb') as f:writer.write(f)
        check=PdfReader(output)
        if mode=='replace-map-page':
            assert len(old.pages)-len(removed)==len(check.pages)
            for i in range(len(old.pages)):
                if i not in changed+removed:
                    j=i-sum(k<i for k in removed)
                    assert old.pages[i].get_contents().get_data()==check.pages[j].get_contents().get_data(),(e['code'],i,'content changed')
                    assert old.pages[i].extract_text()==check.pages[j].extract_text(),(e['code'],i,'text changed')
        assert not check.metadata
        reports.append(dict(code=e['code'],status='ASSEMBLED_NOT_YET_VISUAL_QA',mode=mode,pages=len(check.pages),old_pages=len(old.pages),replaced_pages=[p+1 for p in changed],removed_empty_pages=[p+1 for p in removed],unchanged_page_content_streams_verified=mode=='replace-map-page',sha256=sha(output)))
        print(e['code'],len(check.pages),'pages')
    write_json(RELEASE/'assembly-report.json',reports)
if __name__=='__main__':main()
