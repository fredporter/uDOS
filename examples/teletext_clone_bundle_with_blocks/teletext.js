function fitTeletext(){
  const root = document.documentElement;
  const vw = window.innerWidth - 16, vh = window.innerHeight - 32;
  const fsWidth = vw / (40 * 1.3);
  const fsHeight = vh / 25;
  const fs = Math.max(8, Math.floor(Math.min(fsWidth, fsHeight)));
  root.style.setProperty('--computed-font-size', fs + 'px');
}
function tickClock(){
  const e=document.getElementById('clock');
  if(!e) return;
  const n=new Date(); const p=n=>String(n).padStart(2,'0');
  e.textContent=`${p(n.getHours())}:${p(n.getMinutes())}:${p(n.getSeconds())}`;
}
window.addEventListener('resize',fitTeletext,{passive:true});
window.addEventListener('load',()=>{fitTeletext();tickClock();setInterval(tickClock,1000);});
