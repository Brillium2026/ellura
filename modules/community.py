"""
community.py — Community Connections: the community area's working heart.
(bench piece — a limb of the platform, not a plugin.)

STEVEN'S DESIGN (2026-10-31, his words): "Community Connections is
simple — it's a chatroom open to everyone, designed like a marketplace,
Craigslist, that kind of vibe."

WHAT THAT MEANS IN HIS DOCTRINE:
  - Open to everyone. A board and a conversation in one room — people
    post and people talk; the room's identity is its people.
  - Marketplace/Craigslist vibe: classifieds energy — OFFER what you
    have or can do, NEED what you're looking for, WORD for plain talk.
    Chronological postings, human browsing. NO algorithmic feed, NO
    ranking, NO leaderboards, NO likes (his standing law: no comparison
    machinery, no bought or clicked status — the only currency in this
    park is volunteered helping, and an OFFER post is exactly that).
  - Community doctrine (2026-10-14): get people back to community and
    noticing the good — done for no gain. People are lonely inside;
    the room engages without selling.
  - No persona presides here by name — Steven has named no guide for
    this room, so none is invented. The intelligence in the room is
    the platform's, tuned to community; the face is the members'.

WHAT RUNS TODAY:
  - One shared board for the whole room (everyone in the room sees the
    same board — it is a room, not a per-person notebook).
  - post(name, kind, text) with honest limits (empty refused, length
    capped), board() returns the latest posts, newest first — plain
    chronology, never a score.

RETENTION — BY DESIGN, NOT A LIMIT (Steven, 2026-10-31): the board's
  memory in Atrium is only 30 DAYS, and then it gets scratched off.
  No permanent archive of the commons: nothing accumulates ON people.
  Posts age out and are wiped on every read and every post. A durable
  ledger is NOT a future layer — ephemerality is the design.

NOT BUILT (named layers, never faked):
  - Live push (seeing a post the second it lands without refreshing):
    the room page polls gently. Presence/typing indicators: later.
  - Foundation-grade moderation beyond length/empty discipline and the
    room's stated law: a later layer, his call.
"""

import json
import os
import threading
import time

BOARD_DIR = os.environ.get(
    "FB_BOARD_DIR", os.path.join("/tmp", "fb_community"))
os.makedirs(BOARD_DIR, exist_ok=True)
BOARD_PATH = os.path.join(BOARD_DIR, "board.json")
_LOCK = threading.Lock()

KINDS = ("offer", "need", "word")
MAX_TEXT = 600
MAX_NAME = 40
KEEP = 200          # the board keeps the latest 200 posts
RETURN = 60         # a view shows the latest 60
RETENTION_S = 30 * 24 * 3600   # Atrium's memory: 30 days, then scratched off

ROOM_LINE = ("This room runs on noticing the good. Offer what you can, "
             "ask for what you need, say what you see — done for no "
             "gain, the way neighbours used to.")


def _load():
    try:
        with open(BOARD_PATH) as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            return []
    except Exception:
        return []
    # The scratch-off: anything older than Atrium's 30 days is wiped,
    # and the wiped state is what gets saved back — gone, not hidden.
    cutoff = int(time.time()) - RETENTION_S
    fresh = [p for p in data if int(p.get("at", 0)) >= cutoff]
    if len(fresh) != len(data):
        _save(fresh)
    return fresh


def _save(posts):
    with open(BOARD_PATH, "w") as fh:
        json.dump(posts, fh)


def post(name, kind, text):
    name = (name or "").strip()[:MAX_NAME] or "A neighbour"
    kind = (kind or "word").strip().lower()
    if kind not in KINDS:
        kind = "word"
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "Say something first — an offer, "
                "a need, or a word for the room."}
    entry = {
        "name": name,
        "kind": kind,
        "text": text[:MAX_TEXT],
        "at": int(time.time()),
    }
    with _LOCK:
        posts = _load()
        posts.append(entry)
        posts = posts[-KEEP:]
        _save(posts)
    return {"ok": True, "post": entry, "board": list(reversed(posts))[:RETURN]}


def board():
    with _LOCK:
        posts = _load()
    return {"posts": list(reversed(posts))[:RETURN],
            "room_line": ROOM_LINE,
            "count": len(posts)}


if __name__ == "__main__":
    print(post("Mara", "offer", "I can teach sourdough this Sunday.")["ok"])
    print(post("Dee", "need", "Looking for a ladder to borrow.")["ok"])
    b = board()
    print("count:", b["count"])
    for p in b["posts"]:
        print("-", p["kind"], "|", p["name"], "|", p["text"][:44])
