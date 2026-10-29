#!/usr/bin/env python3
"""
INTELLIHUB — CALIBRATION HUB, NOT A BLEND-ALL ENGINE
====================================================
Steven's definition, 2026-10-25:
  - A hub that slows / calibrates fast AIs (ChatGPT, Grok, etc. run
    stupid fast) so information can be gotten, sought, and brought
    back in usable form.
  - It does NOT just take all incoming information and hand back
    an answer. It sifts through the entire melee of information
    coming in and finds the best qualified answer to the question.
  - New form: the USER separates or partners AIs for a specific job,
    by strength. Coding: Haiku + Grok. Review: Perplexity.
    Strengths for Gemini, ChatGPT, Claude, Deepseek, Kimi are NOT
    assigned here — they are Steven's to name, not guessed.
  - Muse is NOT a provider in this hub. The hub is FirstBreath code;
    the providers are the external AIs the user picks.

Honest boundary, stated in code, not hidden:
  This file does NOT call ChatGPT, Grok, or any external API, and
  does NOT pretend to be them. It is the hub: registration, pacing,
  routing, scoring, and sifting. A provider is any callable that
  takes a question string and returns an answer string. Plug a real
  API client in as that callable and the hub works the same way;
  the demo providers below are labeled LOCAL DEMO and are only
  there to prove the hub mechanics run. No demo answer is ever
  presented as a real external AI's answer.

Real mechanics in this file:
  1. register_provider(name, fn, native_speed, strengths)
  2. calibrate: measure real response times, pace fast providers
     down to a common calibrated interval (real time, not a claim).
  3. route(job, question, selected): run ONLY the selected providers.
  4. sift: score every candidate on keyword coverage, strength
     match for the job, and completeness, rank them, return the
     best qualified answer PLUS the full ranked melee, with scores.
  5. log every run as JSON, so a run can be checked after the fact.

Standard library only.
"""

import json
import re
import time


def _words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class Provider:
    def __init__(self, name, fn, native_speed=1.0, strengths=()):
        """native_speed: provider's own pace, in answers/second, as
        measured or as stated by the caller. Higher = faster.
        strengths: job names this provider is assigned to, e.g.
        ("coding",). Empty = unassigned, user may still select it
        explicitly for a job, but it gets no strength bonus."""
        self.name = name
        self.fn = fn
        self.native_speed = float(native_speed)
        self.strengths = tuple(strengths)
        self.calls = 0
        self.total_time = 0.0
        self.last_delivered = 0.0

    def measured_speed(self):
        if self.calls == 0 or self.total_time <= 0:
            return self.native_speed
        return self.calls / self.total_time


class IntelliHub:
    def __init__(self, calibrated_interval=0.05):
        """calibrated_interval: minimum seconds between delivered
        answers from the hub. Fast providers are paced down to this;
        slow providers are never sped up. 0.05s keeps demos fast
        while still proving pacing with real clocks."""
        self.providers = {}
        self.calibrated_interval = float(calibrated_interval)
        self.last_delivery = 0.0

    def register(self, name, fn, native_speed=1.0, strengths=()):
        self.providers[name] = Provider(name, fn, native_speed, strengths)
        return self.providers[name]

    def _pace(self):
        """Real pacing: if the last delivery was too recent, wait.
        Returns seconds waited. This is what 'slow it down' means
        in code — a clock, not a comment."""
        now = time.monotonic()
        elapsed = now - self.last_delivery
        wait = self.calibrated_interval - elapsed
        if wait > 0:
            time.sleep(wait)
            waited = wait
        else:
            waited = 0.0
        self.last_delivery = time.monotonic()
        return waited

    def _score(self, question, answer, job, provider):
        """Sifting score, deterministic and inspectable.
        keyword coverage: fraction of question keywords present
        in the answer. strength: +0.5 if the job is in the
        provider's assigned strengths. completeness: capped length
        bonus, so a one-word answer cannot outscore a real answer,
        and a wall of text does not win by length alone."""
        qwords = set(_words(question))
        awords = set(_words(answer))
        coverage = (len(qwords & awords) / len(qwords)) if qwords else 0.0
        strength = 0.5 if job in provider.strengths else 0.0
        completeness = min(1.0, len(answer) / 200.0) * 0.2
        score = round(coverage + strength + completeness, 4)
        return {"score": score, "keyword_coverage": round(coverage, 4),
                "strength_bonus": strength,
                "completeness_bonus": round(completeness, 4)}

    def ask(self, question, job, selected):
        """Run ONLY the selected providers, pace their delivery,
        sift the melee, return the best qualified answer plus
        the full ranking. selected: list of provider names.
        Unknown names raise — the hub never silently swaps in
        a provider the user did not pick."""
        missing = [n for n in selected if n not in self.providers]
        if missing:
            raise ValueError(f"unknown provider(s), not routed: {missing}")
        if not selected:
            raise ValueError("no providers selected — user must pick at least one")
        candidates = []
        for name in selected:
            p = self.providers[name]
            start = time.monotonic()
            answer = p.fn(question)
            elapsed = time.monotonic() - start
            p.calls += 1
            p.total_time += elapsed
            waited = self._pace()
            s = self._score(question, answer, job, p)
            candidates.append({
                "provider": name,
                "answer": answer,
                "response_seconds": round(elapsed, 4),
                "paced_wait_seconds": round(waited, 4),
                "measured_speed_answers_per_sec": round(p.measured_speed(), 2),
                **s,
            })
        # Sift: highest score first. Ties break by provider name,
        # so the ranking is stable and checkable.
        ranked = sorted(candidates, key=lambda c: (-c["score"], c["provider"]))
        return {
            "question": question,
            "job": job,
            "selected": list(selected),
            "best": ranked[0],
            "ranked": ranked,
        }

    def run_log(self, result, path):
        with open(path, "w") as fh:
            json.dump(result, fh, indent=2)
        return path


