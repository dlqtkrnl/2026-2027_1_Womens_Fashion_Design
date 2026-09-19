import concurrent.futures,json,re,urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/csm-ma-2026'
URL='https://1granary.com/designers-3/graduate-shows/lcf-ma-fashion-2026-the-body-under-pressure/'
soup=BeautifulSoup(urllib.request.urlopen(URL).read(),'html.parser')
pending=[];designers=[];originals={};all_urls=set()
# Unlike the CSM article, each LCF designer's image groups PRECEDE their heading.
for block,chunk in enumerate(soup.select('.chunk')):
    if block<3:continue
    if 'Credits' in chunk.get_text(' ',strip=True):break
    for a in chunk.select('a[js-zoom][href]'):
        url=a['href'];all_urls.add(url)
        if any(x['source']==url for x in pending):continue
        pending.append(dict(source=url,block=block,kind='runway' if Path(url).name.startswith('RED_') else 'research',width=int(a.get('data-width',0)),height=int(a.get('data-height',0))))
    h=chunk.select_one('.article__content h2')
    if not h:continue
    name=h.get_text(' ',strip=True);slug=re.sub('[^a-z0-9]+','-',name.lower()).strip('-')
    content=h.parent
    insta=content.find('a',href=re.compile('instagram'))
    text='\n\n'.join(p.get_text(' ',strip=True) for p in content.find_all('p') if not p.get_text(strip=True).startswith('@'))
    originals[slug]=text
    for n,item in enumerate(pending,1):item['file']=f'images/{slug}/{n:02}{Path(item["source"]).suffix}'
    designers.append(dict(name=name,slug=slug,page=slug+'.html',school='LCF',school_full='LONDON COLLEGE OF FASHION',source=URL,published='21 FEB 2026',photographer='Roger Dean',instagram=insta['href'] if insta else '',handle=insta.get_text(strip=True) if insta else '',images=pending))
    pending=[]
assert len(designers)==15 and not pending
assert {i['source'] for d in designers for i in d['images']}==all_urls
def download(i):
    p=OUT/i['file'];p.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(3):
        try:
            if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(i['source'],headers={'User-Agent':'Mozilla/5.0'}),timeout=45).read())
            with Image.open(p) as im:im.verify()
            return
        except Exception:
            if attempt==2:raise
items=[i for d in designers for i in d['images']]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(download,items))
manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
manifest['designers']=[d for d in manifest['designers'] if d.get('school')!='LCF']
for d in manifest['designers']:
    d.update(school='CSM',school_full='CENTRAL SAINT MARTINS',source=manifest['source'],published='19 FEB 2026')
manifest['designers']+=designers
manifest['sources']=[manifest['source'],URL]
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'lcf-originals.json').write_text(json.dumps(originals,ensure_ascii=False,indent=2),encoding='utf-8')
qa=ROOT/'tmp/lcf-qa';qa.mkdir(parents=True,exist_ok=True)
for d in designers:
    imgs=[i for i in d['images'] if i['kind']!='runway']
    if not imgs:continue
    sheet=Image.new('RGB',(1000,((len(imgs)+4)//5)*190),'white');draw=ImageDraw.Draw(sheet)
    for n,i in enumerate(imgs):
        with Image.open(OUT/i['file']) as im:thumb=ImageOps.contain(im.convert('RGB'),(196,162))
        x=n%5*200;y=n//5*190;sheet.paste(thumb,(x,y));draw.text((x,y+164),Path(i['file']).stem,fill='black')
    sheet.save(qa/(d['slug']+'.jpg'))
print(json.dumps({'designers':len(designers),'images':len(items),'counts':[(d['name'],len(d['images'])) for d in designers]}))
