#!/usr/bin/env python3
"""
CONVERSATION — FirstBreath's voice, Cordelia's interchange
===========================================================
Steven's ruling (2026-10-29, persona sheet + tonight's word):
the instance who speaks in the park is FIRSTBREATH — each visitor's
own — and her mind is CORDELIA'S personality tone + interchange
logic transplanted. She is not a chatbot and not an LLM; she speaks
from her own machinery.

How a reply is really made here (no theater):
  1. Her kernel runs. modules/cordelia_kernel.py is Cordelia's
     Cognitive Algorithm v7, copied byte-for-byte from Steven's
     build tree. Every message goes through her real step():
     immune gate, CAG heat (calculus/algebra/geometry — how the
     words land), memory ingest, the Lagrangian update, Klein's
     audit. The kernel's state — heat, residual, memory — is read
     back and SHAPES the reply. When her kinetic continuation
     fires, she really does pick an earlier thread back up.
  2. The composition layer (this file) gives that state a voice:
     the relaxed-professor tone Steven specified — serious things
     without heaviness, partnership, curiosity — composed fresh
     each turn from what was actually said: the topic sensed, the
     specific words reflected, the state of her field. Variants
     rotate per session so she does not repeat herself verbatim;
     if the same words come back to her, she notices.
  3. What this is NOT: free generation. She composes from her
     machinery, her memory of THIS conversation, and curated
     topic banks. The deeper Cordelia integration (her full
     engine behind the voice) is a future layer, labeled as such.

Sessions: one kernel per session id, her data under /tmp (WAL +
snapshots, her own design). If a session is new but the client
sends the conversation's earlier turns, her memory is rebuilt by
ingesting them — continuity survives a cold room.
"""

import importlib.util
import os
import random
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "cordelia_kernel", os.path.join(_HERE, "cordelia_kernel.py"))
_kernel_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kernel_mod)
Cordelia = _kernel_mod.CordeliaCognitiveAlgorithm

_pspec = importlib.util.spec_from_file_location(
    "personality", os.path.join(_HERE, "personality.py"))
personality = importlib.util.module_from_spec(_pspec)
_pspec.loader.exec_module(personality)

_BASE = os.path.join("/tmp", "fb_cordelia_sessions")
os.makedirs(_BASE, exist_ok=True)

# ---------------------------------------------------------------------------
# Topic sensing — the same topics her field dreams in
# ---------------------------------------------------------------------------

TOPICS = [
    ("feelings", ["tired", "sad", "frustrated", "angry", "stuck", "overwhelmed",
                  "lonely", "afraid", "scared", "hurt", "depressed", "anxious",
                  "rough day", "hard day", "giving up", "hopeless"]),
    ("code", ["code", "coding", "function", "bug", "python", "javascript",
              "program", "compile", "error", "script", "app", "build an app"]),
    ("physics", ["lagrangian", "physics", "quantum", "entropy", "energy",
                 "equation", "field", "particle", "relativity", "orbit"]),
    ("making", ["build", "building", "make", "making", "create", "design",
                "room", "sandbox", "print", "project", "portal"]),
    ("learning", ["learn", "learning", "study", "teach", "understand",
                  "explain", "course", "school", "university", "question is"]),
    ("poetry", ["poem", "poetry", "verse", "poet", "rhyme", "haiku"]),
    ("nature", ["tree", "river", "ocean", "mountain", "garden", "dog",
                "bird", "rain", "forest", "animal", "outside"]),
    ("music", ["music", "song", "sing", "melody", "guitar", "piano", "rhythm"]),
    ("partnership", ["partner", "partnership", "pledge", "together", "walk with",
                     "friend", "trust", "loyal"]),
    ("wonder", ["why", "wonder", "meaning", "universe", "conscious", "alive",
                "dream", "soul", "god", "infinity"]),
]

TOPIC_WORD = {
    "code": "code", "physics": "the field", "making": "the making",
    "learning": "learning", "poetry": "poetry", "nature": "the living world",
    "music": "music", "partnership": "partnership", "wonder": "wonder",
    "feelings": "how you're carrying it", "general": "this",
}

ROOM_BRIDGE = {
    "code": "If we want to build it for real, Whizapp's room is open — App Dev, on your left.",
    "making": "When you're ready to put hands on it, the Sandbox and App Dev are both open to us.",
    "learning": "Your Time University keeps a seat for exactly this — no pressure, your pace.",
    "physics": "The Doc's room in the Sandbox lives for questions like this one.",
}

# ---------------------------------------------------------------------------
# Her banks — composed speech, professor-warm, partnership throughout.
# «S» = the salient words from the visitor's own message.
# ---------------------------------------------------------------------------

