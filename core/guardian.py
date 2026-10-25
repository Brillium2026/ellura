v"""
Guardian Invariant (G_t) — Spec v2.0, Section II.B

G_t = SHA3-256(x_t || tau)

The guardian seals a checkpoint (state, proper time) after every successful
integration step. At the start of the following step the current state is
re-verified against the sealed checkpoint; any mismatch means the volatile
state was corrupted out-of-band and triggers an immediate rollback to the
last known G_{t-dt} checkpoint.
"""

import hashlib
import struct


class GuardianInvariant:
    def __init__(self):
        self.checkpoint_state = None   # serialized state bytes at last seal
        self.checkpoint_tau = None     # proper time at last seal
        self.checkpoint_digest = None  # G_t hex digest at last seal
        self.seals = 0
        self.rollbacks = 0

    @staticmethod
    def digest(state_bytes: bytes, tau: float) -> str:
        """G_t = SHA3-256(x_t || tau); tau packed as big-endian double."""
        return hashlib.sha3_256(state_bytes + struct.pack(">d", tau)).hexdigest()

    def seal_checkpoint(self, state_bytes: bytes, tau: float) -> str:
        """Persist the current (state, tau) as the authoritative anchor."""
        self.checkpoint_state = bytes(state_bytes)
        self.checkpoint_tau = tau
        self.checkpoint_digest = self.digest(state_bytes, tau)
        self.seals += 1
        return self.checkpoint_digest

    def verify_current(self, state_bytes: bytes, tau: float) -> bool:
        """True iff the live state still matches the sealed checkpoint."""
        if self.checkpoint_digest is None:
            return True
        return self.digest(state_bytes, tau) == self.checkpoint_digest

    def rollback(self):
        """Return the last sealed (state_bytes, tau); raises if none exists."""
        if self.checkpoint_state is None:
            raise RuntimeError("Guardian rollback requested with no sealed checkpoint.")
        self.rollbacks += 1
        return self.checkpoint_state, self.checkpoint_tau

    def status(self) -> dict:
        return {
            "sealed": self.checkpoint_digest is not None,
            "digest_head": (self.checkpoint_digest or "")[:16],
            "seals": self.seals,
            "rollbacks": self.rollbacks,
        }