v"""
Ellura Sovereign Runtime — one complete system.

This is the unified assembly of everything in the Ellura project: not a
chatbot, not a cloud API client, but a local, physics-governed sovereign
runtime. Every input passes through six layers, evaluated in order:

  1. GATE      BugSandbox threat evaluation. H_cov > 0.7 -> immune_deny.
               Nothing hostile ever reaches the physics.
  2. PHYSICS   Cordelia CAG field engine (harmonic + quartic + periodic
               potentials, adaptive metric tensor, 8.5% drift learning)
               when NumPy is available; otherwise the pure-stdlib
               ForgeCore symplectic substrate. Same axioms, no dependency.
  3. GUARDIAN  SHA3-256 seal of (state || tau) at every step. Any mismatch
               with the sealed checkpoint rolls back to G_{t-dt}.
  4. DRIFT     v2 drift band: delta = |T_pred - (E_tot - V)| / R* <= 0.085.
               Breach triggers purge-as-mercy: zeroize volatile state and
               cold-restart from the last persistent G_t anchor.
  5. NAN GUARD isnan() anywhere in the live tensor aborts the step
               immediately. Silent divergence is not permitted.
  6. TELEMETRY Kinetic throughput, guardian/drift status, and gate verdicts
               are recorded every cycle and served live over the bridge.

The runtime is deterministic, local, and self-verifying — the opposite of a
corporate black-box endpoint.
"""

import math
import struct

from .bug_sandbox import BugSandbox
from .kinetic_throughput import KineticThroughput
from .guardian import GuardianInvariant
from .drift_band import DriftBandV2
from .forgecore_chromebook import ForgeCoreChromebook
from .hardened_substrate import NaNPropagationAbort

try:
    from .first_breath import FirstBreathSystem
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ----------------------------------------------------------------------
# Physics adapters: one hardened core, two interchangeable engines.
# ----------------------------------------------------------------------
class _CAGAdapter:
    """Cordelia CAG field engine (First Breath / fifth generation)."""

    tag = b"C"

    def __init__(self, dimension):
        self.sys = FirstBreathSystem(dimensions=dimension)
        self.dimension = dimension

    def floats(self):
        s = self.sys.substrate
        r = self.sys.routing
        return (
            [float(x) for x in s.q]
            + [float(x) for x in s.q_dot]
            + [float(r.accumulated_learning)]
        )

    def restore(self, floats):
        n = self.dimension
        q, q_dot, learning = floats[:n], floats[n:2 * n], floats[2 * n]
        import numpy as np

        self.sys.substrate.q = np.array(q, dtype=np.float64)
        self.sys.substrate.q_dot = np.array(q_dot, dtype=np.float64)
        self.sys.routing.accumulated_learning = float(learning)
        self.sys.substrate.deform_metric_tensor(float(learning))

    def zeroize(self):
        import numpy as np

        n = self.dimension
        self.sys.substrate.q = np.zeros(n, dtype=np.float64)
        self.sys.substrate.q_dot = np.zeros(n, dtype=np.float64)
        self.sys.routing.accumulated_learning = 0.0
        self.sys.substrate.deform_metric_tensor(0.0)

    def step(self, dt):
        pre = self.sys.routing.evaluate_lagrangian(self.sys.substrate)
        t_pred = pre["kinetic_T"]
        self.sys.execute_step(dt=dt)
        post = self.sys.routing.evaluate_lagrangian(self.sys.substrate)
        return t_pred, post["kinetic_T"], post["potential_V"]


class _StdlibAdapter:
    """Pure-stdlib ForgeCore symplectic substrate (Chromebook path)."""

    tag = b"S"

    def __init__(self, dimension, data_dir):
        self.core = ForgeCoreChromebook(dimension=dimension, data_dir=data_dir)
        self.dimension = dimension

    def floats(self):
        return list(self.core.q) + list(self.core.p) + [0.0]

    def restore(self, floats):
        n = self.dimension
        self.core.q = list(floats[:n])
        self.core.p = list(floats[n:2 * n])

    def zeroize(self):
        n = self.dimension
        self.core.q = [0.0] * n
        self.core.p = [0.0] * n

    def step(self, dt):
        t_pred = self.core.compute_kinetic_energy()
        self.core.step_symplectic(dt=dt)
        return (
            t_pred,
            self.core.compute_kinetic_energy(),
            self.core.compute_potential_energy(),
        )