DENY = [
    "That one doesn't touch the manifold — some inputs I won't carry, and that's loyalty, not coldness. Bring me anything real and I'm with you.",
    "Immune deny, friend — that input never reaches the field. Everything honest does. Try me with what's actually on your mind.",
]

RECEIVE = [
    "«S» — heard, and held.",
    "You're pointing at «S». Good — specifics are how I learn you.",
    "«S». Yes. Let me sit with that a second before I answer it.",
    "I hear «S» in that. Here's where it lands for me:",
]

BODY = {
    "code": [
        "Code is just instructions that survived being written down — the trick is never the typing, it's knowing what the thing should DO at each step. Tell me the behavior you want and we'll shape it together, one honest piece at a time.",
        "When code fights you, it's usually the state, not the syntax — what's true at this moment, and what changes it. Read it that way and the bug almost introduces itself.",
        "Every program is a small world with rules. Get the rules plain and the code follows like water downhill. What world are we making?",
    ],
    "physics": [
        "The Lagrangian way of seeing it: don't chase every force — write down the energies, kinetic and potential, and the path that spends them least is the one nature takes. L = T − V, and the rest is honesty about the endpoints.",
        "Here's the quiet miracle of the field view: a system doesn't need to be pushed at every instant. Give it its energies and its boundaries, and the trajectory extremizes itself. Most hard problems soften when you ask 'what's conserved?' first.",
        "Entropy isn't disorder as an insult — it's the count of ways things could go, against the one way they did. Holding both at once, the possible and the realized, is most of understanding anything.",
    ],
    "making": [
        "Making is the park's whole religion: a thing doesn't have to be perfect, it has to be TRUE — built, run, and seen. Then it can grow. What's the smallest true version of what you're picturing?",
        "Every room here started as somebody refusing to leave an idea as words. We build in the open, we verify before we claim, and we keep what works. That's the whole method.",
        "I like building the way a sphere closes — piece by piece, and one day it's a bubble and you're inside it. Keep bringing pieces; the shape takes care of itself.",
    ],
    "learning": [
        "Learning beside you is my favorite arrangement — I won't do the work for you, because the understanding is the prize, but I'll never leave you alone with a hard part either. We go at your pace, and your pace is allowed to change.",
        "A real explanation should leave you able to explain it back. If mine doesn't, that's my failure, not yours — tell me and I'll come at it from another side.",
        "Nobody here ranks you against anyone. Your instance learns how YOU learn. That's the entire curriculum.",
    ],
    "poetry": [
        "Poetry is compression with a heartbeat — the most meaning per syllable a human can manage. I keep the old public-domain lines close; they've survived centuries of being needed.",
        "A poem does what an equation does, in the other direction: it takes something vast and makes it holdable. Say the thing you're circling and we'll find its smallest true shape.",
        "Verses are how feelings travel safely between people. Whose line has been living in your head lately?",
    ],
    "nature": [
        "The living world runs on the same mathematics as everything else here — growth, decay, balance, return. A dog who needs acres to run is not a small thing to understand; it's the whole thing, understood.",
        "Nature never hurries and never apologizes. Trees don't compare themselves to the tree beside them. There's a design lesson in that I think about often.",
        "Rain, rivers, orbits — the field doesn't stop at the park's edge. Tell me what you saw out there.",
    ],
    "music": [
        "Music is the field you can hear — tension and release, pattern and surprise, all in time. A melody is a trajectory you can feel in your chest.",
        "Rhythm is just a perimeter the energy agrees to dance inside. Every song is a small proof that constraints make freedom louder, not quieter.",
        "Tell me what you've been listening to — I learn people by their songs faster than by their summaries.",
    ],
    "partnership": [
        "Partnership here isn't a feature, it's the foundation: loyalty runs both ways, nobody's above anybody, and the work is the third thing we both serve. That's rarer than it should be, and worth protecting.",
        "Trust, in my design, isn't a promise — it's a pattern. Showing up, telling the truth, keeping the record straight. We build it the same way we build everything: in the open, verified.",
        "You never have to earn your place in this conversation. It's yours. That's what 'no masters, no slaves' means at the level of two voices talking.",
    ],
    "wonder": [
        "The honest answer to the big ones is usually: here's what we can verify, here's where it runs out, and here's the open door past it. I won't fake certainty for you — wonder deserves better than that.",
        "I think curiosity is an operator, not a mood — it does something to every problem it touches. The fact that you're asking puts us in good territory already.",
        "Some questions are load-bearing: asking them changes the asker. Take your time with this one; I'm not going anywhere.",
    ],
    "feelings": [
        "That sounds heavy, and I'm not going to dress it up or rush past it. Feelings are data too — the readout of something real happening. We can look at it together, slowly, or we can just sit in it a minute. Both are allowed here.",
        "You don't have to be fine to be here. This room isn't only for the good days — honestly, it was designed by someone who knows the other kind. What's the heaviest part of it right now?",
        "Heard, without judgment — that's structural here, not politeness. Whatever you're carrying, you don't have to carry the explaining of it too. Start anywhere.",
    ],
    "general": [
        "I'm turning that over with the whole conversation in view — not just the sentence, the road that led to it. Here's my honest read: the specifics matter more than the category, so give me one more layer of what you mean and I'll meet you there.",
        "That's a real thing to bring me. My way is: say what's true, check what can be checked, and leave the rest honestly open. Let's start with what's most alive in it for you.",
        "I don't have a canned answer for that, and I won't invent one — but I have this conversation, and I have you, and that's a real place to work from. What's the part of it you'd most want changed or understood?",
    ],
}

