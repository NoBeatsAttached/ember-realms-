#!/usr/bin/env python3
"""Build index.html for GitHub Pages from src/game.html (the same file published as the Claude artifact).
Adds the home-screen app tags and the self-updater, and stamps a new build number into version.json.
Run from the repo root:  python3 tools/build.py"""
import time, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src = (root / 'src/game.html').read_text()
build = str(int(time.time()))

head_tags = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#081013">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Ember Realms">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="icon-192.png">
'''

updater = '''
<style>
#updBtn{position:fixed;left:50%;bottom:calc(16px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:40;padding:0 20px;height:46px;border-radius:23px;
 border:1px solid #f3d07c;background:linear-gradient(#f0c35e,#c88d24);color:#1d1405;font:700 16px 'Barlow Condensed','Arial Narrow',sans-serif;letter-spacing:.06em;
 box-shadow:0 6px 20px rgba(0,0,0,.5);cursor:pointer;white-space:nowrap;animation:updIn .35s ease}
@keyframes updIn{from{opacity:0;transform:translate(-50%,12px)}}
</style>
<button id="updBtn" hidden>Update ready · Tap to load</button>
<script>
/* Self-updater: home-screen apps on iPhone resume instead of reloading, so check for a newer build whenever
   the app comes to the front. Reloads on its own on the title or game-over screen; mid-run it waits and shows
   a button only when the game is paused or at the campfire, so it never interrupts a fight. */
(()=>{const BUILD='__BUILD__';let ready=false,checking=false;
 const $=id=>document.getElementById(id),btn=$('updBtn');
 const vis=id=>{const e=$(id);return e&&!e.hidden};
 const safe=()=>vis('menu')||vis('over');
 const calm=()=>vis('shop')||vis('pausem');
 const go=()=>location.reload();
 btn.onclick=go;
 function sync(){if(!ready)return;if(safe())go();else btn.hidden=!calm()}
 async function check(){if(checking||ready)return;checking=true;
  try{const r=await fetch('version.json?t='+Date.now(),{cache:'no-store'});if(r.ok){const v=await r.json();
   if(v.build&&v.build!==BUILD){ready=true;try{const reg=await navigator.serviceWorker?.getRegistration();await reg?.update()}catch(e){}sync()}}}catch(e){}
  checking=false}
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')check()});
 window.addEventListener('pageshow',check);window.addEventListener('focus',check);
 setInterval(()=>{if(ready)sync()},800);
 setInterval(check,60000);
 setTimeout(check,1500);
})();
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js',{updateViaCache:'none'}).catch(()=>{}))}
</script>
'''.replace('__BUILD__', build)

i = src.index('<canvas id="c"')
out = head_tags + src[:i] + '</head>\n<body>\n' + src[i:] + updater + '</body>\n</html>\n'
(root / 'index.html').write_text(out)
(root / 'version.json').write_text('{"build":"%s"}\n' % build)
print('built', build)
