import json, html
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/csm-ma-2026'
data=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
# Categories reviewed visually against contact sheets; mixed process boards remain research.
studio={
 'luca-fabry':list(range(12,22)), 'pola-wislicz':list(range(11,17)),
 'jaeyoung-bae':list(range(8,13)), 'clay-hattam':list(range(9,14)),
 'gemma-dolan':list(range(8,18)), 'macy-grimshaw':[10,13,15,17,18,20],
 'benaissa-majeri':[14], 'grey-buscemi':[15,17,18,20],
 'kai-ghattaura':[17,18], 'oli-clarke':[16,17],
 'thomas-uhlarik':[9,11,12,15]
}
for d in data['designers']:
    for seq,i in enumerate(d['images'],1):
        if d['slug']=='thomas-uhlarik' and i['block']==72: i['kind']='research'
        if seq in studio.get(d['slug'],[]): i['kind']='studio'
    expected='https://www.instagram.com/'+d['handle'].lstrip('@')+'/'
    if d['instagram'].rstrip('/')!=expected.rstrip('/'):
        d['instagram_source_href']=d['instagram']
        d['instagram']=expected
H=html.escape
source=data['source']
translations=json.loads((OUT/'translations.json').read_text(encoding='utf-8'))
processes=json.loads((OUT/'processes.json').read_text(encoding='utf-8'))
routes={r['id']:r for r in processes['routes']}
dialog='''<dialog id="viewer" aria-label="图片放大 / Image viewer"><div class="viewer-bar"><span id="counter" aria-live="polite"></span><div class="controls"><button id="previous" aria-label="上一张 / Previous image">←</button><button id="next" aria-label="下一张 / Next image">→</button><button id="minus" aria-label="缩小 / Zoom out">−</button><button id="zoom" aria-label="适应屏幕 / Fit">100%</button><button id="plus" aria-label="放大 / Zoom in">＋</button><a id="original" target="_blank" rel="noopener">原图 / Original</a><button id="close">关闭 / Close ✕</button></div></div><div id="stage"><img id="large" alt=""></div><p class="viewer-help">＋ / − 缩放 Zoom · ← → 切换 Images · Esc 关闭 Close</p></dialog>'''
def shell(title,body,script=''):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>{H(title)} · CSM MA 2026</title><link rel="stylesheet" href="slides.css"><link rel="stylesheet" href="fullnotes.css"></head><body>{body}{dialog}<script src="gallery.js"></script>{script}</body></html>'''

def slide(d,n):
    t=translations[d['slug']]
    zh,en=t['zh'],t['en']
    c=processes['designers'][d['slug']]
    route=routes.get(c['primary'])
    route_label=f"{route['id']:02} · {route['zh']} / {route['en']}" if route else '待定 / Unclassified'
    d.pop('summary_ko',None)
    d['description_zh']=zh;d['description_en']=en
    d['theme_zh']=t['theme_zh'];d['theme_en']=t['theme_en'];d['process']=c
    images=d['images']; blocks=[]
    categories=[('runway','系列全貌','RUNWAY'),('studio','造型与细节','STUDIO / DETAILS'),('research','灵感板 · 调研 · 制作过程','BOARDS / RESEARCH / PROCESS')]
    for kind,cn,eng in categories:
        items=[i for i in images if i['kind']==kind]
        if not items: continue
        figures=[]
        for j,i in enumerate(items):
            figures.append(f'<a class="image-link" href="{i["file"]}" title="点击放大 / Click to enlarge"><img src="{i["file"]}" alt="{H(d["name"])} · {eng} {j+1}" loading="eager"><span>{j+1:02}</span></a>')
        blocks.append(f'<section class="group {kind}" data-count="{len(items)}"><h2>{cn} <small>{eng}</small><b>{len(items):02}</b></h2><div class="image-grid">{"".join(figures)}</div></section>')
    missing='' if any(i['kind']=='research' for i in images) else '<p class="missing">原文未附灵感板或调研图。<br><span lang="en">No boards or research images supplied.</span></p>'
    secondary=' · '.join(f"{r:02} {routes[r]['zh']} / {routes[r]['en']}" for r in c['secondary']) or '—'
    course=f'''<div class="course-note"><a href="processes.html#route-{c['primary'] or 'unknown'}"><b>主入口 / PRIMARY: {H(route_label)}</b></a><span class="status">{H(c['status'])}</span><p>辅助 / SECONDARY: {H(secondary)}</p><p><b>依据 / BASIS</b> {H(c['basis_zh'])} <span lang="en">{H(c['basis_en'])}</span></p><p><a href="../womenswear_design_iii_week01.html#{c['w1_anchor']}"><b>W01 ↗</b></a> {H(c['w1'])}</p><p><a href="../womenswear_design_iii_week02.html#{c['w2_anchor']}"><b>W02 · 实验建议 / PROPOSED TEST ↗</b></a> {H(c['task'])} <span lang="en">{H(c['task_en'])}</span></p></div>'''
    return f'''<article class="slide" id="{d['slug']}" aria-label="{H(d['name'])}"><header><span>CENTRAL SAINT MARTINS / MA 2026</span><span>毕业设计档案 / GRADUATE ARCHIVE · {len(images)} IMAGES</span><b>{n+1:02} / 23</b></header><div class="slide-body"><aside><div class="identity"><div><p class="kicker">设计师 / DESIGNER</p><h1>{H(d['name'])}</h1></div><a class="handle" href="{d['instagram']}" target="_blank" rel="noopener">{H(d['handle'])} ↗</a></div><div class="theme"><strong>{H(t['theme_zh'])}</strong><strong lang="en">{H(t['theme_en'])}</strong></div><div class="notes"><div class="notes-heading"><h2>设计说明全文 / FULL DESIGN NOTES</h2><button class="read-notes">放大文字 / Enlarge text ↗</button></div><div class="bilingual"><div lang="zh-CN"><h3>中文全译 / CHINESE TRANSLATION</h3><p>{H(zh)}</p></div><div lang="en"><h3>英文原文 / ENGLISH ORIGINAL</h3><p>{H(en)}</p></div></div></div>{course}</aside><div class="visuals">{''.join(blocks)}{missing}</div></div><footer><a href="{source}" target="_blank" rel="noopener">来源 / SOURCE: 1 GRANARY · 19 FEB 2026 ↗</a><span>主题与流程为教学归纳 / Themes & routes: teaching interpretation · 图片版权归各权利人 / Images © respective owners</span></footer></article>'''

slides=[]
for n,d in enumerate(data['designers']):
    d['page']=d['slug']+'.html'
    markup=slide(d,n);slides.append(markup)
    prev=data['designers'][n-1]['slug']+'.html' if n else 'index.html'
    nxt=data['designers'][n+1]['slug']+'.html' if n<22 else 'index.html'
    bar=f'<nav class="toolbar"><a href="{prev}">← 上一页 / Previous</a><a href="index.html#{d["slug"]}">全部 / All 23</a><a href="{nxt}">下一页 / Next →</a></nav>'
    (OUT/d['page']).write_text(shell(d['name'],bar+'<main class="single">'+markup+'</main>','<script src="slides.js"></script>'),encoding='utf-8')

options=''.join(f'<option value="{d["slug"]}">{n+1:02} · {H(d["name"])}</option>' for n,d in enumerate(data['designers']))
toolbar=f'''<nav class="toolbar"><a href="processes.html">7种设计流程 / 7 Processes ↗</a><div><button id="page-prev" aria-label="上一页 / Previous">←</button><select id="designer" aria-label="选择设计师 / Choose designer">{options}</select><button id="page-next" aria-label="下一页 / Next">→</button></div><a href="CSM-MA-2026-ZH-EN.pdf">PDF · 23页 / pages ↗</a></nav>'''
(OUT/'index.html').write_text(shell('23位设计师 / 23 designers',toolbar+'<main class="deck">'+''.join(slides)+'</main>','<script src="slides.js"></script>'),encoding='utf-8')
(OUT/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Built bilingual 23-slide deck and individual single-page views.')

groups=[]
for r in processes['routes']+[{'id':None,'zh':'资料不足，暂不归类','en':'Insufficient evidence','anchor':'s26','w1_anchor':'slide-evidence-limit','chain':'先补充资料，再判断入口。','chain_en':'Gather evidence before assigning a route.','w1':'判断必须有可核对的依据。','evidence':'设计陈述、样布、草图、制作与试穿记录。'}]:
    rows=[]
    for d in data['designers']:
        c=processes['designers'][d['slug']]
        if c['primary']!=r['id']:continue
        rows.append(f'''<tr><td><a href="index.html#{d['slug']}"><b>{H(d['name'])} ↗</b></a><small>{H(c['status'])}</small></td><td>{H(c['basis_zh'])}<small>{H(c['basis_en'])}</small></td><td><a href="../womenswear_design_iii_week01.html#{c['w1_anchor']}">W01 ↗</a> {H(c['w1'])}<hr><a href="../womenswear_design_iii_week02.html#{c['w2_anchor']}">W02 ↗</a> {H(c['task'])}<small>{H(c['task_en'])}</small></td></tr>''')
    groups.append(f'''<section class="route-card" id="route-{r['id'] or 'unknown'}"><h2>{r['id'] or '—'} · {r['zh']} <small>{r['en']}</small></h2><p class="chain">{r['chain']}<small>{r['chain_en']}</small></p><p><a href="../womenswear_design_iii_week01.html#{r['w1_anchor']}">W01 ↗</a> {r['w1']}</p><p><a href="../womenswear_design_iii_week02.html#{r['anchor']}">W02 ↗</a> 应留下的证据 / REQUIRED EVIDENCE: {r['evidence']}</p><table><thead><tr><th>设计师 / Designer</th><th>分类依据 / Rationale</th><th>课程连接与实验 / Course links & tests</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>''')
overview=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>7种设计流程 / 7 Design Processes</title><link rel="stylesheet" href="processes.css"></head><body><nav><a href="index.html">← 23位设计师 / 23 Designers</a><a href="../womenswear_design_iii_week02.html#s18">第02周原框架 / W02 Framework ↗</a></nav><main><header><p>WEEK 01 × WEEK 02 × CSM MA 2026</p><h1>七种入口，一条证据链。<small>Seven entry points. One evidence chain.</small></h1><p>{processes['note_zh']}<br>{processes['note_en']}</p><p><b>⑥仅有候选，不能把‘适合日常穿着’当作市场流程的证明；Yodea Marquel暂不归类。</b><br>Route 6 has a candidate only: everyday wearability does not prove a market-led process. Yodea Marquel remains unclassified.</p></header>{''.join(groups)}</main></body></html>'''
(OUT/'processes.html').write_text(overview,encoding='utf-8')
