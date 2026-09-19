import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/csm-ma-2026'
data=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
translations=json.loads((OUT/'translations.json').read_text(encoding='utf-8'))
processes=json.loads((OUT/'processes.json').read_text(encoding='utf-8'))
errors=[]
total=len(data['designers'])
image_total=sum(len(d['images']) for d in data['designers'])
assert total==38 and image_total==634
assert sum(d['school']=='LCF' for d in data['designers'])==15
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    page=b.new_page(viewport={'width':1440,'height':900})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((OUT/'index.html').as_uri())
    assert page.locator('.slide').count()==total
    assert page.locator('.image-link').count()==image_total
    assert page.locator('#designer optgroup').count()==2
    for d in data['designers']:
        page.locator('#designer').select_option(d['slug'])
        page.wait_for_function('(slug)=>document.querySelector(".slide.active").id===slug',arg=d['slug'])
        active=page.locator('.slide.active')
        assert page.locator('.slide:visible').count()==1
        assert active.locator('.image-link').count()==len(d['images'])
        assert active.locator('.notes [lang=en]').count()==1
        assert active.locator('.bilingual [lang=en] p').text_content()==translations[d['slug']]['en']
        assert active.locator('.bilingual [lang="zh-CN"] p').text_content()==translations[d['slug']]['zh']
        assert active.locator('.theme strong').count()==2
        assert active.locator('.bilingual mark').count()>=1
        sizes=active.locator('.bilingual>div').evaluate_all('els=>els.map(e=>parseFloat(getComputedStyle(e.querySelector("p")).fontSize))')
        assert sizes[0]>=19 and sizes[0]>sizes[1]*1.5,(d['slug'],sizes)
        assert active.locator('.course-note').count()==1
        assert active.locator('.bilingual>div').evaluate_all('els=>els.every(e=>e.scrollHeight<=e.clientHeight+1)')
        assert not re.search('[\uac00-\ud7af]',active.inner_text())
        assert active.locator('.image-link').evaluate_all('els=>els.every(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.top>=0&&r.bottom<=innerHeight+1&&r.right<=innerWidth+1})')
        active.locator('.image-link').first.click()
        page.wait_for_function('document.querySelector("#large").complete && document.querySelector("#large").naturalWidth>0')
        assert page.locator('#counter').inner_text().startswith('1 / '+str(len(d['images'])))
        page.locator('#plus').click()
        assert page.locator('#zoom').inner_text()=='150%'
        page.keyboard.press('ArrowRight')
        assert page.locator('#counter').inner_text().startswith('2 /')
        page.keyboard.press('Escape')
        page.wait_for_function('!document.body.classList.contains("modal-open")')
        active.locator('.read-notes').click()
        assert page.locator('#reading').is_visible()
        assert page.locator('#reading [lang=en] p').text_content()==translations[d['slug']]['en']
        page.keyboard.press('Escape')
        page.wait_for_function('!document.body.classList.contains("modal-open")')
    page.goto((OUT/'luca-fabry.html').as_uri())
    assert page.locator('.slide').count()==1
    assert page.locator('.image-link').count()==21
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('.image-link').first.click()
    assert page.locator('#close').is_visible()
    page.locator('#close').click()
    page.goto((OUT/'processes.html').as_uri())
    assert page.locator('.route-card').count()==8
    assert page.locator('tbody tr').count()==total
    assert len(processes['routes'])==7
    b.close()
assert not errors,errors
print(f'PASS: {total} one-page views; complete EN/ZH text; larger Chinese; yellow highlights; no overflow; {image_total} images; school navigation; 7 routes + unknown; text/image zoom; mobile bounds; no JS errors.')