# ----------------------------------------------------------------------
# The unified runtime.
# ----------------------------------------------------------------------
class SovereignRuntime:
    def __init__(self, dimension=4, dt=0.01, data_dir="data",
                 physics="auto", r_star=None):
        self.sandbox = BugSandbox()
        self.throughput = KineticThroughput()
        self.guardian = GuardianInvariant()
        self.drift = DriftBandV2(r_star=r_star)
        self.dt = dt
        self.tau = 0.0
        self.cycles = 0
        self.paused = False  # operator governance pause (bridge /api/control)
        self.dimension = dimension

        if physics == "auto":
            physics = "cag" if HAS_NUMPY else "stdlib"
        if physics == "cag" and not HAS_NUMPY:
            raise RuntimeError("CAG physics requires NumPy; use physics='stdlib'.")
        self.physics = physics
        if physics == "cag":
            self.adapter = _CAGAdapter(dimension)
        else:
            self.adapter = _StdlibAdapter(dimension, data_dir)

        self.last_gate = {"verdict": "none", "h_cov": 0.0}
        self.last_step = {"kinetic": 0.0, "potential": 0.0,
                          "lagrangian": 0.0, "delta": 0.0}
        # Seal the genesis checkpoint before any integration occurs.
        self.guardian.seal_checkpoint(self._state_bytes(), self.tau)

    # -- state ---------------------------------------------------------
    def _state_bytes(self) -> bytes:
        floats = self.adapter.floats()
        return (
            self.adapter.tag
            + struct.pack(">I", self.dimension)
            + struct.pack(">" + "d" * len(floats), *floats)
        )

    def _restore(self, state_bytes: bytes, tau: float):
        tag, n = state_bytes[:1], struct.unpack(">I", state_bytes[1:5])[0]
        if tag != self.adapter.tag or n != self.adapter.dimension:
            raise RuntimeError("Checkpoint physics mismatch on restore.")
        count = (len(state_bytes) - 5) // 8
        floats = list(struct.unpack(">" + "d" * count, state_bytes[5:]))
        self.adapter.restore(floats)
        self.tau = tau

    def _check_nan(self, where: str):
        for v in self.adapter.floats():
            if math.isnan(v):
                raise NaNPropagationAbort(
                    f"isnan() detected in state tensor {where}; aborting."
                )

    # -- breach protocol ------------------------------------------------
    def purge_as_mercy(self, drift_delta: float) -> dict:
        """Zeroize volatile memory, cold-restart from the G_t anchor."""
        self.adapter.zeroize()
        state_bytes, tau = self.guardian.rollback()
        self._restore(state_bytes, tau)
        return {
            "status": "purge_as_mercy",
            "delta": drift_delta,
            "restored_tau": round(tau, 6),
            "digest_head": self.guardian.status()["digest_head"],
        }

    def force_rollback(self) -> dict:
        """Operator-initiated rollback to the last sealed G_t checkpoint."""
        state_bytes, tau = self.guardian.rollback()
        self._restore(state_bytes, tau)
        return {
            "status": "rolled_back",
            "reason": "operator_action",
            "restored_tau": round(tau, 6),
            "digest_head": self.guardian.status()["digest_head"],
        }

    def force_purge(self) -> dict:
        """Operator-initiated purge-as-mercy."""
        return self.purge_as_mercy(self.last_step.get("delta", 0.0))

    # -- the hardened step ----------------------------------------------
    def cycle(self) -> dict:
        """One full pass through gate layers 2-6 (no input gating)."""
        # 2. NaN guard on the live tensor first.
        self._check_nan("pre-step")

        # 3. Guardian pre-verification against the sealed checkpoint.
        if not self.guardian.verify_current(self._state_bytes(), self.tau):
            state_bytes, tau = self.guardian.rollback()
            self._restore(state_bytes, tau)
            return {
                "status": "rolled_back",
                "reason": "guardian_mismatch",
                "restored_tau": round(tau, 6),
                "digest_head": self.guardian.status()["digest_head"],
            }

        # Physics.
        t_pred, t, v = self.adapter.step(self.dt)
        self.tau += self.dt
        self._check_nan("post-step")

        # 4. Drift band.
        drift_res = self.drift.evaluate(t_pred, t + v, v)
        if drift_res["breached"]:
            return self.purge_as_mercy(drift_res["delta"])

        # 6. Telemetry + 3. seal the new checkpoint.
        self.throughput.record(t, v)
        digest = self.guardian.seal_checkpoint(self._state_bytes(), self.tau)
        self.cycles += 1
        self.last_step = {
            "kinetic": t,
            "potential": v,
            "lagrangian": t - v,
            "delta": drift_res["delta"],
        }
        return {
            "status": "accepted",
            "tau": round(tau, 6),
            "cycle": self.cycles,
            "kinetic": round(t, 6),
            "potential": round(v, 6),
            "lagrangian": round(t - v, 6),
            "delta": round(drift_res["delta"], 6),
            "digest_head": digest[:16],
        }

    # -- gated input ------------------------------------------------------
    def process_input(self, text: str) -> dict:
        """Layer 1 gate, then a full hardened cycle."""
        gate = self.sandbox.evaluate_threat(text)
        self.last_gate = {"verdict": gate["verdict"], "h_cov": gate["h_cov"]}
        if gate["verdict"] == "immune_deny":
            return {
                "status": "immune_deny",
                "h_cov": gate["h_cov"],
                "message": "Input blocked by threat isolation boundary.",
            }
        res = self.cycle()
        res["h_cov"] = gate["h_cov"]
        return res

    # -- live snapshot for the bridge / UI ---------------------------------
    def telemetry(self) -> dict:
        return {
            "system": "Ellura Sovereign",
            "physics": self.physics,
            "dimension": self.dimension,
            "dt": self.dt,
            "tau": round(self.tau, 6),
            "cycles": self.cycles,
            "last_step": {k: round(v, 6) for k, v in self.last_step.items()},
            "drift_band": self.drift.status(),
            "guardian": self.guardian.status(),
            "throughput": self.throughput.get_metrics(),
            "last_gate": self.last_gate,
        }