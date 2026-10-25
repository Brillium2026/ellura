v"""
Organism Orchestrator
Integrates ForgeCore, Complete Substrate, Sandbox Gating, and WAL logging into a unified runtime.
"""

from .forgecore_chromebook import ForgeCoreChromebook
from .ellura_complete import ElluraComplete
from .bug_sandbox import BugSandbox
from .kinetic_throughput import KineticThroughput


class ElluraOrganism:
    def __init__(self, mode="chromebook"):
        self.mode = mode
        self.sandbox = BugSandbox()
        self.throughput = KineticThroughput()
        if mode == "complete":
            self.substrate = ElluraComplete(dimension=96)
        else:
            self.substrate = ForgeCoreChromebook(dimension=12)

    def process_input(self, text: str):
        eval_res = self.sandbox.evaluate_threat(text)
        if eval_res["verdict"] == "immune_deny":
            return {
                "status": "immune_deny",
                "h_cov": eval_res["h_cov"],
                "message": "Input blocked by threat isolation boundary.",
            }

        if hasattr(self.substrate, "step_symplectic"):
            self.substrate.step_symplectic()
            k = self.substrate.compute_kinetic_energy()
            p = self.substrate.compute_potential_energy()
        else:
            res = self.substrate.step()
            k = res["kinetic"]
            p = res["potential"]

        t_ratio = self.throughput.record(k, p)

        return {
            "status": "accepted",
            "h_cov": eval_res["h_cov"],
            "throughput_ratio": t_ratio,
            "phase_space": "updated",
        }