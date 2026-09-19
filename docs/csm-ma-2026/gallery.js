let links=[...document.querySelectorAll('.image-link')];
const viewer=document.querySelector('#viewer'),stage=document.querySelector('#stage'),large=document.querySelector('#large');
let index=0,zoom=1,opener=null;
function resize(){if(!large.naturalWidth)return;const fit=Math.min(stage.clientWidth/large.naturalWidth,stage.clientHeight/large.naturalHeight);large.style.width=Math.round(large.naturalWidth*fit*zoom)+'px';large.style.height=Math.round(large.naturalHeight*fit*zoom)+'px';document.querySelector('#zoom').textContent=Math.round(zoom*100)+'%';}
function show(next){index=(next+links.length)%links.length;zoom=1;const link=links[index];large.alt=link.querySelector('img').alt;large.src=link.href;document.querySelector('#original').href=link.href;document.querySelector('#counter').textContent=`${index+1} / ${links.length} · ${large.alt}`;stage.scrollTo(0,0);if(large.complete)resize();}
function setZoom(value){zoom=Math.min(5,Math.max(1,value));resize();}
links.forEach(link=>link.addEventListener('click',event=>{event.preventDefault();links=[...link.closest('.slide').querySelectorAll('.image-link')];opener=link;viewer.showModal();document.body.classList.add('modal-open');show(links.indexOf(link));}));
large.addEventListener('load',resize);
document.querySelector('#close').onclick=()=>viewer.close();
viewer.addEventListener('close',()=>{document.body.classList.remove('modal-open');opener?.focus();});
document.querySelector('#previous').onclick=()=>show(index-1);
document.querySelector('#next').onclick=()=>show(index+1);
document.querySelector('#plus').onclick=()=>setZoom(zoom+.5);
document.querySelector('#minus').onclick=()=>setZoom(zoom-.5);
document.querySelector('#zoom').onclick=()=>setZoom(1);
viewer.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();show(index+1);}if(e.key==='ArrowLeft'){e.preventDefault();show(index-1);}if(e.key==='+'||e.key==='='){e.preventDefault();setZoom(zoom+.5);}if(e.key==='-'){e.preventDefault();setZoom(zoom-.5);}});
window.addEventListener('resize',resize);
