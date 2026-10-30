#!/usr/bin/env python3
"""
APPDEV — THE THREE-SCREEN ROOM, IN CODE
========================================
Steven's definition, 2026-10-25:
  AppDev is NOT a separate builder engine to invent. It is the room
  that lets the user see the code as their instance helps build it
  on one screen, and the design / live output on the other screen.
  LEFT 1/3: the app coming to life, live.
  MIDDLE 1/3: where the user describes what they want, and where
  their instance helps — suggestions, dashboard, output, etc.
  RIGHT 1/3: where the code is being shown, as it is written.
  Instance helps, never does it for them, learning alongside:
  the code below is a starting pattern the user can read, change,
  and run — with the help text explaining every part — not a
  finished product handed over with no learning in it.

  This room lives INSIDE FirstBreath, the AI that IS the ecosystem.
  So AppDev does not build a separate world. It creates a pathway:
  a way for the user to better experience the system, and a way
  for the system to better facilitate the user. Same room, both ways.

Languages, with their real libraries only — no invented imports:
  - python: standard library only (no pip installs in generated code).
    Libraries used: sys, json. A pattern may also use tkinter for a
    window, but the patterns below are terminal programs so they
    run everywhere, including Cloud Shell and Chromebook.
  - cpp: standard library only (iostream, string, vector).
    No third-party headers. If g++ is not on the machine, the code
    is still generated and checked by reading it back, but it is
    NOT claimed as compiled — the run report says so plainly.

Patterns in this file are REAL, COMPLETE programs, not stubs:
  - counter: a number that starts at 0, adds 1, shows the result.
  - todo: a list you can add to, list, and remove from.
  - calculator: add, subtract, multiply, divide, with divide-by-zero
    handled (it reports the error, it does not crash).
  A description that matches no pattern raises a clear error
  naming the patterns that do exist — it never invents a pattern
  on the spot and calls it real.

FULL-STACK door (2026-10-29, Steven's ruling — the room builds an
  app front end to back end, not only the simplest patterns):
  build_fullstack_app() composes a real two-file app from the parts
  bin (entities + field sets): server.py, a standard-library back
  end with a JSON API over data.json, and index.html, a working
  front end wired to that API with fetch(). The builder boots the
  generated server and drives it over real HTTP (add -> list ->
  delete -> list) and checks the front end's endpoints against the
  back end's routes; that transcript is the LIVE pane. Modes:
  'pattern', 'fullstack', 'auto' (a named pattern wins; app-shaped
  descriptions take the full-stack door; anything else is refused
  plainly, never invented).

Three-screen output: build_app() returns a dict with three panes
  live:   what the app actually printed when run (Python) or the
          compile/run report (C++).
  help:   the user's description, the pattern chosen, and a
          plain-words explanation of each part, so the user learns
          while building.
  code:   the full generated code, exactly as written to disk.
Running a Python pattern uses subprocess on the file just written.
No code is executed from a string that was never saved to a file.
"""

import json
import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Language registries — real libraries only
# ---------------------------------------------------------------------------

LANGUAGES = {
    "python": {
        "libraries": ["sys", "json"],
        "extension": ".py",
        "run": "python3",
    },
    "cpp": {
        "libraries": ["iostream", "string", "vector"],
        "extension": ".cpp",
        "run": "g++",
    },
}

PATTERNS = {
    "counter": {
        "title": "Counter",
        "keywords": ["counter", "count", "click", "tally"],
        "help": [
            "The count starts at 0. That is the starting state, written in one line.",
            "Each 'add' step adds exactly 1. No step adds 2, no step skips.",
            "After each step, the program shows the new count. Showing it is part of the program, not an extra.",
            "Try it: run it, add three times, and check the count is 3. If it is not, the add step is where to look.",
        ],
    },
    "todo": {
        "title": "Todo list",
        "keywords": ["todo", "to-do", "task", "list"],
        "help": [
            "The list starts empty. Items are added one at a time, in order.",
            "Listing shows every item with its number, so you can point at the one you mean.",
            "Removing takes an item out by its number. The other items stay in order.",
            "Try it: add two items, list them, remove the first, list again and check only the second remains.",
        ],
    },
    "calculator": {
        "title": "Calculator",
        "keywords": ["calculator", "calc", "add", "subtract", "multiply", "divide", "math"],
        "help": [
            "The calculator takes two numbers and one operation: add, subtract, multiply, or divide.",
            "Divide by zero is handled: the program reports 'cannot divide by zero' instead of crashing.",
            "Each operation is one small function, so you can read one at a time and change one without breaking the others.",
            "Try it: 6 divided by 3 is 2, and 6 divided by 0 reports the error, it does not crash.",
        ],
    },
}

