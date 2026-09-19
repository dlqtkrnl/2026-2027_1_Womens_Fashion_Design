import concurrent.futures, json, re, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/csm-ma-2026'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = 'https://1granary.com/designers-3/graduate-shows/csm-ma-2026/'
soup = BeautifulSoup(urllib.request.urlopen(SOURCE).read(), 'html.parser')
designers = []
current = None
for chunk_index, chunk in enumerate(soup.select('.chunk')):
    if chunk_index >= 77: break
    content = chunk.select_one('.article__content')
    first = content.find('p') if content else None
    insta = first.find('a', href=re.compile('instagram')) if first else None
    if insta:
        name = first.get_text(' ', strip=True).split('@')[0].strip()
        slug = re.sub('[^a-z0-9]+', '-', name.lower().replace('é', 'e')).strip('-')
        current = dict(name=name, slug=slug, instagram=insta['href'], handle=insta.get_text(strip=True), images=[])
        designers.append(current)
    if not current: continue
    for a in chunk.select('a[js-zoom][href]'):
        url = a['href']
        if any(i['source']==url for i in current['images']): continue
        n = len(current['images'])+1
        ext = Path(url).suffix
        current['images'].append(dict(source=url, file=f'images/{current["slug"]}/{n:02}{ext}', block=chunk_index, kind='runway' if '1granary-csm-central-saint-martins-ma-fashion-2026-' in url else 'research', width=int(a.get('data-width',0)), height=int(a.get('data-height',0))))

def download(item):
    path = OUT / item['file']
    path.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(3):
        try:
            if not path.exists():
                req=urllib.request.Request(item['source'],headers={'User-Agent':'Mozilla/5.0'})
                path.write_bytes(urllib.request.urlopen(req,timeout=50).read())
            with Image.open(path) as im:
                im.verify()
            return None
        except Exception as e:
            if attempt==2: return {'url':item['source'],'error':str(e)}

items=[i for d in designers for i in d['images']]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    errors=[e for e in pool.map(download,items) if e]
(OUT/'manifest.json').write_text(json.dumps(dict(source=SOURCE,designers=designers,errors=errors),ensure_ascii=False,indent=2),encoding='utf-8')
qa=ROOT/'tmp/csm-qa'
qa.mkdir(parents=True,exist_ok=True)
for d in designers:
    research=[i for i in d['images'] if i['kind']=='research']
    if not research: continue
    sheet=Image.new('RGB',(1000,((len(research)+4)//5)*170),'white')
    draw=ImageDraw.Draw(sheet)
    for n,item in enumerate(research):
        with Image.open(OUT/item['file']) as im:
            thumb=ImageOps.contain(im.convert('RGB'),(195,145))
        x=(n%5)*200; y=(n//5)*170
        sheet.paste(thumb,(x,y))
        draw.text((x,y+147),Path(item['file']).stem+' block '+str(item['block']),fill='black')
    sheet.save(qa/f'{d["slug"]}.jpg')
print(json.dumps({'designers':len(designers),'images':len(items),'errors':errors,'counts':[(d['name'],len(d['images'])) for d in designers]},ensure_ascii=False))