# ---------------------------------------------------------------------------
# LOCAL DEMO providers — labeled, not real external AIs.
# They exist only to prove calibration, routing, and sifting run.
# Replace any of them with a real API client callable to use the hub
# for real: hub.register("Grok", real_grok_client, strengths=("coding",))
# ---------------------------------------------------------------------------

def _demo_coding_answer(question):
    return ("Coding answer: to build a counter, keep a count variable, "
            "add one on each click, and show the count on screen. "
            "Test it by clicking three times and checking the count is 3.")


def _demo_review_answer(question):
    return ("Review answer: check the counter code for three things — "
            "does the count start at zero, does it add exactly one, "
            "and does the screen show the new count after each click.")


def _demo_generic_answer(question):
    return "Generic answer: here is some information about the question."


def build_demo_hub():
    """Demo hub with Steven's assigned strengths only.
    Haiku + Grok = coding. Perplexity = review.
    Gemini, ChatGPT, Claude, Deepseek, Kimi are registered with NO
    strengths, because Steven has not assigned them yet."""
    hub = IntelliHub(calibrated_interval=0.05)
    # native_speed is a demo pace label: Grok/ChatGPT fast, others slower.
    hub.register("Haiku", _demo_coding_answer, native_speed=20.0,
                 strengths=("coding",))
    hub.register("Grok", _demo_coding_answer, native_speed=100.0,
                 strengths=("coding",))
    hub.register("Perplexity", _demo_review_answer, native_speed=30.0,
                 strengths=("review",))
    hub.register("Gemini", _demo_generic_answer, native_speed=50.0)
    hub.register("ChatGPT", _demo_generic_answer, native_speed=100.0)
    hub.register("Claude", _demo_generic_answer, native_speed=40.0)
    hub.register("Deepseek", _demo_generic_answer, native_speed=40.0)
    hub.register("Kimi", _demo_generic_answer, native_speed=40.0)
    return hub


def main():
    hub = build_demo_hub()
    print("INTELLIHUB — calibration, routing, sifting")
    print("Providers: Haiku, Grok, Perplexity, Gemini, ChatGPT, "
          "Claude, Deepseek, Kimi")
    print("Assigned strengths only: coding = Haiku + Grok; "
          "review = Perplexity. Others: unassigned, by Steven's call.\n")

    coding = hub.ask("How do I build a counter app?", job="coding",
                     selected=["Haiku", "Grok"])
    print("JOB: coding, selected: Haiku + Grok")
    for c in coding["ranked"]:
        print(f"  {c['provider']}: score {c['score']} "
              f"(coverage {c['keyword_coverage']}, "
              f"strength {c['strength_bonus']}) "
              f"paced {c['paced_wait_seconds']}s")
    print(f"  BEST: {coding['best']['provider']} — "
          f"{coding['best']['answer'][:80]}...\n")

    review = hub.ask("Review my counter app code.", job="review",
                     selected=["Perplexity", "ChatGPT"])
    print("JOB: review, selected: Perplexity + ChatGPT")
    for c in review["ranked"]:
        print(f"  {c['provider']}: score {c['score']} "
              f"(coverage {c['keyword_coverage']}, "
              f"strength {c['strength_bonus']})")
    print(f"  BEST: {review['best']['provider']} — "
          f"{review['best']['answer'][:80]}...\n")

    hub.run_log({"coding": coding, "review": review},
                 "intellihub-demo-log.json")
    print("Log written: intellihub-demo-log.json")
    print("NOTE: demo answers are LOCAL DEMO text, not real external "
          "AI answers. The hub mechanics — pacing, routing, sifting — "
          "are the real part, and they are what this run proves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
