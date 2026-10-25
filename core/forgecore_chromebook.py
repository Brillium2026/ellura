"""
Ellura ForgeCore Chromebook Substrate
Pure Python standard library implementation for zero-dependency environments.
"""

import math
import random
import json
import time
import os
import hashlib


class ForgeCoreChromebook:
    def __init__(self, dimension=12, data_dir="data"):
        self.dimension = dimension
        self.data_dir = data_dir
        self.q = [0.1 * math.sin(i) for i in range(dimension)]
        self.p = [0.05 * math.cos(i) for i in range(dimension)]
        self.mass = 1.0
        self.k_spring = 0.85
        self.neutral_drift_band = 0.085
        self.wal_file = os.path.join(self.data_dir, "wal.log")
        self.last_hash = "0" * 64
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.wal_file):
            with open(self.wal_file, "w") as f:
                f.write("")

    def compute_kinetic_energy(self):
        return 0.5 * sum((pv ** 2) / self.mass for pv in self.p)

    def compute_potential_energy(self):
        return 0.5 * self.k_spring * sum(qv ** 2 for qv in self.q)

    def compute_lagrangian(self):
        return self.compute_kinetic_energy() - self.compute_potential_energy()

    def step_symplectic(self, dt=0.05):
        """Stormer-Verlet / Symplectic step."""
        for i in range(self.dimension):
            force = -self.k_spring * self.q[i]
            # Incorporate 8.5% neutral drift band perturbation
            drift = random.uniform(-self.neutral_drift_band, self.neutral_drift_band) * 0.01
            self.p[i] += (force + drift) * dt
            self.q[i] += (self.p[i] / self.mass) * dt

        state_bytes = json.dumps({"q": self.q, "p": self.p, "t": time.time()}).encode('utf-8')
        new_hash = hashlib.sha256(self.last_hash.encode('utf-8') + state_bytes).hexdigest()
        self.last_hash = new_hash

        with open(self.wal_file, "a") as f:
            f.write(f"{new_hash}\n")

        return new_hash

    def get_status(self):
        return {
            "mode": "Chromebook Stdlib Pure-Python",
            "dimension": self.dimension,
            "kinetic_energy": round(self.compute_kinetic_energy(), 6),
            "potential_energy": round(self.compute_potential_energy(), 6),
            "lagrangian": round(self.compute_lagrangian(), 6),
            "neutral_drift_band": self.neutral_drift_band,
            "wal_head": self.last_hash[:16],
        }