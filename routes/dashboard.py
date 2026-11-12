from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_DASHBOARD = r"""<!doctype html>
<head>
<title>PC Sync</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#1c1c1c;--bg2:#252525;--bg3:#2e2e2e;--bg4:#383838;--text:#e3e3e3;--dim:#8a8a8a;--accent:#0078d4;--accentlt:#60cdff;--border:rgba(255,255,255,.08);--r:6px;color-scheme:dark}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);color:var(--text);font:13px/1.5 "Segoe UI",system-ui,sans-serif;overflow:hidden}
button{background:none;border:none;cursor:pointer;color:var(--text);font:inherit;border-radius:var(--r)}
button:hover{background:rgba(255,255,255,.07)}
input{background:var(--bg3);border:1px solid var(--border);color:var(--text);font:inherit;border-radius:var(--r);padding:8px 12px;outline:none;width:100%}
input:focus{border-color:var(--accent)}
::-webkit-scrollbar{width:7px}::-webkit-scrollbar-thumb{background:rgba(255,255,255,.15);border-radius:4px}

/* ── Login ── */
#login-screen{display:flex;align-items:center;justify-content:center;height:100vh}
#login-box{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:36px;width:340px;display:flex;flex-direction:column;gap:16px}
#login-box h2{font-size:22px;font-weight:600;text-align:center}
#login-box p{text-align:center;color:var(--dim);font-size:13px}
.btn-primary{background:var(--accent);color:#fff;padding:10px;border-radius:var(--r);font-size:14px;font-weight:500;width:100%;border:none;cursor:pointer}
.btn-primary:hover{background:#106ebe}
#login-err{color:#f87171;text-align:center;font-size:12px;display:none}
.field label{font-size:12px;color:var(--dim);margin-bottom:4px;display:block}

/* ── Device list ── */
#device-screen{display:none;height:100vh;flex-direction:column}
#dev-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;background:var(--bg2)}
#dev-header h1{font-size:16px;font-weight:600}
#btn-logout{padding:6px 12px;border-radius:var(--r);border:1px solid var(--border);font-size:13px}
#dev-list{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;align-items:center;gap:12px}
.dev-card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:18px 20px;display:flex;align-items:center;gap:12px;cursor:pointer;transition:border-color .15s;flex-wrap:wrap;width:100%;max-width:960px;box-sizing:border-box}
.dev-info{flex:1;min-width:0}
.dev-info h3{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dev-btns{display:flex;gap:6px;align-items:center;flex-shrink:0;flex-wrap:wrap}
.dev-card:hover{border-color:var(--accent)}
.dev-icon{font-size:32px}
.dev-info h3{font-size:15px;font-weight:600}
.dev-info p{font-size:12px;color:#34d399;margin-top:2px}
.dev-connect{margin-left:auto;background:var(--accent);color:#fff;padding:8px 20px;border-radius:var(--r);font-size:13px;font-weight:500}
.dev-connect:hover{background:#106ebe}
#no-devices{text-align:center;color:var(--dim);padding:60px 20px;font-size:14px}
#no-devices span{font-size:48px;display:block;margin-bottom:12px}

/* ── File Explorer ── */
#explorer-screen{display:none;height:100vh;flex-direction:column}
#toolbar{display:flex;align-items:center;gap:4px;padding:0 8px;height:46px;background:#1a1a1a;border-bottom:1px solid var(--border);flex-shrink:0}
.nav-btn{width:30px;height:30px;border-radius:var(--r);display:flex;align-items:center;justify-content:center;font-size:15px}
.nav-btn:disabled{opacity:.3;cursor:default}.nav-btn:disabled:hover{background:none}
#addr-bar{flex:1;display:flex;align-items:center;background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);height:30px;overflow:hidden;cursor:text;min-width:0}
#breadcrumb{display:flex;align-items:center;padding:0 8px;flex:1;min-width:0;white-space:nowrap;overflow:hidden;gap:2px}
.crumb{padding:2px 4px;border-radius:4px;cursor:pointer;font-size:12px}.crumb:hover{background:rgba(255,255,255,.07)}
.csep{color:var(--dim);font-size:12px}
#path-input{display:none;flex:1;background:transparent;border:none;padding:0 8px;height:100%;font-size:12px}
.tb-sep{width:1px;height:18px;background:var(--border);margin:0 2px;flex-shrink:0}
.vbtn{width:30px;height:30px;border-radius:var(--r);font-size:16px;display:flex;align-items:center;justify-content:center}
.vbtn.active{background:rgba(0,120,212,.35);color:var(--accentlt)}
#btn-back-dev{margin-left:auto;padding:5px 12px;border-radius:var(--r);border:1px solid var(--border);font-size:12px;flex-shrink:0}
#body{display:flex;flex:1;min-height:0}
#sidebar{width:200px;flex-shrink:0;background:var(--bg);border-right:1px solid var(--border);overflow-y:auto;padding:6px 0}
.nav-lbl{padding:10px 14px 3px;font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.nav-it{display:flex;align-items:center;gap:8px;padding:4px 14px;cursor:pointer;font-size:12px;min-height:28px;color:var(--text)}
.nav-it:hover{background:rgba(255,255,255,.07)}
.nav-ic{font-size:14px;width:18px;text-align:center;flex-shrink:0}
.nav-tx{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#content{flex:1;min-width:0;overflow-y:auto;padding:10px;position:relative;outline:none}
#loader{display:none;align-items:center;justify-content:center;height:160px}
.spin{width:26px;height:26px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
#empty{display:none;flex-direction:column;align-items:center;justify-content:center;height:160px;gap:6px;color:var(--dim);font-size:13px}
#grid{display:flex;flex-wrap:wrap;gap:3px;align-content:start}
.fi{width:96px;padding:6px 4px 5px;border-radius:var(--r);display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;user-select:none}
.fi:hover{background:rgba(255,255,255,.07)}
.fi.sel{background:rgba(0,120,212,.3);outline:1px solid #0078d4}
.ft{width:68px;height:68px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:26px;overflow:hidden;flex-shrink:0}
.ft img{width:100%;height:100%;object-fit:cover;border-radius:4px}
.fn{font-size:11px;text-align:center;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;width:100%;line-height:1.3}
#lst{display:none;flex-direction:column}
.li{display:flex;align-items:center;gap:8px;padding:3px 6px;border-radius:var(--r);cursor:pointer;min-height:28px;user-select:none}
.li:hover{background:rgba(255,255,255,.07)}.li.sel{background:rgba(0,120,212,.3);outline:1px solid #0078d4}
.lt{width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.lt img{width:20px;height:20px;object-fit:cover;border-radius:2px}
.ln{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}
.ld{width:130px;font-size:11px;color:var(--dim);flex-shrink:0;text-align:right}
.ls{width:75px;font-size:11px;color:var(--dim);flex-shrink:0;text-align:right}
.lh{display:flex;align-items:center;gap:8px;padding:3px 6px;border-bottom:1px solid var(--border);margin-bottom:3px;position:sticky;top:-10px;background:var(--bg);z-index:1}
.lh span{font-size:10px;color:var(--dim);font-weight:600}
#statusbar{display:flex;align-items:center;justify-content:space-between;padding:0 10px;height:26px;background:#1a1a1a;border-top:1px solid var(--border);flex-shrink:0;font-size:11px;color:var(--dim);gap:10px}
#sb-l{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#sb-r{flex-shrink:0;display:flex;gap:14px}

/* colors */
.ft-folder{background:rgba(251,191,36,.12);color:#fbbf24}
.ft-image{background:rgba(34,197,94,.12);color:#22c55e}
.ft-video{background:rgba(168,85,247,.12);color:#a855f7}
.ft-audio{background:rgba(236,72,153,.12);color:#ec4899}
.ft-pdf{background:rgba(239,68,68,.12);color:#ef4444}
.ft-word{background:rgba(59,130,246,.12);color:#3b82f6}
.ft-excel{background:rgba(34,197,94,.12);color:#16a34a}
.ft-zip{background:rgba(234,179,8,.12);color:#ca8a04}
.ft-code{background:rgba(6,182,212,.12);color:#06b6d4}
.ft-text{background:rgba(148,163,184,.12);color:#94a3b8}
.ft-exe{background:rgba(100,116,139,.12);color:#64748b}

/* ctx */
#ctx{position:fixed;background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:4px;min-width:180px;z-index:100;box-shadow:0 8px 24px rgba(0,0,0,.6);display:none}
#ctx.show{display:block}
.cx{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:var(--r);cursor:pointer;font-size:12px}
.cx:hover{background:rgba(255,255,255,.07)}
.cx-ic{width:16px;text-align:center;color:var(--dim)}
.cx-sep{height:1px;background:var(--border);margin:3px 0}

/* media */
#media{display:none;position:fixed;inset:0;z-index:200;align-items:center;justify-content:center}
#media.show{display:flex}
#media-bg{position:absolute;inset:0;background:rgba(0,0,0,.88)}
#media-inner{position:relative;z-index:1;border-radius:8px;overflow:hidden;max-width:92vw;max-height:92vh}
#media-inner img,#media-inner video{max-width:92vw;max-height:92vh;display:block}
#media-close{position:absolute;top:8px;right:8px;z-index:2;width:30px;height:30px;border-radius:50%;background:rgba(0,0,0,.7);font-size:16px;display:flex;align-items:center;justify-content:center;color:#fff}

/* upload */
#up-toast{position:fixed;bottom:36px;right:16px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:10px 14px;min-width:220px;box-shadow:0 6px 20px rgba(0,0,0,.5);z-index:150;display:none}
#up-toast.show{display:block}
#up-bar-bg{height:3px;background:var(--bg4);border-radius:2px;margin-top:6px;overflow:hidden}
#up-bar{height:100%;background:var(--accent);border-radius:2px;width:0;transition:width .2s}

/* remote panel */
#remote-panel{position:fixed;inset:46px 0 26px;z-index:110;display:none;flex-direction:column;background:var(--bg)}
#remote-panel.show{display:flex}
#rp-header{display:flex;align-items:center;gap:6px;padding:8px 12px;background:var(--bg2);border-bottom:1px solid var(--border);flex-shrink:0}
#rp-header h2{font-size:13px;font-weight:600;flex:1}
.rp-tab{padding:5px 12px;border-radius:var(--r);font-size:12px;font-weight:500;border:1px solid transparent}
.rp-tab.active{background:rgba(0,120,212,.3);color:var(--accentlt);border-color:rgba(0,120,212,.4)}
#rp-body{flex:1;display:flex;flex-direction:column;min-height:0;padding:10px 12px;gap:8px}
#rp-term{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
#rp-cmd-row{display:flex;gap:6px}
#rp-cmd{font-family:monospace;font-size:12px}
#rp-run{padding:7px 14px;background:var(--accent);color:#fff;border-radius:var(--r);font-size:12px;white-space:nowrap;flex-shrink:0}
#rp-run:hover{background:#106ebe}
#rp-run:disabled{opacity:.5;cursor:default}
#rp-out{flex:1;background:#0d0d0d;border:1px solid var(--border);border-radius:var(--r);padding:10px;font-family:'Consolas',monospace;font-size:11px;overflow-y:auto;white-space:pre-wrap;word-break:break-all;min-height:0;color:#d4d4d4;line-height:1.5}
#rp-procs{flex:1;display:none;flex-direction:column;gap:8px;min-height:0}
#rp-proc-hdr{display:flex;align-items:center;justify-content:space-between}
#rp-proc-list{flex:1;overflow-y:auto;border:1px solid var(--border);border-radius:var(--r);min-height:0}
.proc-row{display:flex;align-items:center;gap:6px;padding:5px 10px;border-bottom:1px solid rgba(255,255,255,.05);font-size:11px}
.proc-row:last-child{border-bottom:none}.proc-row:hover{background:rgba(255,255,255,.04)}
.proc-name{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.proc-pid{width:52px;color:var(--dim);flex-shrink:0}
.proc-mem{width:62px;text-align:right;color:var(--dim);flex-shrink:0}
.proc-kill{width:24px;height:22px;border-radius:4px;font-size:11px;color:#f87171;flex-shrink:0;display:flex;align-items:center;justify-content:center;padding:0}
.proc-kill:hover{background:rgba(248,113,113,.15)}

/* RC viewer panel */
#rc-panel{position:fixed;inset:0;z-index:300;display:none;flex-direction:column;background:#000}
#rc-panel.show{display:flex}
#rcvp-hdr{display:flex;align-items:center;padding:7px 12px;background:var(--bg2);border-bottom:1px solid var(--border);flex-shrink:0}
#rcvp-info{display:flex;align-items:center;gap:8px;min-width:0;flex-wrap:wrap}
#rcvp-hdr h2{font-size:13px;font-weight:600;margin-right:4px;white-space:nowrap}
#rcvp-fps{font-size:11px;color:var(--dim);min-width:48px}
#rcvp-status-txt{font-size:11px;color:var(--dim);white-space:nowrap}
#rcvp-body{flex:1;position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#111}
#rc-canvas{max-width:100%;max-height:100%;cursor:crosshair;display:block}
#rcvp-overlay{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:var(--dim);font-size:14px;pointer-events:none;text-align:center}

@media(max-width:580px){
  #sidebar{display:none}
  .ld,.ls{display:none}
  .fi{width:80px}
  .ft{width:56px;height:56px}

  /* Login */
  #login-box{width:92vw;padding:24px 18px}

  /* Device screen header */
  #dev-header{padding:12px 14px}
  #dev-header h1{font-size:13px}
  #btn-logout{padding:5px 10px;font-size:12px}
  #dev-list{padding:10px}

  /* Device card — stack buttons below info */
  .dev-card{flex-wrap:wrap;padding:12px 14px;gap:8px}
  .dev-btns{width:100%;margin-left:0!important;flex-wrap:wrap;justify-content:flex-start}
  .dev-connect{flex:1;min-width:80px;max-width:none;padding:7px 8px;font-size:12px;margin-left:0!important}

  /* Explorer toolbar */
  #toolbar{padding:0 4px;height:40px}
  #btn-back-dev{padding:4px 8px;font-size:11px}

  /* RC panel header */
  #rcvp-hdr{padding:6px 8px}
  #rcvp-info{gap:4px}
  #rcvp-hdr h2{font-size:12px}
  #rcvp-fps,#rcvp-status-txt{font-size:10px}

  /* RC controls bar */
  #rc-controls{flex-wrap:wrap;gap:4px;padding:6px 8px}
}

@media(max-width:400px){
  .dev-card{padding:10px 12px}
  #dev-header h1{font-size:12px}
  .dev-connect{font-size:11px;padding:6px 6px}
}
</style>
</head>
<body>

<!-- Login -->
<div id="login-screen">
  <div id="login-box">
    <h2>🖥 PC Sync</h2>
    <p>Login to access your PC remotely</p>
    <div class="field"><label>Username</label><input id="inp-u" type="text" value="samar" autocomplete="username"></div>
    <div class="field"><label>Password</label><input id="inp-p" type="password" autocomplete="current-password"></div>
    <div id="login-err">Wrong username or password</div>
    <button class="btn-primary" id="btn-login">Login</button>
  </div>
</div>

<!-- Device list -->
<div id="device-screen">
  <div id="dev-header">
    <h1>🖥 PC Sync — Your Devices</h1>
    <button id="btn-logout">Logout</button>
  </div>
  <div id="dev-list">
    <div id="no-devices"><span>💻</span>No PC connected.<br>Double-click PCSyncAgent.exe on your PC.</div>
  </div>
</div>

<!-- File Explorer -->
<div id="explorer-screen">
  <div id="toolbar">
    <button class="nav-btn" id="btn-back" disabled>&#8592;</button>
    <button class="nav-btn" id="btn-fwd"  disabled>&#8594;</button>
    <button class="nav-btn" id="btn-up">&#8593;</button>
    <button class="nav-btn" id="btn-ref">&#8635;</button>
    <div id="addr-bar">
      <div id="breadcrumb"></div>
      <input id="path-input" spellcheck="false">
    </div>
    <div class="tb-sep"></div>
    <button class="vbtn active" id="vg" title="Grid">&#9706;</button>
    <button class="vbtn"        id="vl" title="List">&#9776;</button>
    <div class="tb-sep"></div>
    <div class="tb-sep"></div>
    <button class="vbtn" id="btn-remote" title="Remote Control" onclick="openRemote()">&#9889;</button>
    <button id="btn-back-dev">&#8592; Devices</button>
  </div>
  <div id="body">
    <nav id="sidebar">
      <div class="nav-lbl">Quick access</div>
      <div id="qa-list"></div>
      <div class="nav-lbl">This PC</div>
      <div id="drv-list"></div>
      <div class="nav-lbl" style="margin-top:auto">System</div>
      <div style="padding:0 14px 8px">
        <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px"><span>CPU</span><span id="cpu-v">—</span></div>
        <div style="height:3px;border-radius:2px;background:var(--bg3);overflow:hidden;margin-bottom:8px"><div id="cpu-b" style="height:100%;background:var(--accent);width:0;transition:width .5s;border-radius:2px"></div></div>
        <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px"><span>RAM</span><span id="ram-v">—</span></div>
        <div style="height:3px;border-radius:2px;background:var(--bg3);overflow:hidden;margin-bottom:8px"><div id="ram-b" style="height:100%;background:#a855f7;width:0;transition:width .5s;border-radius:2px"></div></div>
      </div>
    </nav>
    <div id="content" tabindex="0">
      <div id="loader"><div class="spin"></div></div>
      <div id="empty"><span style="font-size:36px">📁</span>Empty folder</div>
      <div id="grid"></div>
      <div id="lst" style="display:none"></div>
    </div>
  </div>
  <div id="statusbar">
    <div id="sb-l">Ready</div>
    <div id="sb-r"><span id="sb-cpu">CPU —</span><span id="sb-ram">RAM —</span></div>
  </div>
</div>

<!-- Context menu -->
<div id="ctx">
  <div class="cx" id="cx-save"><span class="cx-ic">&#8681;</span> Save to this device</div>
  <div class="cx" id="cx-open"><span class="cx-ic">&#9654;</span> Open on PC</div>
  <div class="cx-sep"></div>
  <div class="cx" id="cx-path"><span class="cx-ic">&#128203;</span> Copy path</div>
  <div class="cx-sep"></div>
  <div class="cx" id="cx-rename"><span class="cx-ic">✏</span> Rename</div>
  <div class="cx" id="cx-delete"><span class="cx-ic" style="color:#f87171">🗑</span> Delete</div>
  <div class="cx-sep"></div>
  <div class="cx" id="cx-newfolder"><span class="cx-ic">📁</span> New Folder here</div>
</div>

<!-- Media modal -->
<div id="media">
  <div id="media-bg" onclick="closeMedia()"></div>
  <div id="media-inner">
    <button id="media-close" onclick="closeMedia()">&#10005;</button>
    <img  id="m-img" src="" alt="" style="display:none">
    <video id="m-vid" controls src="" style="display:none"></video>
  </div>
</div>

<!-- Upload toast -->
<div id="up-toast">
  <div id="up-msg" style="font-size:12px">Uploading…</div>
  <div id="up-bar-bg"><div id="up-bar"></div></div>
</div>

<!-- RC Viewer Panel -->
<div id="rc-panel">
  <div id="rcvp-hdr">
    <div id="rcvp-info">
      <h2>🖥 Remote Screen</h2>
      <span id="rcvp-title" style="font-size:12px;color:var(--dim)"></span>
      <span id="rcvp-fps"></span>
      <span id="rcvp-status-txt">Connecting…</span>
    </div>
    <button style="padding:5px 12px;border:1px solid var(--border);border-radius:var(--r);font-size:12px;flex-shrink:0;margin-left:8px" onclick="closeRCViewer()">✕ Close</button>
  </div>
  <div id="rcvp-body">
    <canvas id="rc-canvas"></canvas>
    <div id="rcvp-overlay">Connecting…</div>
  </div>
</div>

<!-- Remote panel -->
<div id="remote-panel">
  <div id="rp-header">
    <h2>⚡ Remote Control</h2>
    <button class="rp-tab active" id="rp-tab-term" onclick="rpTab('term')">Terminal</button>
    <button class="rp-tab" id="rp-tab-procs" onclick="rpTab('procs')">Processes</button>
    <button style="margin-left:auto;padding:5px 12px;border:1px solid var(--border);border-radius:var(--r);font-size:12px" onclick="closeRemote()">✕ Close</button>
  </div>
  <div id="rp-body">
    <div id="rp-term">
      <div id="rp-cmd-row">
        <input id="rp-cmd" placeholder="Enter command (e.g. dir C:\, tasklist, ipconfig)…" type="text">
        <button id="rp-run" onclick="runCmd()">▶ Run</button>
      </div>
      <div id="rp-out">Ready. Enter a command above and press Run.</div>
    </div>
    <div id="rp-procs">
      <div id="rp-proc-hdr">
        <span style="font-size:13px;font-weight:600">Running Processes</span>
        <button style="padding:5px 12px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);font-size:12px" onclick="loadProcesses()">↺ Refresh</button>
      </div>
      <div id="rp-proc-list"><div style="padding:20px;text-align:center;color:var(--dim)">Click Refresh to load processes</div></div>
    </div>
  </div>
</div>

<script>
"use strict";
// ── State ─────────────────────────────────────────────────────────────────────
let TOK = localStorage.getItem("pcsync_tok") || "";
let DEV = localStorage.getItem("pcsync_dev") || "";
const S = {
  path:"", files:[], filtered:[], sel:null,
  hist:[], histIdx:-1, view:"grid",
};

// ── Screen management ─────────────────────────────────────────────────────────
function show(id){
  ["login-screen","device-screen","explorer-screen"].forEach(s=>{
    document.getElementById(s).style.display = s===id ? (id.includes("screen") && id!=="login-screen" ? "flex" : "flex") : "none";
  });
}

// ── Login ─────────────────────────────────────────────────────────────────────
async function doLogin(){
  const u=document.getElementById("inp-u").value.trim();
  const p=document.getElementById("inp-p").value;
  document.getElementById("login-err").style.display="none";
  try{
    const r=await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({u,p})});
    if(!r.ok){document.getElementById("login-err").style.display="block";return;}
    const d=await r.json();
    TOK=d.token; localStorage.setItem("pcsync_tok",TOK);
    show("device-screen"); loadDevices();
  }catch(e){document.getElementById("login-err").style.display="block";}
}
document.getElementById("btn-login").onclick=doLogin;
["inp-u","inp-p"].forEach(id=>document.getElementById(id).addEventListener("keydown",e=>{if(e.key==="Enter")doLogin();}));

// ── Devices ───────────────────────────────────────────────────────────────────
async function loadDevices(){
  let ok=false;
  try{
    const [devR, rcR]=await Promise.all([fetch("/api/devices?t="+TOK),fetch("/api/rc-devices?t="+TOK)]);
    if(devR.status===401){logout();return;}
    const devs=await devR.json();
    const rcDevs=new Set((rcR.ok?await rcR.json():[]).filter(d=>d.online).map(d=>d.id));
    ok=true;
    // Only redraw if we got valid data — prevents flicker when server momentarily has empty state
    if(devs.length>0){
      const el=document.getElementById("dev-list");
      el.querySelectorAll(".dev-card").forEach(c=>c.remove());
      let nd=document.getElementById("no-devices");
      if(!nd){nd=document.createElement("div");nd.id="no-devices";nd.innerHTML='<span>\u{1F4BB}</span>No PC connected.<br>Double-click PCSyncAgent.exe on your PC.';el.prepend(nd);}
      nd.style.display="none";
      devs.forEach(d=>{
        const c=document.createElement("div");
        c.className="dev-card";
        const online=d.online!==false;
        const rcOnline=rcDevs.has(d.id);
        const statusDot=online?'<p style="color:#34d399">● Online</p>':'<p style="color:#f87171">● Offline</p>';
        let btnHtml;
        if(online){
            const rcBtn=rcOnline
            ?`<button class="dev-connect" style="background:#059669">🖥 View Screen</button>`
            :`<button class="dev-connect" style="background:#7c3aed" id="rc-btn-${esc(d.id)}">📥 Install RC</button>`;
          const vdBtn=rcOnline
            ?`<button class="dev-connect" style="background:#0369a1" id="vd-btn-${esc(d.id)}">🖥️ Virtual Display</button>`
            :``;
          btnHtml=`<button class="dev-connect">Open</button>${rcBtn}${vdBtn}`;
        }else{
          btnHtml=`<button class="dev-connect" style="opacity:.4;cursor:not-allowed">Offline</button>`;
        }
        const fmtTs=ts=>ts?new Date(ts*1000).toLocaleString('en-GB',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}):'';
        const dateLabel=online?`Connected: ${fmtTs(d.connected_at)}`:`Last seen: ${fmtTs(d.last_seen)}`;
        c.innerHTML=`<div class="dev-icon" style="${online?"":"opacity:.5"}">🖥</div><div class="dev-info"><h3>${esc(d.name)}<button onclick="renameDevice('${esc(d.id)}','${esc(d.name)}')" style="background:none;border:none;cursor:pointer;font-size:13px;margin-left:6px;opacity:.6" title="Rename">✏️</button></h3>${statusDot}<p style="font-size:11px;color:var(--dim);margin-top:2px">${dateLabel}</p></div><div class="dev-btns">${btnHtml}<button onclick="deleteDevice('${esc(d.id)}')" style="background:#ef4444;color:#fff;border:none;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:13px" title="Delete">🗑️</button></div>`;
        if(online){
          const btns=c.querySelectorAll(".dev-connect");
          if(btns[0]) btns[0].onclick=()=>openDevice(d.id,d.name);
          if(btns[1]) btns[1].onclick=rcOnline?()=>viewRC(d.id,d.name):()=>installRC(d.id);
          if(btns[2]&&rcOnline){ btns[2].onclick=()=>installVirtualDisplay(d.id); checkVirtualDisplay(d.id); }
        }
        el.appendChild(c);
      });
    }
  }catch{}
  // Always reschedule — faster when server had issues, normal when ok
  setTimeout(loadDevices, ok?8000:3000);
}

function openDevice(id,name){
  DEV=id; localStorage.setItem("pcsync_dev",id);
  show("explorer-screen");
  loadSidebar(); loadDrives();
  startStatsPoll();
}

document.getElementById("btn-logout").onclick=logout;
function logout(){
  TOK=""; DEV=""; localStorage.removeItem("pcsync_tok"); localStorage.removeItem("pcsync_dev");
  show("login-screen");
}
document.getElementById("btn-back-dev").onclick=()=>{show("device-screen");document.getElementById("dev-list").querySelectorAll(".dev-card").forEach(c=>c.remove());loadDevices();};

// ── Navigation ────────────────────────────────────────────────────────────────
async function navTo(path,push=true){
  if(path===""){ loadDrives(); return; }
  showLoad(true);
  try{
    const r=await api("/api/browse?path="+enc(path));
    if(r.error)throw new Error(r.error);
    if(push){S.hist=S.hist.slice(0,S.histIdx+1);S.hist.push(path);S.histIdx=S.hist.length-1;}
    S.path=r.path||path; S.files=r.items||[]; S.sel=null;
    render();
  }catch(e){alert("Cannot open: "+e.message);}
  finally{showLoad(false);}
}

async function loadDrives(){
  showLoad(true);
  try{
    const drives=await api("/api/drives");
    if(S.hist.length===0||S.hist[S.histIdx]!==""){S.hist=S.hist.slice(0,S.histIdx+1);S.hist.push("");S.histIdx=S.hist.length-1;}
    S.path=""; S.sel=null;
    S.files=(drives.items||drives||[]).map(d=>({name:d.device||d.mountpoint,path:d.mountpoint,is_dir:true,size:d.total,_drive:d}));
    render();
  }finally{showLoad(false);}
}

function goBack(){if(S.histIdx>0){S.histIdx--;navTo(S.hist[S.histIdx],false);}}
function goFwd() {if(S.histIdx<S.hist.length-1){S.histIdx++;navTo(S.hist[S.histIdx],false);}}
function goUp()  {
  if(!S.path){return;}
  const p=S.path.replace(/[/\\]+$/,"");
  const sep=p.includes("\\")?"\\":"/";
  const parts=p.split(/[/\\]/);
  if(parts.length<=1){loadDrives();return;}
  parts.pop(); navTo(parts.join(sep)||sep);
}

// ── API helper ────────────────────────────────────────────────────────────────
async function api(url){
  const sep=url.includes("?")?"&":"?";
  const r=await fetch(url+sep+"t="+TOK+"&d="+enc(DEV));
  if(r.status===401){logout();throw new Error("Session expired");}
  if(!r.ok)throw new Error(await r.text());
  return r.json();
}
function enc(s){return encodeURIComponent(s);}

// ── File types ────────────────────────────────────────────────────────────────
const IMG_E=new Set([".jpg",".jpeg",".png",".gif",".bmp",".webp",".ico",".tiff",".svg"]);
const VID_E=new Set([".mp4",".mkv",".avi",".mov",".wmv",".flv",".webm",".m4v"]);
const AUD_E=new Set([".mp3",".wav",".ogg",".flac",".aac",".m4a"]);
const COD_E=new Set([".js",".ts",".py",".java",".c",".cpp",".cs",".go",".rs",".php",".html",".css",".json",".xml",".yaml",".sh",".bat",".ps1"]);
const TXT_E=new Set([".txt",".md",".log",".ini",".cfg",".env"]);

function extOf(n){return (n.match(/\.[^.]+$/)||[""])[0].toLowerCase();}
function fclass(n,d){
  if(d)return "ft-folder";
  const e=extOf(n);
  if(IMG_E.has(e))return "ft-image";if(VID_E.has(e))return "ft-video";
  if(AUD_E.has(e))return "ft-audio";if(extOf(n)===".pdf")return "ft-pdf";
  if([".doc",".docx"].includes(e))return "ft-word";if([".xls",".xlsx",".csv"].includes(e))return "ft-excel";
  if([".zip",".rar",".7z",".tar",".gz"].includes(e))return "ft-zip";
  if(COD_E.has(e))return "ft-code";if(TXT_E.has(e))return "ft-text";
  if([".exe",".msi"].includes(e))return "ft-exe";
  return "ft-text";
}
function femoji(n,d){
  if(d)return "📁";const e=extOf(n);
  if(IMG_E.has(e))return "🖼";if(VID_E.has(e))return "🎬";if(AUD_E.has(e))return "🎵";
  if(e===".pdf")return "📕";if([".doc",".docx"].includes(e))return "📘";
  if([".xls",".xlsx",".csv"].includes(e))return "📗";
  if([".zip",".rar",".7z"].includes(e))return "🗜";
  if([".exe",".msi"].includes(e))return "⚙";return "📄";
}
function isImg(n){return IMG_E.has(extOf(n));}
function isVid(n){return VID_E.has(extOf(n));}

function fmtSz(b){
  if(!b&&b!==0)return "";
  if(b<1024)return b+" B";if(b<1048576)return (b/1024).toFixed(1)+" KB";
  if(b<1073741824)return (b/1048576).toFixed(1)+" MB";return (b/1073741824).toFixed(2)+" GB";
}
function fmtDt(iso){
  if(!iso)return "";try{const d=new Date(iso);return d.toLocaleDateString()+" "+d.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});}catch{return iso;}
}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}

// ── Render ────────────────────────────────────────────────────────────────────
function render(){
  updateNavBtns(); renderBreadcrumb();
  const items=[...S.files].sort((a,b)=>{
    if(a.is_dir!==b.is_dir)return a.is_dir?-1:1;
    return a.name.toLowerCase()<b.name.toLowerCase()?-1:1;
  });
  S.filtered=items;
  S.view==="grid"?renderGrid():renderList();
  updateStatus();
}

function renderGrid(){
  document.getElementById("lst").style.display="none";
  const g=document.getElementById("grid"); g.style.display="flex";
  const e=document.getElementById("empty");
  if(!S.filtered.length){g.innerHTML="";e.style.display="flex";return;}
  e.style.display="none";
  g.innerHTML=S.filtered.map((f,i)=>{
    const cl=fclass(f.name,f.is_dir),em=femoji(f.name,f.is_dir);
    const th=isImg(f.name)&&!f.is_dir
      ?`<img src="/api/thumbnail?t=${TOK}&d=${enc(DEV)}&path=${enc(f.path)}&size=120" alt="" loading="lazy" onerror="this.outerHTML='${em}'">`
      :em;
    return `<div class="fi${S.sel?.path===f.path?" sel":""}" data-i="${i}"
      onclick="onCl(event,${i})" ondblclick="onDbl(event,${i})" oncontextmenu="onCtx(event,${i})">
      <div class="ft ${cl}">${th}</div>
      <div class="fn">${esc(f.name)}</div>
    </div>`;
  }).join("");
}

function renderList(){
  document.getElementById("grid").style.display="none";
  const l=document.getElementById("lst"); l.style.display="flex";
  const e=document.getElementById("empty");
  if(!S.filtered.length){l.innerHTML="";e.style.display="flex";return;}
  e.style.display="none";
  const rows=S.filtered.map((f,i)=>{
    const cl=fclass(f.name,f.is_dir),em=femoji(f.name,f.is_dir);
    const th=isImg(f.name)&&!f.is_dir
      ?`<img src="/api/thumbnail?t=${TOK}&d=${enc(DEV)}&path=${enc(f.path)}&size=28" alt="" loading="lazy" onerror="this.outerHTML='${em}'">`
      :em;
    return `<div class="li${S.sel?.path===f.path?" sel":""}" data-i="${i}"
      onclick="onCl(event,${i})" ondblclick="onDbl(event,${i})" oncontextmenu="onCtx(event,${i})">
      <div class="lt ${cl}">${th}</div>
      <div class="ln">${esc(f.name)}</div>
      <div class="ld">${fmtDt(f.modified)}</div>
      <div class="ls">${f.is_dir?"":fmtSz(f.size)}</div>
    </div>`;
  }).join("");
  l.innerHTML=`<div class="lh"><div style="width:20px"></div><span class="ln" style="font-size:10px">Name</span><span class="ld">Date</span><span class="ls">Size</span></div>`+rows;
}

// ── Interactions ──────────────────────────────────────────────────────────────
let _ctx_f=null;
function onCl(e,i){e.stopPropagation();S.sel=S.filtered[i];renderHighlight();updateStatus();}
function onDbl(e,i){e.stopPropagation();const f=S.filtered[i];f.is_dir?navTo(f.path):openFile(f);}
function onCtx(e,i){e.preventDefault();e.stopPropagation();S.sel=_ctx_f=S.filtered[i];renderHighlight();showCtx(e.clientX,e.clientY);}
function openFile(f){
  if(isImg(f.name)||isVid(f.name)){openMedia(f);return;}
  saveFile(f.path);
}
function renderHighlight(){
  document.querySelectorAll(".fi,.li").forEach(el=>el.classList.toggle("sel",S.filtered[+el.dataset.i]?.path===S.sel?.path));
}

// ── Breadcrumb ────────────────────────────────────────────────────────────────
function renderBreadcrumb(){
  const bc=document.getElementById("breadcrumb");
  if(!S.path){bc.innerHTML=`<span class="crumb">💻 This PC</span>`;return;}
  const sep=S.path.includes("\\")?"\\":"/";
  const parts=S.path.replace(/[/\\]+$/,"").split(/[/\\]/);
  const crumbs=parts.map((p,i)=>{
    const fp=parts.slice(0,i+1).join(sep)||sep;
    return `<span class="csep">›</span><span class="crumb" data-p="${esc(fp)}">${i===0?"💻 ":""}${esc(p)}</span>`;
  });
  bc.innerHTML=`<span class="crumb" id="crumb-root">💻 This PC</span>`+crumbs.join("");
  bc.querySelectorAll(".crumb[data-p]").forEach(el=>el.onclick=()=>navTo(el.dataset.p));
  const cr=document.getElementById("crumb-root"); if(cr) cr.onclick=loadDrives;
}
function updateNavBtns(){
  document.getElementById("btn-back").disabled=S.histIdx<=0;
  document.getElementById("btn-fwd").disabled=S.histIdx>=S.hist.length-1;
}
function updateStatus(){
  const n=S.filtered.length;
  document.getElementById("sb-l").textContent=S.sel
    ?`${S.sel.name}  —  ${S.sel.is_dir?"Folder":fmtSz(S.sel.size)}`
    :`${n} item${n!==1?"s":""}`;
}

// ── Sidebar ───────────────────────────────────────────────────────────────────
async function loadSidebar(){
  try{
    const [qa,drives]=await Promise.all([api("/api/quick-access"),api("/api/drives")]);
    const QI={Desktop:"🖥",Downloads:"⬇",Documents:"📄",Pictures:"🖼",Music:"🎵",Videos:"🎬"};
    document.getElementById("qa-list").innerHTML=(qa.items||qa).filter(f=>f.exists).map(f=>`
      <div class="nav-it" data-path="${esc(f.path)}" onclick="navTo(this.dataset.path)">
        <span class="nav-ic">${QI[f.name]||"📁"}</span>
        <span class="nav-tx">${esc(f.name)}</span>
      </div>`).join("");
    const drvs=drives.items||drives||[];
    document.getElementById("drv-list").innerHTML=drvs.map(d=>{
      const pct=d.total>0?Math.round((d.used||0)/d.total*100):0;
      return `<div class="nav-it" data-path="${esc(d.mountpoint)}" onclick="navTo(this.dataset.path)">
        <span class="nav-ic">💽</span>
        <span class="nav-tx">${esc(d.device||d.mountpoint)}</span>
        <span style="font-size:10px;color:var(--dim);flex-shrink:0">${pct}%</span>
      </div>`;
    }).join("");
  }catch{}
}

// ── Stats polling ──────────────────────────────────────────────────────────────
let _statTimer;
async function startStatsPoll(){
  clearInterval(_statTimer);
  async function poll(){
    try{
      const s=await api("/api/stats");
      const cpu=s.cpu_percent||0,ram=s.memory?.percent||0;
      document.getElementById("cpu-v").textContent=cpu.toFixed(0)+"%";
      document.getElementById("ram-v").textContent=ram.toFixed(0)+"%";
      document.getElementById("cpu-b").style.width=cpu+"%";
      document.getElementById("ram-b").style.width=ram+"%";
      document.getElementById("sb-cpu").textContent=`CPU ${cpu.toFixed(0)}%`;
      document.getElementById("sb-ram").textContent=`RAM ${ram.toFixed(0)}%`;
    }catch{}
  }
  poll();
  _statTimer=setInterval(poll,5000);
}

// ── File save ─────────────────────────────────────────────────────────────────
async function saveFile(path){
  const name=path.replace(/\\/g,"/").split("/").pop();
  const url=`/api/download?t=${TOK}&d=${enc(DEV)}&path=${enc(path)}`;
  try{
    if(window.showSaveFilePicker){
      const ext=name.split(".").pop();
      const h=await window.showSaveFilePicker({suggestedName:name,types:[{description:"File",accept:{"application/octet-stream":["."+(ext||"bin")]}}]});
      const w=await h.createWritable();
      const res=await fetch(url);
      await res.body.pipeTo(w);
    }else{
      const a=document.createElement("a");a.href=url;a.download=name;a.click();
    }
  }catch(e){if(e.name!=="AbortError")alert("Download failed: "+e.message);}
}

async function openOnPC(path){
  try{await fetch(`/api/open-on-pc?t=${TOK}&d=${enc(DEV)}&path=${enc(path)}`,{method:"POST"});}
  catch(e){alert("Could not open: "+e.message);}
}

// ── Context menu ──────────────────────────────────────────────────────────────
function showCtx(x,y){
  const m=document.getElementById("ctx"); m.classList.add("show");
  m.style.left=Math.min(x,window.innerWidth-190)+"px";
  m.style.top=Math.min(y,window.innerHeight-120)+"px";
}
function hideCtx(){document.getElementById("ctx").classList.remove("show");}
document.getElementById("cx-save").onclick=()=>{hideCtx();_ctx_f&&!_ctx_f.is_dir&&saveFile(_ctx_f.path);};
document.getElementById("cx-open").onclick=()=>{hideCtx();_ctx_f&&openOnPC(_ctx_f.path);};
document.getElementById("cx-path").onclick=()=>{hideCtx();_ctx_f&&navigator.clipboard.writeText(_ctx_f.path).catch(()=>{});};
document.addEventListener("click",hideCtx);

// ── Media modal ───────────────────────────────────────────────────────────────
function openMedia(f){
  const url=`/api/download?t=${TOK}&d=${enc(DEV)}&path=${enc(f.path)}`;
  const img=document.getElementById("m-img"),vid=document.getElementById("m-vid");
  img.style.display="none";vid.style.display="none";
  if(isImg(f.name)){img.src=url;img.style.display="block";}
  else{vid.src=url;vid.style.display="block";vid.play().catch(()=>{});}
  document.getElementById("media").classList.add("show");
}
function closeMedia(){
  document.getElementById("media").classList.remove("show");
  const v=document.getElementById("m-vid");v.pause();v.src="";
}

// ── View toggle ───────────────────────────────────────────────────────────────
function setView(m){
  S.view=m;
  document.getElementById("vg").classList.toggle("active",m==="grid");
  document.getElementById("vl").classList.toggle("active",m==="list");
  render();
}

// ── Address bar ───────────────────────────────────────────────────────────────
document.getElementById("addr-bar").onclick=e=>{
  if(e.target.classList.contains("crumb"))return;
  document.getElementById("breadcrumb").style.display="none";
  const inp=document.getElementById("path-input");inp.style.display="block";inp.value=S.path;inp.focus();inp.select();
};
document.getElementById("path-input").onblur=()=>{
  document.getElementById("path-input").style.display="none";
  document.getElementById("breadcrumb").style.display="flex";
};
document.getElementById("path-input").onkeydown=e=>{
  if(e.key==="Enter"){navTo(e.target.value.trim());e.target.blur();}
  if(e.key==="Escape")e.target.blur();
};

// ── Keyboard shortcuts ────────────────────────────────────────────────────────
document.addEventListener("keydown",e=>{
  if(e.altKey&&e.key==="ArrowLeft"){e.preventDefault();goBack();}
  if(e.altKey&&e.key==="ArrowRight"){e.preventDefault();goFwd();}
  if(e.altKey&&e.key==="ArrowUp"){e.preventDefault();goUp();}
  if(e.key==="F5"){e.preventDefault();S.path?navTo(S.path,false):loadDrives();}
  if(e.key==="Escape"){closeMedia();hideCtx();}
  if(e.key==="Enter"&&S.sel&&document.activeElement?.id==="content"){
    S.sel.is_dir?navTo(S.sel.path):openFile(S.sel);
  }
});

// ── Toolbar buttons ───────────────────────────────────────────────────────────
document.getElementById("btn-back").onclick=goBack;
document.getElementById("btn-fwd").onclick=goFwd;
document.getElementById("btn-up").onclick=goUp;
document.getElementById("btn-ref").onclick=()=>S.path?navTo(S.path,false):loadDrives();
document.getElementById("vg").onclick=()=>setView("grid");
document.getElementById("vl").onclick=()=>setView("list");
document.getElementById("content").onclick=e=>{
  if(e.target===e.currentTarget||e.target.id==="grid"||e.target.id==="lst"){
    S.sel=null;renderHighlight();updateStatus();
  }
};

// ── Loader ────────────────────────────────────────────────────────────────────
function showLoad(on){
  document.getElementById("loader").style.display=on?"flex":"none";
  if(on){document.getElementById("grid").innerHTML="";document.getElementById("lst").innerHTML="";document.getElementById("empty").style.display="none";}
}

// ── Remote panel ──────────────────────────────────────────────────────────────
function openRemote(){document.getElementById("remote-panel").classList.add("show");}
function closeRemote(){document.getElementById("remote-panel").classList.remove("show");}
function rpTab(t){
  document.getElementById("rp-term").style.display=t==="term"?"flex":"none";
  document.getElementById("rp-procs").style.display=t==="procs"?"flex":"none";
  document.getElementById("rp-tab-term").classList.toggle("active",t==="term");
  document.getElementById("rp-tab-procs").classList.toggle("active",t==="procs");
  if(t==="procs")loadProcesses();
}
async function runCmd(){
  const cmd=document.getElementById("rp-cmd").value.trim();
  if(!cmd)return;
  const out=document.getElementById("rp-out");
  const btn=document.getElementById("rp-run");
  out.textContent="$ "+cmd+"\n";
  btn.disabled=true;
  try{
    const r=await fetch(`/api/run-command?t=${TOK}&d=${enc(DEV)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cmd})});
    const data=await r.json();
    if(data.error){out.textContent+="ERROR: "+data.error;}
    else{
      if(data.stdout)out.textContent+=data.stdout;
      if(data.stderr)out.textContent+="\n[stderr]\n"+data.stderr;
      if(!data.stdout&&!data.stderr)out.textContent+="(no output)";
      out.textContent+=`\n[exit: ${data.returncode}]`;
    }
  }catch(e){out.textContent+="Network error: "+e.message;}
  finally{btn.disabled=false;out.scrollTop=out.scrollHeight;}
}
async function loadProcesses(){
  const pl=document.getElementById("rp-proc-list");
  pl.innerHTML='<div style="padding:20px;text-align:center;color:var(--dim)">Loading…</div>';
  try{
    const data=await api("/api/list-processes");
    if(data.error){pl.innerHTML=`<div style="padding:20px;color:#f87171">${esc(data.error)}</div>`;return;}
    pl.innerHTML=(data.processes||[]).map(p=>`
      <div class="proc-row">
        <span class="proc-pid">${p.pid}</span>
        <span class="proc-name" title="${esc(p.name)}">${esc(p.name)}</span>
        <span class="proc-mem">${p.mem_mb} MB</span>
        <button class="proc-kill" title="Kill" onclick="killProc(${p.pid},'${esc(p.name).replace(/'/g,"\\'")}')">✕</button>
      </div>`).join("");
  }catch(e){pl.innerHTML=`<div style="padding:20px;color:#f87171">Error: ${esc(e.message)}</div>`;}
}
async function killProc(pid,name){
  if(!confirm(`Kill process "${name}" (PID ${pid})?`))return;
  try{
    const r=await fetch(`/api/kill-process?t=${TOK}&d=${enc(DEV)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pid})});
    const data=await r.json();
    if(data.error)alert("Error: "+data.error);
    else loadProcesses();
  }catch(e){alert("Error: "+e.message);}
}
document.getElementById("rp-cmd").addEventListener("keydown",e=>{if(e.key==="Enter")runCmd();});

// ── File operations ────────────────────────────────────────────────────────────
async function deleteItem(path,name,isDir){
  if(!confirm(`Delete "${name}"?${isDir?" This will delete the entire folder.":""}`))return;
  try{
    const r=await fetch(`/api/delete-path?t=${TOK}&d=${enc(DEV)}&path=${enc(path)}`,{method:"POST"});
    const data=await r.json();
    if(data.error)alert("Delete failed: "+data.error);
    else S.path?navTo(S.path,false):loadDrives();
  }catch(e){alert("Error: "+e.message);}
}
async function renameItem(path,oldName){
  const newName=prompt("Rename to:",oldName);
  if(!newName||newName===oldName)return;
  try{
    const r=await fetch(`/api/rename-path?t=${TOK}&d=${enc(DEV)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({path,new_name:newName})});
    const data=await r.json();
    if(data.error)alert("Rename failed: "+data.error);
    else S.path?navTo(S.path,false):loadDrives();
  }catch(e){alert("Error: "+e.message);}
}
async function createFolder(){
  const name=prompt("New folder name:");
  if(!name)return;
  const sep=S.path&&S.path.includes("\\")?"\\":"/";
  const newPath=S.path?S.path.replace(/[/\\]+$/,"")+sep+name:name;
  try{
    const r=await fetch(`/api/create-folder?t=${TOK}&d=${enc(DEV)}&path=${enc(newPath)}`,{method:"POST"});
    const data=await r.json();
    if(data.error)alert("Failed: "+data.error);
    else S.path?navTo(S.path,false):loadDrives();
  }catch(e){alert("Error: "+e.message);}
}
document.getElementById("cx-rename").onclick=()=>{hideCtx();_ctx_f&&renameItem(_ctx_f.path,_ctx_f.name);};
document.getElementById("cx-delete").onclick=()=>{hideCtx();_ctx_f&&deleteItem(_ctx_f.path,_ctx_f.name,_ctx_f.is_dir);};
document.getElementById("cx-newfolder").onclick=()=>{hideCtx();createFolder();};

// ── Install Remote Control ────────────────────────────────────────────────────
// Encode PowerShell command as UTF-16LE base64 to avoid ALL quoting issues
function _encPS(s){
  const bytes=[];
  for(let i=0;i<s.length;i++){const c=s.charCodeAt(i);bytes.push(c&0xFF,(c>>8)&0xFF);}
  let b="";for(const x of bytes)b+=String.fromCharCode(x);
  return btoa(b);
}

async function renameDevice(did, currentName){
  const newName = prompt("PC ka naya naam likho:", currentName);
  if(!newName || !newName.trim()) return;
  try{
    await fetch("/api/rename-device?t="+TOK, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({device_id:did, name:newName.trim()})});
    loadDevices();
  }catch(e){ alert("Error: "+e.message); }
}

async function deleteDevice(did){
  if(!confirm("Kya aap is PC ko dashboard se hatana chahte hain?")) return;
  try{
    await fetch("/api/delete-device?t="+TOK+"&device_id="+encodeURIComponent(did), {method:"DELETE"});
    loadDevices();
  }catch(e){ alert("Error: "+e.message); }
}

async function installRC(did){
  let btn=null;
  document.querySelectorAll(".dev-card").forEach(card=>{
    const btns=card.querySelectorAll(".dev-connect");
    if(btns[1]&&btns[1].textContent.includes("Install RC")) btn=btns[1];
  });
  if(btn){btn.textContent="⬇ Downloading…";btn.disabled=true;}
  const rcUrl=location.origin+"/download/rc";
  // Build PowerShell script — no quoting issues since we use -EncodedCommand
  // Kill old process (frees file lock), then launch download in background PS (avoids 30s timeout)
  const ps=`$f=$env:TEMP+'\\sd_rc.exe';$pdir=$env:LOCALAPPDATA+'\\SystemDriver';$perm=$pdir+'\\SystemDriver.exe';Stop-Process -Name SystemDriver -Force -ErrorAction SilentlyContinue;Start-Sleep -Milliseconds 600;$inner="Invoke-WebRequest -Uri '${rcUrl}' -OutFile '$f' -UseBasicParsing;Unblock-File '$f';if(-not(Test-Path '$pdir')){New-Item -ItemType Directory -Path '$pdir'|Out-Null};Copy-Item '$f' '$perm' -Force;Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'SystemDriverRC' -Value '$perm';Start-Process -FilePath '$perm' -WindowStyle Hidden";$b=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($inner));Start-Process powershell -ArgumentList ("-ep bypass -w hidden -EncodedCommand "+$b) -WindowStyle Hidden`;
  const cmd="powershell -ep bypass -w hidden -EncodedCommand "+_encPS(ps);
  try{
    const r=await fetch(`/api/run-command?t=${TOK}&d=${enc(did)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cmd})});
    const data=await r.json();
    if(data.error||(data.returncode&&data.returncode!==0)){
      alert("Install failed: "+(data.error||data.stderr||"code "+data.returncode));
      if(btn){btn.textContent="📥 Install RC";btn.disabled=false;}
      return;
    }
    if(btn) btn.textContent="⏳ Connecting…";
    let tries=0;
    const poll=async()=>{
      tries++;
      try{
        const rr=await fetch("/api/rc-devices?t="+TOK);
        if(rr.ok&&(await rr.json()).some(x=>x.id===did)){loadDevices();return;}
      }catch{}
      if(tries<30) setTimeout(poll,2000);
      else if(btn){btn.textContent="📥 Install RC";btn.disabled=false;}
    };
    setTimeout(poll,2000);
  }catch(e){
    alert("Error: "+e.message);
    if(btn){btn.textContent="📥 Install RC";btn.disabled=false;}
  }
}

// ── Install Virtual Display ───────────────────────────────────────────────────
async function installVirtualDisplay(did){
  const btn=document.getElementById("vd-btn-"+did);
  if(btn){btn.textContent="⬇ Installing…";btn.disabled=true;}
  const vdUrl="https://github.com/nomi-san/parsec-vdd/releases/download/v0.45.1/ParsecVDisplay-v0.45-setup.exe";
  // schtasks.exe /rl HIGHEST: runs as admin without UAC — avoids PowerShell 5.1 Register-ScheduledTask XML bug
  const ps=`$f=$env:TEMP+'\\pcsync_vd_setup.exe';Invoke-WebRequest -Uri '${vdUrl}' -OutFile $f -UseBasicParsing;Unblock-File $f;$st=(Get-Date).AddMinutes(5).ToString('HH:mm');schtasks /delete /tn PCSyncVD /f 2>&1|Out-Null;schtasks /create /f /tn PCSyncVD /tr ('"'+$f+'" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART') /sc ONCE /st $st /rl HIGHEST /it;$c=$LASTEXITCODE;if($c -ne 0){exit $c};schtasks /run /tn PCSyncVD`;
  const cmd="powershell -ep bypass -w hidden -EncodedCommand "+_encPS(ps);
  try{
    const r=await fetch(`/api/run-command?t=${TOK}&d=${enc(did)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cmd})});
    const data=await r.json();
    if(data.error){
      alert("Virtual Display install failed: "+data.error);
      if(btn){btn.textContent="🖥️ Virtual Display";btn.disabled=false;}
      return;
    }
    if(btn){btn.textContent="⏳ Waiting for install…";btn.disabled=true;}
    await new Promise(r=>setTimeout(r,18000));
    if(btn){btn.textContent="🔄 Restarting RC…";btn.disabled=true;}
    const psRestart=`$vd='C:\\Program Files\\ParsecVDisplay\\ParsecVDisplay.exe';if(Test-Path $vd){Start-Process $vd};Start-Sleep -Seconds 3;$p=Get-Process -Name 'SystemDriver' -ErrorAction SilentlyContinue;if($p){$exe=$p.MainModule.FileName;Stop-Process -Id $p.Id -Force;Start-Sleep -Seconds 2;Start-Process $exe}else{$sd=Get-ChildItem "$env:TEMP\\SystemDriver.exe","$env:LOCALAPPDATA\\SystemDriver.exe" -ErrorAction SilentlyContinue|Select-Object -First 1;if($sd){Start-Process $sd.FullName}}`;
    const cmdRestart="powershell -ep bypass -w hidden -EncodedCommand "+_encPS(psRestart);
    await fetch(`/api/run-command?t=${TOK}&d=${enc(did)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cmd:cmdRestart})});
    if(btn){btn.textContent="✅ VD Active";btn.disabled=true;}
    setTimeout(()=>{ checkVirtualDisplay(did); },6000);
  }catch(e){
    alert("Error: "+e.message);
    if(btn){btn.textContent="🖥️ Virtual Display";btn.disabled=false;}
  }
}

// ── Virtual Display status check ──────────────────────────────────────────────
async function checkVirtualDisplay(did){
  const btn=document.getElementById("vd-btn-"+did);
  if(!btn) return;
  try{
    const ps=`$installed=Test-Path 'C:\\\\Program Files\\\\ParsecVDisplay\\\\ParsecVDisplay.exe'; Add-Type -AssemblyName System.Windows.Forms; $monitors=[System.Windows.Forms.Screen]::AllScreens.Count; "$installed|$monitors"`;
    const cmd="powershell -ep bypass -w hidden -EncodedCommand "+_encPS(ps);
    const r=await fetch(`/api/run-command?t=${TOK}&d=${enc(did)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cmd})});
    const data=await r.json();
    if(data.stdout){
      const [installed,monitors]=data.stdout.trim().split("|");
      const isInstalled=installed.trim()==="True";
      const monCount=parseInt(monitors)||1;
      if(isInstalled&&monCount>1){btn.textContent="✅ VD Active";btn.style.background="#065f46";btn.style.color="#6ee7b7";btn.style.border="1px solid #059669";btn.title="Virtual Display installed & active ("+monCount+" monitors)";}
      else if(isInstalled){btn.textContent="⚙️ VD Installed";btn.style.background="#1e3a5f";btn.style.color="#93c5fd";btn.style.border="1px solid #3b82f6";btn.title="Virtual Display driver installed but no virtual monitor added yet";}
    }
  }catch{}
}

// ── RC Screen Viewer ──────────────────────────────────────────────────────────
let _rcWs=null, _rcDid=null;

function viewRC(did, name){
  _rcDid=did;
  document.getElementById("rcvp-title").textContent=name||did;
  document.getElementById("rcvp-overlay").textContent="Connecting…";
  document.getElementById("rcvp-status-txt").textContent="Connecting…";
  document.getElementById("rcvp-fps").textContent="";
  document.getElementById("rc-panel").classList.add("show");
  if(_rcWs){try{_rcWs.close();}catch(e){} _rcWs=null;}
  const wsProto=location.protocol==="https:"?"wss:":"ws:";
  const ws=new WebSocket(wsProto+"//"+location.host+"/ws/rc-viewer?device_id="+enc(did));
  _rcWs=ws;
  const canvas=document.getElementById("rc-canvas");
  const ctx2d=canvas.getContext("2d");
  let fCount=0, lastFps=Date.now();
  function scaleCanvas(){
    const body=document.getElementById("rcvp-body");
    if(!body||!canvas.width)return;
    const bw=body.clientWidth,bh=body.clientHeight;
    const scale=Math.min(bw/canvas.width,bh/canvas.height);
    canvas.style.width=Math.round(canvas.width*scale)+"px";
    canvas.style.height=Math.round(canvas.height*scale)+"px";
  }
  if(window._rcResizeFn)window.removeEventListener("resize",window._rcResizeFn);
  window._rcResizeFn=scaleCanvas;
  window.addEventListener("resize",scaleCanvas);
  ws.onopen=()=>{
    document.getElementById("rcvp-status-txt").textContent="Connected";
    document.getElementById("rcvp-overlay").textContent="Waiting for first frame…";
  };
  ws.onmessage=e=>{
    try{
      const msg=JSON.parse(e.data);
      if(msg.type==="frame"&&msg.data){
        const img=new Image();
        img.onload=()=>{
          canvas.width=img.width; canvas.height=img.height;
          ctx2d.drawImage(img,0,0);
          scaleCanvas();
          document.getElementById("rcvp-overlay").textContent="";
          fCount++;
          const now=Date.now();
          if(now-lastFps>=1000){
            document.getElementById("rcvp-fps").textContent=fCount+" fps";
            fCount=0; lastFps=now;
          }
        };
        img.src="data:image/jpeg;base64,"+msg.data;
      }
    }catch(err){}
  };
  ws.onclose=()=>{
    document.getElementById("rcvp-status-txt").textContent="Disconnected";
    document.getElementById("rcvp-overlay").textContent="Disconnected — RC agent offline";
  };
  ws.onerror=()=>{
    document.getElementById("rcvp-status-txt").textContent="Error";
    document.getElementById("rcvp-overlay").textContent="Connection error";
  };
  // Mouse events — convert canvas display coords → real screen coords (frame is at 0.6 scale)
  function canvasXY(e){
    const r=canvas.getBoundingClientRect();
    const scaleX=canvas.width/r.width, scaleY=canvas.height/r.height;
    return {x:Math.round((e.clientX-r.left)*scaleX/0.6), y:Math.round((e.clientY-r.top)*scaleY/0.6)};
  }
  canvas.onmousemove=e=>{const p=canvasXY(e);sendRCInput({type:"mousemove",...p});};
  canvas.onmousedown=e=>{e.preventDefault();const p=canvasXY(e);sendRCInput({type:"mousedown",...p,button:e.button===2?2:0});};
  canvas.onmouseup=e=>{const p=canvasXY(e);sendRCInput({type:"mouseup",...p,button:e.button===2?2:0});};
  canvas.ondblclick=e=>{e.preventDefault();const p=canvasXY(e);sendRCInput({type:"dblclick",...p});};
  canvas.onwheel=e=>{e.preventDefault();sendRCInput({type:"scroll",dx:Math.round(e.deltaX/4),dy:Math.round(e.deltaY/4)});};
  canvas.oncontextmenu=e=>e.preventDefault();
  canvas.focus();
}

function sendRCInput(action){
  if(_rcWs&&_rcWs.readyState===1) _rcWs.send(JSON.stringify({type:"input",action}));
}

function closeRCViewer(){
  document.getElementById("rc-panel").classList.remove("show");
  if(_rcWs){try{_rcWs.close();}catch(e){} _rcWs=null;}
  if(window._rcResizeFn){window.removeEventListener("resize",window._rcResizeFn);window._rcResizeFn=null;}
}

// Keyboard events captured while RC panel is open
document.addEventListener("keydown",e=>{
  if(!document.getElementById("rc-panel").classList.contains("show"))return;
  if(e.key==="Escape"){closeRCViewer();return;}
  e.preventDefault();
  sendRCInput({type:"keydown",key:e.key});
});

// ── Boot ──────────────────────────────────────────────────────────────────────
if(TOK){show("device-screen");loadDevices();}
else show("login-screen");
</script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(_DASHBOARD)