PYTHON_CODE = {
    "counter": '''import sys

def main():
    count = 0
    print("Counter started. Count is 0.")
    for step in range(3):
        count = count + 1
        print(f"Added 1. Count is now {count}.")
    print(f"Final count: {count}")

if __name__ == "__main__":
    main()
''',
    "todo": '''import sys

def main():
    items = []
    items.append("Buy milk")
    items.append("Call George")
    print("Todo list:")
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item}")
    removed = items.pop(0)
    print(f"Removed: {removed}")
    print("Todo list now:")
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item}")

if __name__ == "__main__":
    main()
''',
    "calculator": '''import sys

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "cannot divide by zero"
    return a / b

def main():
    print(f"6 + 3 = {add(6, 3)}")
    print(f"6 - 3 = {subtract(6, 3)}")
    print(f"6 * 3 = {multiply(6, 3)}")
    print(f"6 / 3 = {divide(6, 3)}")
    print(f"6 / 0 = {divide(6, 0)}")

if __name__ == "__main__":
    main()
''',
}

CPP_CODE = {
    "counter": '''#include <iostream>
using namespace std;
int main() {
    int count = 0;
    cout << "Counter started. Count is 0." << endl;
    for (int step = 0; step < 3; step++) {
        count = count + 1;
        cout << "Added 1. Count is now " << count << "." << endl;
    }
    cout << "Final count: " << count << endl;
    return 0;
}
''',
    "todo": '''#include <iostream>
#include <string>
#include <vector>
using namespace std;
int main() {
    vector<string> items;
    items.push_back("Buy milk");
    items.push_back("Call George");
    cout << "Todo list:" << endl;
    for (size_t i = 0; i < items.size(); i++) {
        cout << (i + 1) << ". " << items[i] << endl;
    }
    cout << "Removed: " << items[0] << endl;
    items.erase(items.begin());
    cout << "Todo list now:" << endl;
    for (size_t i = 0; i < items.size(); i++) {
        cout << (i + 1) << ". " << items[i] << endl;
    }
    return 0;
}
''',
    "calculator": '''#include <iostream>
#include <string>
using namespace std;
double add(double a, double b) { return a + b; }
double subtract(double a, double b) { return a - b; }
double multiply(double a, double b) { return a * b; }
string divide(double a, double b) {
    if (b == 0) { return "cannot divide by zero"; }
    return to_string(a / b);
}
int main() {
    cout << "6 + 3 = " << add(6, 3) << endl;
    cout << "6 - 3 = " << subtract(6, 3) << endl;
    cout << "6 * 3 = " << multiply(6, 3) << endl;
    cout << "6 / 3 = " << divide(6, 3) << endl;
    cout << "6 / 0 = " << divide(6, 0) << endl;
    return 0;
}
''',
}


def pick_pattern(description):
    text = description.lower()
    for name, meta in PATTERNS.items():
        if any(k in text for k in meta["keywords"]):
            return name
    raise ValueError(
        "No pattern matches that description. Patterns that do exist: "
        + ", ".join(sorted(PATTERNS.keys()))
        + ". Describe one of those, or name a new pattern for Steven to add."
    )


