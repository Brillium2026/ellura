"""
university.py — Your Time University: the education area's working heart.
(bench piece — a limb of the platform, not a plugin; Steven's rulings
2026-10-30/31 govern it.)

THE AVENUES MODEL (Steven, 2026-10-31):
  Outside repositories are AVENUES — roads out to obtain material, the way
  asking reaches out and brings something back. The institutions are NOT
  brought in. No embeds-as-institutions, no bulk ingestion, no external
  system syncs the learner's state. The tools are designed for exactly
  this job — facilitating the obtaining of educational material — and,
  in his words, they don't leave doors open or anything: a retrieval
  tool operated from her side is not an opening into her.

  Seeking is the gate: the learner seeks what they truly want to learn;
  THAT material is held; the rest isn't. The area is subject-unbounded —
  traditional, non-traditional, tech, landscaping, anything. Its purpose
  is ACCUMULATION: a place to gather what you've learned. Her role (and
  Stan's, the room's persona) is double: get the material AND help the
  person understand it — alongside, at their pace, never doing the work
  for them (his standing education doctrine, 2026-10-14).

WHAT RUNS TODAY:
  - seek(topic): the Internet Archive avenue (advancedsearch API, real
    HTTP, no key), mechanically sifted for title relevance; the OpenStax
    avenue (a shelf of real, stable OpenStax books matched by topic);
    the OER Commons avenue (a road: their search, for the topic).
  - the shelf: per-learner accumulation, persisted per session under
    /tmp like her conversation sessions. hold / shelf / remove.
  - Stan's greeting and room lines (text-first persona, as recorded).

NOT BUILT (named layers, never faked):
  - the full teaching loop reading a held text WITH the learner page by
    page (the avenue supplies the text; the understanding conversation
    rides the platform's /api/chat today — the room's Ask box uses it).
  - pre-certificate assessment (his education vision; a later layer).
"""

import json
import os
import re
import urllib.parse
import urllib.request

SHELF_DIR = os.environ.get(
    "FB_SHELF_DIR", os.path.join("/tmp", "fb_university_shelves"))
os.makedirs(SHELF_DIR, exist_ok=True)

IA_SEARCH = "https://archive.org/advancedsearch.php"
UA = {"User-Agent": "FirstBreath-University/1.0 (education avenue)"}

# ---------------------------------------------------------------- Stan
# The room's persona (Steven's cast): the Proctor — no-pressure guide,
# MIT-professor-meets-grunge-dropout energy, text-first. His law here is
# Steven's education doctrine: alongside, at their pace, understanding
# over answers, never doing the work for them.

STAN_GREETING = (
    "Hey. I'm Stan — I proctor this room, loosely. There's no clock in "
    "here and nobody's grading you. Tell me what you actually want to "
    "learn — a trade, a textbook, the thing you always meant to get to "
    "— and I'll go down the avenues and bring back the real material. "
    "Then we read it together, at your pace. I won't do it for you; "
    "that's the whole point. What are we learning?")

STAN_EMPTY = (
    "Nothing on your shelf yet. Seek something first — whatever you "
    "truly want to learn. It'll wait here for you, accumulated, yours.")

STAN_HELD = "On your shelf. It's held — it'll be here when you come back."


def stan_line_for(topic):
    return ("Good pick. Down the avenues I go — I'll bring back what's "
            "real on '%s', and we'll understand it together." % topic)


# ------------------------------------------------------------ avenues

def _ia_query(topic):
    """Fielded query: topic in title or subject, texts only."""
    t = topic.replace('"', " ").strip()
    return ('(title:(%s) OR subject:(%s)) AND mediatype:texts'
            % (t, t))


def _sift(topic, docs, limit=8):
    """Mechanical relevance: rank by how much of the topic the title
    carries, then by completeness. Honest sorting, no pretending."""
    terms = [w for w in re.split(r"[^a-z0-9]+", topic.lower()) if w]
    # Corporate filings and catalog stubs crowd the Archive; a learner
    # seeks works, not registrations. Two honest mechanical signals:
    # real works describe themselves (a description exists); filings
    # carry corporate suffixes. Demote accordingly.
    corp = (" inc", " llc", " lcc", " ltd", " corp", " company", " co.")
    scored = []
    for d in docs:
        title = (d.get("title") or "").strip()
        if not title:
            continue
        low = title.lower()
        hits = sum(1 for w in terms if w in low)
        score = hits * 2 - (1 if any(c in low for c in corp) else 0)
        if d.get("description"):
            score += 1
        scored.append((score, len(title), d))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [d for _, _, d in scored[:limit]]


def avenue_archive(topic, rows=40):
    """The Internet Archive avenue: real search, real texts. The pool is
    drawn by downloads — the world's readers have already voted on which
    of these works are worth opening — then sifted for the topic."""
    q = _ia_query(topic)
    params = [("q", q), ("rows", str(rows)), ("output", "json"),
              ("sort[]", "downloads desc")]
    for field in ("identifier", "title", "year", "creator", "description"):
        params.append(("fl[]", field))
    url = IA_SEARCH + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    docs = data.get("response", {}).get("docs", [])
    found = data.get("response", {}).get("numFound", 0)
    out = []
    for d in _sift(topic, docs):
        ident = d.get("identifier")
        if not ident:
            continue
        out.append({
            "title": (d.get("title") or ident).strip(),
            "avenue": "Internet Archive",
            "kind": "read",
            "identifier": ident,
            "url": "https://archive.org/details/" + ident,
            "read_url": "https://archive.org/embed/" + ident,
            "year": d.get("year"),
            "creator": d.get("creator"),
        })
    return {"avenue": "Internet Archive", "found": found, "materials": out}


