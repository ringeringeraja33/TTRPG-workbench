"""Read-only source inventory and bounded, page-anchored extraction. UTF-8 JSON."""
import argparse, hashlib, json, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

def classify(name):
    rules = [(r'COC|CoC|Cthulhu|克苏鲁|调查员|守秘人|燃烧的星辰', 'CoC family; edition needs confirmation'), (r'3R|3r', 'D&D 3.5 candidate'), (r'5E|5e', 'D&D 5e; 2014/2024 unresolved'), (r'Pathfinder','Pathfinder; file version is not game edition'), (r'TOC|迷踪','Trail of Cthulhu'), (r'BRP','BRP; edition unresolved'), (r'圣杯|Fate Gug','Fate franchise fan rules; not Evil Hat Fate'), (r'方舟|泰拉','Arknights fan rules'), (r'诡秘|诡团','Lord of Mysteries fan rules'), (r'战锤|黑暗异端','Warhammer family'), (r'迷雾之城','City of Mist'), (r'龙族|混血种','Dragon Raja fan rules')]
    for pattern, system in rules:
        if re.search(pattern,name): return system
    return 'unclassified; inspect source'

def units(path):
    suffix=path.suffix.lower()
    if suffix=='.pdf':
        from pypdf import PdfReader
        reader=PdfReader(path)
        for i,page in enumerate(reader.pages,1):
            yield {'anchor':f'PDF:{i}', 'printed_page':'unverified', 'text':page.extract_text() or ''}
    elif suffix in ('.docx','.pptx'):
        with zipfile.ZipFile(path) as z:
            names=['word/document.xml'] if suffix=='.docx' else sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),key=lambda n:int(re.search(r'(\d+)\.xml',n)[1]))
            for name in names:
                root=ET.fromstring(z.read(name))
                for i,paragraph in enumerate((e for e in root.iter() if e.tag.endswith('}p')),1):
                    yield {'anchor':f'{name}:paragraph:{i}', 'text':''.join(e.text or '' for e in paragraph.iter() if e.tag.endswith('}t'))}
    elif suffix=='.xlsx':
        import openpyxl
        book=openpyxl.load_workbook(path,read_only=True,data_only=False)
        try:
            for sheet in book:
                for row_index,row in enumerate(sheet,1):
                    vals=[f'{c.coordinate}={c.value}' for c in row if c.value is not None]
                    if vals: yield {'anchor':f'sheet:{sheet.title}:row:{row_index}', 'text':' | '.join(vals)}
        finally: book.close()
    elif suffix in ('.txt','.md'):
        for i,line in enumerate(path.read_text(encoding='utf-8-sig',errors='strict').splitlines(),1):
            yield {'anchor':f'line:{i}','text':line}
    else:
        raise ValueError('Unsupported extraction format; CHM/CHW/DOC/images need a separate reader or OCR')

def inventory(root):
    for p in sorted(root.rglob('*')):
        if not p.is_file() or any(x in {'.obsidian','.git','ttrpg-workbench','ttrpg-workbench-audit','__pycache__'} for x in p.relative_to(root).parts): continue
        row={'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'format':p.suffix.lower(),'system_candidate':classify(p.name),'edition_candidate':'; '.join(re.findall(r'(?i)v?\d+(?:\.\d+)+|[567]版|3[Rr]|[57][Ee]',p.name)) or 'unverified','language':'unverified','authority':'unverified; filename is not provenance','kind':'character sheet' if re.search('角色卡|人物卡|自动卡|空白卡|示例卡',p.name) else 'module/handout' if '燃烧的星辰' in p.parts else 'unclassified','content_status':'not inspected'}
        try:
            with p.open('rb') as f: row['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
            if p.suffix.lower() in {'.pdf','.docx','.pptx','.xlsx','.txt'}:
                sample=[]
                for i,u in enumerate(units(p)):
                    sample.append(u['text'])
                    if i>=2: break
                t=' '.join(sample)
                row['content_status']='opening sampled' if t.strip() else 'no opening text; scan/OCR or later pages needed'
                row['language']='Chinese present' if re.search(r'[\u4e00-\u9fff]',t) else 'English/other or insufficient text'
                # Inventory carries metadata, not copyrighted excerpts or character secrets.
            else: row['content_status']='metadata only; separate reader needed'
        except Exception as e: row['content_status']=f'ERROR: {type(e).__name__}: {e}'
        yield row

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='mode',required=True)
    inv=sub.add_parser('inventory'); inv.add_argument('root',type=Path); inv.add_argument('--output',type=Path,required=True)
    read=sub.add_parser('read'); read.add_argument('file',type=Path); read.add_argument('--query'); read.add_argument('--start',type=int,default=1); read.add_argument('--end',type=int); read.add_argument('--limit',type=int,default=8); read.add_argument('--chars',type=int,default=2500)
    a=ap.parse_args()
    if a.mode=='inventory':
        rows=list(inventory(a.root)); a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'files':len(rows),'output':str(a.output)},ensure_ascii=False))
    else:
        count=0
        for i,u in enumerate(units(a.file),1):
            if i<a.start: continue
            if a.end and i>a.end: break
            if a.query and a.query.casefold() not in u['text'].casefold(): continue
            if a.query:
                pos=u['text'].casefold().find(a.query.casefold()); u['text']=u['text'][max(0,pos-150):max(0,pos-150)+a.chars]
            else: u['text']=u['text'][:a.chars]
            print(json.dumps(u,ensure_ascii=False)); count+=1
            if count>=a.limit: break
        if not count: print(json.dumps({'matches':0,'note':'No textual match does not prove rule absence.'}))
if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
