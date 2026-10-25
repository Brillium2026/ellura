v"""
Bug Sandbox & Threat Diagnostic Engine
Evaluates input safety and returns immune_deny when threat bounds (H_cov > 0.7) are exceeded.
"""

import re


class BugSandbox:
    def __init__(self):
        # Known threat patterns: execution injections, curl piping, system overrides
        self.injection_patterns = [
            r"curl\s+",
            r"wget\s+",
            r"\|\s*sh",
            r"\|\s*bash",
            r"eval\(",
            r"exec\(",
            r"import\s+os",
            r"subprocess",
            r"drop\s+table",
            r"<script>",
        ]

    def evaluate_threat(self, payload: str) -> dict:
        threat_score = 0.0
        detected_features = []

        for pattern in self.injection_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threat_score += 0.4
                detected_features.append(pattern)

        # Length anomaly or unexpected binary chars check
        if len(payload) > 2048:
            threat_score += 0.25

        h_cov = min(1.0, threat_score)
        verdict = "immune_deny" if h_cov > 0.7 else "accepted"

        return {
            "payload_snippet": payload[:30],
            "h_cov": round(h_cov, 3),
            "verdict": verdict,
            "detected_threats": detected_features,
        }