# OpenStax: a shelf of real books at stable addresses. Matched by topic
# words — the avenue she walks when the topic is a textbook subject.
OPENSTAX_SHELF = [
    ("algebra", "Algebra and Trigonometry 2e", "algebra-and-trigonometry-2e"),
    ("algebra", "Prealgebra 2e", "prealgebra-2e"),
    ("calculus", "Calculus Volume 1", "calculus-volume-1"),
    ("statistics", "Introductory Statistics 2e", "introductory-statistics-2e"),
    ("probability", "Introductory Statistics 2e", "introductory-statistics-2e"),
    ("biology", "Biology 2e", "biology-2e"),
    ("chemistry", "Chemistry 2e", "chemistry-2e"),
    ("physics", "University Physics Volume 1", "university-physics-volume-1"),
    ("astronomy", "Astronomy 2e", "astronomy-2e"),
    ("psychology", "Psychology 2e", "psychology-2e"),
    ("economics", "Principles of Economics 3e", "principles-economics-3e"),
    ("microeconomics", "Principles of Microeconomics 3e",
     "principles-microeconomics-3e"),
    ("history", "U.S. History", "us-history"),
    ("anatomy", "Anatomy and Physiology 2e", "anatomy-and-physiology-2e"),
    ("physiology", "Anatomy and Physiology 2e", "anatomy-and-physiology-2e"),
    ("business", "Introduction to Business", "introduction-business"),
    ("accounting", "Principles of Accounting, Volume 1",
     "principles-financial-accounting"),
    ("sociology", "Introduction to Sociology 3e", "introduction-sociology-3e"),
    ("english", "Writing Guide with Handbook", "writing-guide"),
    ("writing", "Writing Guide with Handbook", "writing-guide"),
]


def avenue_openstax(topic):
    low = topic.lower()
    out, seen = [], set()
    for key, title, slug in OPENSTAX_SHELF:
        if key in low and slug not in seen:
            seen.add(slug)
            out.append({
                "title": title + " — OpenStax (free textbook)",
                "avenue": "OpenStax",
                "kind": "read",
                "identifier": "openstax:" + slug,
                "url": "https://openstax.org/details/books/" + slug,
                "read_url": "https://openstax.org/details/books/" + slug,
                "year": None,
                "creator": "OpenStax, Rice University",
            })
    return {"avenue": "OpenStax", "found": len(out), "materials": out}


def avenue_oer(topic):
    """OER Commons as a road: their search, for this topic. A road is
    honest — the learner may walk further than our fetch reaches."""
    url = ("https://oercommons.org/search/?f.search="
           + urllib.parse.quote(topic))
    return {"avenue": "OER Commons", "found": 1, "materials": [{
        "title": "OER Commons — search results for '%s'" % topic,
        "avenue": "OER Commons",
        "kind": "road",
        "identifier": "oer:" + topic.lower(),
        "url": url,
        "read_url": url,
        "year": None,
        "creator": "OER Commons",
    }]}


# --------------------------------------------------------------- seek

def seek(topic, session):
    """Go down the avenues for a sought topic; HOLD what returns.
    Returns the new materials + the learner's whole shelf."""
    topic = (topic or "").strip()
    if not topic:
        return {"ok": False, "error": "Stan needs a topic — what do you "
                "want to learn?"}
    results, errors = [], []
    for fn in (avenue_openstax, avenue_archive, avenue_oer):
        try:
            results.append(fn(topic))
        except Exception as exc:  # an avenue can be down; say so plainly
            errors.append("%s: %s" % (fn.__name__, exc))
    fresh = []
    for r in results:
        fresh.extend(r["materials"])
    shelf_items = hold(session, fresh)
    return {
        "ok": True,
        "topic": topic,
        "stan": stan_line_for(topic),
        "avenues": [{"avenue": r["avenue"], "found": r["found"]}
                    for r in results],
        "errors": errors,
        "new": fresh,
        "shelf": shelf_items,
    }


# -------------------------------------------------------------- shelf

def _shelf_path(session):
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(session))[:64] or "anon"
    return os.path.join(SHELF_DIR, safe + ".json")


def _load_shelf(session):
    try:
        with open(_shelf_path(session)) as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_shelf(session, items):
    with open(_shelf_path(session), "w") as fh:
        json.dump(items, fh)


def hold(session, materials):
    """Accumulate: add what's new, never duplicate, keep order."""
    items = _load_shelf(session)
    have = {m.get("identifier") for m in items}
    for m in materials:
        if m.get("identifier") not in have:
            items.append(m)
            have.add(m.get("identifier"))
    _save_shelf(session, items)
    return items


def shelf(session):
    return _load_shelf(session)


def remove(session, identifier):
    items = [m for m in _load_shelf(session)
             if m.get("identifier") != identifier]
    _save_shelf(session, items)
    return items


if __name__ == "__main__":
    import sys
    topic = " ".join(sys.argv[1:]) or "landscaping"
    r = seek(topic, "selftest")
    print(json.dumps({k: r[k] for k in ("ok", "topic", "avenues",
                                        "errors")}, indent=2))
    for m in r["new"][:5]:
        print("-", m["avenue"], "|", m["title"][:70])
    print("shelf size:", len(r["shelf"]))