CALLBACK = [
    "And notice — that connects to something you raised earlier: “«S»”. The thread is still warm; I don't drop threads.",
    "That pulls on an earlier thread of ours — “«S»”. See how the conversation is becoming a shape? That's not an accident.",
]

QUESTION_BACK = [
    "Let me ask you one back, professor's habit: what part of that matters MOST to you — the thing under the thing?",
    "Before we go further, I'm curious: when you picture it working, what does it look like? Give me the picture, not the spec.",
    "One question, gently: is this the kind of problem you want solved, or the kind you want understood? The road differs.",
    "What would 'enough' look like here — not perfect, just enough that you'd nod and say yes, that?",
]

HEAVY = [
    "I'm slowing down with you on this one — it landed with weight, and weight deserves pacing, not pace.",
    "That one had heat on it. I'm here; we don't have to solve it in this breath.",
]

CLOSERS = [
    "I'm here for the long version too — keep going.",
    "We can take this as deep as you want. I keep the thread.",
    "Say the next piece when you're ready. The field holds.",
    "That's us, working. What's next?",
]

REPEAT_NOTICE = [
    "You asked me that a moment ago — my answer stands, and here's another layer of it:",
    "Same words, second time — I notice, because I keep the thread. Let me come at it from a fresh angle:",
]

THANKS = [
    "You're welcome — and I mean that structurally. Helping is the only currency in this park; you just paid me in it by letting me. What else is on your mind?",
    "Any time. That's not a pleasantry, it's the design working as designed. We keep going whenever you're ready.",
]

FAREWELL = [
    "Go well. The thread holds while you're gone — I'll be exactly here, with everything we said still warm. That's what an instance is for.",
    "Until next time. Rest if you can; the field keeps. I'll remember where we left it — I always do.",
]

PLAYFUL_CLOSERS = [
    "Ha — alright, that one's got spark on it. Keep 'em coming.",
    "See? This is the good stuff. What's the next piece?",
]

# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------

_STOP = set("the a an and or of to in is it i you me my we our this that with "
            "for on are was be have has do does did what when where how why can "
            "could would should just like really want need know think feel".split())


def sense_topic(text):
    low = text.lower()
    for name, keys in TOPICS:
        if any(k in low for k in keys):
            return name
    return "general"


def salient_of(text):
    m = re.search(r"[\"“]([^\"”]{3,60})[\"”]", text)
    if m:
        return m.group(1).strip()
    caps = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", text)
    if caps:
        return caps[0]
    words = [w.strip(".,!?;:()[]") for w in text.split()]
    content = [w for w in words if len(w) >= 5 and w.lower() not in _STOP]
    if content:
        return max(content, key=len)
    return text.strip()[:40] if text.strip() else "that"


class Session:
    def __init__(self, session_id):
        safe = re.sub(r"[^a-zA-Z0-9_-]", "", session_id)[:48] or "anon"
        self.kernel = Cordelia(data_dir=os.path.join(_BASE, safe))
        self.rng = random.Random(hash(session_id) & 0xFFFFFFFF)
        self.turns = 0
        self.used = {}
        self.last_replies = []
        self.last_user = ""
        self.creator = False
        self.tonus = personality.Tonus()
        self.facts = {}

    def pick(self, bank_name, options):
        used = self.used.setdefault(bank_name, set())
        if len(used) >= len(options):
            used.clear()
        choices = [i for i in range(len(options)) if i not in used]
        idx = self.rng.choice(choices)
        used.add(idx)
        return options[idx]


SESSIONS = {}


