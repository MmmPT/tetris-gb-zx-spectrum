'use strict';
const startButton=document.getElementById('start');
const host=document.getElementById('emulator');
const statusLine=document.getElementById('game-status');
const fullscreenButton=document.getElementById('fullscreen');
let emulator=null,ready=false;
const held=new Map();
function keyEvent(type,key,code){host.dispatchEvent(new KeyboardEvent(type,{key,code:key==='Enter'?'Enter':'Key'+key.toUpperCase(),keyCode:code,which:code,bubbles:true,cancelable:true}));}
startButton.addEventListener('click',()=>{
 if(emulator)return;
 if(typeof JSSpeccy!=='function'){statusLine.textContent='The emulator could not load. Please download the TAP or try refreshing the page.';return;}
 startButton.disabled=true;startButton.textContent='Loading the Spectrum…';statusLine.textContent='Starting Spectrum 128K emulation…';
 try{
  emulator=JSSpeccy(host,{machine:128,zoom:2,autoStart:true,openUrl:'dist/Tetris_GB.z80',sandbox:true,keyboardEventRoot:host});
  emulator.onReady(()=>{ready=true;document.getElementById('start-screen').hidden=true;fullscreenButton.disabled=false;statusLine.textContent='Ready. Press Enter to start. Q rotates · A drops · O/P move · M toggles music.';host.focus({preventScroll:true});});
  setTimeout(()=>{if(!ready)statusLine.textContent='Still loading. If your browser blocks WebAssembly, download the TAP to play in a Spectrum emulator.';},15000);
 }catch(error){statusLine.textContent='Browser play could not start. You can still watch the video or download the game.';startButton.disabled=false;startButton.textContent='Try again';if(emulator)emulator.exit();emulator=null;}
});
fullscreenButton.addEventListener('click',()=>{if(emulator&&ready)emulator.toggleFullscreen();});
function release(button){const data=held.get(button);if(!data)return;keyEvent('keyup',data.key,data.code);held.delete(button);button.classList.remove('held');}
for(const button of document.querySelectorAll('[data-key]')){
 button.addEventListener('pointerdown',event=>{if(!ready){statusLine.textContent='Press Play Tetris GB first to load the game.';return;}event.preventDefault();button.setPointerCapture(event.pointerId);host.focus({preventScroll:true});const key=button.dataset.key,code=Number(button.dataset.code);held.set(button,{key,code});button.classList.add('held');keyEvent('keydown',key,code);});
 for(const event of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(event,()=>release(button));
 button.addEventListener('keydown',event=>{if(!ready||event.repeat||!['Enter',' '].includes(event.key))return;event.preventDefault();const key=button.dataset.key,code=Number(button.dataset.code);held.set(button,{key,code});keyEvent('keydown',key,code);});
 button.addEventListener('keyup',event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();release(button);}});
 button.addEventListener('blur',()=>release(button));
}
window.addEventListener('blur',()=>{for(const button of held.keys())release(button);});
