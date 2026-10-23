#!/usr/bin/env python3
"""Private evidence index and structural review staging. Python 3.10+, stdlib only."""
import argparse
import csv
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

DOMAINS = ['通则','交通','旅游','文化娱乐','体育','教育','医疗卫生','邮政电信','餐饮住宿','商业金融']
CONFIG = Path.home() / '.tiskill/public-service.json'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def safe(root, relative):
    q = Path(relative)
    if q.is_absolute() or '..' in q.parts:
        raise ValueError('unsafe relative pointer')
    p = root / q
    if any(x.is_symlink() for x in [p, *p.parents]):
        raise ValueError('symlink refused')
    if not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('pointer escapes sourceRoot')
    return p

def exclusive(p, value):
    if any(x.is_symlink() for x in [p,*p.parents]):
        raise ValueError('symlink refused')
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')

def load_root(config):
    if not config.exists():
        raise ValueError('missing_local_registry: configure sourceRoot or use supplied material; evidence pending')
    root=Path(json.loads(config.read_text())['sourceRoot']).expanduser()
    if not root.is_absolute() or not root.is_dir() or any(x.is_symlink() for x in [root,*root.parents]):
        raise ValueError('sourceRoot must be an existing absolute nonsymlink directory')
    safe(root,'source-index.csv').read_text(encoding='utf-8-sig')
    return root

class Table(HTMLParser):
    """Expand spans while preserving cell text, not inferred semantics."""
    def __init__(self):
        super().__init__(); self.rows=[]; self.cells=None; self.cell=None; self.spans={}
    def handle_starttag(self,tag,attrs):
        if tag=='tr': self.cells=[]
        if tag in ('td','th'):
            a=dict(attrs); self.cell=['',int(a.get('rowspan',1)),int(a.get('colspan',1))]
            if not all(1 <= x <= 1000 for x in self.cell[1:]): raise ValueError('invalid span')
        if tag=='br' and self.cell is not None: self.cell[0]+=' '
    def handle_data(self,data):
        if self.cell is not None:self.cell[0]+=data
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            if self.cells is not None:self.cells.append(self.cell)
            self.cell=None
        if tag=='tr' and self.cells is not None:
            row={c:t for c,(t,n) in self.spans.items()}; future={c:(t,n-1) for c,(t,n) in self.spans.items() if n>1}; c=0
            for text,rs,cs in self.cells:
                while c in row:c+=1
                text=' '.join(text.split())
                for j in range(cs):
                    row[c+j]=text
                    if rs>1:future[c+j]=(text,rs-1)
                c+=cs
            self.rows.append([row.get(i,'') for i in range(max(row,default=-1)+1)])
            self.spans=future;self.cells=None

def extract(root):
    rows=[]; blocks=[]
    for source in csv.DictReader(safe(root,'source-index.csv').read_text(encoding='utf-8-sig').splitlines()):
        md=safe(root,source['md']); folder=md.parent
        lists=list(folder.glob('*content_list.json'))
        if len(lists)!=1:raise ValueError('expected one content list per source')
        listing=safe(root,str(lists[0].relative_to(root))); data=json.loads(listing.read_text()); table=''; context=''
        for i,b in enumerate(data):
            if b.get('type')=='text':
                text=b.get('text','')
                if '附录' in text or '说明' in text:context=text
            if b.get('type')!='table':continue
            bid=f"p{source['part']}-b{i}"; body=b.get('table_body','') or ''
            caption=' '.join(b.get('table_caption',[]));table=caption or table
            base={'block_id':bid,'domain':source['domain'],'standard':source['standard_id'],'source_version':2013 if source['part']=='1' else 2017,'pdf_page':b['page_idx']+1,'printed_page':None,'source_sha256':source['sha256'],'content_pointer':str(listing.relative_to(root)),'content_sha256':digest(listing),'markdown_pointer':str(md.relative_to(root)),'markdown_sha256':digest(md),'block':i,'table':table,'annex_type':'informative','notes':b.get('table_footnote',[]),'annex_context':context,'status':'candidate'}
            blocks.append(dict(base,kind='html' if body.strip() else 'image_only',bbox=b.get('bbox')))
            if body.strip():
                parser=Table();parser.feed(body)
                for j,cells in enumerate(parser.rows):
                    if len(cells)<3 or not re.fullmatch(r'\d+',cells[0]):continue
                    rows.append(dict(base,id=f'{bid}-r{j}',row_label=cells[0],zh=cells[1],en=cells[2],cells=cells,kind='html_row'))
    return rows,blocks

