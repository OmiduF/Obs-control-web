#!/usr/bin/env python3
"""
OBS Control Deck - server local
================================
Ruleaza panoul (Auto Switch + Timer + Materiale) local pe PC-ul tau.

Cum folosesti:
  1. Ai nevoie de Python 3 instalat.
  2. Dublu-click pe acest fisier SAU in terminal:  python obs_control_server.py
  3. Se deschide singur in browser la  http://localhost:8080
  4. In OBS: Tools -> WebSocket Server Settings -> Enable WebSocket server (ia portul si parola).
  5. In pagina: pune portul + parola, apasa Conecteaza, alege scenele/sursele.

Optional alt port:  python obs_control_server.py 9000

Lasa fereastra de terminal deschisa cat timp folosesti panoul. Ctrl+C ca sa opresti.
"""

import http.server
import socketserver
import threading
import webbrowser
import sys

PORT = 8080
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

HTML = r'''<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>OBS Control Deck</title>
<style>
  :root{
    --bg:#0a0b0d;--panel:#141619;--panel2:#1b1e23;--line:#262a31;--text:#e7eaee;
    --muted:#8b929e;--accent:#23e5a4;--accent2:#14c2ff;--danger:#ff5c6c;--warn:#ffcc4d;
  }
  *{box-sizing:border-box}
  body{
    margin:0;min-height:100vh;color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
    background:
      radial-gradient(900px 500px at 85% -10%,rgba(35,229,164,.08),transparent 60%),
      radial-gradient(700px 500px at 0% 110%,rgba(20,194,255,.07),transparent 55%),var(--bg);
  }
  .shell{max-width:940px;margin:0 auto;padding:44px 20px 40px}
  .badge{display:inline-flex;align-items:center;gap:8px;font-size:12px;letter-spacing:2px;
    color:var(--accent);border:1px solid rgba(35,229,164,.3);background:rgba(35,229,164,.06);
    padding:6px 12px;border-radius:999px;font-family:monospace}
  h1{font-size:clamp(32px,6vw,52px);font-weight:800;margin:14px 0 8px;letter-spacing:-1.5px}
  .sub{color:var(--muted);max-width:560px;line-height:1.6;margin:0 0 26px}
  .conn{display:flex;flex-wrap:wrap;align-items:center;gap:12px;justify-content:space-between;
    background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);
    border-radius:16px;padding:14px 16px;margin-bottom:20px}
  .conn-fields{display:flex;gap:8px;flex:1;flex-wrap:wrap;min-width:260px}
  input,select{background:#0e1013;border:1px solid var(--line);border-radius:9px;padding:10px 12px;
    color:var(--text);font-size:13px;font-family:monospace;outline:none;transition:.2s}
  input:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(35,229,164,.12)}
  input:disabled,select:disabled{opacity:.5}
  .conn input{flex:1;min-width:110px}
  .conn .port{max-width:88px;flex:none}
  .pill{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-family:monospace;
    padding:6px 10px;border-radius:999px;border:1px solid var(--line);white-space:nowrap}
  .st-off{color:var(--muted)} .st-wait{color:var(--warn)}
  .st-on{color:var(--accent);border-color:rgba(35,229,164,.4);background:rgba(35,229,164,.08)}
  .dot{width:9px;height:9px;border-radius:50%;background:currentColor;display:inline-block}
  .tabs{display:flex;gap:6px;background:#0e1013;border:1px solid var(--line);border-radius:12px;padding:5px;margin-bottom:16px}
  .tab{flex:1;background:transparent;border:none;color:var(--muted);font-weight:700;font-size:14px;
    padding:11px;border-radius:8px;cursor:pointer;transition:.2s}
  .tab:hover{color:var(--text)}
  .tab.active{background:rgba(35,229,164,.12);color:var(--accent)}
  .card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);
    border-radius:18px;padding:24px;margin-bottom:20px;box-shadow:0 20px 40px -30px rgba(0,0,0,.9)}
  .desc{color:var(--muted);font-size:13.5px;line-height:1.6;margin:0 0 20px}
  .desc b{color:var(--text)}
  .panel{display:none} .panel.active{display:block}
  label.f{display:flex;flex-direction:column;gap:7px}
  label.f>span{font-size:11.5px;color:var(--muted);font-family:monospace}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  @media(max-width:620px){.grid2{grid-template-columns:1fr}}
  .rule{display:flex;align-items:flex-end;gap:12px;background:#0e1013;border:1px solid var(--line);
    border-radius:12px;padding:14px;margin-bottom:12px}
  .rule .f{flex:1}
  .arrow{color:var(--accent);font-size:20px;margin-bottom:8px}
  .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:none;border-radius:12px;
    padding:13px 18px;font-weight:700;font-size:14px;cursor:pointer;transition:transform .12s,background .2s}
  .btn:hover:not(:disabled){transform:translateY(-1px)}
  .btn:disabled{opacity:.45;cursor:not-allowed}
  .mini{padding:10px 14px;font-size:13px;border-radius:10px}
  .primary{background:linear-gradient(90deg,var(--accent),var(--accent2));color:#04211a}
  .ghost{background:transparent;color:var(--danger);border:1px solid rgba(255,92,108,.4)}
  .arm{background:#21252b;color:var(--text);border:1px solid var(--line)}
  .armed{background:rgba(35,229,164,.14);color:var(--accent);border:1px solid var(--accent);box-shadow:0 0 0 3px rgba(35,229,164,.1)}
  .icon{background:transparent;border:1px solid var(--line);color:var(--muted);border-radius:8px;padding:9px;cursor:pointer}
  .icon:hover{color:var(--danger);border-color:rgba(255,92,108,.4)}
  .actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px;align-items:center}
  .actions .btn{flex:1;min-width:200px}
  .timer-display{font-family:monospace;font-weight:700;font-size:clamp(56px,14vw,100px);text-align:center;
    color:var(--accent);letter-spacing:2px;margin:6px 0 22px;text-shadow:0 0 40px rgba(35,229,164,.25)}
  .timer-inputs{display:flex;gap:14px;justify-content:center;margin-bottom:18px}
  .timer-inputs .f{width:120px}
  .timer-inputs input{text-align:center;font-size:18px}
  .toggle{display:flex;align-items:center;gap:10px;cursor:pointer}
  .toggle input{display:none}
  .track{width:42px;height:24px;border-radius:999px;background:#2a2e35;position:relative;flex:none;transition:.2s}
  .thumb{position:absolute;top:3px;left:3px;width:18px;height:18px;border-radius:50%;background:#6b7280;transition:.2s}
  .toggle input:checked+.track{background:rgba(35,229,164,.25)}
  .toggle input:checked+.track .thumb{transform:translateX(18px);background:var(--accent)}
  .log-head{display:flex;align-items:center;gap:10px;margin-bottom:14px;color:var(--accent)}
  .log-head h2{font-size:16px;color:var(--text);margin:0;flex:1}
  .log{background:#0c0e11;border:1px solid var(--line);border-radius:12px;padding:10px;max-height:260px;
    overflow-y:auto;font-family:monospace}
  .lrow{display:flex;gap:12px;padding:6px 8px;border-radius:7px;font-size:12.5px;line-height:1.4}
  .lt{color:#5b6270;flex:none}
  .l-info{color:var(--muted)} .l-success{color:var(--accent)} .l-error{color:var(--danger)} .l-event{color:var(--accent2)}
  .empty{color:var(--muted);text-align:center;padding:26px 0}
  .foot{text-align:center;color:#4d5461;font-size:12px;font-family:monospace;margin-top:28px}
  .err{color:var(--danger);font-size:12.5px;font-family:monospace;flex-basis:100%;margin:2px 0 0}
</style>
</head>
<body>
<div class="shell">
  <div class="badge">OBS CONTROL DECK</div>
  <h1>Stream Automations</h1>
  <p class="sub">Auto switch, timer si materiale - conectare directa la OBS prin WebSocket. Ruleaza local pe PC-ul tau.</p>

  <div class="conn">
    <div class="conn-fields">
      <input id="host" placeholder="localhost sau IP (ex. 192.168.1.20)" />
      <input id="port" class="port" placeholder="4455" />
      <input id="pass" type="password" placeholder="parola WebSocket" />
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      <span id="status" class="pill st-off"><span class="dot"></span> Deconectat</span>
      <button id="connectBtn" class="btn mini primary">Conecteaza</button>
      <button id="disconnectBtn" class="btn mini ghost" style="display:none">Deconecteaza</button>
    </div>
    <div id="connErr" class="err" style="display:none"></div>
  </div>

  <div class="tabs">
    <button class="tab active" data-tab="switch">Auto Switch</button>
    <button class="tab" data-tab="timer">Timer</button>
    <button class="tab" data-tab="materials">Materiale</button>
  </div>

  <div class="card panel active" id="panel-switch">
    <p class="desc">Cand o sursa media se termina, comut pe scena aleasa. Poti adauga mai multe reguli (ex. <b>Play &#8594; Main</b>).</p>
    <div id="rules"></div>
    <div class="actions">
      <button id="addRule" class="btn mini arm" style="flex:none">+ Adauga regula</button>
      <button id="autoArm" class="btn arm">Porneste automatizarea</button>
    </div>
  </div>

  <div class="card panel" id="panel-timer">
    <p class="desc">Numaratoare inversa. La final comut pe <b>INTRO</b>; cand se termina materialul din INTRO, trec pe <b>MAIN</b>.</p>
    <div class="timer-display" id="tDisplay">05:00</div>
    <div class="timer-inputs">
      <label class="f"><span>Minute</span><input id="tMin" type="number" min="0" value="5" /></label>
      <label class="f"><span>Secunde</span><input id="tSec" type="number" min="0" max="59" value="0" /></label>
    </div>
    <div class="grid2">
      <label class="f"><span>Scena INTRO</span><select id="tIntro"></select></label>
      <label class="f"><span>Scena MAIN</span><select id="tMain"></select></label>
      <label class="f"><span>Media din INTRO (optional)</span><select id="tMedia"></select></label>
      <label class="f"><span>Text OBS pt. countdown (optional)</span><select id="tText"></select></label>
    </div>
    <div class="actions">
      <button id="tStart" class="btn primary">Start countdown</button>
      <button id="tStop" class="btn ghost" style="display:none">Stop</button>
      <button id="tReset" class="btn mini arm" style="flex:none">Reset</button>
    </div>
  </div>

  <div class="card panel" id="panel-materials">
    <p class="desc">Cand materialul din scena <b>MATERIALE</b> se termina, trec pe <b>MAIN</b>. Butonul de start comuta pe scena materiale si reporneste materialul.</p>
    <div class="grid2">
      <label class="f"><span>Scena MATERIALE</span><select id="mScene"></select></label>
      <label class="f"><span>Scena MAIN</span><select id="mMain"></select></label>
      <label class="f"><span>Sursa media (optional)</span><select id="mMedia"></select></label>
      <label class="toggle" style="align-self:end;padding-bottom:8px">
        <input id="mOnlyLive" type="checkbox" checked /><span class="track"><span class="thumb"></span></span>
        <span>Doar cand MATERIALE e live</span>
      </label>
    </div>
    <div class="actions">
      <button id="mStart" class="btn mini primary" style="flex:none">Start material</button>
      <button id="mArm" class="btn arm">Porneste automatizarea</button>
    </div>
  </div>

  <div class="card">
    <div class="log-head"><h2>Activitate</h2><button id="clearLog" class="icon">Sterge</button></div>
    <div class="log" id="log"><p class="empty">Niciun eveniment inca. Conecteaza-te si porneste o automatizare.</p></div>
  </div>

  <div class="foot">OBS WebSocket &#8226; ruleaza local &#8226; datele raman pe acest calculator</div>
</div>

<script>
"use strict";
let ws=null, connected=false, reqId=0;
const pending={}, mediaSubs=[];
let scenes=[], mediaInputs=[], textInputs=[];
const $ = (id)=>document.getElementById(id);

function log(msg,type){
  type=type||"info";
  const box=$("log");
  if(box.querySelector(".empty")) box.innerHTML="";
  const row=document.createElement("div");
  row.className="lrow";
  row.innerHTML='<span class="lt">'+new Date().toLocaleTimeString()+'</span><span class="l-'+type+'">'+msg+'</span>';
  box.insertBefore(row,box.firstChild);
  while(box.children.length>150) box.removeChild(box.lastChild);
}
async function sha256b64(str){
  const buf=await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
  return btoa(String.fromCharCode.apply(null,new Uint8Array(buf)));
}
async function makeAuth(pw,salt,challenge){
  const secret=await sha256b64(pw+salt);
  return await sha256b64(secret+challenge);
}
function setStatus(state){
  const el=$("status");
  const map={disconnected:["st-off","Deconectat"],connecting:["st-wait","Se conecteaza..."],connected:["st-on","Conectat"]};
  el.className="pill "+map[state][0];
  el.innerHTML='<span class="dot"></span> '+map[state][1];
  $("connectBtn").style.display = state==="connected" ? "none":"inline-flex";
  $("disconnectBtn").style.display = state==="connected" ? "inline-flex":"none";
  ["host","port","pass"].forEach(function(id){ $(id).disabled = state!=="disconnected"; });
}
function req(type,data){
  return new Promise(function(res,rej){
    if(!ws||ws.readyState!==1) return rej(new Error("neconectat"));
    const id=String(++reqId);
    pending[id]={res:res,rej:rej};
    ws.send(JSON.stringify({op:6,d:{requestType:type,requestId:id,requestData:data||{}}}));
    setTimeout(function(){ if(pending[id]){delete pending[id]; rej(new Error("timeout"));} },5000);
  });
}
async function refreshSources(){
  try{
    const sl=await req("GetSceneList");
    scenes=(sl.scenes||[]).map(function(s){return s.sceneName;});
    const il=await req("GetInputList");
    const inp=il.inputs||[];
    mediaInputs=inp.filter(function(i){return ["ffmpeg_source","vlc_source"].indexOf(i.inputKind)>=0;}).map(function(i){return i.inputName;});
    textInputs=inp.filter(function(i){return i.inputKind&&i.inputKind.indexOf("text")>=0;}).map(function(i){return i.inputName;});
    populateSelects();
    log("Scene: "+scenes.length+" - surse media: "+mediaInputs.length,"info");
  }catch(e){ log("Nu am putut citi scenele/sursele: "+e.message,"error"); }
}
async function switchScene(name){
  if(!name) return;
  try{ await req("SetCurrentProgramScene",{sceneName:name}); log('Comutat pe scena "'+name+'".',"success"); }
  catch(e){ log("Eroare la comutare: "+e.message,"error"); }
}
async function getCurrentScene(){
  try{ const r=await req("GetCurrentProgramScene"); return r.currentProgramSceneName||r.sceneName; }catch(e){ return null; }
}
function connect(){
  const host=$("host").value||"localhost", port=$("port").value||"4455", pass=$("pass").value;
  saveState(); $("connErr").style.display="none";
  setStatus("connecting"); log("Ma conectez la ws://"+host+":"+port+" ...");
  try{ ws=new WebSocket("ws://"+host+":"+port); }
  catch(e){ setStatus("disconnected"); showErr(e.message); return; }
  ws.onmessage=async function(ev){
    var m; try{ m=JSON.parse(ev.data); }catch(e){ return; }
    var op=m.op, d=m.d;
    if(op===0){
      var idf={op:1,d:{rpcVersion:1}};
      if(d.authentication){
        if(!(window.crypto&&crypto.subtle)){ showErr("Browserul nu permite crypto (foloseste Chrome/Edge)."); ws.close(); return; }
        idf.d.authentication=await makeAuth(pass,d.authentication.salt,d.authentication.challenge);
      }
      ws.send(JSON.stringify(idf));
    } else if(op===2){
      connected=true; setStatus("connected"); log("Conectat la OBS.","success"); refreshSources();
    } else if(op===7){
      var p=pending[d.requestId];
      if(p){ delete pending[d.requestId];
        if(d.requestStatus&&d.requestStatus.result) p.res(d.responseData||{});
        else p.rej(new Error((d.requestStatus&&d.requestStatus.comment)||"cerere esuata")); }
    } else if(op===5){
      if(d.eventType==="MediaInputPlaybackEnded"){
        var name=d.eventData.inputName;
        log('Media terminata: "'+name+'".',"event");
        mediaSubs.forEach(function(cb){ try{cb(name);}catch(e){} });
      }
    }
  };
  ws.onerror=function(){ showErr("Nu m-am putut conecta. Verifica portul, parola si ca OBS ruleaza cu WebSocket pornit."); };
  ws.onclose=function(){ connected=false; setStatus("disconnected"); log("Conexiune inchisa.","error"); };
}
function showErr(msg){ var e=$("connErr"); e.textContent=msg; e.style.display="block"; }
function disconnect(){ if(ws){ try{ws.close();}catch(e){} } ws=null; connected=false; setStatus("disconnected"); log("Deconectat."); }

function fillSelect(sel, opts, cfg){
  cfg=cfg||{};
  var cur=sel.value;
  sel.innerHTML="";
  var first=document.createElement("option");
  first.value=""; first.textContent = cfg.any ? cfg.anyLabel : "- alege scena -";
  sel.appendChild(first);
  opts.forEach(function(o){ var op=document.createElement("option"); op.value=o; op.textContent=o; sel.appendChild(op); });
  for(var i=0;i<sel.options.length;i++){ if(sel.options[i].value===cur){ sel.value=cur; break; } }
}
function populateSelects(){
  fillSelect($("tIntro"),scenes); fillSelect($("tMain"),scenes);
  fillSelect($("tMedia"),mediaInputs,{any:true,anyLabel:"orice media"});
  fillSelect($("tText"),textInputs,{any:true,anyLabel:"nu afisa in OBS"});
  fillSelect($("mScene"),scenes); fillSelect($("mMain"),scenes);
  fillSelect($("mMedia"),mediaInputs,{any:true,anyLabel:"orice sursa media"});
  var rows=$("rules").querySelectorAll(".rule");
  rows.forEach(function(row){
    fillSelect(row.querySelector(".r-src"),mediaInputs,{any:true,anyLabel:"orice sursa media"});
    fillSelect(row.querySelector(".r-tgt"),scenes);
  });
  loadRuleValues();
}

document.querySelectorAll(".tab").forEach(function(t){ t.onclick=function(){
  document.querySelectorAll(".tab").forEach(function(x){x.classList.remove("active");});
  document.querySelectorAll(".panel").forEach(function(x){x.classList.remove("active");});
  t.classList.add("active");
  $("panel-"+t.dataset.tab).classList.add("active");
};});

var autoArmed=false;
function addRule(src,tgt){
  src=src||""; tgt=tgt||"";
  var row=document.createElement("div");
  row.className="rule";
  row.innerHTML='<label class="f"><span>Sursa media</span><select class="r-src"></select></label>'+
    '<span class="arrow">&#8594;</span>'+
    '<label class="f"><span>Scena destinatie</span><select class="r-tgt"></select></label>'+
    '<button class="icon r-del">X</button>';
  $("rules").appendChild(row);
  fillSelect(row.querySelector(".r-src"),mediaInputs,{any:true,anyLabel:"orice sursa media"});
  fillSelect(row.querySelector(".r-tgt"),scenes);
  row.querySelector(".r-src").value=src; row.querySelector(".r-tgt").value=tgt;
  row.querySelector(".r-del").onclick=function(){ if($("rules").children.length>1){row.remove(); saveRules();} };
  row.querySelectorAll("select").forEach(function(s){ s.onchange=saveRules; });
}
$("addRule").onclick=function(){ addRule(); saveRules(); };
$("autoArm").onclick=function(){
  autoArmed=!autoArmed;
  $("autoArm").className="btn "+(autoArmed?"armed":"arm");
  $("autoArm").textContent=autoArmed?"Activ - ascult finalul media":"Porneste automatizarea";
  log(autoArmed?"[Auto Switch] PORNIT.":"[Auto Switch] oprit.",autoArmed?"success":"info");
};
mediaSubs.push(function(name){
  if(!autoArmed) return;
  var rows=$("rules").children;
  for(var i=0;i<rows.length;i++){
    var src=rows[i].querySelector(".r-src").value, tgt=rows[i].querySelector(".r-tgt").value;
    if(tgt && (!src||src===name)){ log('[Auto Switch] "'+name+'" -> "'+tgt+'".',"event"); switchScene(tgt); break; }
  }
});

var tInterval=null, tRemaining=0, tWaitingIntro=false;
function fmt(s){ s=Math.max(0,s); return String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0"); }
function renderTimer(){ $("tDisplay").textContent=fmt(tRemaining); }
async function pushText(t){ var ts=$("tText").value; if(!ts) return; try{ await req("SetInputSettings",{inputName:ts,inputSettings:{text:t}}); }catch(e){} }
$("tStart").onclick=function(){
  var total=(+$("tMin").value||0)*60+(+$("tSec").value||0);
  if(total<=0) return;
  clearInterval(tInterval); tRemaining=total; renderTimer(); pushText(fmt(total));
  $("tStart").style.display="none"; $("tStop").style.display="inline-flex"; tWaitingIntro=false;
  log("[Timer] Pornit "+fmt(total)+".");
  tInterval=setInterval(function(){
    tRemaining--; renderTimer(); pushText(fmt(Math.max(tRemaining,0)));
    if(tRemaining<=0){
      clearInterval(tInterval); tInterval=null;
      $("tStart").style.display="inline-flex"; $("tStop").style.display="none";
      log("[Timer] Gata -> comut pe INTRO.","event"); switchScene($("tIntro").value); tWaitingIntro=true;
    }
  },1000);
};
$("tStop").onclick=function(){ clearInterval(tInterval); tInterval=null; tWaitingIntro=false; $("tStart").style.display="inline-flex"; $("tStop").style.display="none"; };
$("tReset").onclick=function(){ clearInterval(tInterval); tInterval=null; tWaitingIntro=false; tRemaining=(+$("tMin").value||0)*60+(+$("tSec").value||0); renderTimer(); $("tStart").style.display="inline-flex"; $("tStop").style.display="none"; };
mediaSubs.push(function(name){
  if(!tWaitingIntro) return;
  var im=$("tMedia").value; if(im && name!==im) return;
  tWaitingIntro=false; log("[Timer] Intro terminat -> Main.","event"); switchScene($("tMain").value);
});

var matArmed=false;
$("mStart").onclick=async function(){
  var scene=$("mScene").value, media=$("mMedia").value;
  if(scene) await switchScene(scene);
  if(media){ try{ await req("TriggerMediaInputAction",{inputName:media,mediaAction:"OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"}); log('[Materiale] Pornesc "'+media+'".'); }catch(e){ log("Nu am putut porni materialul: "+e.message,"error"); } }
};
$("mArm").onclick=function(){
  matArmed=!matArmed;
  $("mArm").className="btn "+(matArmed?"armed":"arm");
  $("mArm").textContent=matArmed?"Activ - ascult finalul materialului":"Porneste automatizarea";
  log(matArmed?"[Materiale] PORNIT.":"[Materiale] oprit.",matArmed?"success":"info");
};
mediaSubs.push(async function(name){
  if(!matArmed) return;
  var media=$("mMedia").value; if(media && name!==media) return;
  var scene=$("mScene").value;
  if($("mOnlyLive").checked && scene){ var cur=await getCurrentScene(); if(cur!==scene){ log('[Materiale] Live e "'+cur+'", nu "'+scene+'" -> nu comut.',"info"); return; } }
  log('[Materiale] "'+name+'" -> "'+$("mMain").value+'".',"event"); switchScene($("mMain").value);
});

var FIELDS=["host","port","pass","tMin","tSec","tIntro","tMain","tMedia","tText","mScene","mMain","mMedia"];
function saveState(){
  var o={}; FIELDS.forEach(function(id){ o[id]=$(id).value; }); o.mOnlyLive=$("mOnlyLive").checked;
  localStorage.setItem("obs_deck_v1",JSON.stringify(o));
}
function loadState(){
  var o={}; try{ o=JSON.parse(localStorage.getItem("obs_deck_v1"))||{}; }catch(e){}
  FIELDS.forEach(function(id){ if(o[id]!==undefined && $(id)) $(id).value=o[id]; });
  if(o.mOnlyLive!==undefined) $("mOnlyLive").checked=o.mOnlyLive;
}
function saveRules(){
  var rules=[].map.call($("rules").children,function(r){ return {src:r.querySelector(".r-src").value,tgt:r.querySelector(".r-tgt").value}; });
  localStorage.setItem("obs_deck_rules_v1",JSON.stringify(rules));
}
var _savedRules=null;
function loadRuleValues(){
  if(!_savedRules) return;
  var rows=$("rules").children;
  _savedRules.forEach(function(r,i){ if(rows[i]){ rows[i].querySelector(".r-src").value=r.src||""; rows[i].querySelector(".r-tgt").value=r.tgt||""; } });
}

$("connectBtn").onclick=connect;
$("disconnectBtn").onclick=disconnect;
$("clearLog").onclick=function(){ $("log").innerHTML='<p class="empty">Niciun eveniment inca.</p>'; };
FIELDS.forEach(function(id){ $(id).addEventListener("change",saveState); });
$("mOnlyLive").addEventListener("change",saveState);
["tMin","tSec"].forEach(function(id){ $(id).addEventListener("input",function(){ if(!tInterval){ tRemaining=(+$("tMin").value||0)*60+(+$("tSec").value||0); renderTimer(); } }); });

(function init(){
  loadState();
  try{ _savedRules=JSON.parse(localStorage.getItem("obs_deck_rules_v1")); }catch(e){}
  if(_savedRules&&_savedRules.length){ _savedRules.forEach(function(r){ addRule(r.src,r.tgt); }); }
  else { addRule(); }
  renderTimer();
})();
</script>
</body>
</html>
'''


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    url = "http://localhost:%d" % PORT
    try:
        httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
    except OSError as e:
        print("Nu am putut porni pe portul %d (%s)." % (PORT, e))
        print("Incearca alt port:  python obs_control_server.py 9000")
        sys.exit(1)

    print("=" * 52)
    print(" OBS Control Deck ruleaza la:  %s" % url)
    print(" Lasa aceasta fereastra deschisa. Ctrl+C = stop.")
    print("=" * 52)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nInchid serverul. Pa!")
        httpd.shutdown()


if __name__ == "__main__":
    main()
