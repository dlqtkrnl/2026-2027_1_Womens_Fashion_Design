import json,zipfile
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/csm-ma-2026'
data=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
pdf=fitz.open()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    page=b.new_page(viewport={'width':2000,'height':1308},device_scale_factor=2)
    for n,d in enumerate(data['designers']):
        page.goto((OUT/d['page']).as_uri())
        page.wait_for_function('Array.from(document.querySelectorAll(".image-link img")).every(i=>i.complete&&i.naturalWidth>0)')
        rendered=page.locator('.slide').screenshot(type='jpeg',quality=93)
        target=pdf.new_page(width=1500,height=937.5)
        target.insert_image(target.rect,stream=rendered)
        print(f'PDF {n+1}/{len(data["designers"])}',flush=True)
    b.close()
pdf.set_metadata({'title':'CSM + LCF MA 2026 - Chinese / English - 38 designers','subject':'One designer per page; 634 images; source: 1 Granary'})
pdf.save(OUT/'CSM-LCF-MA-2026-ZH-EN.pdf',deflate=True)
assert len(pdf)==38
csm=fitz.open();csm.insert_pdf(pdf,from_page=0,to_page=22)
csm.set_metadata({'title':'CSM MA 2026 - Chinese / English - 23 designers'})
csm.save(OUT/'CSM-MA-2026-ZH-EN.pdf',deflate=True);csm.close()
pdf.close()
with zipfile.ZipFile(ROOT/'tmp/CSM-MA-2026.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for path in OUT.rglob('*'):
        if path.is_file():z.write(path,Path('CSM-MA-2026')/path.relative_to(OUT))
print('Saved 38-page combined PDF, updated 23-page CSM PDF and ZIP.',flush=True)