def build(root, generation, apply=False):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',generation):raise ValueError('unsafe generation')
    rows,blocks=extract(root)
    recovery=safe(root,'derived-public-service-v1/recovery-ledger.json')
    if recovery.exists():
        for b in json.loads(recovery.read_text()):
            base=next((x for x in blocks if x['block_id']==b['id']),None)
            if base is None:raise ValueError('unknown recovery block')
            crop=safe(root,b['crop'])
            for i,line in enumerate(b.get('lines',[])):
                rows.append(dict(base,id=f"{b['id']}-ocr{i}",kind='ocr_line',zh='',en='',text=line['text'],bbox=line['bbox'],crop=b['crop'],crop_sha256=digest(crop),status='candidate',warning='Unaligned OCR line, never a term pair'))
    review=safe(root,'derived-public-service-v1/row-reviews.json')
    if review.exists():
        byid={x['id']:x for x in rows}
        for a in json.loads(review.read_text()):
            item=byid[a['id']]
            if a['status'] not in ['verified','rejected'] or not a.get('reviewer') or not a.get('method'):raise ValueError('invalid review')
            if any(item[k]!=a[k] for k in ['source_sha256','content_sha256','zh','en']):raise ValueError('stale review provenance')
            item.update(status=a['status'],review=a)
    stats={'records':len(rows),'verified':sum(x['status']=='verified' for x in rows),'candidate':sum(x['status']=='candidate' for x in rows),'rejected':sum(x['status']=='rejected' for x in rows),'layout_blocks':len(blocks),'html_blocks':sum(x['kind']=='html' for x in blocks),'image_only_blocks':sum(x['kind']=='image_only' for x in blocks),'html_rows':sum(x['kind']=='html_row' for x in rows),'ocr_lines':sum(x['kind']=='ocr_line' for x in rows)}
    if apply:exclusive(safe(root,f'public-service-index/{generation}.json'),{'schema':1,'stats':stats,'records':rows,'blocks':blocks})
    return dict(stats,applied=apply,generation=generation,warning='Counts are extracted occurrences, not unique terms or fully checked rows')

def search(root,generation,query,domain,candidates=False):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',generation):raise ValueError('unsafe generation')
    data=json.loads(safe(root,f'public-service-index/{generation}.json').read_text()); found=[]
    for row in data['records']:
        if row['domain']!=domain or row['status'] not in (['verified','candidate'] if candidates else ['verified']):continue
        if query.casefold() not in ' '.join(str(row.get(k,'')) for k in ['zh','en','text']).casefold():continue
        if digest(safe(root,row['content_pointer']))!=row['content_sha256']:raise ValueError('stale source content; rebuild and review')
        if row.get('markdown_pointer') and digest(safe(root,row['markdown_pointer']))!=row['markdown_sha256']:raise ValueError('stale source markdown')
        found.append(row)
    return {'matches':found,'count':len(found),'verified_count':sum(x['status']=='verified' for x in found),'index_stats':data['stats'],'warning':'Verified means transcription checked, applicability still requires scenario review; candidates cannot support definitive recommendations'}

def batch(data):
    if not isinstance(data,dict) or not isinstance(data.get('rows'),list):raise ValueError('rows array required')
    conditions=data.get('clientConditions',{})
    if not isinstance(conditions,dict):raise ValueError('clientConditions object required')
    out=[];seen=set()
    for item in data['rows']:
        if not isinstance(item,dict):raise ValueError('row object required')
        for key in ['id','source','domain','scenario']:
            if not isinstance(item.get(key),str) or not item[key].strip():raise ValueError(f'{key} required')
        if item['id'] in seen:raise ValueError('duplicate row ID')
        seen.add(item['id'])
        if item['domain'] not in DOMAINS:raise ValueError('unknown domain')
        for key in ['initialTranslation','notes']:
            if key in item and not isinstance(item[key],str):raise ValueError(f'{key} must be string')
        missing=[k for k in ['placeFunction','audience','properNames','jurisdiction','existingTermMap'] if not conditions.get(k)]
        out.append({'id':item['id'],'input':item,'clientConditions':conditions,'proposedTranslation':None,'reason':'Human/AI translation and source applicability review required','evidence':[],'stage':'pending_human_ai_review','pendingConditions':missing,'semanticAssessment':'not_performed'})
    return {'schema':1,'rowCount':len(out),'rows':out,'stage':'structural_validation_only'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,default=CONFIG);sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('configure');c.add_argument('sourceRoot',type=Path);c.add_argument('--apply',action='store_true')
    b=sub.add_parser('build-index');b.add_argument('--generation',required=True);b.add_argument('--apply',action='store_true')
    q=sub.add_parser('search');q.add_argument('query');q.add_argument('--domain',required=True,choices=DOMAINS);q.add_argument('--generation',required=True);q.add_argument('--include-candidates',action='store_true')
    b=sub.add_parser('batch');b.add_argument('--input',type=Path,required=True);b.add_argument('--output',type=Path)
    a=p.parse_args()
    try:
        if a.command=='configure':
            root=a.sourceRoot.expanduser()
            if not root.is_absolute() or not root.is_dir() or any(x.is_symlink() for x in [root,*root.parents]):raise ValueError('invalid sourceRoot')
            extract(root)
            value={'sourceRoot':str(root)}
            if a.config.exists() and json.loads(a.config.read_text())!=value:raise ValueError('existing configuration conflict')
            if a.apply and not a.config.exists():exclusive(a.config,value)
            result={'valid':True,'applied':a.apply}
        elif a.command=='batch':
            result=batch(json.loads(a.input.read_text()))
            if a.output:exclusive(a.output,result)
        elif a.command=='build-index':result=build(load_root(a.config),a.generation,a.apply)
        else:result=search(load_root(a.config),a.generation,a.query,a.domain,a.include_candidates)
        print(json.dumps(result,ensure_ascii=False))
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'error':str(e),'status':'pending'},ensure_ascii=False));return 2
    return 0
if __name__=='__main__':sys.exit(main())
