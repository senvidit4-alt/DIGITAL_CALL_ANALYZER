"""
services/analyzer.py
====================
Core scam analysis logic + ML model loader.

ML Integration:
- Drop model.pkl in the project root when P1 delivers it → auto-loads.
- Until then, DummyClassifier handles predictions (rule engine still works).
"""

import os
import joblib

from models.scam_patterns import SCAM_KEYWORDS, SCAM_STAGES, ESCAPE_SCRIPTS

# ---------------------------------------------------------------------------
# ML MODEL LOADING (P1 integration point)
# ---------------------------------------------------------------------------
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model.pkl"
)

_model_is_real = False

try:
    if os.path.exists(_MODEL_PATH):
        ml_pipeline = joblib.load(_MODEL_PATH)
        _model_is_real = True
        print("✅ ML Model (model.pkl) loaded successfully.")
    else:
        raise FileNotFoundError
except Exception:
    print("⚠️  model.pkl not found — using DummyClassifier until P1 delivers the model.")

    class _DummyModel:
        def predict_proba(self, X):
            text = X[0].lower()
            scam_hints = ["otp", "police", "arrest", "cbi", "transfer", "warrant"]
            prob = 0.8 if any(w in text for w in scam_hints) else 0.2
            return [[1 - prob, prob]]

    ml_pipeline = _DummyModel()


def is_real_model_loaded() -> bool:
    """Returns True when a real model.pkl is loaded, False for DummyClassifier."""
    return _model_is_real


# ---------------------------------------------------------------------------
# CORE ANALYSIS
# ---------------------------------------------------------------------------

def process_text_analysis(text: str) -> dict:
    """
    Run rule engine + ML model on input text.
    Returns a structured result dict ready to be JSON-serialized.
    """
    text_lower = text.lower()

    detected_signals: dict = {}
    rule_score: int = 0
    stages_detected: list = []

    for category, words in SCAM_KEYWORDS.items():
        matched = [w for w in words if w in text_lower or w in text]
        if matched:
            detected_signals[category] = matched
            rule_score += 20
            stages_detected.append(category)

    try:
        ml_prob  = ml_pipeline.predict_proba([text])[0][1]
        ml_score = float(ml_prob * 100)
    except Exception as exc:
        print(f"ML prediction error: {exc}")
        ml_score = 50.0

    base_score = (rule_score * 0.5) + (ml_score * 0.5)

    has_isolation = "Isolation" in detected_signals
    has_extract   = "Extract"   in detected_signals
    if has_isolation and has_extract:
        base_score *= 1.2

    final_score = min(round(base_score, 2), 100.0)

    if final_score >= 70:
        verdict = "SCAM"
    elif final_score >= 40:
        verdict = "WARNING"
    else:
        verdict = "SAFE"

    current_stage = "Unknown"
    for stage in reversed(SCAM_STAGES):
        if stage in stages_detected:
            current_stage = stage
            break

    return {
        "score":   final_score,
        "verdict": verdict,
        "breakdown": {
            "ml_contribution":    round(ml_score  * 0.5, 2),
            "rule_contribution":  round(rule_score * 0.5, 2),
            "multiplier_applied": has_isolation and has_extract,
        },
        "detected_signals": detected_signals,
        "stage_tracker": {
            "current_stage": current_stage,
            "stages_hit":    stages_detected,
        },
        "escape_script": ESCAPE_SCRIPTS.get(current_stage, ESCAPE_SCRIPTS["Unknown"]),
    }