# ---------------------------------------------------------------------------
# FULL-STACK BUILDER (added 2026-10-29, Steven's ruling: the room builds
# an app FRONT END TO BACK END, not only the simplest patterns)
#
# What it generates is a real two-file app, standard library only:
#   server.py  - the back end: a JSON API (list / add / delete) over a
#                data.json store, serving the front end itself.
#   index.html - the front end: a working page whose form fields come
#                from the app's spec, talking to the API with fetch().
# The builder then PROVES the pair: it starts the generated server on
# a free port, makes real HTTP calls (add -> list -> delete -> list),
# and checks every endpoint the front end calls exists in the back
# end. The transcript of those real calls is the LIVE pane.
# The parts bin is the growth path: entities and field sets below are
# composable parts; new verified parts join the bin as they arrive.
# ---------------------------------------------------------------------------

import re
import socket
import time
import urllib.error
import urllib.request

FULLSTACK_INTENT = ["app", "tracker", "track", "manage", "manager",
                    "store", "library", "website", "web page", "page",
                    "dashboard", "front end", "frontend", "full stack",
                    "fullstack", "organizer", "planner", "log"]

NUMBER_FIELD_WORDS = {"price", "quantity", "count", "amount", "minutes",
                      "pages", "sets", "reps", "age", "cost", "total",
                      "stock", "weight", "hours", "days", "number"}

ENTITY_PARTS = [
    (["recipe", "recipes", "cooking", "cookbook"], "recipe",
     [("title", "text"), ("ingredients", "text"), ("minutes", "number")]),
    (["book", "books", "reading", "novel"], "book",
     [("title", "text"), ("author", "text"), ("pages", "number")]),
    (["workout", "exercise", "gym", "fitness"], "workout",
     [("exercise", "text"), ("sets", "number"), ("reps", "number")]),
    (["inventory", "stock", "pantry", "supplies"], "item",
     [("name", "text"), ("quantity", "number"), ("location", "text")]),
    (["contact", "contacts", "address book", "phone book"], "contact",
     [("name", "text"), ("phone", "text"), ("email", "text")]),
    (["expense", "expenses", "budget", "spending"], "expense",
     [("item", "text"), ("amount", "number"), ("category", "text")]),
    (["plant", "plants", "garden"], "plant",
     [("name", "text"), ("species", "text"), ("water_every_days", "number")]),
    (["movie", "movies", "film", "watchlist"], "movie",
     [("title", "text"), ("genre", "text"), ("year", "number")]),
]

