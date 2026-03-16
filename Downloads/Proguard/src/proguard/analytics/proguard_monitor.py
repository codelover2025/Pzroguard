"""
ProGuard Master Monitor
Integrates all 18 features into a unified monitoring system
"""

import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import all collectors
from ..collectors.mouse_keyboard import MouseKeyboardCollector  # type: ignore
from ..collectors.screen_activity import ScreenActivityMonitor  # type: ignore
from ..collectors.webcam_monitor import WebcamMonitor  # type: ignore

# Import all analyzers
from .typing_rhythm import TypingRhythmAnalyzer  # type: ignore
from .macro_detector import MacroPatternDetector  # type: ignore
from .baseline_model import BaselineModeler  # type: ignore
from .explainable_ai import ExplainableAI  # type: ignore
from .meeting_monitor import MeetingMonitor  # type: ignore
from .screenshot_analyzer import ScreenshotAnalyzer  # type: ignore
from .heatmap_generator import HeatmapGenerator  # type: ignore
from .timeline_generator import TimelineGenerator  # type: ignore

# Import scoring
from .scoring import calculate_authenticity_score  # type: ignore

# Import feature extraction pipeline
from .feature_extractor import FeatureExtractor  # type: ignore


class ProGuardMonitor:
    """
    Master controller for all ProGuard monitoring features
    Orchestrates data collection, analysis, and reporting
    """
    
    def __init__(self, user_id, config=None):
        self.user_id = user_id
        self.config = config or {}
        self.running = False
        
        # Initialize analyzers first (Features 3, 9, 11, 12, 15)
        self.typing_rhythm = TypingRhythmAnalyzer()
        self.macro_detector = MacroPatternDetector()

        # Buffers for macro sequence detection (collects batches of events)
        self._key_buffer_keys: List[str] = []
        self._key_buffer_times: List[float] = []
        self._mouse_buffer_pos: List[tuple] = []
        self._mouse_buffer_times: List[float] = []

        # Initialize collectors with live callbacks (Features 1, 2, 4, 5)
        self.mouse_keyboard = MouseKeyboardCollector(
            on_key_press_callback=self._on_key_event,
            on_mouse_move_callback=self._on_mouse_event,
        )
        self.screen_activity = ScreenActivityMonitor()
        self.webcam_monitor = WebcamMonitor()
        self.baseline_model = BaselineModeler(user_id)
        self.meeting_monitor = MeetingMonitor()
        self.screenshot_analyzer = ScreenshotAnalyzer(
            interval=self.config.get('screenshot_interval', 300)
        )
        
        # Initialize ML feature extraction pipeline
        self.feature_extractor = FeatureExtractor()

        # Initialize visualization & reporting (Features 7, 8, 16)
        self.explainer = ExplainableAI()
        self.heatmap_generator = HeatmapGenerator()
        self.timeline_generator = TimelineGenerator()
        
        # Link webcam to meeting monitor
        self.meeting_monitor.link_webcam_monitor(self.webcam_monitor)
        
        # Current state
        self.current_score: float = 0
        self.current_signals: Dict[str, Any] = {}
        self.current_features: Dict[str, float] = {}  # Full ML feature vector
        self.score_history: List[float] = []
        
        # Analysis thread
        self.analysis_thread: Optional[threading.Thread] = None
        
        # Load Core ML Ensemble Model
        self.core_model: Any = None
        self.core_scaler: Any = None
        try:
            import joblib  # type: ignore
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'models', 'trained')
            self.core_model = joblib.load(os.path.join(model_path, 'core_ensemble_rf.pkl'))
            self.core_scaler = joblib.load(os.path.join(model_path, 'ensemble_scaler.pkl'))
            print("[INFO] ProGuard ML: Loaded Core RandomForest Ensemble")
        except Exception as e:
            print(f"[WARNING] Core ML Models not found: {e}. Falling back to Baseline Heuristics.")
            
        print(f"[OK] ProGuard Monitor initialized for user: {user_id}")

    # ------------------------------------------------------------------
    # Live event handlers — called by MouseKeyboardCollector callbacks
    # ------------------------------------------------------------------

    def _on_key_event(self, key_char: str, timestamp: float) -> None:
        """Receive a live keystroke, feed into typing analyzer and macro buffer."""
        try:
            self.typing_rhythm.add_keystroke(timestamp, key_char)
            self._key_buffer_keys.append(key_char)
            self._key_buffer_times.append(timestamp)
            # Feed macro detector every 20 keystrokes
            if len(self._key_buffer_keys) >= 20:
                self.macro_detector.add_keyboard_sequence(
                    list(self._key_buffer_keys), list(self._key_buffer_times)
                )
                self._key_buffer_keys.clear()
                self._key_buffer_times.clear()
        except Exception:
            pass

    def _on_mouse_event(self, x: int, y: int, timestamp: float) -> None:
        """Receive a live mouse-move, buffer and feed into macro detector."""
        try:
            self._mouse_buffer_pos.append((x, y))
            self._mouse_buffer_times.append(timestamp)
            # Feed macro detector every 20 positions
            if len(self._mouse_buffer_pos) >= 20:
                self.macro_detector.add_mouse_sequence(
                    list(self._mouse_buffer_pos), list(self._mouse_buffer_times)
                )
                self._mouse_buffer_pos.clear()
                self._mouse_buffer_times.clear()
        except Exception:
            pass


    def start_monitoring(self):
        """Start all monitoring components"""
        print("[STARTING] Starting ProGuard monitoring...")
        
        self.running = True
        
        # Start collectors
        self.mouse_keyboard.start()
        self.screen_activity.start()
        self.webcam_monitor.start()
        
        # Start analyzers
        self.screenshot_analyzer.start()
        
        # Start analysis loop
        analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread = analysis_thread
        analysis_thread.start()
        
        # Immediate first-pass analysis so dashboard isn't empty on start
        threading.Thread(target=self._perform_analysis, daemon=True).start()
        
        print("[OK] All ProGuard monitoring components started")
    
    def stop_monitoring(self):
        """Stop all monitoring components"""
        print("[STOPPING] Stopping ProGuard monitoring...")
        
        self.running = False
        
        # Stop collectors
        self.mouse_keyboard.stop()
        self.screen_activity.stop()
        self.webcam_monitor.stop()
        
        # Stop analyzers
        self.screenshot_analyzer.stop()
        
        # Wait for analysis thread
        thread_to_stop = self.analysis_thread
        if thread_to_stop is not None:
            thread_to_stop.join(timeout=5)
        
        # Save final daily baseline
        self._save_daily_baseline()
        
        print("[OK] ProGuard monitoring stopped")
    
    def _analysis_loop(self):
        """Main analysis loop - runs every 5 seconds"""
        while self.running:
            try:
                self._perform_analysis()
            except Exception as e:
                print(f"[ERROR] Analysis error: {e}")
            
            time.sleep(5)  # Analyze frequently for real-time dashboard
    
    def _perform_analysis(self):
        """Perform comprehensive analysis of all signals"""
        # ── Step 1: Collect raw metrics from all sources ──
        input_metrics = self.mouse_keyboard.get_current_metrics()
        screen_metrics = self.screen_activity.get_current_metrics()
        typing_metrics = self.typing_rhythm.get_current_metrics()
        webcam_metrics = self.webcam_monitor.get_current_metrics()
        macro_metrics = self.macro_detector.get_current_metrics()

        # Feature 12: Meeting Monitor
        self.meeting_monitor.update_meeting_status()

        # ── Step 2: Feature Extraction (ML Pipeline) ──
        # Convert raw collector data → normalized feature vector
        features = self.feature_extractor.extract_features(
            input_metrics=input_metrics,
            screen_metrics=screen_metrics,
            typing_metrics=typing_metrics,
            webcam_metrics=webcam_metrics,
            macro_metrics=macro_metrics,
        )

        # ── Step 3: Build signals dict for scoring engine ──
        # Map extracted features to the scoring interface
        signals = {
            'typing_entropy': features['typing_entropy'],
            'mouse_entropy': features['mouse_entropy'],
            'gaze_presence': features['gaze_presence'],
            'app_focus': features['app_focus'],
            'emotion_focus': features['emotion_focus'],
        }

        # Compute anomaly score using ML model or heuristic baseline
        signals['anomaly_score'] = self._calculate_anomaly_score(signals)

        # Store full feature vector alongside signals for dashboard
        self.current_signals = signals
        self.current_features = features  # Full 10-feature vector

        # ── Step 4: Calculate Work Authenticity Score ──
        score_result = calculate_authenticity_score(signals)
        self.current_score = score_result['score']

        # Add to history
        self.score_history.append(float(self.current_score))
        if len(self.score_history) > 1440:
            while len(self.score_history) > 1440:
                self.score_history.pop(0)

        # ── Step 5: Feed downstream modules ──
        # Feature 8: Heatmap
        self.heatmap_generator.add_score(datetime.now(), self.current_score)

        # Feature 16: Timeline
        self._add_timeline_events(signals, self.current_score, input_metrics, screen_metrics)

        # Feature 11: Baseline anomaly check
        if self.baseline_model.baseline_stats:
            is_normal, anomaly_score, deviating = self.baseline_model.is_behavior_normal(signals)
            if not is_normal:
                print(f"[WARNING] Abnormal behavior detected (anomaly: {anomaly_score:.2f})")
                print(f"   Deviating features: {[f['feature'] for f in deviating]}")
    
    def _calculate_emotion_focus(self, webcam_metrics):
        """
        Calculate emotion focus score
        Higher for focused emotions (neutral, happy)
        Lower for distracted emotions (bored, sad)
        """
        emotion_dist = webcam_metrics.get('emotion_distribution', {})
        
        # Positive weights for focused emotions
        emotion_weights = {
            'neutral': 1.0,
            'happy': 0.9,
            'surprise': 0.6,
            'sad': 0.3,
            'angry': 0.2,
            'fear': 0.2,
            'disgust': 0.1
        }
        
        weighted_score = sum(
            emotion_dist.get(emotion, 0) * weight
            for emotion, weight in emotion_weights.items()
        )
        
        return weighted_score
    
    def _calculate_anomaly_score(self, signals):
        """Calculate true ML anomaly score using RandomForest probability thresholds"""
        # ML Inference Path
        if getattr(self, 'core_model', None) and getattr(self, 'core_scaler', None):
            try:
                import pandas as pd  # type: ignore
                # Extract features in exactly the same order as training
                features = {
                    'typing_entropy': signals.get('typing_entropy', 1.0),
                    'mouse_entropy': signals.get('mouse_entropy', 1.0),
                    'gaze_presence': signals.get('gaze_presence', 1.0),
                    'app_focus': signals.get('app_focus', 1.0),
                    'emotion_focus': signals.get('emotion_focus', 1.0)
                }
                
                df = pd.DataFrame([features])
                X_scaled = self.core_scaler.transform(df)
                
                # prediction probabilities: [0: Human Working, 1: Slacking, 2: Active Bot]
                probs = self.core_model.predict_proba(X_scaled)[0]
                
                # Final Anomaly Score Calculation
                # Weight "Bot" heavily (1.0) and "Slacking" moderately (0.4)
                anomaly_score = (probs[1] * 0.4) + (probs[2] * 1.0)
                
                return min(anomaly_score, 1.0)
            except Exception as e:
                print(f"[ERROR] ML Core Ensemble Inference failed: {e}")
                # Fallthrough to Heuristics
                
        # Fallback to standard Baseline heuristics
        if not self.baseline_model.baseline_stats:
            return 0.0  # No baseline yet
        
        return self.baseline_model.calculate_anomaly_score(signals)
    
    def _add_timeline_events(self, signals, score, input_metrics, screen_metrics):
        """Add events to timeline generator"""
        timestamp = datetime.now()
        
        # Add keyboard events if macro detected
        if input_metrics.get('macro_detected'):
            self.timeline_generator.add_event(
                timestamp,
                'keyboard',
                'Macro pattern detected in keyboard input',
                0,  # Score 0 for detected macro
                {'entropy': signals['typing_entropy']}
            )
        
        # Add screen activity event
        self.timeline_generator.add_event(
            timestamp,
            'screen',
            f"Current app: {screen_metrics.get('current_app', 'unknown')}",
            score,
            {'productivity_ratio': signals['app_focus']}
        )
    
    def _save_daily_baseline(self):
        """Save end-of-day baseline data"""
        if self.current_signals:
            # Add today's behavior to baseline
            daily_vector = {
                **self.current_signals,
                'hours_worked': len(self.score_history) / 60,  # Convert minutes to hours
                'average_score': sum(self.score_history) / len(self.score_history) if self.score_history else 0
            }
            
            self.baseline_model.add_daily_behavior(daily_vector)
            
            # Retrain baseline model (Feature 14: Self-learning)
            if len(self.baseline_model.behavior_history) >= 20:
                self.baseline_model.train_lstm_baseline()
    
    def get_current_dashboard_data(self):
        """
        Feature 18: Get all data for dashboard display
        
        Returns comprehensive dashboard data dict
        """
        # Feature 7: Get explanation for current score
        explanation = self.explainer.explain_score(self.current_signals, self.current_score)
        
        # Feature 7: Get trend analysis
        trend = self.explainer.explain_trend(self.score_history[-60:], self.current_score) if len(self.score_history) > 2 else None
        
        # Feature 8: Generate heatmaps
        daily_heatmap = self.heatmap_generator.generate_daily_heatmap()
        
        # Feature 16: Get timeline patterns
        timeline_patterns = self.timeline_generator.get_pattern_analysis()
        
        return {
            'current_score': self.current_score,
            'risk_level': self._get_risk_level(self.current_score),
            'signals': self.current_signals,
            'feature_vector': getattr(self, 'current_features', {}),
            'feature_descriptions': self.feature_extractor.describe_features(
                getattr(self, 'current_features', {})
            ),
            'explanation': explanation,
            'trend': trend,
            'heatmap_daily': daily_heatmap,
            'timeline_patterns': timeline_patterns,
            'macro_detection': self.macro_detector.get_current_metrics(),
            'meeting_status': self.meeting_monitor.get_current_metrics(),
            'screen_activity': self.screen_activity.get_current_metrics(),
            'webcam_status': self.webcam_monitor.get_current_metrics(),
            'baseline_summary': self.baseline_model.get_baseline_summary(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_risk_level(self, score):
        """Convert score to risk level"""
        if score >= 80:
            return 'low'
        elif score >= 60:
            return 'medium'
        elif score >= 40:
            return 'high'
        else:
            return 'critical'
    
    def generate_daily_report(self, output_path=None):
        """
        Generate comprehensive daily report
        Combines all features into PDF
        """
        if output_path is None:
            output_path = str(Path.home() / 'Downloads')
        Path(output_path).mkdir(exist_ok=True)
        
        # Feature 16: Generate timeline PDF
        report_file = Path(output_path) / f'proguard_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        self.timeline_generator.generate_pdf_report(
            str(report_file),
            start_date=datetime.now().replace(hour=0, minute=0, second=0),
            end_date=datetime.now()
        )
        
        print(f"[OK] Daily report generated: {report_file}")
        
        return str(report_file)
    
    def trigger_break_recommendation(self):
        """
        Feature 10: AI-Based Break Recommender
        Checks if user needs a break
        """
        webcam_metrics = self.webcam_monitor.get_current_metrics()
        
        # Check for fatigue indicators
        attention_ratio = webcam_metrics.get('attention_ratio', 1.0)
        dominant_emotion = webcam_metrics.get('dominant_emotion', 'neutral')
        
        # Typing slowdown
        typing_speed = self.typing_rhythm.get_typing_speed_stats()
        
        needs_break = False
        reason = ""
        
        if attention_ratio < 0.3:
            needs_break = True
            reason = "Low attention detected - looking away frequently"
        elif dominant_emotion in ['sad', 'angry', 'tired']:
            needs_break = True
            reason = f"Emotional fatigue detected ({dominant_emotion})"
        elif typing_speed > 0 and typing_speed < 20:  # Very slow typing
            needs_break = True
            reason = "Typing speed significantly decreased"
        
        if needs_break:
            return {
                'recommended': True,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
        
        return {'recommended': False}
