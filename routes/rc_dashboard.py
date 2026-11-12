from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

router = APIRouter()

_RC_DASHBOARD = r"""<!doctype html>
<head>
<title>PC Remote Control</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#111;--bg2:#1c1c1c;--text:#e3e3e3;--dim:#888;--accent:#0078d4;--border:rgba(255,255,255,.08);color-scheme:dark}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);color:var(--text);font:13px/1.5 "Segoe UI",system-ui,sans-serif;overflow:hidden}
button{background:none;border:none;cursor:pointer;color:var(--text);font:inherit;border-radius:4px}
button:hover{background:rgba(255,255,255,.07)}
input{background:#1e1e1e;border:1px solid var(--border);color:var(--text);font:inherit;border-radius:4px;padding:7px 10px;outline:none;width:100%}
input:focus{border-color:var(--accent)}
.btn-primary{background:var(--accent);color:#fff;padding:9px 20px;border-radius:4px;font-size:13px;cursor:pointer;border:none}
.btn-primary:hover{background:#106ebe}

/* Login */
#login{display:flex;align-items:center;justify-content:center;height:100vh}
#lbox{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:32px;width:320px;display:flex;flex-direction:column;gap:14px}
#lbox h2{font-size:20px;font-weight:600;text-align:center}
#lerr{color:#f87171;font-size:12px;text-align:center;display:none}
.fld label{font-size:11px;color:var(--dim);margin-bottom:3px;display:block}

/* Device pick */
#devscreen{display:none;height:100vh;flex-direction:column}
#devhdr{padding:14px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;background:var(--bg2)}
#devhdr h1{font-size:15px;font-weight:600}
#devlist{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.dcard{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:16px 18px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.dev-btns{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}
.dev-connect{background:var(--accent);color:#fff;padding:7px 14px;border-radius:4px;font-size:12px;font-weight:500;white-space:nowrap}
.dev-connect:hover{background:#106ebe}
.dev-connect.secondary{background:#2a2a2a;color:var(--text);border:1px solid var(--border)}
.dev-connect.secondary:hover{background:#333}
.dev-connect:disabled{opacity:0.4;cursor:not-allowed}

/* Viewer */
#viewer{display:none;height:100vh;flex-direction:column}
#vbar{display:flex;align-items:center;gap:6px;padding:0 10px;height:40px;background:var(--bg2);border-bottom:1px solid var(--border);flex-shrink:0;font-size:12px}
#vbar h2{font-size:13px;font-weight:600;margin-right:6px}
#vstatus{font-size:11px;color:var(--dim);margin-left:auto}
#vwrap{flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000;position:relative;cursor:none}
#screen{max-width:100%;max-height:100%;display:block;user-select:none}
#cursor{position:absolute;width:16px;height:16px;pointer-events:none;transform:translate(-50%,-50%)}
#cursor::before{content:"";position:absolute;top:0;left:0;width:0;height:0;border-style:solid;border-width:0 6px 12px 0;border-color:transparent #fff transparent transparent}
#noconn{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--dim)}

@media(max-width:600px){
  #devhdr{padding:10px 14px}
  #devhdr h1{font-size:13px}
  #devlist{padding:12px}
  .dcard{padding:12px 14px;gap:8px}
  .dev-btns{width:100%;margin-left:0;justify-content:flex-start}
  .dev-connect{flex:1;min-width:70px;text-align:center;padding:7px 8px}
}
</style>
</head>
<body>

<!-- Login -->
<div id="login">
  <div id="lbox">
    <h2>🖥 Remote Control</h2>
    <div class="fld"><label>Username</label><input id="lu" type="text" value="samar"></div>
    <div class="fld"><label>Password</label><input id="lp" type="password"></div>
    <div id="lerr">Wrong username or password</div>
    <button class="btn-primary" id="lbtn">Login</button>
  </div>
</div>

<!-- Device list -->
<div id="devscreen">
  <div id="devhdr">
    <h1>🖥 Remote Control — Select PC</h1>
    <button onclick="rcLogout()" style="padding:5px 12px;border:1px solid var(--border);border-radius:4px;font-size:12px">Logout</button>
  </div>
  <div id="devlist">
    <div id="nodev" style="text-align:center;color:var(--dim);padding:40px;font-size:13px">No PC has Remote Control installed.<br><br>Install it from PC Sync → Terminal:<br><code style="font-size:11px;color:#60cdff">run_remote_control_install</code></div>
  </div>
</div>

<!-- Screen viewer -->
<div id="viewer">
  <div id="vbar">
    <button onclick="backToDevs()" style="padding:4px 10px;border:1px solid var(--border);border-radius:4px;font-size:12px">← Back</button>
    <h2 id="vdevname">Remote PC</h2>
    <button onclick="toggleFullscreen()" style="padding:4px 10px;border:1px solid var(--border);border-radius:4px;font-size:12px">⛶ Fullscreen</button>
    <span id="vstatus">Connecting…</span>
  </div>
  <div id="vwrap">
    <img id="screen" alt="" src="">
    <div id="cursor"></div>
    <div id="noconn">Waiting for screen data…</div>
  </div>
</div>

<script>
"use strict";
let TOK = localStorage.getItem("rc_tok") || "";
let WS = null;
let DEVID = "";
let SCALE_X = 1, SCALE_Y = 1;
let SCREEN_W = 0, SCREEN_H = 0;

function enc(s){return encodeURIComponent(s);}
function _encPS(ps){return btoa(String.fromCharCode(...new TextEncoder().encode(ps).reduce((a,b)=>{a.push(b,0);return a;},[])));}

// ── Login ────────────────────────────────────────────────────────────────────
async function doLogin(){
  const u = document.getElementById("lu").value.trim();
  const p = document.getElementById("lp").value;
  document.getElementById("lerr").style.display = "none";
  try{
    const r = await fetch("/api/login", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({u,p})});
    if(!r.ok){document.getElementById("lerr").style.display="block"; return;}
    const d = await r.json();
    TOK = d.token; localStorage.setItem("rc_tok", TOK);
    showDevs(); loadRCDevs();
  }catch{document.getElementById("lerr").style.display="block";}
}
document.getElementById("lbtn").onclick = doLogin;
document.getElementById("lp").onkeydown = e => e.key==="Enter" && doLogin();

function rcLogout(){TOK=""; DEVID=""; localStorage.removeItem("rc_tok"); showLogin();}
function showLogin(){document.getElementById("login").style.display="flex";document.getElementById("devscreen").style.display="none";document.getElementById("viewer").style.display="none";}
function showDevs(){document.getElementById("login").style.display="none";document.getElementById("devscreen").style.display="flex";document.getElementById("viewer").style.display="none";}
function showViewer(){document.getElementById("login").style.display="none";document.getElementById("devscreen").style.display="none";document.getElementById("viewer").style.display="flex";}

// ── Device list ───────────────────────────────────────────────────────────────
async function loadRCDevs(){
  try{
    const r = await fetch("/api/rc-devices?t="+TOK);
    if(r.status===401){rcLogout();return;}
    const devs = await r.json();
    const el = document.getElementById("devlist");
    el.querySelectorAll(".dcard").forEach(c=>c.remove());
    document.getElementById("nodev").style.display = devs.length?"none":"block";
    devs.forEach(d=>{
      const c = document.createElement("div"); c.className="dcard";
      const statusColor = d.online ? "#34d399" : "#f87171";
      const statusTxt   = d.online ? "● Online" : "● Offline";
      const name = d.name || d.id;
      c.innerHTML = `<span style="font-size:28px">🖥</span><div style="min-width:0"><div style="font-size:14px;font-weight:600">${name}</div><div style="font-size:11px;color:${statusColor};margin-top:2px">${statusTxt}</div></div>`;
      const btns = document.createElement("div"); btns.className="dev-btns";

      const connectBtn = document.createElement("button");
      connectBtn.className="dev-connect"; connectBtn.textContent="▶ View Screen";
      connectBtn.disabled = !d.online;
      if(d.online) connectBtn.onclick = () => connectDevice(d.id, name);
      btns.appendChild(connectBtn);

      const vdBtn = document.createElement("button");
      vdBtn.className="dev-connect secondary"; vdBtn.id="vd-btn-"+d.id;
      vdBtn.textContent="🖥️ Virtual Display";
      vdBtn.disabled = !d.online;
      if(d.online){
        vdBtn.onclick = () => installVirtualDisplay(d.id);
        checkVirtualDisplay(d.id);
      }
      btns.appendChild(vdBtn);

      c.appendChild(btns); el.appendChild(c);
    });
    setTimeout(loadRCDevs, 8000);
  }catch{}
}

// ── Virtual Display status check ──────────────────────────────────────────────
function checkVirtualDisplay(did){
  // no-op: virtual desktop is stateless from server side
}

// ── Create Virtual Desktop (Windows CreateDesktopW via agent) ─────────────────
async function installVirtualDisplay(did){
  const btn = document.getElementById("vd-btn-"+did);
  if(btn){btn.textContent="⏳ Creating…";btn.disabled=true;}
  try{
    const r=await fetch(`/api/rc-virtual-desktop?t=${TOK}&d=${enc(did)}`,{method:"POST"});
    const data=await r.json();
    if(data.ok){
      if(btn){btn.textContent="✅ Virtual Desktop On";btn.disabled=false;btn.style.background="#065f46";btn.style.color="#6ee7b7";btn.style.border="1px solid #059669";}
    } else {
      alert("Virtual Desktop failed: "+(data.detail||"unknown error"));
      if(btn){btn.textContent="🖥️ Virtual Display";btn.disabled=false;}
    }
  }catch(e){
    alert("Error: "+e.message);
    if(btn){btn.textContent="🖥️ Virtual Display";btn.disabled=false;}
  }
}

// ── Screen viewer ─────────────────────────────────────────────────────────────
function connectDevice(id, name){
  DEVID = id;
  document.getElementById("vdevname").textContent = name || id;
  showViewer();
  openWS(id);
}

function openWS(did){
  if(WS){WS.close(); WS=null;}
  const proto = location.protocol==="https:"?"wss":"ws";
  WS = new WebSocket(`${proto}://${location.host}/ws/rc-viewer?device_id=${encodeURIComponent(did)}`);
  WS.onopen = () => {document.getElementById("vstatus").textContent = "Connected";};
  WS.onclose = () => {
    document.getElementById("vstatus").textContent = "Disconnected — reconnecting…";
    setTimeout(()=>DEVID&&openWS(DEVID), 3000);
  };
  WS.onmessage = e => {
    try{
      const msg = JSON.parse(e.data);
      if(msg.type==="frame" && msg.data){
        const img = document.getElementById("screen");
        img.src = "data:image/jpeg;base64," + msg.data;
        document.getElementById("noconn").style.display = "none";
        img.onload = () => {
          SCREEN_W = img.naturalWidth; SCREEN_H = img.naturalHeight;
          const rect = img.getBoundingClientRect();
          SCALE_X = SCREEN_W / rect.width;
          SCALE_Y = SCREEN_H / rect.height;
        };
      } else if(msg.type==="viewer_count"){
        document.getElementById("vstatus").textContent = "Connected · " + msg.count + " viewer" + (msg.count!==1?"s":"");
      }
    }catch{}
  };
}

function backToDevs(){
  if(WS){WS.close();WS=null;} DEVID="";
  showDevs(); document.getElementById("devlist").querySelectorAll(".dcard").forEach(c=>c.remove());
  loadRCDevs();
}

function toggleFullscreen(){
  if(!document.fullscreenElement) document.getElementById("vwrap").requestFullscreen().catch(()=>{});
  else document.exitFullscreen();
}

// ── Input capture ─────────────────────────────────────────────────────────────
const wrap = document.getElementById("vwrap");
const cur = document.getElementById("cursor");

function toPC(e){
  const img = document.getElementById("screen");
  const rect = img.getBoundingClientRect();
  return {
    x: Math.round((e.clientX - rect.left) * SCALE_X),
    y: Math.round((e.clientY - rect.top) * SCALE_Y)
  };
}

function send(action){
  if(WS && WS.readyState===1) WS.send(JSON.stringify({type:"input", action}));
}

wrap.addEventListener("mousemove", e => {
  const {x,y} = toPC(e);
  cur.style.left = e.clientX - wrap.getBoundingClientRect().left + "px";
  cur.style.top = e.clientY - wrap.getBoundingClientRect().top + "px";
  send({type:"mousemove", x, y});
});

wrap.addEventListener("mousedown", e => {
  e.preventDefault();
  const {x,y} = toPC(e);
  send({type:"mousedown", x, y, button: e.button});
});

wrap.addEventListener("mouseup", e => {
  const {x,y} = toPC(e);
  send({type:"mouseup", x, y, button: e.button});
});

wrap.addEventListener("click", e => {
  e.preventDefault();
  const {x,y} = toPC(e);
  send({type:"click", x, y, button: e.button});
});

wrap.addEventListener("dblclick", e => {
  e.preventDefault();
  const {x,y} = toPC(e);
  send({type:"dblclick", x, y});
});

wrap.addEventListener("contextmenu", e => e.preventDefault());

wrap.addEventListener("wheel", e => {
  e.preventDefault();
  send({type:"scroll", dx: Math.round(e.deltaX), dy: Math.round(e.deltaY)});
}, {passive:false});

document.addEventListener("keydown", e => {
  if(document.getElementById("viewer").style.display==="none") return;
  e.preventDefault();
  send({type:"keydown", key: e.key});
});

// ── Boot ─────────────────────────────────────────────────────────────────────
if(TOK) showDevs(), loadRCDevs();
else showLogin();
</script>
</body>
</html>
"""

@router.get("/rc", response_class=HTMLResponse)
async def rc_root():
    return HTMLResponse(_RC_DASHBOARD)


@router.post("/api/rc-virtual-desktop")
async def api_rc_virtual_desktop(t: str = Query(...), d: str = Query(...)):
    from .utils import _auth
    from .state import rc_devices
    import json
    _auth(t)
    if d not in rc_devices:
        raise HTTPException(503, "Device offline")
    await rc_devices[d]["ws"].send_text(json.dumps({"type": "virtual_desktop"}))
    return {"ok": True}