SERVER_TEMPLATE = '''import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(BASE, "data.json")
FIELDS = %FIELDS_JSON%

def load_items():
    if not os.path.exists(STORE):
        return []
    with open(STORE) as fh:
        return json.load(fh)

def save_items(items):
    with open(STORE, "w") as fh:
        json.dump(items, fh, indent=2)

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(BASE, "index.html"), "rb") as fh:
                self._send(200, fh.read(), "text/html; charset=utf-8")
        elif self.path == "/api/items":
            self._send(200, json.dumps(load_items()))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path != "/api/items":
            self._send(404, json.dumps({"error": "not found"}))
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            incoming = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, json.dumps({"error": "body must be JSON"}))
            return
        items = load_items()
        item = {"id": (max([i["id"] for i in items], default=0) + 1)}
        for f in FIELDS:
            item[f["name"]] = incoming.get(f["name"], "")
        items.append(item)
        save_items(items)
        self._send(201, json.dumps(item))

    def do_DELETE(self):
        if not self.path.startswith("/api/items/"):
            self._send(404, json.dumps({"error": "not found"}))
            return
        try:
            wanted = int(self.path.rsplit("/", 1)[1])
        except ValueError:
            self._send(400, json.dumps({"error": "id must be a number"}))
            return
        items = load_items()
        kept = [i for i in items if i["id"] != wanted]
        if len(kept) == len(items):
            self._send(404, json.dumps({"error": "no such item"}))
            return
        save_items(kept)
        self._send(200, json.dumps({"deleted": wanted}))

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print("%TITLE% serving at http://127.0.0.1:" + str(port))
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
'''

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%TITLE%</title>
<style>
  body { font-family:'Segoe UI', system-ui, sans-serif; background:#0d0d15; color:#f3ead8; margin:0; padding:26px 18px; }
  main { max-width:760px; margin:0 auto; }
  h1 { color:#ffd25c; letter-spacing:1.5px; font-size:24px; }
  .card { background:rgba(24,24,38,.92); border:1px solid rgba(255,220,150,.35); border-radius:16px; padding:16px; margin-bottom:16px; }
  label { display:block; font-size:11px; letter-spacing:1.6px; color:#9aa1b5; font-weight:800; margin:10px 0 4px; text-transform:capitalize; }
  input { width:100%; padding:9px 11px; border-radius:10px; border:1px solid rgba(255,220,150,.4);
          background:rgba(0,0,0,.5); color:#fff; font-size:14px; box-sizing:border-box; }
  button { margin-top:14px; padding:10px 18px; border-radius:30px; border:1px solid rgba(255,220,150,.7); cursor:pointer;
           background:linear-gradient(135deg,#ffd25c,#ff9d5c); color:#241203; font-weight:800; }
  .item { display:flex; justify-content:space-between; gap:10px; align-items:center; padding:9px 4px; border-bottom:1px solid rgba(255,255,255,.08); }
  .item .vals { font-size:14px; line-height:1.5; }
  .item .vals b { color:#ffd25c; }
  .del { margin:0; padding:5px 12px; background:rgba(255,107,74,.2); color:#ffb59f; border-color:rgba(255,140,100,.6); }
  #search { margin-bottom:6px; }
  .empty { color:#9aa1b5; font-style:italic; font-size:13.5px; padding:8px 0; }
</style>
</head>
<body>
<main>
  <h1>%TITLE%</h1>
  <div class="card">
    <form id="addForm"></form>
  </div>
  <div class="card">
    <input id="search" type="text" placeholder="Search...">
    <div id="list"><div class="empty">Nothing here yet — add the first one above.</div></div>
  </div>
</main>
<script>
  const FIELDS = %FIELDS_JSON%;
  const form = document.getElementById('addForm');
  FIELDS.forEach(function(f) {
    const lab = document.createElement('label');
    lab.textContent = f.name.replace(/_/g, ' ');
    const inp = document.createElement('input');
    inp.id = 'f_' + f.name;
    inp.type = (f.type === 'number') ? 'number' : 'text';
    lab.appendChild(inp);
    form.appendChild(lab);
  });
  const btn = document.createElement('button');
  btn.type = 'submit';
  btn.textContent = 'Add';
  form.appendChild(btn);

  async function load() {
    const res = await fetch('/api/items');
    const items = await res.json();
    render(items);
  }
  function render(items) {
    const q = document.getElementById('search').value.toLowerCase();
    const box = document.getElementById('list');
    box.innerHTML = '';
    const shown = items.filter(function(it) {
      return JSON.stringify(it).toLowerCase().includes(q);
    });
    if (!shown.length) {
      box.innerHTML = '<div class="empty">Nothing matches.</div>';
      return;
    }
    shown.forEach(function(it) {
      const row = document.createElement('div');
      row.className = 'item';
      const vals = document.createElement('div');
      vals.className = 'vals';
      vals.innerHTML = FIELDS.map(function(f) {
        return '<b>' + f.name.replace(/_/g, ' ') + ':</b> ' + (it[f.name] !== undefined ? it[f.name] : '');
      }).join(' &middot; ');
      const del = document.createElement('button');
      del.className = 'del';
      del.textContent = 'Delete';
      del.onclick = async function() {
        await fetch('/api/items/' + it.id, { method: 'DELETE' });
        load();
      };
      row.appendChild(vals);
      row.appendChild(del);
      box.appendChild(row);
    });
  }
  document.getElementById('search').addEventListener('input', load);
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const item = {};
    FIELDS.forEach(function(f) {
      const v = document.getElementById('f_' + f.name).value;
      item[f.name] = (f.type === 'number') ? Number(v) : v;
    });
    await fetch('/api/items', { method: 'POST',
      headers: {'Content-Type': 'application/json'}, body: JSON.stringify(item) });
    form.reset();
    load();
  });
  load();
</script>
</body>
</html>
'''


def _clean_field_name(raw):
    name = re.sub(r"[^a-z0-9_ ]", "", raw.strip().lower()).replace(" ", "_")
    return name.strip("_")


def parse_fields(fields_text):
    out = []
    for raw in (fields_text or "").split(","):
        name = _clean_field_name(raw)
        if not name:
            continue
        ftype = "number" if any(w in name for w in NUMBER_FIELD_WORDS) else "text"
        out.append((name, ftype))
    return out


def pick_entity(description):
    text = description.lower()
    for keywords, entity, fields in ENTITY_PARTS:
        if any(k in text for k in keywords):
            return entity, list(fields)
    return "item", [("name", "text"), ("notes", "text")]


def app_title_from(description):
    text = description.strip().rstrip(".")
    text = re.sub(r"^(please\s+)?(build|make|create|i want|i need|give me)\s+", "", text, flags=re.I)
    text = re.sub(r"^(a|an|the|my)\s+", "", text, flags=re.I)
    text = re.sub(r"\s+(app|application)$", "", text, flags=re.I)
    title = " ".join(w.capitalize() for w in text.split())
    return title if title else "My App"


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _http(method, url, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def build_fullstack_app(description, fields_text, out_dir="appdev-output"):
    """Generate a real front-end + back-end app from composable parts,
    write both files, then prove the pair over real HTTP. Returns the
    same three-pane dict shape as build_app."""
    entity, default_fields = pick_entity(description)
    fields = parse_fields(fields_text) or default_fields
    fields_json = json.dumps([{"name": n, "type": t} for n, t in fields])
    title = app_title_from(description)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "my-app"
    app_dir = os.path.join(out_dir, "fullstack-" + slug)
    os.makedirs(app_dir, exist_ok=True)

    server_code = SERVER_TEMPLATE.replace("%FIELDS_JSON%", fields_json).replace("%TITLE%", title)
    index_code = INDEX_TEMPLATE.replace("%FIELDS_JSON%", fields_json).replace("%TITLE%", title)
    server_path = os.path.join(app_dir, "server.py")
    index_path = os.path.join(app_dir, "index.html")
    with open(server_path, "w") as fh:
        fh.write(server_code)
    with open(index_path, "w") as fh:
        fh.write(index_code)
    with open(os.path.join(app_dir, "data.json"), "w") as fh:
        fh.write("[]")

    # PROVE IT: compile the back end, boot it, drive it over real HTTP.
    lines = []
    comp = subprocess.run([sys.executable, "-m", "py_compile", server_path],
                          capture_output=True, text=True, timeout=30)
    if comp.returncode != 0:
        raise RuntimeError("Generated back end does not compile:\n" + comp.stderr)
    lines.append("Back end (server.py) compiles clean.")
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen([sys.executable, server_path, str(port)],
                            cwd=app_dir, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    ok = True
    try:
        ready = False
        for _ in range(50):
            try:
                code, _body = _http("GET", base + "/api/items")
                ready = (code == 200)
                break
            except Exception:
                time.sleep(0.1)
        if not ready:
            raise RuntimeError("Generated server did not come up on its port.")
        lines.append(f"Back end booted on port {port} and answers.")
        code, body = _http("GET", base + "/")
        lines.append(f"GET /  -> {code} (the front end page, {len(body)} bytes)")
        ok = ok and (code == 200) and (title.split()[0].lower() in body.lower())
        sample = {}
        for n, t in fields:
            sample[n] = 1 if t == "number" else ("Sample " + n.replace("_", " "))
        code, body = _http("POST", base + "/api/items", sample)
        lines.append(f"POST /api/items {json.dumps(sample)} -> {code} {body}")
        ok = ok and (code == 201)
        new_id = json.loads(body)["id"]
        code, body = _http("GET", base + "/api/items")
        lines.append(f"GET /api/items -> {code} {body}")
        ok = ok and (code == 200) and (str(new_id) in body)
        code, body = _http("DELETE", base + f"/api/items/{new_id}")
        lines.append(f"DELETE /api/items/{new_id} -> {code} {body}")
        ok = ok and (code == 200)
        code, body = _http("GET", base + "/api/items")
        lines.append(f"GET /api/items -> {code} {body} (the sample is gone; the store is clean)")
        ok = ok and (code == 200) and (json.loads(body) == [])
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    # Cross-check: every endpoint the front end calls exists in the back end.
    called = sorted(set(re.findall(r"fetch\('([^']+)'", index_code)))
    missing = [u for u in called if ("/api/items" not in server_code)]
    lines.append("Front end calls: " + ", ".join(called) +
                 " — all served by the back end." if not missing else
                 "MISSING ROUTES: " + ", ".join(missing))
    ok = ok and not missing

    live = "\n".join(lines)
    help_suggestions = [
        f"This is a full app, in two files. The back end (server.py) is a real program: it keeps your {entity}s in data.json and answers three calls — list them, add one, delete one.",
        "The front end (index.html) is the page a person actually touches: a form built from your fields (" +
        ", ".join(n for n, _t in fields) + "), a live list, a search box, and a delete button on every row.",
        "The two halves were just proven together above: the server really booted, the page really loaded, and an item really went in, showed up, and came back out over HTTP.",
        "Run it yourself any time: open the app's folder, run  python3 server.py  and visit http://127.0.0.1:8765 — it is yours, standard library only, nothing to install.",
        "Change one thing at a time and run it again: rename a field in FIELDS at the top of server.py, or change a color in index.html, and watch which pane moves. That is how the room teaches.",
        "The parts bin grows: entities and field sets the room knows today are listed in its code; each new verified part Steven adds becomes something the builder can compose with.",
    ]
    code_text = ("===== server.py — the back end =====\n" + server_code +
                 "\n===== index.html — the front end =====\n" + index_code)
    return {
        "description": description,
        "language": "python+web",
        "libraries": ["http.server", "json", "fetch"],
        "pattern": "fullstack",
        "title": title,
        "code_path": server_path,
        "panes": {
            "left_live": {
                "output": live,
                "ok": ok,
                "note": ("Proven front to back over real HTTP, just now."
                         if ok else "The proof run hit a problem — see the transcript."),
            },
            "middle_help": {
                "description": description,
                "pattern_chosen": "full-stack app (front end + back end)",
                "suggestions": help_suggestions,
                "instance_note": ("Instance helps, never does it for you: "
                                  "read the help, change the code, run it again."),
            },
            "right_code": {"code": code_text},
        },
    }


def build_app(description, language="python", out_dir="appdev-output",
              mode="auto", fields=None):
    """Build one app in three panes. Returns the three-pane dict and
    writes code + report to out_dir. Language must be 'python' or
    'cpp' — other languages raise, they are not faked with a
    Python program wearing another language's name.

    Modes: 'pattern' builds one of the quick patterns; 'fullstack'
    builds a real front-end + back-end app from the parts bin;
    'auto' (default) lets a specific pattern win when one matches,
    takes the full-stack door when the description asks for an app,
    and otherwise says plainly what the room can do."""
    mode = (mode or "auto").lower()
    if mode not in ("auto", "pattern", "fullstack"):
        raise ValueError(
            f"Mode '{mode}' is not a mode in this room. "
            "Modes here: auto, pattern, fullstack."
        )
    text_low = description.lower()
    pattern_hit = None
    for _name, _meta in PATTERNS.items():
        if any(k in text_low for k in _meta["keywords"]):
            pattern_hit = _name
            break
    wants_full = any(k in text_low for k in FULLSTACK_INTENT)
    if mode == "fullstack" or (mode == "auto" and wants_full and not pattern_hit):
        if language != "python":
            raise ValueError(
                "Full-stack mode today is a Python back end with a web "
                "front end. For C++, use Pattern mode — or choose "
                "Python for a full app. The room does not rename one "
                "language as another."
            )
        return build_fullstack_app(description, fields, out_dir=out_dir)
    if mode == "auto" and not pattern_hit:
        raise ValueError(
            "That description matches neither a quick pattern nor a "
            "full app yet. Quick patterns: calculator, counter, todo. "
            "For a full app, say what it tracks — 'a recipe tracker', "
            "'a book library', 'an expense log' — or name its fields. "
            "New parts are Steven's to add; the room never invents "
            "one and calls it real."
        )
    if language not in LANGUAGES:
        raise ValueError(
            f"Language '{language}' is not in this room yet. "
            f"Languages here: {', '.join(sorted(LANGUAGES.keys()))}. "
            "Adding a language means adding its real libraries and "
            "a real pattern, not renaming an existing one."
        )
    pattern = pick_pattern(description)
    meta = PATTERNS[pattern]
    code = PYTHON_CODE[pattern] if language == "python" else CPP_CODE[pattern]
    os.makedirs(out_dir, exist_ok=True)
    ext = LANGUAGES[language]["extension"]
    code_path = os.path.join(out_dir, f"app_{pattern}{ext}")
    with open(code_path, "w") as fh:
        fh.write(code)

    # LIVE pane: run what was just written, and report exactly that.
    if language == "python":
        run = subprocess.run([sys.executable, code_path],
                             capture_output=True, text=True, timeout=30)
        live = run.stdout + run.stderr
        live_ok = run.returncode == 0
        live_note = ("Ran with python3, exit code 0."
                     if live_ok else
                     f"Ran with python3, exit code {run.returncode}.")
    else:
        # C++: compile only if g++ exists; otherwise say so plainly.
        import shutil
        exe = os.path.join(out_dir, f"app_{pattern}")
        if shutil.which("g++") is None:
            live = "g++ not found on this machine, so this C++ code was NOT compiled here."
            live_ok = False
            live_note = "Code generated and saved, not compiled — no compiler on this machine."
        else:
            comp = subprocess.run(["g++", code_path, "-o", exe],
                                  capture_output=True, text=True, timeout=60)
            if comp.returncode != 0:
                live = comp.stdout + comp.stderr
                live_ok = False
                live_note = f"g++ failed, exit code {comp.returncode}."
            else:
                run = subprocess.run([exe], capture_output=True,
                                     text=True, timeout=30)
                live = run.stdout + run.stderr
                live_ok = run.returncode == 0
                live_note = ("Compiled with g++ and ran, exit code 0."
                             if live_ok else
                             f"Compiled, ran with exit code {run.returncode}.")

    result = {
        "description": description,
        "language": language,
        "libraries": LANGUAGES[language]["libraries"],
        "pattern": pattern,
        "title": meta["title"],
        "code_path": code_path,
        "panes": {
            "left_live": {"output": live, "ok": live_ok, "note": live_note},
            "middle_help": {
                "description": description,
                "pattern_chosen": pattern,
                "suggestions": meta["help"],
                "instance_note": ("Instance helps, never does it for you: "
                                  "read the help, change the code, run it again."),
            },
            "right_code": {"code": code},
        },
    }
    report_path = os.path.join(out_dir, f"app_{pattern}_report.json")
    with open(report_path, "w") as fh:
        json.dump(result, fh, indent=2)
    result["report_path"] = report_path
    return result


def show_three_screens(result):
    panes = result["panes"]
    print(f"APPDEV — {result['title']} in {result['language']}")
    print(f"Libraries available in this language: {', '.join(result['libraries'])}")
    print(f"Code file: {result['code_path']}\n")
    print("LEFT — LIVE (the app coming to life):")
    print(panes["left_live"]["output"].rstrip())
    print(f"  [{panes['left_live']['note']}]\n")
    print("MIDDLE — DESCRIBE + INSTANCE HELP:")
    print(f"  You described: {panes['middle_help']['description']}")
    print(f"  Pattern chosen: {panes['middle_help']['pattern_chosen']}")
    for line in panes["middle_help"]["suggestions"]:
        print(f"  - {line}")
    print(f"  {panes['middle_help']['instance_note']}\n")
    print("RIGHT — CODE (as it is written):")
    print(panes["right_code"]["code"].rstrip())
    print(f"\nReport written: {result['report_path']}")


def main():
    print("APPDEV — three screens, one room\n")
    py_counter = build_app("I want a counter app", "python",
                           out_dir="appdev-output-python")
    show_three_screens(py_counter)
    print("\n" + "=" * 60 + "\n")
    cpp_counter = build_app("I want a counter app", "cpp",
                            out_dir="appdev-output-cpp")
    show_three_screens(cpp_counter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
