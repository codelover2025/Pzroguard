"""
Feature Extraction Module for ProGuard ML Pipeline

Converts raw behavioral data from collectors into normalized ML feature vectors.
This is the bridge between data collection and ML model inference.

Pipeline:  Collectors → Feature Extractor → ML Models → Scoring → Dashboard
"""

import numpy as np
from datetime import datetime
from typing import Any, Dict, Optional


class FeatureExtractor:
    """
    Extracts and normalizes ML features from raw collector data.

    Input: Raw metrics from MouseKeyboardCollector, ScreenActivityMonitor,
           WebcamMonitor, TypingRhythmAnalyzer, MacroPatternDetector.

    Output: A standardized feature vector dict with values in [0, 1] range,
            ready for ML model inference.

    Feature List:
        - typing_speed:           Words per minute (normalized)
        - typing_entropy:         Shannon entropy of keystroke intervals
        - mouse_entropy:          Shannon entropy of mouse movement vectors
        - mouse_variance:         Variance in mouse speed (normalized)
        - idle_ratio:             Fraction of time with no input activity
        - task_switch_frequency:  App window switches per minute (normalized)
        - gaze_presence:          Fraction of time face is detected on screen
        - emotion_focus:          Weighted emotion engagement score
        - macro_pattern_score:    Combined macro detection confidence
        - app_focus_ratio:        Fraction of time on productive applications
    """

    # Normalization constants (based on empirical human behavior ranges)
    _TYPING_SPEED_MAX = 120.0       # WPM — fast professional typist
    _MOUSE_VARIANCE_MAX = 500.0     # Pixel variance ceiling
    _TASK_SWITCH_MAX = 15.0         # Switches/minute ceiling

    # Emotion weights for focus scoring
    _EMOTION_WEIGHTS = {
        'neutral': 1.0,
        'happy': 0.9,
        'focused': 1.0,
        'surprise': 0.6,
        'sad': 0.3,
        'angry': 0.2,
        'fear': 0.2,
        'disgust': 0.1,
    }

    def __init__(self):
        self._last_extraction_time: Optional[datetime] = None

    @staticmethod
    def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        """Clamp a value to [lo, hi]."""
        return max(lo, min(hi, value))

    # ------------------------------------------------------------------
    # Core extraction entry point
    # ------------------------------------------------------------------

    def extract_features(
        self,
        input_metrics: Dict[str, Any],
        screen_metrics: Dict[str, Any],
        typing_metrics: Dict[str, Any],
        webcam_metrics: Dict[str, Any],
        macro_metrics: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Extract a complete, normalized feature vector from all collectors.

        Args:
            input_metrics:  From MouseKeyboardCollector.get_current_metrics()
            screen_metrics: From ScreenActivityMonitor.get_current_metrics()
            typing_metrics: From TypingRhythmAnalyzer.get_current_metrics()
            webcam_metrics: From WebcamMonitor.get_current_metrics()
            macro_metrics:  From MacroPatternDetector.get_current_metrics()

        Returns:
            Dict with normalized features in [0, 1] range.
        """
        features: Dict[str, float] = {}

        # --- Typing features ---
        features['typing_speed'] = self._extract_typing_speed(typing_metrics)
        features['typing_entropy'] = self._extract_typing_entropy(typing_metrics)

        # --- Mouse features ---
        features['mouse_entropy'] = self._extract_mouse_entropy(input_metrics)
        features['mouse_variance'] = self._extract_mouse_variance(input_metrics)

        # --- Activity features ---
        features['idle_ratio'] = self._extract_idle_ratio(input_metrics, screen_metrics)
        features['task_switch_frequency'] = self._extract_task_switch(screen_metrics)
        features['app_focus'] = self._extract_app_focus(screen_metrics)

        # --- Webcam / biometric features ---
        features['gaze_presence'] = self._extract_gaze_presence(webcam_metrics)
        features['emotion_focus'] = self._extract_emotion_focus(webcam_metrics)

        # --- Macro / anomaly features ---
        features['macro_pattern_score'] = self._extract_macro_score(macro_metrics)

        self._last_extraction_time = datetime.now()

        return features

    # ------------------------------------------------------------------
    # Individual feature extractors
    # ------------------------------------------------------------------

    def _extract_typing_speed(self, typing_metrics: Dict[str, Any]) -> float:
        """Normalize typing speed (WPM) to [0, 1]."""
        wpm = float(typing_metrics.get('typing_speed', 0.0))
        return self._clamp(wpm / self._TYPING_SPEED_MAX)

    def _extract_typing_entropy(self, typing_metrics: Dict[str, Any]) -> float:
        """Extract rhythm entropy — already [0, 1] from TypingRhythmAnalyzer."""
        return self._clamp(float(typing_metrics.get('rhythm_entropy', 0.0)))

    def _extract_mouse_entropy(self, input_metrics: Dict[str, Any]) -> float:
        """Extract mouse movement entropy — already [0, 1] from collector."""
        return self._clamp(float(input_metrics.get('mouse_entropy', 0.0)))

    def _extract_mouse_variance(self, input_metrics: Dict[str, Any]) -> float:
        """
        Calculate mouse speed variance from recent positions.
        High variance = natural human movement, Low = bot/macro.
        """
        positions = input_metrics.get('recent_positions', [])
        if len(positions) < 3:
            return 0.5  # Neutral default when no data

        try:
            coords = np.array(positions[-50:])  # Last 50 positions
            # Calculate displacement between consecutive points
            diffs = np.diff(coords, axis=0)
            speeds = np.sqrt(np.sum(diffs ** 2, axis=1))
            variance = float(np.var(speeds))
            return self._clamp(variance / self._MOUSE_VARIANCE_MAX)
        except (ValueError, TypeError):
            return 0.5

    def _extract_idle_ratio(
        self,
        input_metrics: Dict[str, Any],
        screen_metrics: Dict[str, Any],
    ) -> float:
        """
        Calculate idle ratio — fraction of time with no meaningful input.
        Lower is better (more active).
        """
        # Use keyboard/mouse event counts as activity proxy
        total_keys = float(input_metrics.get('total_keystrokes', 0))
        total_clicks = float(input_metrics.get('total_clicks', 0))
        total_events = total_keys + total_clicks

        # If we have fewer than 5 events per minute, consider partially idle
        # Normalize: 0 events = fully idle (1.0), 30+ events = active (0.0)
        if total_events <= 0:
            return 0.8  # Mostly idle
        activity_rate = min(total_events / 30.0, 1.0)
        return self._clamp(1.0 - activity_rate)

    def _extract_task_switch(self, screen_metrics: Dict[str, Any]) -> float:
        """
        Normalize task/window switching frequency.
        Moderate switching is normal; excessive or zero is suspicious.
        """
        switches = float(screen_metrics.get('window_switches', 0))
        return self._clamp(switches / self._TASK_SWITCH_MAX)

    def _extract_app_focus(self, screen_metrics: Dict[str, Any]) -> float:
        """Extract productive app ratio — already [0, 1] from collector."""
        return self._clamp(float(screen_metrics.get('productivity_ratio', 0.5)))

    def _extract_gaze_presence(self, webcam_metrics: Dict[str, Any]) -> float:
        """Extract face/gaze presence ratio — already [0, 1]."""
        return self._clamp(float(webcam_metrics.get('presence_ratio', 0.0)))

    def _extract_emotion_focus(self, webcam_metrics: Dict[str, Any]) -> float:
        """
        Calculate weighted emotion engagement score.
        Focused/neutral emotions score high, distracted emotions score low.
        """
        emotion_dist = webcam_metrics.get('emotion_distribution', {})
        if not emotion_dist:
            # Fallback to dominant emotion
            dominant = webcam_metrics.get('dominant_emotion', 'neutral')
            return self._EMOTION_WEIGHTS.get(dominant, 0.5)

        weighted_score = sum(
            emotion_dist.get(emotion, 0.0) * weight
            for emotion, weight in self._EMOTION_WEIGHTS.items()
        )
        return self._clamp(weighted_score)

    def _extract_macro_score(self, macro_metrics: Dict[str, Any]) -> float:
        """
        Combined macro detection confidence.
        Returns inverse — higher = more suspicious (macro detected).
        """
        kb_conf = float(macro_metrics.get('keyboard_macro_confidence', 0.0))
        mouse_conf = float(macro_metrics.get('mouse_macro_confidence', 0.0))
        return self._clamp(max(kb_conf, mouse_conf))

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_feature_names(self) -> list:
        """Return ordered list of feature names for ML model input."""
        return [
            'typing_speed',
            'typing_entropy',
            'mouse_entropy',
            'mouse_variance',
            'idle_ratio',
            'task_switch_frequency',
            'app_focus',
            'gaze_presence',
            'emotion_focus',
            'macro_pattern_score',
        ]

    def features_to_vector(self, features: Dict[str, float]) -> list:
        """Convert feature dict to ordered list for model input."""
        return [features.get(name, 0.0) for name in self.get_feature_names()]

    def describe_features(self, features: Dict[str, float]) -> Dict[str, str]:
        """Return human-readable descriptions for each feature value."""
        descriptions = {
            'typing_speed': f"Typing speed: {features.get('typing_speed', 0) * self._TYPING_SPEED_MAX:.0f} WPM",
            'typing_entropy': f"Typing rhythm variability: {features.get('typing_entropy', 0) * 100:.0f}%",
            'mouse_entropy': f"Mouse movement randomness: {features.get('mouse_entropy', 0) * 100:.0f}%",
            'mouse_variance': f"Mouse speed variance: {features.get('mouse_variance', 0) * 100:.0f}%",
            'idle_ratio': f"Idle time: {features.get('idle_ratio', 0) * 100:.0f}%",
            'task_switch_frequency': f"Window switches: {features.get('task_switch_frequency', 0) * self._TASK_SWITCH_MAX:.1f}/min",
            'app_focus': f"Productive app usage: {features.get('app_focus', 0) * 100:.0f}%",
            'gaze_presence': f"Screen presence: {features.get('gaze_presence', 0) * 100:.0f}%",
            'emotion_focus': f"Emotional engagement: {features.get('emotion_focus', 0) * 100:.0f}%",
            'macro_pattern_score': f"Macro suspicion: {features.get('macro_pattern_score', 0) * 100:.0f}%",
        }
        return descriptions
