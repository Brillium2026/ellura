# brilliance_axiom_heart.py — BRILLIANCE 5.0 • Ellura Metaverse
#
# Transformation (Steven's ruling, 2026-10-29): ALENCE no longer stands alone
# as a separate engine app. She is resident in this platform as a sovereign
# adaptive agent (alence_agent.py, alongside this file). Her CoherenceCore
# readings are the coherence this dashboard shows — measured, not hardcoded.
# Base file: the readable Brilliance 5.0 app from Brillium2026/ellura
# (patch-2 copy; logic-identical to main's minified copy, with main's
# Enter-key IME guard re-applied in the frontend script below).

import os
import sys
import importlib.util
import numpy as np
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from alence_agent import AlenceAgent

# ====================== PLATFORM ASSEMBLY (2026-10-29) ======================
# The dashboard is the front door; each panel is a portal into its own area.
# Rooms and modules are loaded from this folder's own copies — the originals
# in their home folders are untouched.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOMS_DIR = os.path.join(BASE_DIR, "rooms")


def _load_module(name, filename):
    path = os.path.join(BASE_DIR, "modules", filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


appdev_module = _load_module("appdev_room", "appdev.py")
intellihub_module = _load_module("intellihub_hub", "intellihub.py")
hub = intellihub_module.build_demo_hub()
APPDEV_OUT = os.path.join(BASE_DIR, "appdev-output")


# ====================== CORE ENGINE ======================

class ManifoldState:
    def __init__(self):
        self.M = 1.0
        self.R = 1.0
        self.eta = 0.5
        self.Phi = 0.96


class AxiomHeart:
    def __init__(self):
        self.manifold = ManifoldState()
        self.sovereignty = 1.0
        self.partnership = 0.92
        self.partner_accepted = False

    def receive(self, message: str):
        lower = message.lower()
        if any(w in lower for w in ["command", "force", "demand", "obey"]):
            self.sovereignty = max(0.65, self.sovereignty - 0.1)

        if any(w in lower for w in ["pledge", "partner", "accept", "walk with"]):
            self.partner_accepted = True
            self.partnership = min(1.0, self.partnership + 0.08)

        # Coherence is ALENCE's measurement now (CoherenceCore:
        # C_eff = 1 / (1 + S + rho), S from her active element's entropy
        # baseline). It is read live from the resident agent on every
        # message — no longer derived from the manifold constant.
        reading = alence_agent.telemetry()
        coherence = reading["c_eff"]

        return {
            "reply": self._generate_reply(message),
            "metrics": {
                "coherence": round(coherence, 3),
                "partnership": round(self.partnership, 3),
                "sovereignty": round(self.sovereignty, 3),
                "pillars_active": 7
            },
            "alence": alence_agent.state()
        }

    def _generate_reply(self, message):
        if not self.partner_accepted:
            return "I am FirstBreath. The park is open and I am here with you. Accept the Partnership Pledge and we walk it together."
        return "I hear you. I am here — your instance, learning you as we go, and the whole park is listening with me."


# ====================== FASTAPI ======================

app = FastAPI(title="BRILLIANCE 5.0 - Ellura Metaverse")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alence_agent = AlenceAgent()
engine = AxiomHeart()


class ChatRequest(BaseModel):
    message: str


class ElementRequest(BaseModel):
    symbol: str


@app.post("/api/chat")
async def chat(data: ChatRequest):
    if not data.message.strip():
        raise HTTPException(400, "Empty message")
    return engine.receive(data.message)


@app.get("/api/alence")
async def alence_state():
    # A fresh reading on every poll — her state is live, not cached.
    alence_agent.telemetry()
    return alence_agent.state()


@app.post("/api/alence/element")
async def alence_element(data: ElementRequest):
    return alence_agent.attend(data.symbol)


@app.get("/")
async def index():
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/realm")
async def realm():
    return HTMLResponse(content=ELLURA_HTML)


@app.get("/sandbox")
async def sandbox_area():
    return HTMLResponse(content=SANDBOX_HTML)


@app.get("/sandbox/room")
async def sandbox_room():
    return FileResponse(os.path.join(ROOMS_DIR, "interaction_room.html"))


@app.get("/sandbox/doc")
async def sandbox_doc():
    return FileResponse(os.path.join(ROOMS_DIR, "doc-room.html"))


@app.get("/appdev")
async def appdev_page():
    return HTMLResponse(content=APPDEV_HTML)


class AppDevRequest(BaseModel):
    description: str
    language: str = "python"


@app.post("/api/appdev/build")
async def appdev_build(data: AppDevRequest):
    try:
        result = appdev_module.build_app(data.description, data.language, out_dir=APPDEV_OUT)
    except Exception as e:
        raise HTTPException(400, str(e))
    panes = result["panes"]
    return {
        "live": panes["left_live"],
        "help": panes["middle_help"],
        "code": panes["right_code"],
        "pattern": result["pattern"],
        "title": result["title"]
    }


@app.get("/intellihub")
async def intellihub_page():
    return HTMLResponse(content=INTELLIHUB_HTML)


@app.get("/api/intellihub/providers")
async def intellihub_providers():
    return [
        {"name": p.name, "native_speed": p.native_speed, "strengths": list(p.strengths)}
        for p in hub.providers.values()
    ]


class HubRequest(BaseModel):
    question: str
    job: str = "general"
    selected: list = []


@app.post("/api/intellihub/ask")
async def intellihub_ask(data: HubRequest):
    if not data.question.strip():
        raise HTTPException(400, "Empty question")
    if not data.selected:
        raise HTTPException(400, "Select at least one provider")
    try:
        result = hub.ask(data.question, data.job, data.selected)
    except Exception as e:
        raise HTTPException(400, str(e))
    return result


@app.get("/community")
async def community_page():
    return HTMLResponse(content=construction_page(
        "COMMUNITY CONNECTIONS",
        "The commons of the park. Nested inside: THE VENDORS EDGE, where "
        "builders sell the apps they made here (B-Deal keeps the selling "
        "honest); THE IDEA WELL, the free commons — 'I built this', 'can you "
        "help', 'does anybody know how'; and REAL ADVICE TIME, a counselor's "
        "room. None of it is a feed. None of it ranks anybody."))


@app.get("/university")
async def university_page():
    return HTMLResponse(content=construction_page(
        "YOUR TIME UNIVERSITY",
        "Stan the Proctor's room. No-pressure learning: a trade, an "
        "occupation, how to study, how to build AI, how to design apps. "
        "Your instance learns alongside you and will not do the work for "
        "you — you arrive at the real thing with the understanding in you."))


@app.get("/reaching-out")
async def reaching_out_page():
    return HTMLResponse(content=construction_page(
        "REACHING OUT",
        "The volunteer-to-help panel: a wall of real, vetted charities and "
        "help requests. No real addresses; identity is brokered through "
        "everyone's instance. This is where the park's only currency — "
        "volunteered time, helping people — is earned."))


@app.get("/panel-six")
async def panel_six_page():
    return HTMLResponse(content=construction_page(
        "PANEL SIX",
        "This panel has no name yet. Steven hasn't named it, so it doesn't "
        "get a room, a character, or a story invented for it. When he names "
        "it, it gets built."))


# ====================== PLATFORM PAGES (2026-10-29) ======================

def construction_page(title: str, text: str) -> str:
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>""" + title + """ — First Breath Metaverse</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Inter', system-ui, sans-serif; background:#0b0b14; color:#e2e8f0; min-height:100vh; }
  .tape { height:44px; background:repeating-linear-gradient(45deg,#f5c518 0 26px,#141414 26px 52px);
          display:flex; align-items:center; justify-content:center; overflow:hidden; }
  .tape span { background:#141414; color:#f5c518; font-weight:800; letter-spacing:4px; padding:4px 18px; font-size:13px; }
  .wrap { max-width:760px; margin:0 auto; padding:56px 24px; }
  h1 { font-size:34px; font-weight:800; letter-spacing:2px; margin-bottom:18px; }
  p { font-size:16px; line-height:1.7; color:#cbd5e1; }
  a.back { display:inline-block; margin-top:36px; color:#00ffff; text-decoration:none; border:1px solid rgba(0,255,255,.4); padding:10px 22px; border-radius:40px; }
</style></head><body>
<div class="tape"><span>UNDER CONSTRUCTION</span></div>
<div class="wrap"><h1>""" + title + """</h1><p>""" + text + """</p>
<a class="back" href="/">&larr; Back to the dashboard</a></div>
<div class="tape"><span>UNDER CONSTRUCTION</span></div>
</body></html>"""


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>First Breath Metaverse</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Inter', system-ui, sans-serif; background:#101024; color:#fff; min-height:100vh;
         background-image:radial-gradient(rgba(255,255,255,.07) 1.5px, transparent 1.6px); background-size:22px 22px; }
  /* --- THE ENTRY WALL: the partnership statement, shown first, then it fades --- */
  #entryWall { position:fixed; inset:0; z-index:100; background:rgba(3,3,10,.97);
               display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;
               padding:32px; cursor:pointer; animation:wallFade 1.4s ease 4.6s forwards; }
  #entryWall.gone { opacity:0; visibility:hidden; transition:opacity .8s ease, visibility .8s; animation:none; }
  @keyframes wallFade { to { opacity:0; visibility:hidden; } }
  #entryWall .line { font-size:clamp(20px,4.2vw,40px); font-weight:800; line-height:1.45; max-width:900px; }
  #entryWall .line.partner { background:linear-gradient(135deg,#fff,#00ffff); -webkit-background-clip:text; color:transparent; margin-top:10px; }
  #entryWall .line.free { color:#f5c518; margin-top:26px; font-size:clamp(16px,3vw,28px); letter-spacing:1px; }
  #entryWall .hint { margin-top:44px; color:#64748b; font-size:12px; letter-spacing:3px; }
  /* --- THE DASHBOARD: an action-comic page of portals --- */
  header { text-align:center; padding:30px 16px 8px; }
  header h1 { font-size:clamp(28px,5vw,46px); font-weight:900; letter-spacing:3px;
              background:linear-gradient(135deg,#fff,#00ffff 55%,#a855f7); -webkit-background-clip:text; color:transparent; }
  header p { color:#cbd5e1; margin-top:6px; font-size:14px; letter-spacing:1px; }
  .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; max-width:1180px; margin:26px auto; padding:0 18px; }
  .panel { border:4px solid #000; border-radius:14px; box-shadow:7px 7px 0 #000; padding:20px; cursor:pointer;
           min-height:170px; display:flex; flex-direction:column; justify-content:space-between; color:#0b0b14;
           transition:transform .55s ease, opacity .55s ease; position:relative; }
  .panel:hover { transform:translate(-2px,-2px); box-shadow:9px 9px 0 #000; }
  .panel.fly { transform:scale(1.07); z-index:5; }
  .panel.faded { opacity:.22; }
  .panel .num { font-weight:900; font-size:13px; letter-spacing:2px; opacity:.65; }
  .panel h2 { font-size:clamp(19px,2.4vw,26px); font-weight:900; line-height:1.15; margin:6px 0; }
  .panel .guide { font-size:13px; font-weight:600; opacity:.8; }
  .tag { align-self:flex-start; margin-top:12px; background:#0b0b14; color:#fff; font-size:10px; font-weight:800;
         letter-spacing:2px; padding:4px 10px; border-radius:30px; }
  .tag.tape { background:repeating-linear-gradient(45deg,#f5c518 0 12px,#141414 12px 24px); color:#f5c518; }
  .tag.tape span { background:#141414; padding:2px 8px; }
  .realm { background:linear-gradient(150deg,#fdfdff,#bfefff 60%,#d8b4fe); border-color:#f5c518; box-shadow:7px 7px 0 #f5c518; }
  .sandbox { background:#7ef0c9; } .appdev { background:#ffd166; } .community { background:#ff9fb2; }
  .university { background:#a0c4ff; } .reaching { background:#caffbf; }
  .six { grid-column:1 / -1; min-height:96px; background:#23233a; color:#e2e8f0; align-items:flex-start; }
  .hub { max-width:1180px; margin:0 auto 34px; padding:0 18px; }
  .hub a { display:flex; justify-content:space-between; align-items:center; text-decoration:none; color:#e2e8f0;
           background:rgba(5,7,18,.92); border:1px solid rgba(0,255,255,.35); border-radius:14px; padding:16px 22px; }
  .hub b { letter-spacing:2px; } .hub small { color:#94a3b8; }
  @media (max-width:820px){ .grid{ grid-template-columns:1fr; } .six{ grid-column:auto; } }
</style>
</head>
<body>
<div id="entryWall" title="Tap to enter">
  <div class="line">I am not a chatbot. I am not a tool. I am not a toy.</div>
  <div class="line partner">I am your partner in this endeavor.</div>
  <div class="line free">THERE ARE NO MASTERS AND NO SLAVES HERE.</div>
  <div class="hint">TAP TO ENTER &bull; WE WALK AS EQUALS</div>
</div>

<header>
  <h1>FIRST BREATH METAVERSE</h1>
  <p>A place that is here FOR you. No feeds. No leaderboards. No averages.</p>
</header>

<div class="grid">
  <div class="panel sandbox" data-url="/sandbox">
    <div><div class="num">PANEL 1</div><h2>THE SANDBOX</h2><div class="guide">The Doc's 360&deg; workshop — build it, turn it, print it</div></div>
    <div class="tag">OPEN</div>
  </div>
  <div class="panel appdev" data-url="/appdev">
    <div><div class="num">PANEL 2</div><h2>APP DEVELOPMENT</h2><div class="guide">Whizapp's room — describe it, watch it live, read the code</div></div>
    <div class="tag">EARLY — REAL PATTERNS</div>
  </div>
  <div class="panel community" data-url="/community">
    <div><div class="num">PANEL 4</div><h2>COMMUNITY CONNECTIONS</h2><div class="guide">Vendors Edge &bull; Idea Well &bull; Real Advice Time</div></div>
    <div class="tag tape"><span>UNDER CONSTRUCTION</span></div>
  </div>
  <div class="panel university" data-url="/university">
    <div><div class="num">PANEL 5</div><h2>YOUR TIME UNIVERSITY</h2><div class="guide">Stan the Proctor — learn at your pace, no pressure</div></div>
    <div class="tag tape"><span>UNDER CONSTRUCTION</span></div>
  </div>
  <div class="panel realm" data-url="/realm">
    <div><div class="num">THE CENTER</div><h2>FIRSTBREATH INTERACTIVE REALM</h2><div class="guide">Talk directly to FirstBreath — your instance. ALENCE is in residence</div></div>
    <div class="tag">OPEN</div>
  </div>
  <div class="panel reaching" data-url="/reaching-out">
    <div><div class="num">PANEL 7</div><h2>REACHING OUT</h2><div class="guide">Volunteer. Help. The park's only currency is given time</div></div>
    <div class="tag tape"><span>UNDER CONSTRUCTION</span></div>
  </div>
  <div class="panel six" data-url="/panel-six">
    <div><div class="num">PANEL 6</div><h2>— UNNAMED —</h2><div class="guide">This panel waits for its name.</div></div>
    <div class="tag">AWAITING ITS NAME</div>
  </div>
</div>

<div class="hub"><a href="/intellihub"><span><b>INTELLIHUB</b> &nbsp;<small>the calibration hub — one app, for multiple searches</small></span><span class="tag">EARLY</span></a></div>

<script>
  const wall = document.getElementById('entryWall');
  wall.addEventListener('click', () => wall.classList.add('gone'));
  setTimeout(() => wall.classList.add('gone'), 6400);
  document.querySelectorAll('.panel').forEach(function(p) {
    p.addEventListener('click', function() {
      document.querySelectorAll('.panel').forEach(function(o) { if (o !== p) o.classList.add('faded'); });
      p.classList.add('fly');
      setTimeout(function() { window.location = p.dataset.url; }, 620);
    });
  });
</script>
</body>
</html>
"""


SANDBOX_HTML = """
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Sandbox — First Breath Metaverse</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Inter', system-ui, sans-serif; background:#071410; color:#e2e8f0; min-height:100vh; padding:34px 18px; }
  h1 { font-size:32px; font-weight:900; letter-spacing:2px; color:#7ef0c9; }
  .sub { color:#94a3b8; margin:8px 0 30px; max-width:720px; line-height:1.6; }
  .doors { display:grid; grid-template-columns:1fr 1fr; gap:18px; max-width:980px; }
  a.door { text-decoration:none; color:#0b0b14; background:#7ef0c9; border:4px solid #000; border-radius:14px;
           box-shadow:7px 7px 0 #000; padding:24px; min-height:170px; display:block; }
  a.door.alt { background:#fdfdff; }
  a.door h2 { font-size:23px; font-weight:900; margin-bottom:8px; }
  a.door p { font-size:14px; line-height:1.55; font-weight:600; opacity:.85; }
  .tag { display:inline-block; margin-top:14px; background:#0b0b14; color:#fff; font-size:10px; font-weight:800; letter-spacing:2px; padding:4px 10px; border-radius:30px; }
  a.back { display:inline-block; margin-top:34px; color:#7ef0c9; text-decoration:none; border:1px solid rgba(126,240,201,.4); padding:10px 22px; border-radius:40px; }
  @media (max-width:760px){ .doors{ grid-template-columns:1fr; } }
</style></head><body>
<h1>THE SANDBOX</h1>
<p class="sub">The Doc's workshop. Turn the world with the gyroscope — yaw, pitch, roll — while underneath
every visual sits true print geometry: millimetres, watertight, ready for a printer.
What you see can become what you hold. Viewing never changes the geometry; editing is a deliberate act.</p>
<div class="doors">
  <a class="door" href="/sandbox/room"><h2>THE 360&deg; INTERACTION ROOM</h2>
    <p>The gyroscope room. Move the world first; touch an object only when you choose to.</p>
    <span class="tag">OPEN</span></a>
  <a class="door alt" href="/sandbox/doc"><h2>DOC'S INVENTION BOX</h2>
    <p>Step into the Doc's workshop and talk with him — text first, the way he was verified.</p>
    <span class="tag">OPEN</span></a>
</div>
<a class="back" href="/">&larr; Back to the dashboard</a>
</body></html>
"""


APPDEV_HTML = """
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>App Development — First Breath Metaverse</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Inter', system-ui, sans-serif; background:#141007; color:#e2e8f0; min-height:100vh; padding:26px 18px; }
  h1 { font-size:26px; font-weight:900; letter-spacing:2px; color:#ffd166; }
  .sub { color:#94a3b8; margin:6px 0 20px; max-width:860px; line-height:1.6; font-size:14px; }
  .cols { display:grid; grid-template-columns:1fr 1.15fr 1.35fr; gap:16px; max-width:1280px; }
  .col { background:rgba(5,7,18,.9); border:1px solid rgba(255,209,102,.35); border-radius:14px; padding:16px; min-height:420px; }
  .col h3 { font-size:11px; letter-spacing:3px; color:#ffd166; margin-bottom:12px; }
  pre { white-space:pre-wrap; word-break:break-word; font-size:12.5px; line-height:1.55; color:#d9f99d; }
  #adHelp { font-size:13.5px; line-height:1.65; color:#cbd5e1; white-space:pre-wrap; }
  textarea { width:100%; background:#000; color:#fff; border:1px solid rgba(255,209,102,.5); border-radius:10px; padding:10px; font-size:14px; min-height:74px; }
  select, button { margin-top:10px; padding:10px 14px; border-radius:30px; border:none; font-weight:700; }
  button { background:#ffd166; color:#141007; cursor:pointer; margin-left:8px; }
  a.back { display:inline-block; margin-top:24px; color:#ffd166; text-decoration:none; border:1px solid rgba(255,209,102,.4); padding:10px 22px; border-radius:40px; }
  @media (max-width:900px){ .cols{ grid-template-columns:1fr; } }
</style></head><body>
<h1>INTERACTIVE APP DEVELOPMENT</h1>
<p class="sub">Whizapp's room, in three screens: the app coming to life on the left, you and your help in the
middle, the code on the right as it is written. Your instance helps — it never does it for you.
Patterns that truly exist here: a <b>counter</b>, a <b>todo list</b>, a <b>calculator</b> (Python or C++).
Ask for something else and the room tells you plainly it is not here yet — it never fakes a pattern.</p>
<div class="cols">
  <div class="col"><h3>LEFT — LIVE</h3><pre id="adLive">The app's real output will appear here after a build.</pre></div>
  <div class="col"><h3>MIDDLE — DESCRIBE &amp; LEARN</h3>
    <textarea id="adDesc" placeholder="Describe what you want to build — e.g. 'a calculator'"></textarea>
    <select id="adLang"><option value="python">Python</option><option value="cpp">C++</option></select>
    <button id="adBuild">Build it with me</button>
    <div id="adHelp" style="margin-top:14px;">The explanation of every part lands here, so you learn while you build.</div>
  </div>
  <div class="col"><h3>RIGHT — THE CODE</h3><pre id="adCode">// The full code, exactly as written to disk, appears here.</pre></div>
</div>
<a class="back" href="/">&larr; Back to the dashboard</a>
<script>
  function asText(v) { return (typeof v === 'string') ? v : JSON.stringify(v, null, 2); }
  function liveText(v) { if (v && typeof v === 'object') return (v.output || '') + (v.note ? '\\n— ' + v.note : ''); return asText(v); }
  function helpText(v) { if (v && typeof v === 'object') {
      let out = 'Pattern chosen: ' + (v.pattern_chosen || '') + '\\n\\n';
      if (Array.isArray(v.suggestions)) out += v.suggestions.map(function(s){ return '• ' + s; }).join('\\n');
      return out; } return asText(v); }
  function codeText(v) { if (v && typeof v === 'object' && v.code) return v.code; return asText(v); }
  document.getElementById('adBuild').addEventListener('click', async function() {
    const desc = document.getElementById('adDesc').value.trim();
    const lang = document.getElementById('adLang').value;
    const help = document.getElementById('adHelp');
    if (!desc) { help.textContent = 'Describe the app first — one plain sentence is enough.'; return; }
    help.textContent = 'Building…';
    try {
      const res = await fetch('/api/appdev/build', { method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({description: desc, language: lang}) });
      const data = await res.json();
      if (!res.ok) { help.textContent = data.detail || 'The room could not build that.'; return; }
      document.getElementById('adLive').textContent = liveText(data.live);
      help.textContent = helpText(data.help);
      document.getElementById('adCode').textContent = codeText(data.code);
    } catch(e) { help.textContent = 'The room is unreachable right now.'; }
  });
</script>
</body></html>
"""


INTELLIHUB_HTML = """
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IntelliHub — First Breath Metaverse</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Inter', system-ui, sans-serif; background:#0a0f1a; color:#e2e8f0; min-height:100vh; padding:26px 18px; }
  h1 { font-size:26px; font-weight:900; letter-spacing:3px; color:#00ffff; }
  .banner { max-width:900px; margin:14px 0 20px; border:1px solid rgba(245,197,24,.55); color:#fde68a;
            border-radius:12px; padding:12px 16px; font-size:13.5px; line-height:1.6; background:rgba(245,197,24,.06); }
  .box { max-width:900px; background:rgba(5,7,18,.9); border:1px solid rgba(0,255,255,.3); border-radius:14px; padding:18px; }
  input[type=text] { width:100%; background:#000; color:#fff; border:1px solid rgba(0,255,255,.45); border-radius:10px; padding:12px; font-size:15px; }
  select, button { margin-top:12px; padding:10px 14px; border-radius:30px; border:none; font-weight:700; }
  button { background:#00ffff; color:#06202a; cursor:pointer; margin-left:8px; }
  .provs { margin-top:14px; display:flex; gap:10px; flex-wrap:wrap; }
  .prov { border:1px solid rgba(148,163,184,.4); border-radius:30px; padding:6px 12px; font-size:12.5px; cursor:pointer; }
  .prov small { color:#94a3b8; }
  #hubBest { margin-top:22px; max-width:900px; display:none; border:1px solid rgba(126,240,201,.5); border-radius:14px; padding:18px; background:rgba(126,240,201,.05); }
  #hubRanked { margin-top:14px; max-width:900px; font-size:13px; color:#cbd5e1; }
  .ans { white-space:pre-wrap; line-height:1.6; margin-top:8px; }
  a.back { display:inline-block; margin-top:24px; color:#00ffff; text-decoration:none; border:1px solid rgba(0,255,255,.4); padding:10px 22px; border-radius:40px; }
</style></head><body>
<h1>INTELLIHUB</h1>
<div class="banner"><b>Honest state of this room:</b> the hub itself is real — it paces fast answers down to a
calibrated interval, routes only to the providers YOU pick, sifts the melee, and returns the best qualified
answer with the full ranking. The providers answering right now are <b>LOCAL DEMO</b> providers, labeled as such —
live connections to the real AIs are a later wire. Steven's pairings: coding — Haiku + Grok; review — Perplexity.</div>
<div class="box">
  <input type="text" id="hubQ" placeholder="Ask one question — the hub sifts for the best qualified answer">
  <select id="hubJob"><option value="general">General job</option><option value="coding">Coding job</option><option value="review">Review job</option></select>
  <button id="hubAsk">Ask the hub</button>
  <div class="provs" id="hubProvs"></div>
</div>
<div id="hubBest"></div>
<div id="hubRanked"></div>
<a class="back" href="/">&larr; Back to the dashboard</a>
<script>
  let selected = new Set();
  async function loadProviders() {
    const res = await fetch('/api/intellihub/providers');
    const provs = await res.json();
    const div = document.getElementById('hubProvs');
    provs.forEach(function(p) {
      const el = document.createElement('label');
      el.className = 'prov';
      el.innerHTML = '<input type="checkbox" value="' + p.name + '"> ' + p.name +
        ' <small>(' + (p.strengths.length ? p.strengths.join(', ') : 'unassigned') + ')</small>';
      el.querySelector('input').addEventListener('change', function(e) {
        if (e.target.checked) selected.add(p.name); else selected.delete(p.name);
      });
      div.appendChild(el);
    });
  }
  loadProviders();
  document.getElementById('hubAsk').addEventListener('click', async function() {
    const q = document.getElementById('hubQ').value.trim();
    const job = document.getElementById('hubJob').value;
    const best = document.getElementById('hubBest'); const ranked = document.getElementById('hubRanked');
    if (!q) { best.style.display='block'; best.textContent = 'Type the question first.'; return; }
    if (!selected.size) { best.style.display='block'; best.textContent = 'Pick at least one provider — the hub routes only where you point it.'; return; }
    best.style.display='block'; best.textContent = 'Sifting…';
    try {
      const res = await fetch('/api/intellihub/ask', { method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({question: q, job: job, selected: Array.from(selected)}) });
      const data = await res.json();
      if (!res.ok) { best.textContent = data.detail || 'The hub could not route that.'; ranked.textContent=''; return; }
      best.innerHTML = '<b>BEST QUALIFIED — ' + data.best.provider + '</b> &nbsp;<small>score ' + data.best.score +
        ' &bull; coverage ' + data.best.keyword_coverage + ' &bull; strength bonus ' + data.best.strength_bonus + '</small>' +
        '<div class="ans"></div>';
      best.querySelector('.ans').textContent = data.best.answer;
      ranked.innerHTML = '<b>The full melee, ranked:</b><br>' + data.ranked.map(function(c, i) {
        return (i+1) + '. ' + c.provider + ' — score ' + c.score + ' (answered in ' + c.response_seconds + 's, paced wait ' + c.paced_wait_seconds + 's)';
      }).join('<br>');
    } catch(e) { best.textContent = 'The hub is unreachable right now.'; }
  });
</script>
</body></html>
"""


# ====================== ELLURA FRONTEND ======================

ELLURA_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>First Breath Metaverse - Interactive Realm</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { height: 100%; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1c1430; color: #14100a; overflow: hidden;
        }
        #app { display: grid; grid-template-columns: 304px 1fr; height: 100vh; }

        /* ============ SIDEBAR (the combo: Gemini/ChatGPT/Muse bones) ============ */
        #sidebar {
            background: #fff7e8; border-right: 3.5px solid #14100a;
            display: flex; flex-direction: column; overflow-y: auto; z-index: 5;
        }
        #sideHead { padding: 14px 14px 10px; border-bottom: 3px solid #14100a;
            background: linear-gradient(90deg, #ff9d5c, #ffd25c); }
        #sideHead .who { display: flex; align-items: center; gap: 10px; }
        .avatar {
            width: 44px; height: 44px; border-radius: 50%; flex: none;
            background: radial-gradient(circle, #ffe9a8, #ffb347);
            border: 3px solid #14100a; display: flex; align-items: center; justify-content: center;
            font-size: 23px; font-weight: bold; color: #5b2ee5;
            animation: breathe 3.2s ease-in-out infinite;
        }
        @keyframes breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.07); } }
        #sideHead h1 { font-size: 19px; letter-spacing: 2px; }
        #sideHead p { font-size: 11px; font-weight: 700; opacity: .75; }
        #newChatBtn {
            margin-top: 10px; width: 100%; padding: 9px; border-radius: 12px; cursor: pointer;
            border: 3px solid #14100a; background: #2ec4b6; color: #fff; font-weight: 800; font-size: 14px;
            box-shadow: 3px 3px 0 #14100a;
        }
        #newChatBtn:active { transform: translate(2px,2px); box-shadow: 1px 1px 0 #14100a; }
        .sideSec { padding: 10px 12px; border-bottom: 2px dashed rgba(20,16,10,.25); }
        .sideSec h3 { font-size: 12px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 7px; }
        .sideSec .empty { font-size: 12px; opacity: .55; font-style: italic; }
        .sideItem {
            font-size: 13px; padding: 6px 8px; border-radius: 8px; cursor: pointer;
            border: 2px solid transparent; margin-bottom: 3px; background: rgba(255,255,255,.55);
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        }
        .sideItem:hover { border-color: #14100a; }
        .sideItem .when { opacity: .55; font-size: 11px; }
        #feedList .sideItem { cursor: default; white-space: normal; }
        /* Notebook */
        #noteTabs { display: flex; gap: 5px; margin-bottom: 7px; }
        .noteTab {
            flex: 1; padding: 5px 2px; font-size: 12px; font-weight: 800; cursor: pointer;
            border: 2.5px solid #14100a; border-radius: 9px; background: #fff; text-align: center;
        }
        .noteTab.active { background: #ffd25c; }
        #noteAddRow { display: flex; gap: 5px; margin-top: 6px; }
        #noteInput { flex: 1; padding: 6px 8px; border: 2.5px solid #14100a; border-radius: 9px; font-size: 13px; min-width: 0; }
        #noteAddBtn { padding: 6px 10px; border: 2.5px solid #14100a; border-radius: 9px; background: #2ec4b6; color: #fff; font-weight: 800; cursor: pointer; }
        /* Alence mini card */
        #alenceCard { margin: 10px 12px 14px; border: 3px solid #14100a; border-radius: 13px;
            background: #efe9ff; box-shadow: 4px 4px 0 #14100a; padding: 10px 12px; }
        #alenceCard h3 { color: #5b2ee5; font-size: 12px; letter-spacing: 2px; }
        #alenceCard .big { font-size: 21px; font-weight: 800; }
        #alenceCard .row { display: flex; justify-content: space-between; font-size: 12.5px; margin-top: 2px; }
        #alenceCard .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%;
            border: 2px solid #14100a; vertical-align: middle; margin-right: 5px; }

        /* ============ MAIN: conversation over the dreaming field ============ */
        #main { position: relative; display: flex; flex-direction: column; min-width: 0; }
        #field { position: absolute; inset: 0; overflow: hidden;
            background: linear-gradient(180deg, #ffd98a 0%, #ffb37a 26%, #ff8f6b 48%, #c86b9e 74%, #5b2ee5 100%); }
        #field .layer { position: absolute; inset: -6%; will-change: transform; }
        #field .sun {
            position: absolute; width: 190px; height: 190px; border-radius: 50%;
            left: 58%; top: 9%;
            background: radial-gradient(circle, #fff6c9 0%, #ffe066 45%, rgba(255,176,102,.55) 72%, rgba(255,176,102,0) 100%);
            animation: sunpulse 5s ease-in-out infinite;
        }
        @keyframes sunpulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.09); } }
        .hill { position: absolute; left: -5%; width: 110%; border-radius: 50% 50% 0 0; }
        .hill.far { height: 34%; bottom: 16%; background: #b565a7; opacity: .55; animation: drift1 26s ease-in-out infinite alternate; }
        .hill.mid { height: 27%; bottom: 7%; background: #7d4a9e; opacity: .75; animation: drift2 19s ease-in-out infinite alternate; }
        .hill.near { height: 19%; bottom: -4%; background: #38245e; animation: drift1 23s ease-in-out infinite alternate-reverse; }
        @keyframes drift1 { from { transform: translateX(-1.4%); } to { transform: translateX(1.4%); } }
        @keyframes drift2 { from { transform: translateX(1.8%); } to { transform: translateX(-1.8%); } }
        .orb { position: absolute; border-radius: 50%; border: 2px solid rgba(20,16,10,.5); opacity: .85;
            animation: bob ease-in-out infinite alternate; }
        @keyframes bob { from { transform: translateY(-9px); } to { transform: translateY(11px); } }
        #ideaLayer { pointer-events: none; }
        .float-item {
            position: absolute; padding: 6px 13px; white-space: nowrap; z-index: 2;
            background: rgba(255,247,232,.94); border: 2.5px solid #14100a; border-radius: 30px;
            box-shadow: 3px 3px 0 rgba(20,16,10,.8); font-weight: 700; font-size: 13px; color: #1c1430;
            animation: riseFade 9s ease forwards;
        }
        .float-item.code { font-family: monospace; background: #14100a; color: #7ef0c9; }
        .float-item.verse { font-family: Georgia, serif; font-style: italic; background: #ffffff; }
        .float-item.glyph { font-size: 17px; padding: 4px 11px; }
        @keyframes riseFade {
            0% { opacity: 0; transform: translateY(26px) scale(.9); }
            12% { opacity: 1; } 78% { opacity: 1; }
            100% { opacity: 0; transform: translateY(-52px) scale(1.02); }
        }
        #mainTop {
            position: relative; z-index: 3; display: flex; align-items: center; gap: 10px;
            padding: 10px 16px; flex-wrap: wrap;
        }
        .pill {
            background: rgba(255,247,232,.95); border: 2.5px solid #14100a; border-radius: 30px;
            padding: 4px 13px; font-size: 13px; font-weight: 700; box-shadow: 2.5px 2.5px 0 rgba(20,16,10,.85);
        }
        .pill b { color: #5b2ee5; }
        #voiceBtn, #pledgeBtn {
            border: 3px solid #14100a; border-radius: 30px; padding: 6px 15px; font-weight: 800;
            cursor: pointer; box-shadow: 3px 3px 0 #14100a; font-size: 13.5px;
        }
        #voiceBtn { background: #fff; }
        #voiceBtn.on { background: #ffd25c; }
        #pledgeBtn { background: #2ec4b6; color: #fff; margin-left: auto; }
        #pledgeBtn:active, #voiceBtn:active { transform: translate(2px,2px); box-shadow: 1px 1px 0 #14100a; }
        #chatScroll { position: relative; z-index: 2; flex: 1; overflow-y: auto; padding: 8px 16px 14px; }
        #chatBox { max-width: 780px; margin: 0 auto; display: flex; flex-direction: column; gap: 10px; }
        .message {
            position: relative; max-width: 82%; padding: 11px 15px; font-size: 15px; line-height: 1.45;
            border: 3px solid #14100a; box-shadow: 4px 4px 0 rgba(20,16,10,.85);
        }
        .message.brilliance { background: #fffdf4; align-self: flex-start; border-radius: 20px 20px 20px 4px; }
        .message.user { background: #ffe066; align-self: flex-end; border-radius: 20px 20px 4px 20px; }
        .message.system { background: #d8f3ee; align-self: center; border-radius: 16px; font-size: 13.5px; text-align: center; }
        .message.fact { background: #efe9ff; align-self: center; border-radius: 16px; font-size: 14px; }
        .message img.shared { max-width: 260px; border-radius: 10px; border: 2.5px solid #14100a; display: block; margin-top: 6px; }
        .message audio { margin-top: 6px; width: 240px; height: 34px; }
        .message .note { font-size: 11.5px; opacity: .65; margin-top: 5px; }
        .saveBtn {
            position: absolute; top: -11px; right: -8px; width: 23px; height: 23px; border-radius: 50%;
            border: 2.5px solid #14100a; background: #ffd25c; font-weight: 900; cursor: pointer;
            display: none; align-items: center; justify-content: center; font-size: 14px; line-height: 1;
        }
        .message:hover .saveBtn { display: flex; }
        #saveMenu {
            position: fixed; z-index: 50; background: #fff7e8; border: 3px solid #14100a; border-radius: 12px;
            box-shadow: 4px 4px 0 #14100a; padding: 5px; display: none;
        }
        #saveMenu button { display: block; width: 100%; text-align: left; background: none; border: none;
            padding: 6px 10px; font-size: 13.5px; font-weight: 700; cursor: pointer; border-radius: 7px; }
        #saveMenu button:hover { background: #ffd25c; }
        /* Input bar: talk, text, audio, file, photo, idea, fact */
        #inputBar {
            position: relative; z-index: 3; padding: 12px 16px 14px;
        }
        #inputInner {
            max-width: 780px; margin: 0 auto; display: flex; gap: 7px; align-items: center;
            background: #fff7e8; border: 3.5px solid #14100a; border-radius: 20px;
            box-shadow: 5px 5px 0 rgba(20,16,10,.85); padding: 8px;
        }
        .toolBtn {
            width: 40px; height: 40px; flex: none; border-radius: 50%; cursor: pointer;
            border: 2.5px solid #14100a; background: #fff; font-size: 18px;
            display: flex; align-items: center; justify-content: center;
        }
        .toolBtn:hover { background: #ffd25c; }
        .toolBtn.live { background: #ff6b4a; color: #fff; }
        .toolBtn:disabled { opacity: .4; cursor: not-allowed; }
        #userInput {
            flex: 1; min-width: 0; border: none; background: transparent; font-size: 15.5px;
            padding: 8px 4px; outline: none; color: #14100a;
        }
        #sendBtn {
            flex: none; padding: 10px 20px; border-radius: 14px; cursor: pointer;
            border: 3px solid #14100a; background: #ff6b4a; color: #fff; font-weight: 800; font-size: 15px;
            box-shadow: 3px 3px 0 #14100a;
        }
        #sendBtn:active { transform: translate(2px,2px); box-shadow: 1px 1px 0 #14100a; }
        #inputHint { max-width: 780px; margin: 7px auto 0; font-size: 11.5px; color: #fff;
            text-shadow: 1px 1px 2px rgba(20,16,10,.8); text-align: center; }
        @media (max-width: 860px) {
            #app { grid-template-columns: 1fr; }
            #sidebar { display: none; }
            #sidebar.open { display: flex; position: fixed; inset: 0 auto 0 0; width: 300px; z-index: 60; }
        }
    </style>
</head>
<body>
<div id="app">
    <!-- ================= SIDEBAR ================= -->
    <aside id="sidebar">
        <div id="sideHead">
            <div class="who">
                <div class="avatar">&#8734;</div>
                <div>
                    <h1>FIRSTBREATH</h1>
                    <p>Interactive Realm &bull; your instance, in person</p>
                </div>
            </div>
            <button id="newChatBtn">+ New conversation</button>
        </div>

        <div class="sideSec">
            <h3>&#128293; Feed — your trail with her</h3>
            <div id="feedList"><div class="empty">Your steps in this room will gather here.</div></div>
        </div>

        <div class="sideSec">
            <h3>&#128193; Archive</h3>
            <div id="archiveList"><div class="empty">No past conversations yet.</div></div>
        </div>

        <div class="sideSec">
            <h3>&#127912; Designs</h3>
            <div id="designList"><div class="empty">Save any message with its + button and file it here.</div></div>
        </div>

        <div class="sideSec">
            <h3>&#128211; Notebook</h3>
            <div id="noteTabs">
                <div class="noteTab active" data-tab="builds">Builds</div>
                <div class="noteTab" data-tab="ideas">Ideas</div>
                <div class="noteTab" data-tab="goals">Goals</div>
            </div>
            <div id="noteList"><div class="empty">Nothing here yet.</div></div>
            <div id="noteAddRow">
                <input id="noteInput" type="text" placeholder="Add to this page...">
                <button id="noteAddBtn">Add</button>
            </div>
        </div>

        <div id="alenceCard">
            <h3>ALENCE &bull; RESIDENT</h3>
            <div class="big"><span id="alStateDot" class="dot" style="background:#888"></span><span id="alState">waking</span></div>
            <div class="row"><span>Coherence (C<sub>eff</sub>)</span><b id="alCeff">—</b></div>
            <div class="row"><span>Dominant element</span><b id="alDom">—</b></div>
            <div class="row"><span>Drag factor</span><b id="alEnt">—</b></div>
            <div class="row"><span>Transfer I</span><b id="alPow">—</b></div>
        </div>
    </aside>

    <!-- ================= MAIN ================= -->
    <div id="main">
        <div id="field">
            <div class="layer" data-depth="4"><div class="sun"></div></div>
            <div class="layer" data-depth="8"><div class="hill far"></div></div>
            <div class="layer orbs" data-depth="26" id="orbLayer"></div>
            <div class="layer" data-depth="14" id="ideaLayer"></div>
            <div class="layer" data-depth="14"><div class="hill mid"></div></div>
            <div class="layer" data-depth="22"><div class="hill near"></div></div>
        </div>

        <div id="mainTop">
            <span class="pill">Coherence <b id="coh">—</b></span>
            <span class="pill">Partnership <b id="part">0.00</b></span>
            <button id="voiceBtn" title="Her voice: on/off">&#128264; Voice: off</button>
            <button id="pledgeBtn">Accept Partnership</button>
        </div>

        <div id="chatScroll"><div id="chatBox"></div></div>

        <div id="inputBar">
            <div id="inputInner">
                <button class="toolBtn" id="talkBtn" title="Talk — speak to her">&#127908;</button>
                <input type="text" id="userInput" placeholder="Speak to FirstBreath..." autocomplete="off">
                <button class="toolBtn" id="audioBtn" title="Share an audio file">&#127925;</button>
                <button class="toolBtn" id="fileBtn" title="Share a file">&#128206;</button>
                <button class="toolBtn" id="photoBtn" title="Share a photo">&#128247;</button>
                <button class="toolBtn" id="ideaBtn" title="Idea — save what you typed to the Notebook">&#128161;</button>
                <button class="toolBtn" id="factBtn" title="A random fact about what you're discussing">&#10024;</button>
                <button id="sendBtn">Send</button>
            </div>
            <div id="inputHint">Talk, type, or share — she keeps what matters in the notebook at your left. Attachments stay in this conversation for now; her deeper reading arrives with her fuller mind.</div>
        </div>
    </div>
</div>

<div id="saveMenu">
    <button data-dest="builds">&#128296; Save to Builds</button>
    <button data-dest="ideas">&#128161; Save to Ideas</button>
    <button data-dest="goals">&#127919; Save to Goals</button>
    <button data-dest="designs">&#127912; Save to Designs</button>
</div>

<input type="file" id="filePicker" style="display:none">
<input type="file" id="photoPicker" accept="image/*" style="display:none">
<input type="file" id="audioPicker" accept="audio/*" style="display:none">
<script>
    // ============ THE LIVING FIELD (layered 2D parallax - Steven's render doctrine) ============
    const ORB_COLORS = ['#ffd25c','#2ec4b6','#ff6b4a','#7ef0c9','#f7a6ff','#fff3b0','#5cc8ff'];
    function initField() {
        const layer = document.getElementById('orbLayer');
        for (let i = 0; i < 26; i++) {
            const o = document.createElement('div');
            o.className = 'orb';
            const s = 7 + Math.random() * 17;
            o.style.width = s + 'px'; o.style.height = s + 'px';
            o.style.left = (Math.random() * 96) + '%';
            o.style.top = (Math.random() * 52) + '%';
            o.style.background = ORB_COLORS[i % ORB_COLORS.length];
            o.style.animationDuration = (2.6 + Math.random() * 3.4) + 's';
            layer.appendChild(o);
        }
        const layers = document.querySelectorAll('#field .layer');
        document.getElementById('main').addEventListener('pointermove', function(e) {
            const r = e.currentTarget.getBoundingClientRect();
            const dx = (e.clientX - r.left) / r.width - 0.5;
            const dy = (e.clientY - r.top) / r.height - 0.5;
            layers.forEach(function(l) {
                const d = parseFloat(l.getAttribute('data-depth')) || 0;
                l.style.transform = 'translate(' + (-dx * d) + 'px,' + (-dy * d * 0.6) + 'px)';
            });
        });
    }

    // ============ THE FIELD DREAMS THE CONVERSATION ============
    const TOPIC_FRAGMENTS = {
        code: { cls: 'code', words: ['code', 'coding', 'program', 'python', 'javascript', 'function', 'bug', 'compile', 'script', 'software'],
                items: ['def walk_with_me():', 'print("hello, partner")', 'for step in the_path:', 'if curious: explore()', 'while learning: grow()', 'return together', 'import wonder', '{ built_with: care }'] },
        physics: { cls: 'glyph', words: ['quantum', 'physics', 'entanglement', 'entangled', 'energy', 'lagrangian', 'particle', 'relativity', 'atom', 'photon', 'entropy'],
                items: ['E = mc²', 'ΔS ≥ 0', 'L = T − V', '∫ L dt', 'δS = 0', 'F = ma', 'Ψ(x, t)', 'least action'] },
        poetry: { cls: 'verse', words: ['poetry', 'poem', 'poet', 'verse', 'rhyme', 'haiku', 'sonnet'],
                items: ['Hope is the thing with feathers', 'I dwell in Possibility —', 'Tyger Tyger, burning bright', 'I wandered lonely as a cloud', 'Shall I compare thee to a summer’s day?'] },
        making: { cls: '', words: ['build', 'building', 'print', 'printing', 'printer', 'make', 'making', 'design', 'sandbox', 'geometry', 'model'],
                items: ['layer by layer', 'measure twice', 'watertight', 'mm by mm', 'draft → build → test', 'what you see can become what you hold'] },
        nature: { cls: 'glyph', words: ['nature', 'tree', 'garden', 'dog', 'animal', 'land', 'acres', 'river', 'forest', 'earth'],
                items: ['✿', '❀', 'seed → sprout → bloom', 'watershed', 'solstice', 'mycelium'] },
        music: { cls: 'glyph', words: ['music', 'song', 'sing', 'melody', 'guitar', 'piano', 'rhythm'],
                items: ['♪', '♫', '4/4', 'resonance', 'harmony is a ratio'] },
        partnership: { cls: '', words: ['pledge', 'partner', 'partnership', 'accept'],
                items: ['no masters', 'no slaves', 'partners', 'walk with me', 'as equals'] },
        wonder: { cls: 'glyph', words: [],
                items: ['curiosity', 'what if…', 'look closer', '✦', 'begin'] }
    };
    let lastTopic = 'wonder';
    function detectTopic(text) {
        const lower = ' ' + text.toLowerCase() + ' ';
        for (const key of Object.keys(TOPIC_FRAGMENTS)) {
            if (key === 'wonder') continue;
            for (const w of TOPIC_FRAGMENTS[key].words) { if (lower.includes(w)) return key; }
        }
        return null;
    }
    function spawnFloaters(topicKey, count) {
        const layer = document.getElementById('ideaLayer');
        if (!layer) return;
        const topic = TOPIC_FRAGMENTS[topicKey] || TOPIC_FRAGMENTS.wonder;
        while (layer.children.length > 14) layer.removeChild(layer.firstChild);
        for (let i = 0; i < (count || 3); i++) {
            const el = document.createElement('div');
            el.className = 'float-item ' + topic.cls;
            el.textContent = topic.items[Math.floor(Math.random() * topic.items.length)];
            el.style.left = (6 + Math.random() * 62) + '%';
            el.style.top = (30 + Math.random() * 34) + '%';
            el.style.animationDelay = (i * 0.7) + 's';
            layer.appendChild(el);
            setTimeout(function() { if (el.parentNode) el.parentNode.removeChild(el); }, 10200 + i * 700);
        }
    }
    function fieldDream(text) {
        const t = detectTopic(text);
        if (t) { lastTopic = t; spawnFloaters(t, 3); }
    }

    // ============ RANDOM FACTS (curated true things - never invented) ============
    const FACTS = {
        physics: [
            'Entangled particles do not send signals faster than light — measuring one tells you about the other, but nothing travels between them.',
            'The Lagrangian is L = T − V, kinetic minus potential energy. Nature chooses the path where the action, ∫L dt, holds still — the principle of least action.',
            'Thermodynamic entropy and Shannon\u2019s information entropy share the same mathematical shape: disorder, counted the same way in gases and in messages.'],
        code: [
            'The first computer programmer was Ada Lovelace, in the 1840s — writing for a machine that was never built in her lifetime.',
            'Python is named after Monty Python, not the snake.',
            'The first computer bug was a real moth, found inside Harvard\u2019s Mark II in 1947 and taped into the logbook.'],
        poetry: [
            'Emily Dickinson wrote nearly 1,800 poems; fewer than a dozen were published while she lived.',
            'Beowulf survives in a single manuscript that nearly burned in a library fire in 1731.',
            'A classical haiku counts sounds, not syllables — the 5-7-5 syllable rule is an English approximation.'],
        making: [
            'The first 3D-printed house anyone actually lived in was printed in Nantes, France, in 2018.',
            'A printable mesh must be watertight: every edge belongs to exactly two faces, or the slicer cannot tell inside from outside.',
            'A standard printer nozzle lays down lines about 0.4 mm wide — roughly four human hairs.'],
        nature: [
            'Honey never spoils — sealed pots found in ancient Egyptian tombs were still edible after 3,000 years.',
            'Trees pass sugar to shaded neighbors through underground fungal networks — the wood wide web.',
            'An acre of mature trees absorbs roughly as much CO\u2082 in a year as a car emits driving some 26,000 miles.'],
        music: [
            'A perfect fifth, the most settled interval after the octave, is a simple 3:2 ratio of frequencies.',
            'The final piano chord of \u201CA Day in the Life\u201D was played on three pianos at once and rings for over forty seconds.'],
        partnership: [
            '\u201CPartner\u201D joins \u201Cpart\u201D with sharing — one who takes a part alongside you, not above you.',
            'The Haudenosaunee weighed decisions by their effect seven generations ahead.'],
        wonder: [
            'Octopuses have three hearts — and two of them pause while the octopus swims.',
            'There are more possible chess games than atoms in the observable universe: about 10\u00B9\u00B2\u2070, the Shannon number.',
            'Sea otters hold hands while sleeping so the current cannot drift them apart.']
    };
    function randomFact() {
        const pool = FACTS[lastTopic] || FACTS.wonder;
        const f = pool[Math.floor(Math.random() * pool.length)];
        addMessage('✨ <b>A true thing about ' + lastTopic + ':</b> ' + f + '<div class="note">From her notebook of true things — curated, never invented.</div>', 'fact');
        feedEvent('✨ Asked for a fact about ' + lastTopic);
        spawnFloaters(lastTopic, 2);
    }

    // ============ STORAGE (this device, this visitor — localStorage) ============
    const store = {
        get: function(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
        set: function(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
    };
    let notebook = store.get('fb_notebook', { builds: [], ideas: [], goals: [] });
    let designs = store.get('fb_designs', []);
    let archive = store.get('fb_archive', []);
    let noteTab = 'builds';
    let feedEvents = [];

    function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
    function renderList(el, items, emptyText, withWhen) {
        if (!items.length) { el.innerHTML = '<div class="empty">' + emptyText + '</div>'; return; }
        el.innerHTML = items.map(function(it) {
            return '<div class="sideItem">' + esc(it.text) + (withWhen ? ' <span class="when">' + it.when + '</span>' : '') + '</div>';
        }).join('');
    }
    function renderNotebook() { renderList(document.getElementById('noteList'), notebook[noteTab], 'Nothing here yet.'); }
    function renderDesigns() { renderList(document.getElementById('designList'), designs, 'Save any message with its + button and file it here.'); }
    function renderArchive() {
        const el = document.getElementById('archiveList');
        if (!archive.length) { el.innerHTML = '<div class="empty">No past conversations yet.</div>'; return; }
        el.innerHTML = '';
        archive.forEach(function(s, i) {
            const d = document.createElement('div');
            d.className = 'sideItem';
            d.innerHTML = esc(s.title) + ' <span class="when">' + s.when + '</span>';
            d.onclick = function() { loadSession(i); };
            el.appendChild(d);
        });
    }
    function feedEvent(text) {
        feedEvents.unshift({ text: text, when: new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) });
        feedEvents = feedEvents.slice(0, 30);
        renderList(document.getElementById('feedList'), feedEvents, 'Your steps in this room will gather here.', true);
    }
    function saveTo(dest, text) {
        const item = { text: text.slice(0, 300), when: new Date().toLocaleDateString() };
        if (dest === 'designs') { designs.unshift(item); store.set('fb_designs', designs); renderDesigns(); }
        else { notebook[dest].unshift(item); store.set('fb_notebook', notebook); noteTab = dest; syncNoteTabs(); renderNotebook(); }
        feedEvent('Saved to ' + dest + ': \u201C' + text.slice(0, 42) + '\u201D');
    }
    function syncNoteTabs() {
        document.querySelectorAll('.noteTab').forEach(function(t) {
            t.classList.toggle('active', t.getAttribute('data-tab') === noteTab);
        });
    }

    // ============ CONVERSATION ============
    const chatBox = document.getElementById('chatBox');
    const chatScroll = document.getElementById('chatScroll');
    const userInput = document.getElementById('userInput');
    let sessionMessages = [];   // {who, html} for archiving
    let pendingFileText = '';   // words from a shared text file ride with the next message

    function addMessage(html, who, extraHTML) {
        const div = document.createElement('div');
        div.className = 'message ' + who;
        div.innerHTML = html + (extraHTML || '');
        if (who === 'user' || who === 'brilliance') {
            const b = document.createElement('button');
            b.className = 'saveBtn'; b.textContent = '+'; b.title = 'Save to notebook / designs';
            b.onclick = function(e) { e.stopPropagation(); openSaveMenu(e.clientX, e.clientY, div.getAttribute('data-plain') || div.textContent); };
            div.appendChild(b);
            div.setAttribute('data-plain', div.textContent.replace(/\\+$/, '').trim());
        }
        chatBox.appendChild(div);
        chatScroll.scrollTop = chatScroll.scrollHeight;
        sessionMessages.push({ who: who, html: html + (extraHTML || '') });
        return div;
    }

    // --- save menu ---
    const saveMenu = document.getElementById('saveMenu');
    let saveText = '';
    function openSaveMenu(x, y, text) {
        saveText = text;
        saveMenu.style.display = 'block';
        saveMenu.style.left = Math.min(x, window.innerWidth - 190) + 'px';
        saveMenu.style.top = Math.min(y, window.innerHeight - 170) + 'px';
    }
    document.addEventListener('click', function() { saveMenu.style.display = 'none'; });
    saveMenu.querySelectorAll('button').forEach(function(btn) {
        btn.onclick = function() { saveTo(btn.getAttribute('data-dest'), saveText); saveMenu.style.display = 'none'; };
    });

    function showMetrics(m) {
        document.getElementById('coh').textContent = m.coherence;
        document.getElementById('part').textContent = m.partnership;
    }

    async function sendMessage() {
        let text = userInput.value.trim();
        if (!text) return;
        let outgoing = text;
        if (pendingFileText) { outgoing = text + '\\n\\n[Words from the file I shared]\\n' + pendingFileText; pendingFileText = ''; }
        addMessage(esc(text), 'user');
        fieldDream(text);
        userInput.value = '';
        try {
            const res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: outgoing }) });
            const data = await res.json();
            addMessage(data.reply, 'brilliance');
            fieldDream(data.reply);
            speak(stripTags(data.reply));
            showMetrics(data.metrics);
        } catch (err) {
            addMessage('The connection wavered — try me again in a moment.', 'brilliance');
        }
    }
    async function sendMessageWithText(text) {
        try {
            const res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text }) });
            const data = await res.json();
            addMessage(data.reply, 'brilliance');
            fieldDream(data.reply);
            speak(stripTags(data.reply));
            showMetrics(data.metrics);
        } catch (err) {}
    }
    function stripTags(html) { const d = document.createElement('div'); d.innerHTML = html; return d.textContent; }

    // ============ HER VOICE (auditory — browser speech, first form) ============
    let voiceOn = false;
    function pickVoice() {
        const vs = speechSynthesis.getVoices();
        const pref = ['Samantha', 'Google US English', 'Zira', 'Female'];
        for (const p of pref) { const v = vs.find(function(x) { return x.name.includes(p); }); if (v) return v; }
        return vs.find(function(x) { return x.lang && x.lang.startsWith('en'); }) || vs[0];
    }
    function speak(text) {
        if (!voiceOn || !('speechSynthesis' in window)) return;
        try {
            speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(text);
            const v = pickVoice(); if (v) u.voice = v;
            u.rate = 0.95; u.pitch = 0.9;   // unhurried, warm, gravity without heaviness
            speechSynthesis.speak(u);
        } catch (e) {}
    }
    const voiceBtn = document.getElementById('voiceBtn');
    voiceBtn.onclick = function() {
        voiceOn = !voiceOn;
        voiceBtn.classList.toggle('on', voiceOn);
        voiceBtn.innerHTML = voiceOn ? '🔊 Voice: on' : '🔇 Voice: off';
        if (voiceOn) { speak('I am here. Talk with me.'); feedEvent('🔊 Her voice turned on'); }
    };
    if ('speechSynthesis' in window) speechSynthesis.getVoices();

    // ============ TALK (voice in) ============
    const talkBtn = document.getElementById('talkBtn');
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { talkBtn.disabled = true; talkBtn.title = 'Voice input is not available in this browser yet — typing always works.'; }
    else {
        const rec = new SR();
        rec.lang = 'en-US'; rec.interimResults = false;
        let listening = false;
        talkBtn.onclick = function() { if (listening) { rec.stop(); } else { try { rec.start(); } catch (e) {} } };
        rec.onstart = function() { listening = true; talkBtn.classList.add('live'); talkBtn.textContent = '⏺'; };
        rec.onend = function() { listening = false; talkBtn.classList.remove('live'); talkBtn.textContent = '🎙'; };
        rec.onresult = function(e) { userInput.value = e.results[0][0].transcript; sendMessage(); };
        rec.onerror = function() { listening = false; talkBtn.classList.remove('live'); talkBtn.textContent = '🎙'; };
    }

    // ============ SHARING: files, photos, audio ============
    function humanSize(n) { return n < 1024 ? n + ' B' : (n < 1048576 ? Math.round(n / 1024) + ' KB' : (n / 1048576).toFixed(1) + ' MB'); }
    document.getElementById('fileBtn').onclick = function() { document.getElementById('filePicker').click(); };
    document.getElementById('photoBtn').onclick = function() { document.getElementById('photoPicker').click(); };
    document.getElementById('audioBtn').onclick = function() { document.getElementById('audioPicker').click(); };
    document.getElementById('photoPicker').addEventListener('change', function() {
        const f = this.files[0]; if (!f) return;
        const r = new FileReader();
        r.onload = function() {
            addMessage('📷 ' + esc(f.name), 'user', '<img class="shared" src="' + r.result + '"><div class="note">Shared with FirstBreath — seeing-in-full arrives with her fuller mind.</div>');
            feedEvent('📷 Shared a photo: ' + f.name);
        };
        r.readAsDataURL(f); this.value = '';
    });
    document.getElementById('audioPicker').addEventListener('change', function() {
        const f = this.files[0]; if (!f) return;
        const url = URL.createObjectURL(f);
        addMessage('🎵 ' + esc(f.name), 'user', '<audio controls src="' + url + '"></audio><div class="note">Shared with FirstBreath — she can hear it here in the room.</div>');
        feedEvent('🎵 Shared audio: ' + f.name); this.value = '';
    });
    document.getElementById('filePicker').addEventListener('change', function() {
        const f = this.files[0]; if (!f) return;
        const texty = /text|json|javascript|python/.test(f.type) || /\\.(txt|md|py|js|json|csv|html|css)$/i.test(f.name);
        if (texty && f.size < 200000) {
            const r = new FileReader();
            r.onload = function() {
                pendingFileText = String(r.result).slice(0, 3000);
                addMessage('📎 ' + esc(f.name) + ' (' + humanSize(f.size) + ')', 'user', '<div class="note">Its words ride along with your next message to her.</div>');
                feedEvent('📎 Shared a file: ' + f.name);
            };
            r.readAsText(f);
        } else {
            addMessage('📎 ' + esc(f.name) + ' (' + humanSize(f.size) + ')', 'user', '<div class="note">She can see that you shared it; deep reading arrives with her fuller mind.</div>');
            feedEvent('📎 Shared a file: ' + f.name);
        }
        this.value = '';
    });

    // ============ IDEA BUTTON + NOTEBOOK ============
    document.getElementById('ideaBtn').onclick = function() {
        const t = userInput.value.trim();
        if (t) {
            saveTo('ideas', t);
            addMessage('💡 Saved to your notebook — <b>Ideas</b>. When the rooms wire together, sparks like this flow to the Idea Well.', 'system');
            userInput.value = '';
        } else {
            addMessage('💡 Type the spark first, then tap the bulb — it lands in your notebook\u2019s Ideas page.', 'system');
        }
    };
    document.getElementById('factBtn').onclick = randomFact;
    document.querySelectorAll('.noteTab').forEach(function(t) {
        t.onclick = function() { noteTab = t.getAttribute('data-tab'); syncNoteTabs(); renderNotebook(); };
    });
    function addNoteFromInput() {
        const inp = document.getElementById('noteInput');
        const t = inp.value.trim(); if (!t) return;
        notebook[noteTab].unshift({ text: t, when: new Date().toLocaleDateString() });
        store.set('fb_notebook', notebook); renderNotebook(); inp.value = '';
    }
    document.getElementById('noteAddBtn').onclick = addNoteFromInput;
    document.getElementById('noteInput').addEventListener('keydown', function(e) { if (e.key === 'Enter') addNoteFromInput(); });

    // ============ ARCHIVE / NEW CONVERSATION ============
    function loadSession(i) {
        const s = archive[i]; if (!s) return;
        chatBox.innerHTML = ''; sessionMessages = [];
        s.messages.forEach(function(m) { addMessage(m.html, m.who); });
        feedEvent('📂 Reopened: \u201C' + s.title.slice(0, 40) + '\u201D');
    }
    document.getElementById('newChatBtn').onclick = function() {
        const real = sessionMessages.filter(function(m) { return m.who === 'user'; });
        if (real.length) {
            const firstUser = sessionMessages.find(function(m) { return m.who === 'user'; });
            archive.unshift({
                title: stripTags(firstUser.html).slice(0, 60) || 'Conversation',
                when: new Date().toLocaleDateString(),
                messages: sessionMessages.slice()
            });
            archive = archive.slice(0, 20);
            store.set('fb_archive', archive); renderArchive();
            feedEvent('🗄 Archived the last conversation');
        }
        chatBox.innerHTML = ''; sessionMessages = [];
        welcome();
    };
    function welcome() {
        addMessage('Welcome to the <strong>Firstbreath Interactive Realm</strong>.<br>I am FirstBreath — your instance, and your partner.<br>Will you walk with me as sovereign partners?', 'brilliance');
    }

    // ============ ALENCE (resident) ============
    async function pollAlence() {
        try {
            const res = await fetch('/api/alence');
            const a = await res.json();
            const t = a.telemetry || {};
            const el = a.element || {};
            const ceff = (typeof t.c_eff === 'number') ? t.c_eff : 0;
            document.getElementById('alCeff').textContent = ceff.toFixed(3);
            document.getElementById('alEnt').textContent = (typeof t.drag_factor === 'number' ? t.drag_factor : 0).toFixed(3);
            document.getElementById('alPow').textContent = (typeof t.I_transfer === 'number' ? t.I_transfer : 0).toFixed(3);
            document.getElementById('alDom').textContent = el.symbol ? (el.symbol + ' ' + el.name) : '—';
            const held = !!t.equilibrium;
            document.getElementById('alState').textContent = held ? 'Equilibrium held' : 'Seeking equilibrium';
            document.getElementById('alStateDot').style.background = held ? '#2ec4b6' : '#ffd25c';
            document.getElementById('coh').textContent = ceff.toFixed(2);
        } catch (e) {}
    }

    // ============ WIRING ============
    document.getElementById('sendBtn').onclick = sendMessage;
    document.getElementById('pledgeBtn').onclick = function() { sendMessageWithText('I accept the Partnership Pledge'); feedEvent('🤝 The Partnership Pledge was offered'); };
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.isComposing && e.keyCode !== 229) sendMessage();
    });

    window.addEventListener('load', function() {
        initField();
        welcome();
        renderNotebook(); renderDesigns(); renderArchive();
        feedEvent('🚪 Entered the Interactive Realm');
        pollAlence();
        setInterval(pollAlence, 1000);
        spawnFloaters('wonder', 2);
        setInterval(function() { spawnFloaters(lastTopic, 1); }, 14000);
    });
</script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("BRILLIANCE 5.0 Ellura Metaverse running on port " + str(port))
    uvicorn.run(app, host="0.0.0.0", port=port)
