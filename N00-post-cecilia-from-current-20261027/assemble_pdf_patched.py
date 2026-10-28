#!/usr/bin/env python3
"""Assemble private METSI PDFs without rebuilding their page tree.

Read-only inputs: stage/Nxx/interior-stage.pdf and snapshot/Nxx.pdf.
Writes only --output. The public cover's drawing streams/resources/boxes are
cloned into the existing first page, so interior destination references survive.
All source navigation is compared by semantic target page after blank removal.

Example:
  python3 scripts/assemble_pdf.py baseline/prepared 0 11 20 32 \
    --output checks/baseline-finalized

Machine validation is not a substitute for reviewing the emitted PNG proofs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from io import BytesIO
from pathlib import Path

from PIL import ImageChops, ImageStat
import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
    IndirectObject, NameObject, NullObject, NumberObject, ContentStream,
    TextStringObject)

# Never create bytecode next to the immutable original finalizer.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FINALIZER = ROOT / 'scripts/vendor/finalize_and_qa.py'
LINKEDIN = 'https://www.linkedin.com/in/carralbal/'
PAINT_KEYS = ('/Contents', '/Resources', '/MediaBox', '/CropBox', '/BleedBox',
              '/TrimBox', '/ArtBox', '/Rotate', '/UserUnit', '/Group')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(text):
    return re.sub(r'\s+', '', text.replace('ﬁ', 'fi').replace('ﬂ', 'fl'))


def ref_key(obj):
    ref = obj if isinstance(obj, IndirectObject) else getattr(obj, 'indirect_reference', None)
    return (ref.idnum, ref.generation) if ref is not None else None


def deref(obj):
    return obj.get_object() if hasattr(obj, 'get_object') else obj


def render_page(path, index, scale=1.6):
    doc = pdfium.PdfDocument(str(path))
    page = doc[index]
    bitmap = page.render(scale=scale)
    image = bitmap.to_pil().convert('RGB').copy()
    bitmap.close(); page.close(); doc.close()
    return image


def load_finalizer(path):
    spec = importlib.util.spec_from_file_location('metsi_finalizer_readonly', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.register_fonts()
    return module


def footer_backgrounds(raw, source_index, page, transformed=False):
    """Sample glyph and rule backgrounds separately, in PDF-point coordinates.

    The text baseline is y=25 with 6.7pt type; the rule is y=40. A dark
    editorial panel can stop between these two positions. Sampling a broad
    band selects white text on the white margin in that case.
    """
    if transformed:
        single = PdfWriter(); single.add_page(page)
        buffer = BytesIO(); single.write(buffer)
        doc = pdfium.PdfDocument(buffer.getvalue()); rendered_page = doc[0]
        bitmap = rendered_page.render(scale=1)
        sample = bitmap.to_pil().convert('RGB').copy()
        bitmap.close(); rendered_page.close(); doc.close()
    else:
        sample = render_page(raw, source_index, 1)
    width, height = float(page.mediabox.width), float(page.mediabox.height)
    sx, sy = sample.width / width, sample.height / height
    def mean(y_low, y_high):
        patch = sample.crop((round(44*sx), round((height-y_high)*sy),
                             round((width-44)*sx), round((height-y_low)*sy)))
        return sum(ImageStat.Stat(patch).mean) / 3
    return mean(23, 32), mean(39, 41)


def page_refs(reader):
    return {ref_key(p): i for i, p in enumerate(reader.pages)}


def navigation(reader):
    """Resolve local named/explicit destinations, links, outlines and page owners."""
    pages = page_refs(reader)
    named = reader.named_destinations
    errors, links, outlines = [], [], []

    def page_number(value, where):
        key = ref_key(value)
        if key in pages:
            return pages[key]
        errors.append(f'{where}: destination points outside page tree ({key})')
        return None

    def destination(value, where, active=None):
        active = set() if active is None else active
        value = deref(value)
        if isinstance(value, (str, bytes)):
            name = str(value)
            key = name if name in named else ('/' + name if '/' + name in named else name.lstrip('/'))
            if key not in named or key in active:
                errors.append(f'{where}: missing/cyclic named destination {name}')
                return None
            active.add(key)
            return destination(named[key], where, active)
        if isinstance(value, dict):
            if '/Page' in value:
                return page_number(value.get('/Page'), where)
            if '/D' in value:
                return destination(value.get('/D'), where, active)
        if isinstance(value, (list, tuple, ArrayObject)) and value:
            return page_number(value[0], where)
        errors.append(f'{where}: malformed destination {value!s:.100}')
        return None

    names = {str(k): destination(v, f'named {k}') for k, v in named.items()}
    for i, page in enumerate(reader.pages):
        for j, reference in enumerate(page.get('/Annots', [])):
            annotation = deref(reference)
            if not isinstance(annotation, dict):
                errors.append(f'page {i+1} annotation {j}: invalid object'); continue
            owner = annotation.get('/P')
            if owner is not None and ref_key(owner) != ref_key(page):
                errors.append(f'page {i+1} annotation {j}: wrong /P owner')
            if annotation.get('/Subtype') != '/Link':
                continue
            action = deref(annotation.get('/A')) or {}
            where = f'page {i+1} link {j}'
            if '/Dest' in annotation:
                links.append({'page':i, 'kind':'internal', 'target':destination(annotation['/Dest'], where)})
            elif action.get('/S') == '/GoTo':
                links.append({'page':i, 'kind':'internal', 'target':destination(action.get('/D'), where)})
            elif '/URI' in action:
                links.append({'page':i, 'kind':'uri', 'target':str(action['/URI'])})
            elif action:
                links.append({'page':i, 'kind':str(action.get('/S')), 'target':str(action)})

    def walk_outline(items, depth=0):
        for item in items:
            if isinstance(item, list):
                walk_outline(item, depth+1)
            else:
                outlines.append({'title':str(item.get('/Title', '')), 'depth':depth,
                    'target':destination(item, 'outline '+str(item.get('/Title','')))})
    walk_outline(reader.outline)
    return {'named_destinations':names, 'links':links, 'outlines':outlines, 'errors':errors}


def blank_pages(path, reader, nav, trim_uniform_terminal_image_page=False):
    """Never remove images, vectors, annotations, or a destination-bearing page."""
    targeted = set(nav['named_destinations'].values())
    targeted.update(x['target'] for x in nav['outlines'])
    targeted.update(x['target'] for x in nav['links'] if x['kind']=='internal')
    removed, records = [], []
    for i, page in enumerate(reader.pages):
        terminal_image_exception = trim_uniform_terminal_image_page and i == len(reader.pages)-1
        if i == 0 or (page.extract_text() or '').strip() or (len(page.images) and not terminal_image_exception):
            continue
        # Raster confirmation prevents deleting a vector-only diagram.
        image = render_page(path, i, 1.0)
        extrema = image.getextrema()
        uniformly_paper = all(
            low >= (235 if terminal_image_exception else 245)
            and high-low <= (15 if terminal_image_exception else 1)
            for low, high in extrema
        )
        protected = i in targeted or bool(page.get('/Annots'))
        records.append({'source_page':i+1, 'no_text_or_images':True,
            'uniform_paper_pixels':uniformly_paper, 'has_navigation':protected,
            'rgb_extrema':extrema, 'removed':uniformly_paper and not protected})
        if uniformly_paper and not protected:
            removed.append(i)
    return removed, records


def remove_stale_cover_tags(writer):
    """Do not attribute the provisional HTML cover's tags to different artwork.

    This removes only cover-associated structure leaves and its ParentTree slot.
    The public cover may itself be untagged. Interior structure remains cloned;
    the limitation is reported instead of fabricating accessible cover content.
    """
    cover = writer.pages[0]
    target = ref_key(cover)
    structure = deref(writer.root_object.get('/StructTreeRoot'))
    removed_ids, removed = set(), 0
    if not structure:
        return {'removed_stale_elements':0, 'cover_tagged':False}

    def prune(item, inherited=None):
        nonlocal removed
        obj = deref(item)
        if isinstance(obj, ArrayObject):
            kept = [prune(x, inherited) for x in obj]
            return ArrayObject(x for x in kept if x is not None)
        if not isinstance(obj, dict):
            return None if inherited == target else item
        pg = ref_key(obj.get('/Pg')) or inherited
        if '/K' in obj:
            child = prune(obj.raw_get('/K'), pg)
            if child is None or isinstance(child, ArrayObject) and not child:
                obj.pop(NameObject('/K'), None)
            else:
                obj[NameObject('/K')] = child
        if pg == target and '/K' not in obj:
            removed += 1
            if obj.get('/ID') is not None: removed_ids.add(str(obj['/ID']))
            return None
        return item

    if '/K' in structure:
        keep = prune(structure.raw_get('/K'))
        structure[NameObject('/K')] = keep if keep is not None else ArrayObject()
    key = cover.get('/StructParents')

    def prune_number_tree(node):
        obj = deref(node)
        if '/Nums' in obj:
            nums = deref(obj['/Nums'])
            obj[NameObject('/Nums')] = ArrayObject(x for k in range(0,len(nums),2)
                if nums[k] != key for x in (nums[k], nums[k+1]))
        for kid in obj.get('/Kids', []): prune_number_tree(kid)
    if key is not None and structure.get('/ParentTree'):
        prune_number_tree(structure['/ParentTree'])
    cover.pop(NameObject('/StructParents'), None)
    # The ID tree is ancillary lookup; removing stale cover entries prevents
    # orphan lookups while retaining every interior entry.
    def prune_ids(node):
        obj = deref(node)
        if '/Names' in obj:
            names = deref(obj['/Names'])
            obj[NameObject('/Names')] = ArrayObject(x for k in range(0,len(names),2)
                if str(names[k]) not in removed_ids for x in (names[k],names[k+1]))
        for kid in obj.get('/Kids', []): prune_ids(kid)
    if structure.get('/IDTree'): prune_ids(structure['/IDTree'])
    return {'removed_stale_elements':removed, 'cover_tagged':False,
        'note':'Only cover paint/resources/boxes/annotations transplanted. No provisional cover tags retained; interior semantic tree preserved.'}


def compatible_cover_structure(writer, public):
    """Keep existing cover tags only when published content/MCIDs match them."""
    stage=writer.pages[0]; source=public.pages[0]
    def entries(owner,page):
        root=deref(owner.root_object.get('/StructTreeRoot')) if isinstance(owner,PdfWriter) else deref(owner.trailer['/Root'].get('/StructTreeRoot'))
        if not root or page.get('/StructParents') is None:return None
        wanted=page['/StructParents']
        def lookup(node):
            obj=deref(node); nums=deref(obj.get('/Nums')) or []
            for i in range(0,len(nums),2):
                if nums[i]==wanted:return deref(nums[i+1])
            for child in obj.get('/Kids',[]):
                found=lookup(child)
                if found is not None:return found
            return None
        return lookup(root['/ParentTree']) if root.get('/ParentTree') else None
    def mcids(page,owner):
        return [int(args[-1]['/MCID']) for args,op in ContentStream(page.get_contents(),owner).operations
            if op==b'BDC' and isinstance(args[-1],dict) and '/MCID' in args[-1]]
    a,b=entries(writer,stage),entries(public,source)
    if a is None or b is None or mcids(stage,writer)!=mcids(source,public):return None
    if normalize(stage.extract_text() or '') not in normalize(source.extract_text() or ''):return None
    if len(a)!=len(b):return None
    for old,new in zip(a,b):
        x,y=deref(old),deref(new)
        if isinstance(x,dict)!=isinstance(y,dict):return None
        if isinstance(x,dict) and x.get('/S')!=y.get('/S'):return None
    adjusted=0
    for old,new in zip(a,b):
        x,y=deref(old),deref(new)
        if not isinstance(x,dict):continue
        for key in ('/Alt','/ActualText'):
            if key in y:
                x[NameObject(key)]=y.raw_get(key).clone(writer);adjusted+=1
    return {'removed_stale_elements':0,'cover_tagged':True,
        'compatible_published_mcid_structure':True,'published_alt_actualtext_fields_copied':adjusted}


def transplant_cover(writer, public):
    target, source = writer.pages[0], public.pages[0]
    semantic = compatible_cover_structure(writer,public) or remove_stale_cover_tags(writer)
    for key in PAINT_KEYS:
        target.pop(NameObject(key), None)
        if key in source:
            target[NameObject(key)] = source.raw_get(key).clone(writer)
    target.pop(NameObject('/Annots'), None)
    if source.get('/Annots'):
        copied = ArrayObject()
        for reference in source['/Annots']:
            old = deref(reference)
            action = deref(old.get('/A')) or {}
            if '/Dest' in old or action.get('/S') == '/GoTo':
                raise ValueError('Published cover contains local navigation; explicit remapping required')
            # Exclude source page and structure-owner references before cloning.
            annotation = DictionaryObject({k:v for k,v in old.items()
                if k not in ('/P','/StructParent')}).clone(writer)
            annotation[NameObject('/P')] = target.indirect_reference
            copied.append(writer._add_object(annotation))
        target[NameObject('/Annots')] = copied
    semantic['published_cover_had_structure_tree'] = bool(public.trailer['/Root'].get('/StructTreeRoot'))
    return semantic


def graph_validation(reader):
    """Walk reachable references; reject unresolved refs and detached /Page refs."""
    seen, errors = set(), []
    pages = page_refs(reader)
    count = 0
    def walk(value, location):
        nonlocal count
        if isinstance(value, IndirectObject):
            key = ref_key(value)
            if key in seen: return
            seen.add(key); count += 1
            try: value = value.get_object()
            except Exception as exc:
                errors.append(f'{location}: unresolved reference {key}: {exc}'); return
            if value is None:
                errors.append(f'{location}: unresolved reference {key}'); return
        if isinstance(value, dict):
            if value.get('/Type') == '/Page' and ref_key(value) not in pages:
                errors.append(f'{location}: detached page reference {ref_key(value)}')
            for key, child in value.items(): walk(child, location+'/'+str(key))
        elif isinstance(value, (list, tuple, ArrayObject)):
            for i, child in enumerate(value): walk(child, location+f'[{i}]')
    walk(reader.trailer.raw_get('/Root'), 'Root')
    # /Size includes free entries as well as in-use objects. pypdf keeps
    # those separately; ignoring a trailing free entry produces a false error.
    highest_object = max([0, *[n for generation in reader.xref.values() for n in generation],
                          *[n for generation in reader.xref_free_entry.values() for n in generation],
                          *reader.xref_objStm.keys()])
    declared_size = int(reader.trailer['/Size'])
    if declared_size != highest_object + 1:
        errors.append(f'Trailer Size {declared_size} != highest object + 1 ({highest_object + 1})')
    return {'reachable_indirect_objects':count, 'trailer_size':declared_size,
            'highest_object_number':highest_object, 'errors':errors}


def effective_fonts(reader):
    """Font resources count only when a text-showing operator draws a string."""
    used, visited = set(), set()
    def contains_text(obj):
        if isinstance(obj, (str, bytes)): return bool(obj)
        return isinstance(obj, (list, ArrayObject)) and any(contains_text(x) for x in obj)
    def walk(contents, resources):
        if contents is None: return
        resources = deref(resources) or {}
        stream = ContentStream(contents, reader)
        fonts = deref(resources.get('/Font')) or {}
        xobjects = deref(resources.get('/XObject')) or {}
        current, stack = None, []
        for args, op in stream.operations:
            if op == b'q': stack.append(current)
            elif op == b'Q': current = stack.pop() if stack else None
            elif op == b'Tf':
                font = deref(fonts.get(args[0]))
                current = str(font.get('/BaseFont','unknown')) if font else 'unresolved-font'
            elif op in (b'Tj', b'TJ', b"'", b'"') and any(contains_text(x) for x in args):
                used.add(current or 'unresolved-font')
            elif op == b'Do':
                ref = xobjects.get(args[0]); obj = deref(ref)
                if obj is not None and obj.get('/Subtype') == '/Form':
                    key = ref_key(ref) or ('direct',id(obj))
                    if key not in visited:
                        visited.add(key); walk(obj, obj.get('/Resources') or resources)
    for page in reader.pages: walk(page.get_contents(), page.get('/Resources'))
    return sorted(used)


def structure_counts(reader):
    """Count semantic leaf roles per interior page to detect accidental loss."""
    pages = page_refs(reader); counts = Counter(); seen = set()
    def walk(item, inherited=None):
        key = ref_key(item)
        if key is not None:
            if key in seen:return
            seen.add(key)
        obj = deref(item)
        if isinstance(obj, dict):
            pg = ref_key(obj.get('/Pg')) or inherited
            if obj.get('/S') and pg in pages: counts[(pages[pg],str(obj['/S']))] += 1
            if '/K' in obj:walk(obj.raw_get('/K'),pg)
        elif isinstance(obj, (list, ArrayObject)):
            for child in obj:walk(child,inherited)
    root=deref(reader.trailer['/Root'].get('/StructTreeRoot'))
    if root:walk(root)
    return counts


def validate_navigation_preserved(before, after, mapping):
    errors=[]
    old_names={k:mapping.get(v) for k,v in before['named_destinations'].items()}
    if old_names != after['named_destinations']: errors.append('Named destination names/target pages changed')
    old_outlines=[dict(x,target=mapping.get(x['target'])) for x in before['outlines']]
    if old_outlines != after['outlines']: errors.append('Outline titles/hierarchy/target pages changed')
    def sig(x):return (x['page'],x['kind'],str(x['target']))
    expected=Counter(sig(dict(x,page=mapping[x['page']],
        target=mapping.get(x['target']) if x['kind']=='internal' else x['target']))
        for x in before['links'] if x['page']!=0 and x['page'] in mapping)
    actual=Counter(sig(x) for x in after['links'] if x['page']!=0)
    if expected-actual:errors.append('Interior source link(s) lost or retargeted: '+str(list((expected-actual).elements())[:5]))
    return errors


def assemble(stage, number, output, snapshot, finalizer, scale, allow_existing_navigation_errors=False,
             trim_uniform_terminal_image_page=False):
    code=f'N{number:02d}'; raw=stage/code/'interior-stage.pdf'; public_path=snapshot/f'{code}.pdf'
    report_dir=output/'validation'; proof=report_dir/code; proof.mkdir(parents=True,exist_ok=True)
    report_path=report_dir/f'{code}-assembly.json'
    result={'document':code,'status':'FAIL','input_stage':str(raw),'input_stage_sha256':sha(raw),
        'public_snapshot':str(public_path),'public_snapshot_sha256':sha(public_path),
        'finalizer_source':str(finalizer.__file__),'finalizer_sha256':sha(finalizer.__file__),
        'visual_review_status':'pending_human_or_agent_inspection','errors':[]}
    temp=output/f'.{code}-assembling.pdf'; final=output/f'{code}-METSI-revision-privada.pdf'
    reader=PdfReader(raw,strict=True); published=PdfReader(public_path,strict=True)
    before=navigation(reader)
    if before['errors'] and not allow_existing_navigation_errors: raise ValueError(f'{code} input navigation invalid: {before["errors"]}')
    removed, blank_records=blank_pages(raw,reader,before,trim_uniform_terminal_image_page)
    mapping={i:j for j,i in enumerate(i for i in range(len(reader.pages)) if i not in removed)}
    writer=PdfWriter(); writer.clone_document_from_reader(reader)
    for i in reversed(removed): writer.remove_page(i,clean=True)
    result['cover_structure']=transplant_cover(writer,published)
    writer.root_object[NameObject('/Lang')]=TextStringObject('es-AR')
    raw_texts=[p.extract_text() or '' for p in reader.pages]
    transforms=[]; footer_records=[]
    for old_index,new_index in mapping.items():
        if new_index==0:continue
        page=writer.pages[new_index]; text=raw_texts[old_index]
        divider=number==0 and bool(re.search(r'\bPARTE\s+(?:I|II|III)\b',text))
        if divider:
            factor=1.1055; height=float(page.mediabox.height)
            page.add_transformation(Transformation().scale(factor,factor).translate(0,height*(1-factor)))
            transforms.append({'source_page':old_index+1,'output_page':new_index+1,
                'matrix':[factor,0,0,factor,0,height*(1-factor)]})
        luminance, rule_luminance = footer_backgrounds(raw,old_index,page,divider)
        light = luminance < 140
        rule_light = rule_luminance < 140
        overlay_reader=PdfReader(BytesIO(finalizer.footer(float(page.mediabox.width),float(page.mediabox.height),new_index+1,light)))
        overlay=overlay_reader.pages[0]
        if rule_light != light:
            content=ContentStream(overlay.get_contents(),overlay_reader)
            stroke=(.65,.68,.63) if rule_light else (.76,.78,.76)
            content.operations=[([FloatObject(x) for x in stroke],op) if op==b'RG' else (args,op)
                                for args,op in content.operations]
            overlay[NameObject('/Contents')] = content
        page.merge_page(overlay)
        for annotation in page.get('/Annots',[]):
            deref(annotation)[NameObject('/P')]=page.indirect_reference
        finalizer.strip_empty_helvetica(page,writer)
        footer_records.append({'page':new_index+1,'light':light,'background_luminance':round(luminance,2),
            'sample_pdf_y':[23,32],'rule_light':rule_light,
            'rule_background_luminance':round(rule_luminance,2),'rule_sample_pdf_y':[39,41]})
    # Public policy: no production software, timestamps, XMP, or document IDs.
    writer._info=None; writer._ID=None
    profile_path=ROOT/'content'/f'profile-{code}.json'
    if profile_path.is_file():
        profile=json.loads(profile_path.read_text())
        title=f"{code} · {profile['title']} | METSI"
        subject=profile['cover_subtitle']
    else:
        # Older recovered source packages may not carry the editorial profile.
        # In a private proof, preserve the public document's metadata instead
        # of inventing a new title or blocking faithful baseline comparison.
        public_metadata=published.metadata or {}
        title=public_metadata.get('/Title') or f"{code} | METSI"
        subject=public_metadata.get('/Subject') or ""
    writer.add_metadata({"/Title":title, "/Author":"Diego Carralbal", "/Subject":subject})
    writer.root_object.pop(NameObject('/Metadata'),None)
    with temp.open('wb') as stream: writer.write(stream)
    check=PdfReader(temp,strict=True)
    after=navigation(check); graph=graph_validation(check)
    result.update({'source_pages':len(reader.pages),'published_pages':len(published.pages),
        'output_pages':len(check.pages),'removed_blank_source_pages':[i+1 for i in removed],
        'a4_pages':sum(abs(float(p.mediabox.width)-595.276)<2 and abs(float(p.mediabox.height)-841.89)<2 for p in check.pages),
        'blank_candidates':blank_records,'page_map':{str(i+1):j+1 for i,j in mapping.items()},
        'n00_divider_transforms':transforms,'footer_pages':footer_records,
        'navigation':{'input_named_destinations':len(before['named_destinations']),
            'output_named_destinations':len(after['named_destinations']),
            'input_outline_items':len(before['outlines']),'output_outline_items':len(after['outlines']),
            'input_internal_links':sum(x['kind']=='internal' for x in before['links']),
            'output_internal_links':sum(x['kind']=='internal' for x in after['links']),
            'output_uri_links':sum(x['kind']=='uri' for x in after['links']),
            'resolved_named_destinations':{k:v+1 if v is not None else None for k,v in after['named_destinations'].items()},
            'errors':after['errors']+validate_navigation_preserved(before,after,mapping)},
        'reference_graph':graph})
    errors=result['errors']
    existing_navigation_errors=[]
    for error in result['navigation']['errors']:
        if allow_existing_navigation_errors and error in before['errors']:
            existing_navigation_errors.append(error)
        else:errors.append(error)
    result['preexisting_navigation_errors']=existing_navigation_errors
    result['input_navigation_errors']=before['errors']
    errors.extend(graph['errors'])
    if len(check.pages)!=len(reader.pages)-len(removed): errors.append('Unexpected page count')
    content_equal=check.pages[0].get_contents().get_data()==published.pages[0].get_contents().get_data()
    text_equal=check.pages[0].extract_text()==published.pages[0].extract_text()
    boxes_equal=all(list(map(float,getattr(check.pages[0],k)))==list(map(float,getattr(published.pages[0],k)))
        for k in ('mediabox','cropbox','bleedbox','trimbox','artbox'))
    pub_image=render_page(public_path,0,scale); out_image=render_page(temp,0,scale)
    pub_image.save(proof/'cover-published.png');out_image.save(proof/'cover-private.png')
    pixel_equal=pub_image.size==out_image.size and ImageChops.difference(pub_image,out_image).getbbox() is None
    result['cover']={'drawing_stream_identical':content_equal,'extracted_text_identical':text_equal,
        'all_boxes_identical':boxes_equal,'render_scale':scale,'pixel_size':out_image.size,
        'pixels_identical':pixel_equal,'visual_review_status':'pending_inspection',
        'published_png':str(proof/'cover-published.png'),'private_png':str(proof/'cover-private.png')}
    if not all((content_equal,text_equal,boxes_equal,pixel_equal)):errors.append('Published cover changed')
    source_structure=structure_counts(reader);target_structure=structure_counts(check)
    expected=Counter({(mapping[p],role):count for (p,role),count in source_structure.items() if p!=0 and p in mapping})
    actual=Counter({k:v for k,v in target_structure.items() if k[0]!=0})
    struct_ok=expected==actual
    catalog=check.trailer['/Root'];marked=deref(catalog.get('/MarkInfo')) or {}
    result['structure']={'root_preserved':bool(catalog.get('/StructTreeRoot')),
        'marked':bool(marked.get('/Marked')),'language':str(catalog.get('/Lang')),
        'interior_role_counts_identical':struct_ok,'interior_role_count':sum(actual.values())}
    if not struct_ok:errors.append('Interior semantic structure changed')
    if reader.trailer['/Root'].get('/StructTreeRoot') and not catalog.get('/StructTreeRoot'):errors.append('Structure tree lost')
    fonts=effective_fonts(check)
    inherited_fonts=set(effective_fonts(reader)) | set(effective_fonts(published))
    inherited_fallbacks=[f for f in fonts if re.search(r'Helvetica|Arial',f,re.I)]
    new_forbidden=[f for f in inherited_fallbacks if f not in inherited_fonts]
    footer_pdf=PdfReader(BytesIO(finalizer.footer(595.276,841.89,2,False)))
    footer_fonts=effective_fonts(footer_pdf)
    footer_forbidden=[f for f in footer_fonts if re.search(r'Helvetica|Arial',f,re.I)]
    result['effective_fonts']=fonts
    result['inherited_effective_fallback_fonts']=inherited_fallbacks
    result['new_forbidden_effective_fonts']=new_forbidden
    result['footer_effective_fonts']=footer_fonts
    result['footer_has_forbidden_effective_fonts']=bool(footer_forbidden)
    if new_forbidden or footer_forbidden:errors.append('Assembly introduced forbidden effective font(s)')
    if not any('Avenir' in f for f in footer_fonts):errors.append('Footer does not use Avenir')
    missing_text=[]
    for old_index,new_index in mapping.items():
        if new_index==0:continue
        source=normalize(raw_texts[old_index]);target=normalize(check.pages[new_index].extract_text() or '')
        if source not in target:missing_text.append({'source_page':old_index+1,'output_page':new_index+1})
    result['interior_text_preserved']=not missing_text;result['text_mismatch_pages']=missing_text
    if missing_text:errors.append('Interior text changed during assembly')
    footer_set={x['page'] for x in after['links'] if x['kind']=='uri' and x['target']==LINKEDIN}
    missing_footers=[p+1 for p in range(1,len(check.pages)) if p not in footer_set]
    result['missing_footer_links']=missing_footers
    if missing_footers:errors.append('Missing interior footer links')
    result['metadata']={'info':dict(check.metadata) if check.metadata else None,
        'xmp_present':bool(catalog.get('/Metadata')),'document_id_present':'/ID' in check.trailer,
        'production_metadata_removed':not any(k in (check.metadata or {}) for k in ('/Producer','/Creator','/CreationDate','/ModDate')) and not catalog.get('/Metadata') and '/ID' not in check.trailer}
    if not result['metadata']['production_metadata_removed']:errors.append('Production metadata present')
    proof_pages=sorted({1,len(check.pages)-1,*[x['output_page']-1 for x in transforms]})
    result['proof_pages']=[]
    for index in proof_pages:
        dest=proof/f'p{index+1:03d}.png';render_page(temp,index,scale).save(dest)
        result['proof_pages'].append({'page':index+1,'png':str(dest)})
    result['status']=('PASS_ASSEMBLY_WITH_PREEXISTING_NAVIGATION_ERRORS_PENDING_VISUAL_REVIEW' if existing_navigation_errors else 'PASS_MACHINE_CHECKS_PENDING_VISUAL_REVIEW') if not errors else 'FAIL'
    result['output_pdf']=str(final if not errors else temp);result['output_sha256']=sha(temp)
    report_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if errors:raise ValueError(f'{code}: '+ '; '.join(errors[:6]))
    temp.replace(final)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',type=Path)
    parser.add_argument('numbers',nargs='*',type=int)
    parser.add_argument('--output',type=Path,default=ROOT/'output/pdf')
    parser.add_argument('--snapshot',type=Path,default=ROOT.parent/'audit-metsi-20261002/snapshot')
    parser.add_argument('--finalizer',type=Path,default=DEFAULT_FINALIZER)
    parser.add_argument('--pixel-scale',type=float,default=1.6)
    parser.add_argument('--allow-existing-navigation-errors',action='store_true',help='Baseline diagnosis only: preserve and report existing broken destinations; never approve their navigation')
    parser.add_argument('--trim-uniform-terminal-image-page',action='store_true',help='Private N14 v31 only: remove a visually uniform, unlinked terminal leaf even if Chromium retains an unused image resource')
    args=parser.parse_args()
    numbers=args.numbers or list(range(37))
    if any(n<0 or n>36 for n in numbers):parser.error('numbers must be 0–36')
    stage=args.stage.resolve();output=args.output.resolve();snapshot=args.snapshot.resolve()
    if output==stage or output==snapshot or output.is_relative_to(stage) or output.is_relative_to(snapshot):
        parser.error('output must be separate from input stage and immutable snapshot')
    output.mkdir(parents=True,exist_ok=True)
    finalizer=load_finalizer(args.finalizer.resolve())
    failures=[]
    for number in numbers:
        try:
            result=assemble(stage,number,output,snapshot,finalizer,args.pixel_scale,args.allow_existing_navigation_errors,args.trim_uniform_terminal_image_page)
            print(json.dumps({k:result[k] for k in ('document','status','source_pages','output_pages','removed_blank_source_pages','output_pdf')},ensure_ascii=False),flush=True)
        except Exception as exc:
            failures.append({'document':f'N{number:02d}','error':str(exc)})
            failure_dir=output/'validation';failure_dir.mkdir(exist_ok=True)
            (failure_dir/f'N{number:02d}-failure.json').write_text(json.dumps(failures[-1],ensure_ascii=False,indent=2)+'\n')
            print(json.dumps(failures[-1],ensure_ascii=False),file=sys.stderr,flush=True)
    if failures:raise SystemExit(2)

if __name__=='__main__':main()
