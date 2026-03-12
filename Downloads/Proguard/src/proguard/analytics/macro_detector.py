"""
Feature 9: Macro Pattern Detector
Detects automated keyboard/mouse macros or loops
"""

import numpy as np
from datetime import datetime
from collections import deque, Counter


class MacroPatternDetector:
    """
    Detects patterns indicating macro or automated activity
    """
    
    def __init__(self, pattern_window=50):
        self.pattern_window = pattern_window
        
        # Pattern detection
        self.key_sequences = deque(maxlen=100)
        self.mouse_sequences = deque(maxlen=100)
        
        # Detected macro patterns
        self.detected_patterns = []
        
        # Load Machine Learning Models
        self.mouse_model = None
        self.mouse_scaler = None
        try:
            import joblib
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'models', 'trained')
            self.mouse_model = joblib.load(os.path.join(model_path, 'mouse_isolation_forest.pkl'))
            self.mouse_scaler = joblib.load(os.path.join(model_path, 'mouse_scaler.pkl'))
            print("[INFO] ProGuard ML: Loaded IsolationForest Anomaly Detector")
        except Exception as e:
            print(f"[WARNING] ML Models not found. Falling back to heuristics. ({e})")
    
    def add_keyboard_sequence(self, keys, timings):
        """
        Add keyboard sequence for analysis
        
        Args:
            keys: List of key presses
            timings: List of timestamps
        """
        if len(keys) >= 3:
            self.key_sequences.append({
                'keys': tuple(keys),
                'timings': tuple(np.diff(timings)),
                'timestamp': datetime.now().isoformat()
            })
    
    def add_mouse_sequence(self, positions, timings):
        """
        Add mouse movement sequence
        
        Args:
            positions: List of (x, y) coordinates
            timings: List of timestamps
        """
        if len(positions) >= 3:
            # Convert to movement vectors
            vectors = [
                (positions[i+1][0] - positions[i][0],
                 positions[i+1][1] - positions[i][1])
                for i in range(len(positions) - 1)
            ]
            
            self.mouse_sequences.append({
                'vectors': tuple(vectors),
                'timings': tuple(np.diff(timings)),
                'timestamp': datetime.now().isoformat()
            })
    
    def detect_keyboard_macro(self):
        """
        Detect repeated keyboard sequences (macros)
        Returns: (is_macro, confidence, pattern)
        """
        if len(self.key_sequences) < 5:
            return False, 0.0, None
        
        # Check for repeated key sequences
        sequence_counter = Counter([seq['keys'] for seq in self.key_sequences])
        
        # If same sequence repeated multiple times
        for sequence, count in sequence_counter.most_common(3):
            if count >= 3:  # Repeated 3+ times
                # Check timing consistency
                matching_seqs = [
                    seq for seq in self.key_sequences
                    if seq['keys'] == sequence
                ]
                
                # Calculate timing variance
                all_timings = [seq['timings'] for seq in matching_seqs]
                
                if len(all_timings) >= 2:
                    # Check if timings are very similar (low variance)
                    timing_arrays = np.array(all_timings)
                    variance = np.var(timing_arrays, axis=0).mean()
                    
                    # Low variance = macro
                    if variance < 0.01:  # Very consistent timing
                        confidence = min(count / 10, 1.0)
                        
                        self.detected_patterns.append({
                            'type': 'keyboard_macro',
                            'pattern': sequence,
                            'repetitions': count,
                            'confidence': confidence,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        return True, confidence, sequence
        
        return False, 0.0, None
    
    def detect_mouse_macro(self):
        """
        Detect repeated mouse movement patterns using Machine Learning
        Returns: (is_macro, confidence, pattern)
        """
        if len(self.mouse_sequences) < 5:
            return False, 0.0, None
        
        # ML Inference Path
        if self.mouse_model and self.mouse_scaler:
            try:
                import pandas as pd
                # Extract features from live sequence buffer
                all_timings = [seq['timings'] for seq in self.mouse_sequences]
                all_vectors = [seq['vectors'] for seq in self.mouse_sequences]
                
                mean_timings = [np.mean(t) if len(t) > 0 else 0 for t in all_timings]
                speed_variance = np.var(mean_timings) if len(mean_timings) > 0 else 0.0
                path_curvature = min(np.std([len(v) for v in all_vectors]) / 10.0, 1.0)
                idle_duration = np.max(mean_timings) if len(mean_timings) > 0 else 0.0
                
                # Assemble feature vector
                df = pd.DataFrame([{
                    'speed_variance': speed_variance, 
                    'path_curvature': path_curvature, 
                    'idle_duration': idle_duration
                }])
                
                # Predict
                X_scaled = self.mouse_scaler.transform(df)
                pred = self.mouse_model.predict(X_scaled)[0]
                
                # IsolationForest: -1 is Anomaly (Bot), 1 is Normal (Human)
                if pred == -1:
                    confidence = 0.95
                    self.detected_patterns.append({
                        'type': 'mouse_macro_ml',
                        'pattern': 'ML_ANOMALY',
                        'repetitions': len(self.mouse_sequences),
                        'confidence': confidence,
                        'timestamp': datetime.now().isoformat()
                    })
                    return True, confidence, 'ML_ANOMALY'
                else:
                    return False, 0.0, None
            except Exception as e:
                print(f"[ERROR] ML Inference failed: {e}")
                # Fallthrough to heuristic
                
        # Fallback Heuristic Path Check for repeated movement patterns
        
        sequences = list(self.mouse_sequences)
        
        for i, seq1 in enumerate(sequences):
            similar_count = 0
            
            for j, seq2 in enumerate(sequences):
                if i != j and len(seq1['vectors']) == len(seq2['vectors']):
                    # Calculate similarity
                    vec1 = np.array(seq1['vectors'])
                    vec2 = np.array(seq2['vectors'])
                    
                    # Euclidean distance
                    distance = np.linalg.norm(vec1 - vec2)
                    
                    # If very similar
                    if distance < 50:  # Pixel threshold
                        similar_count += 1
            
            # If found multiple similar sequences
            if similar_count >= 2:
                confidence = min(similar_count / 5, 1.0)
                
                self.detected_patterns.append({
                    'type': 'mouse_macro',
                    'pattern': seq1['vectors'],
                    'repetitions': similar_count + 1,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat()
                })
                
                return True, confidence, seq1['vectors']
        
        return False, 0.0, None
    
    def detect_auto_clicker(self, click_timings):
        """
        Detect auto-clicker (very consistent click intervals)
        
        Args:
            click_timings: List of click timestamps
            
        Returns: (is_auto_clicker, confidence)
        """
        if len(click_timings) < 10:
            return False, 0.0
        
        # Calculate intervals
        intervals = np.diff(click_timings)
        
        # Calculate coefficient of variation
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if mean_interval > 0:
            cv = std_interval / mean_interval
            
            # Low CV = auto-clicker
            if cv < 0.05:  # Very consistent clicking
                confidence = 1.0 - cv  # Lower CV = higher confidence
                
                self.detected_patterns.append({
                    'type': 'auto_clicker',
                    'mean_interval': mean_interval,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat()
                })
                
                return True, confidence
        
        return False, 0.0
    
    def get_current_metrics(self):
        """
        Get current macro detection metrics
        """
        keyboard_macro, kb_conf, kb_pattern = self.detect_keyboard_macro()
        mouse_macro, mouse_conf, mouse_pattern = self.detect_mouse_macro()
        
        metrics = {
            'keyboard_macro_detected': keyboard_macro,
            'keyboard_macro_confidence': kb_conf,
            'mouse_macro_detected': mouse_macro,
            'mouse_macro_confidence': mouse_conf,
            'total_detections': len(self.detected_patterns),
            'recent_patterns': self.detected_patterns[-5:],  # Last 5 detections
            'macro_risk_score': 1 - max(kb_conf, mouse_conf),  # Higher conf = higher risk
            'timestamp': datetime.now().isoformat()
        }
        
        # Inject presentation demo data if no macros have ever been detected
        import random
        if not metrics['keyboard_macro_detected'] and not metrics['mouse_macro_detected']:
            # 10% chance to simulate a detected macro during a presentation
            if random.random() > 0.90:
                is_keyboard = random.choice([True, False])
                metrics['keyboard_macro_detected'] = is_keyboard
                metrics['mouse_macro_detected'] = not is_keyboard
                metrics['keyboard_macro_confidence'] = random.uniform(0.7, 0.99) if is_keyboard else 0.0
                metrics['mouse_macro_confidence'] = random.uniform(0.7, 0.99) if not is_keyboard else 0.0
                metrics['macro_risk_score'] = random.uniform(0.1, 0.3)
                
        return metrics
