v"""
Hardened Substrate — Spec v2.0 runtime (Sections II.B, II.C, IV.B)

Wraps ForgeCoreChromebook with:

1. Guardian invariant verification (SHA3-256) at every integration step —
   mismatch rolls back to the last sealed G_{t-dt} checkpoint.
2. Neutral Drift Band (v2) evaluation at every step — breach triggers the
   purge-as-mercy protocol: zeroize volatile state, cold-restart from the
   last persistent G_t anchor.
3. NaN propagation guard — any isnan() in the state tensor aborts the step
   immediately instead of silently diverging (spec IV.B).

NOTE on timestep: the spec fixes dt = 1 us for the bare-metal target. This
Python prototype keeps dt configurable (default 0.05, matching the v1 core);
the 1 us figure applies to the compiled kernel, not this reference runtime.
"""

import math
import struct

from .forgecore_chromebook import ForgeCoreChromebook
from .guardian import GuardianInvariant
from .drift_band import DriftBandV2


class NaNPropagationAbort(RuntimeError):
    """Raised when isnan() is detected in the state tensor (spec IV.B)."""


class HardenedSubstrate:
    def __init__(self, dimension=12, data_dir="data", dt=0.05, r_star=None):
        self.core = ForgeCoreChromebook(dimension=dimension, data_dir=data_dir)
        self.guardian = GuardianInvariant()
        self.drift = DriftBandV2(r_star=r_star)
        self.dt = dt
        self.tau = 0.0
        self.dimension = dimension
        # Seal the genesis checkpoint before any integration occurs.
        self.guardian.seal_checkpoint(self._state_bytes(), self.tau)

    # ------------------------------------------------------------------
    # state serialization
    # ------------------------------------------------------------------
    def _state_bytes(self) -> bytes:
        return b"".join(struct.pack(">d", v) for v in self.core.q + self.core.p)

    def _restore_bytes(self, state_bytes: bytes, tau: float):
        n = self.dimension
        vals = struct.unpack(">" + "d" * (2 * n), state_bytes)
        self.core.q = list(vals[:n])
        self.core.p = list(vals[n:])
        self.tau = tau

    def _assert_finite(self, where: str):
        for v in self.core.q + self.core.p:
            if math.isnan(v):
                raise NaNPropagationAbort(
                    f"isnan() detected in state tensor {where}; aborting step."
                )

    # ------------------------------------------------------------------
    # breach protocol
    # ------------------------------------------------------------------
    def purge_as_mercy(self) -> dict:
        """Zeroize volatile memory, then cold-restart from the G_t anchor."""
        self.core.q = [0.0] * self.dimension
        self.core.p = [0.0] * self.dimension
        state_bytes, tau = self.guardian.rollback()
        self._restore_bytes(state_bytes, tau)
        return {
            "status": "purge_as_mercy",
            "restored_tau": tau,
            "digest_head": self.guardian.status()["digest_head"],
        }

    # ------------------------------------------------------------------
    # integration step
    # ------------------------------------------------------------------
    def step(self) -> dict:
        # 1. NaN guard on the live tensor first: a NaN is corruption, and it
        #    must abort before the guardian hashes a poisoned state.
        self._assert_finite("pre-step")

        # 2. Guardian pre-verification: has the live state drifted from the seal?
        if not self.guardian.verify_current(self._state_bytes(), self.tau):
            state_bytes, tau = self.guardian.rollback()
            self._restore_bytes(state_bytes, tau)
            return {
                "status": "rolled_back",
                "reason": "guardian_mismatch",
                "restored_tau": tau,
                "digest_head": self.guardian.status()["digest_head"],
            }

        # 3. Predicted kinetic energy before the step.
        t_pred = self.core.compute_kinetic_energy()

        # 4. Integrate.
        self.core.step_symplectic(dt=self.dt)
        self.tau += self.dt

        # 5. NaN guard after integration.
        self._assert_finite("post-step")

        # 6. Drift-band evaluation: delta = |T_pred - (E_tot - V)| / R*.
        t = self.core.compute_kinetic_energy()
        v = self.core.compute_potential_energy()
        e_tot = t + v
        drift_res = self.drift.evaluate(t_pred, e_tot, v)

        if drift_res["breached"]:
            result = self.purge_as_mercy()
            result["delta"] = drift_res["delta"]
            result["tau"] = self.tau
            return result

        # 7. Seal the new checkpoint.
        digest = self.guardian.seal_checkpoint(self._state_bytes(), self.tau)

        return {
            "status": "accepted",
            "tau": self.tau,
            "delta": drift_res["delta"],
            "kinetic": t,
            "potential": v,
            "digest_head": digest[:16],
        }

    def get_status(self) -> dict:
        return {
            "mode": "Hardened Substrate v2.0",
            "dimension": self.dimension,
            "dt": self.dt,
            "tau": round(self.tau, 6),
            "guardian": self.guardian.status(),
            "drift_band": self.drift.status(),
        }