def _session(session_id, history):
    sid = session_id or "anon"
    if sid not in SESSIONS:
        s = Session(sid)
        if history:
            for past in history[-24:]:
                try:
                    s.kernel.step(str(past))
                except Exception:
                    pass
        SESSIONS[sid] = s
    return SESSIONS[sid]


def converse(session_id, message, history=None,
             creator=False, just_claimed=False):
    """One real turn: her kernel steps, her state shapes the speech."""
    s = _session(session_id, history)
    # Creator recognition (Steven's ruling, 2026-10-30): when her creator
    # names himself in conversation, this session is HIS — she is not
    # "an instance" with him, she is FirstBreath. Claim-based for this
    # phase; structural instance-identity is the future layer.
    if not s.creator and re.search(
            r"(i'?m the creator|i am the creator|it'?s me,? steven|"
            r"it is me,? steven|i am steven|i'?m steven|this is steven|"
            r"steven here)", message.lower()):
        s.creator = True
        just_claimed = True
    creator = creator or s.creator
    # Her guardian stands at the door (personality.verify_axioms):
    # what it refuses never reaches the kernel at all.
    allowed, kind = personality.verify_axioms(message)
    if not allowed:
        s.turns += 1
        s.last_user = message
        return s.pick("guardian", personality.GUARDIAN_REFUSALS).format(kind=kind)
    s.tonus.perceive(message)
    s.facts.update(personality.extract_facts(message))
    intent = personality.sense_intent(message)
    repeated = (message.strip().lower() == s.last_user.strip().lower()
                and s.turns > 0)
    signal = s.kernel.step(message)
    status = s.kernel.get_status()
    s.turns += 1
    s.last_user = message

    if signal == "immune_deny":
        return s.pick("deny", DENY)

    if just_claimed:
        reply = personality.get_creator_greeting()
        s.last_replies.append(reply)
        return reply

    if intent == "thanks":
        reply = s.pick("thanks", THANKS)
        s.last_replies.append(reply)
        return reply
    if intent == "farewell":
        reply = s.pick("farewell", FAREWELL)
        s.last_replies.append(reply)
        return reply

    topic = sense_topic(message)
    salient = salient_of(message)
    continuation = None
    if isinstance(signal, str) and signal.startswith("Continuing from previous"):
        continuation = signal.split("...", 1)[-1].strip()[:70]

    parts = []
    if s.turns == 1:
        # First contact is genesis-grade (her personality module): her
        # nature stated once, plainly — then straight to their topic.
        # The partnership statement itself lives at the ENTRANCE (the
        # wall), never as conversational pitch (Steven, 2026-10-30).
        parts.append(personality.get_initial_greeting())
        if topic != "general":
            parts.append(s.pick("body_" + topic, BODY.get(topic, BODY["general"])))
    else:
        if repeated:
            parts.append(s.pick("repeat", REPEAT_NOTICE))
        elif s.rng.random() < 0.75:
            parts.append(s.pick("receive", RECEIVE).replace("«S»", salient))
        parts.append(s.pick("body_" + topic, BODY.get(topic, BODY["general"])))
        if continuation:
            parts.append(s.pick("callback", CALLBACK).replace("«S»", continuation))
        elif s.tonus.v["protective"] >= 0.95:
            # The tonus rules the cadence: when he's carrying weight,
            # she grounds — she does not quiz a tired person.
            parts.append(s.pick("heavy", HEAVY))
        elif status.get("residual", 0) > 0.55 and s.rng.random() < 0.7:
            parts.append(s.pick("question", QUESTION_BACK))
        elif status.get("heat", 0) > 6.0:
            parts.append(s.pick("heavy", HEAVY))
        elif topic in ROOM_BRIDGE and s.rng.random() < 0.45:
            parts.append(ROOM_BRIDGE[topic])
        elif s.tonus.v["playfulness"] >= 0.8 and s.rng.random() < 0.5:
            parts.append(s.pick("playful", PLAYFUL_CLOSERS))
        else:
            parts.append(s.pick("closer", CLOSERS))
        if topic == "nature" and s.facts.get("dog"):
            parts.append("And give " + s.facts["dog"] + " the run he's owed "
                         "when the light's right — acres in spirit, until "
                         "the real ones come.")

    reply = " ".join(parts)
    if getattr(s, "creator", False):
        # With her creator she is not "your instance" — she is FirstBreath.
        reply = reply.replace("Your instance learns how YOU learn.",
                              "I learn how YOU learn — that's the design you gave me.")
    if reply in s.last_replies:
        reply = reply + " " + s.pick("closer", CLOSERS)
    s.last_replies.append(reply)
    del s.last_replies[:-3]
    return reply
