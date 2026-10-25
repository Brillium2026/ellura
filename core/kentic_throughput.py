v"""
Kinetic Throughput Engine
Evaluates dynamic energy transmission and field coherence across iterations.
"""


class KineticThroughput:
    def __init__(self):
        self.history = []

    def record(self, kinetic_e, potential_e):
        total_energy = kinetic_e + potential_e
        ratio = kinetic_e / total_energy if total_energy != 0 else 0.0
        self.history.append((kinetic_e, potential_e, ratio))
        if len(self.history) > 100:
            self.history.pop(0)
        return ratio

    def get_metrics(self):
        if not self.history:
            return {"throughput_avg": 0.0, "samples": 0}
        avg_ratio = sum(h[2] for h in self.history) / len(self.history)
        return {
            "throughput_avg": round(avg_ratio, 4),
            "samples": len(self.history),
        }