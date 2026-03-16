"""Scoring helpers for ProGuard authenticity analysis.

Uses a research-grade weighted scoring model with configurable weights
loaded from config.yaml. Falls back to built-in defaults if config is
unavailable.

Scoring Formula:
    score = (
        typing_score * W_typing  +
        gaze_score   * W_gaze    +
        emotion_score * W_emotion +
        app_score    * W_app     +
        mouse_score  * W_mouse   -
        anomaly_penalty * W_anomaly
    ) * 100
"""

import os
from typing import Any, Dict, List

# Load config once at module level
_CONFIG: Dict[str, Any] = {}
try:
    import yaml  # type: ignore
    _config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'config.yaml'
    )
    if os.path.exists(_config_path):
        with open(_config_path, 'r') as f:
            _CONFIG = yaml.safe_load(f) or {}
        print(f"[INFO] Scoring: Loaded weights from config.yaml")
except Exception:
    pass

# ── Scoring Weights (from config or defaults) ──
_WEIGHTS = _CONFIG.get('SCORING_WEIGHTS', {})
W_TYPING   = float(_WEIGHTS.get('typing_entropy', 0.20))
W_MOUSE    = float(_WEIGHTS.get('mouse_entropy',  0.15))
W_GAZE     = float(_WEIGHTS.get('gaze_presence',  0.25))
W_APP      = float(_WEIGHTS.get('app_focus',       0.20))
W_EMOTION  = float(_WEIGHTS.get('emotion_focus',   0.10))
W_ANOMALY  = float(_WEIGHTS.get('anomaly_penalty', 0.10))

# ── Risk Level Thresholds (from config or defaults) ──
_RISK = _CONFIG.get('RISK_LEVELS', {})
GENUINE_THRESHOLD   = int(_RISK.get('genuine_work', 80))
SUSPICIOUS_THRESHOLD = int(_RISK.get('suspicious', 50))


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _risk_level(score: float) -> str:
    """
    Risk Levels:
        80-100  → Genuine Work  (low risk)
        50-80   → Suspicious    (medium risk)
         0-50   → Fake Activity (high risk)
    """
    if score >= GENUINE_THRESHOLD:
        return "low"
    if score >= SUSPICIOUS_THRESHOLD:
        return "medium"
    return "high"


def calculate_authenticity_score(signals: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate an authenticity score using a weighted scoring model.

    Formula:
        score = (
            typing_entropy  * 0.20 +
            gaze_presence   * 0.25 +
            emotion_focus   * 0.10 +
            app_focus       * 0.20 +
            mouse_entropy   * 0.15 -
            anomaly_score   * 0.10
        ) × 100

    Expected input values are in the 0..1 range.
    """
    # Normalize inputs
    n = {
        "typing_entropy": _clamp(_coerce_float(signals.get("typing_entropy"), 0.5)),
        "mouse_entropy":  _clamp(_coerce_float(signals.get("mouse_entropy"),  0.5)),
        "gaze_presence":  _clamp(_coerce_float(signals.get("gaze_presence"),  0.5)),
        "app_focus":      _clamp(_coerce_float(signals.get("app_focus"),      0.5)),
        "emotion_focus":  _clamp(_coerce_float(signals.get("emotion_focus"),  0.5)),
        "anomaly_score":  _clamp(_coerce_float(signals.get("anomaly_score"),  0.0)),
    }

    # ── Weighted Score Calculation ──
    weighted_sum = (
        n["typing_entropy"] * W_TYPING  +
        n["mouse_entropy"]  * W_MOUSE   +
        n["gaze_presence"]  * W_GAZE    +
        n["app_focus"]      * W_APP     +
        n["emotion_focus"]  * W_EMOTION
    )

    # Anomaly acts as a penalty — subtract from the positive score
    anomaly_penalty = n["anomaly_score"] * W_ANOMALY

    # Convert to 0-100 scale
    raw_score = (weighted_sum - anomaly_penalty) * 100.0

    # Build reason list for transparency
    reasons: List[str] = []

    if n["typing_entropy"] > 0.0 and n["typing_entropy"] < 0.35:
        reasons.append(f"Low typing variability ({n['typing_entropy']:.0%})")

    if n["mouse_entropy"] > 0.0 and n["mouse_entropy"] < 0.35:
        reasons.append(f"Repetitive mouse movement ({n['mouse_entropy']:.0%})")

    if n["gaze_presence"] < 0.5:
        reasons.append(f"Low screen presence ({n['gaze_presence']:.0%})")

    if n["app_focus"] < 0.5:
        reasons.append(f"Low productive app focus ({n['app_focus']:.0%})")

    if n["emotion_focus"] < 0.4:
        reasons.append(f"Distracted expression detected ({n['emotion_focus']:.0%})")

    if n["anomaly_score"] > 0.4:
        reasons.append(f"High anomaly score ({n['anomaly_score']:.0%})")

    score = max(0.0, min(100.0, raw_score))

    return {
        "score": int(round(score)),
        "risk_level": _risk_level(score),
        "reasons": reasons,
        "signals": n,
        "weights_used": {
            "typing": W_TYPING, "mouse": W_MOUSE, "gaze": W_GAZE,
            "app": W_APP, "emotion": W_EMOTION, "anomaly": W_ANOMALY,
        },
    }
