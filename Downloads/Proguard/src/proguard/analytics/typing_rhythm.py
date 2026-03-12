"""
Feature 3: Typing Rhythm Analysis
Uses LSTM to detect natural vs automated typing patterns
"""

import numpy as np
from datetime import datetime
from collections import deque
import joblib

try:
    from tensorflow import keras
    from keras.models import Sequential, load_model
    from keras.layers import LSTM, Dense, Dropout
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

from ..storage import SecureStorage


class TypingRhythmAnalyzer:
    """
    Analyzes typing patterns using LSTM neural network
    Detects automated/macro typing vs natural human typing
    """
    
    def __init__(self, sequence_length=50, storage_path='data/typing_logs'):
        self.sequence_length = sequence_length
        self.storage = SecureStorage(storage_path)
        
        # Keystroke timing data
        self.keystroke_intervals = deque(maxlen=1000)
        self.keystroke_chars = deque(maxlen=1000)
        # Last keystroke timestamp — used to compute inter-key intervals
        self._last_key_time: float = 0.0
        
        # LSTM model
        self.model = None
        self.model_path = storage_path + '/typing_lstm_model.h5'
        
        # Try to load existing model
        if KERAS_AVAILABLE:
            self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing LSTM model or create new one"""
        try:
            import os
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                print("[OK] Loaded existing typing rhythm LSTM model")
            else:
                self._create_model()
        except Exception as e:
            print(f"[WARNING] Could not load typing model: {e}")
            self._create_model()
    
    def _create_model(self):
        """Create new LSTM model for typing pattern classification"""
        if not KERAS_AVAILABLE:
            print("[WARNING] Keras not available - typing rhythm analysis disabled")
            return
        
        model = Sequential([
            LSTM(64, input_shape=(self.sequence_length, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')  # 0 = bot, 1 = human
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        print("[OK] Created new typing rhythm LSTM model")
    
    def add_keystroke(self, timestamp, key_char=None):
        """
        Add keystroke timing data

        Args:
            timestamp: Unix timestamp of keystroke
            key_char: Character pressed (optional)
        """
        if self._last_key_time > 0.0:
            # We have a previous keystroke — compute and store the interval
            interval = timestamp - self._last_key_time
            # Ignore suspiciously large gaps (> 30 s means user was idle)
            if 0.0 < interval < 30.0:
                self.keystroke_intervals.append((timestamp, interval))
                if key_char:
                    self.keystroke_chars.append(key_char)

        # Always seed/update the last-key timestamp
        self._last_key_time = timestamp
    
    def get_typing_speed_stats(self):
        """
        Calculate typing speed statistics
        Returns: words per minute (WPM) estimate
        """
        if len(self.keystroke_intervals) < 10:
            return 0
        
        # Get recent intervals (last 100 keystrokes)
        recent_intervals = [
            interval for _, interval in list(self.keystroke_intervals)[-100:]
        ]
        
        avg_interval = np.mean(recent_intervals)
        
        # Convert to WPM (assuming 5 chars per word)
        if avg_interval > 0:
            chars_per_second = 1 / avg_interval
            wpm = (chars_per_second * 60) / 5
            return wpm
        
        return 0
    
    def calculate_rhythm_entropy(self):
        """
        Calculate entropy of typing rhythm
        Low entropy = repetitive/robotic typing
        """
        if len(self.keystroke_intervals) < 5:
            return 0.0  # Not enough data yet

        intervals = [interval for _, interval in list(self.keystroke_intervals)[-100:]]

        # Use smaller bins when we have little data so the histogram isn't empty
        n_bins = min(10, max(2, len(intervals) // 2))

        # Bin intervals
        hist, _ = np.histogram(intervals, bins=n_bins)
        if hist.sum() == 0:
            return 0.0
        hist = hist / hist.sum()  # Normalize

        # Shannon entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        normalized_entropy = min(1.0, entropy / np.log2(n_bins + 1))

        return float(normalized_entropy)
    
    def predict_authenticity(self):
        """
        Use LSTM model to predict if typing is authentic human typing
        Returns: score 0-1 (0=bot, 1=human)
        """
        if not KERAS_AVAILABLE or self.model is None:
            # Fallback to entropy-based detection
            return self.calculate_rhythm_entropy()
        
        if len(self.keystroke_intervals) < self.sequence_length:
            return 0.0  # Not enough data, show 0% until real typing detected
        
        # Prepare sequence
        intervals = [
            interval for _, interval in list(self.keystroke_intervals)[-self.sequence_length:]
        ]
        
        # Normalize intervals (0-1 range)
        max_interval = max(intervals) if max(intervals) > 0 else 1
        normalized = np.array(intervals) / max_interval
        
        # Reshape for LSTM input
        sequence = normalized.reshape(1, self.sequence_length, 1)
        
        try:
            # Predict
            prediction = self.model.predict(sequence, verbose=0)[0][0]
            return float(prediction)
        except Exception as e:
            print(f"[WARNING] Typing prediction error: {e}")
            return self.calculate_rhythm_entropy()
    
    def detect_burst_typing(self):
        """
        Detect unnaturally fast burst typing (copy-paste indicator)
        Returns: True if burst detected
        """
        if len(self.keystroke_intervals) < 10:
            return False
        
        recent_intervals = [
            interval for _, interval in list(self.keystroke_intervals)[-10:]
        ]
        
        # If all intervals < 0.05 seconds, likely paste or macro
        if all(i < 0.05 for i in recent_intervals):
            return True
        
        return False
    
    def get_current_metrics(self):
        """
        Get current typing rhythm metrics
        Returns: normalized scores and statistics
        """
        return {
            'typing_authenticity': self.predict_authenticity(),
            'rhythm_entropy': self.calculate_rhythm_entropy(),
            'typing_speed_wpm': self.get_typing_speed_stats(),
            'burst_detected': self.detect_burst_typing(),
            'total_keystrokes': len(self.keystroke_intervals),
            'timestamp': datetime.now().isoformat()
        }
    
    def train_on_labeled_data(self, sequences, labels):
        """
        Train LSTM model on labeled typing data
        
        Args:
            sequences: List of keystroke interval sequences
            labels: List of labels (0=bot, 1=human)
        """
        if not KERAS_AVAILABLE or self.model is None:
            print("[WARNING] Cannot train: Keras not available")
            return
        
        # Prepare training data
        X = np.array(sequences)
        y = np.array(labels)
        
        # Train model
        self.model.fit(
            X, y,
            epochs=10,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        # Save model
        try:
            self.model.save(self.model_path)
            print("[OK] Typing rhythm model trained and saved")
        except Exception as e:
            print(f"[WARNING] Could not save model: {e}")
    
    def save_logs(self):
        """Save typing rhythm logs"""
        data = {
            'keystroke_intervals': list(self.keystroke_intervals),
            'keystroke_chars': list(self.keystroke_chars) if self.keystroke_chars else [],
            'metrics': self.get_current_metrics()
        }
        
        self.storage.save_encrypted(
            f'typing_log_{datetime.now().strftime("%Y%m%d")}.json',
            data
        )
