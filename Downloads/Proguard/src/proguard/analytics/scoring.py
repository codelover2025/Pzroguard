"""Scoring helpers for ProGuard authenticity analysis."""

from typing import Any, Dict, List


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
    if score >= 80:
        return "low"
    if score >= 55:
        return "medium"
    return "high"


def calculate_authenticity_score(signals: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate an authenticity score from normalized signals.

    Expected input values are in the 0..1 range. Missing values are defaulted
    to neutral (0.5) unless noted.
    """
    normalized = {
        "typing_entropy": _clamp(_coerce_float(signals.get("typing_entropy"), 0.5)),
        "mouse_entropy": _clamp(_coerce_float(signals.get("mouse_entropy"), 0.5)),
        "gaze_presence": _clamp(_coerce_float(signals.get("gaze_presence"), 0.5)),
        "app_focus": _clamp(_coerce_float(signals.get("app_focus"), 0.5)),
        "emotion_focus": _clamp(_coerce_float(signals.get("emotion_focus"), 0.5)),
        "anomaly_score": _clamp(_coerce_float(signals.get("anomaly_score"), 0.0)),
    }

    penalties = 0.0
    reasons: List[str] = []

    if normalized["anomaly_score"] > 0.4:
        penalty = normalized["anomaly_score"] * 50.0
        penalties += penalty
        reasons.append("High anomaly score detected")

    # Only penalize low typing entropy if we actually have typing data
    # (0.0 means no data collected yet, not suspicious activity)
    if normalized["typing_entropy"] > 0.0 and normalized["typing_entropy"] < 0.35:
        penalties += (0.35 - normalized["typing_entropy"]) * 40.0
        reasons.append("Low typing variability")

    # Only penalize low mouse entropy if we actually have mouse data
    if normalized["mouse_entropy"] > 0.0 and normalized["mouse_entropy"] < 0.35:
        penalties += (0.35 - normalized["mouse_entropy"]) * 30.0
        reasons.append("Repetitive mouse movement")

    if normalized["gaze_presence"] < 0.5:
        penalties += (0.5 - normalized["gaze_presence"]) * 40.0
        reasons.append("Low screen presence")

    if normalized["app_focus"] < 0.5:
        penalties += (0.5 - normalized["app_focus"]) * 25.0
        reasons.append("Low productive app focus")

    if normalized["emotion_focus"] < 0.7:
        # Heavily penalize negative/distracted facial expressions
        penalties += (0.7 - normalized["emotion_focus"]) * 45.0
        reasons.append("Distracted or negative facial expression detected")
        
    # Emotion Reward: Actively spike score if expression is highly positive/focused
    reward = 0.0
    if normalized["emotion_focus"] >= 0.8:
        reward = (normalized["emotion_focus"] - 0.8) * 30.0

    score = max(0.0, min(100.0, 100.0 - penalties + reward))

    return {
        "score": int(round(score)),
        "risk_level": _risk_level(score),
        "reasons": reasons,
        "signals": normalized,
    }
