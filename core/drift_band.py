v"""
Neutral Drift Band (v2) — Spec v2.0, Section II.C

    delta = |T_pred - (E_tot - V)| / R*  <=  0.085

T_pred is the kinetic energy predicted/measured before the integration step;
(E_tot - V) is the measured kinetic energy after the step. delta therefore
quantifies per-step kinetic drift normalized by the scale R*.

NOTE: the spec does not define R*. This implementation locks R* on the first
evaluation to the magnitude of the initial total energy |E_tot| (falling back
to 1.0 for a degenerate zero-energy state), making delta dimensionless
relative to the system's own energy scale. Pass r_star explicitly to override.

Breach (delta > 0.085) invokes the purge-as-mercy protocol: volatile state is
zeroized and the substrate cold-restarts from the last persistent G_t anchor.

This is deliberately distinct from the v1 "neutral_drift_band" parameter in
forgecore_chromebook.py, which is a stochastic perturbation amplitude.
"""

LIMIT = 0.085


class DriftBandV2:
    def __init__(self, r_star=None, limit=LIMIT):
        self.r_star = r_star
        self.limit = limit
        self.r_star_locked = r_star is not None
        self.evaluations = 0
        self.breaches = 0
        self.max_delta = 0.0

    def evaluate(self, t_pred: float, e_tot: float, v: float) -> dict:
        """Compute delta and whether the breach threshold is exceeded."""
        if not self.r_star_locked:
            scale = abs(e_tot)
            self.r_star = scale if scale > 1e-300 else 1.0
            self.r_star_locked = True

        t_measured = e_tot - v
        delta = abs(t_pred - t_measured) / self.r_star
        breached = delta > self.limit

        self.evaluations += 1
        if breached:
            self.breaches += 1
        if delta > self.max_delta:
            self.max_delta = delta

        return {
            "delta": delta,
            "breached": breached,
            "limit": self.limit,
            "t_pred": t_pred,
            "t_measured": t_measured,
            "r_star": self.r_star,
        }

    def status(self) -> dict:
        return {
            "r_star": self.r_star,
            "limit": self.limit,
            "evaluations": self.evaluations,
            "breaches": self.breaches,
            "max_delta": round(self.max_delta, 6),
        }