"""
Feature 11: User Behavior Baseline Modeling
Learns each user's normal work pattern using LSTM
"""

import numpy as np
from datetime import datetime, timedelta
import joblib

try:
    from keras.models import Sequential, load_model
    from keras.layers import LSTM, Dense, Dropout
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

from ..storage import SecureStorage


class BaselineModeler:
    """
    Builds personalized baseline model of user's genuine work behavior
    Detects deviations from normal patterns
    """
    
    def __init__(self, user_id, sequence_length=20, storage_path='data/baselines'):
        self.user_id = user_id
        self.sequence_length = sequence_length
        self.storage = SecureStorage(storage_path)
        
        # Historical behavior data
        self.behavior_history = []  # List of daily behavior vectors
        
        # Baseline statistics
        self.baseline_stats = None
        
        # Anomaly detection model
        self.model = None
        self.model_path = f"{storage_path}/baseline_{user_id}.h5"
        
        # Load existing baseline if available
        self._load_baseline()
    
    def _load_baseline(self):
        """Load existing baseline data and model"""
        # Load statistics
        baseline_data = self.storage.load_encrypted(f'baseline_{self.user_id}.json')
        if baseline_data:
            self.baseline_stats = baseline_data.get('stats')
            self.behavior_history = baseline_data.get('history', [])
            print(f"[OK] Loaded baseline for user {self.user_id}")
        
        # Load LSTM model
        if KERAS_AVAILABLE:
            try:
                import os
                if os.path.exists(self.model_path):
                    self.model = load_model(self.model_path)
                    print(f"[OK] Loaded baseline LSTM model for user {self.user_id}")
            except Exception as e:
                print(f"[WARNING] Could not load baseline model: {e}")
    
    def add_daily_behavior(self, behavior_vector):
        """
        Add a day's worth of behavior data
        
        Args:
            behavior_vector: Dict containing daily metrics:
                - typing_entropy, mouse_entropy, gaze_presence,
                - app_focus, emotion_focus, hours_worked, etc.
        """
        # Add timestamp
        behavior_vector['timestamp'] = datetime.now().isoformat()
        
        # Add to history
        self.behavior_history.append(behavior_vector)
        
        # Keep only last 90 days
        if len(self.behavior_history) > 90:
            self.behavior_history = self.behavior_history[-90:]
        
        # Update baseline statistics
        self._update_baseline_stats()
    
    def _update_baseline_stats(self):
        """Calculate baseline statistics from history"""
        if len(self.behavior_history) < 5:
            return  # Need at least 5 days of data
        
        # Extract features
        features = [
            'typing_entropy', 'mouse_entropy', 'gaze_presence',
            'app_focus', 'emotion_focus', 'hours_worked'
        ]
        
        stats = {}
        
        for feature in features:
            values = [
                day.get(feature, 0.5) for day in self.behavior_history
                if feature in day
            ]
            
            if values:
                stats[feature] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values))
                }
        
        self.baseline_stats = stats
        
        # Save updated baseline
        self._save_baseline()
    
    def _save_baseline(self):
        """Save baseline data"""
        data = {
            'user_id': self.user_id,
            'stats': self.baseline_stats,
            'history': self.behavior_history,
            'last_updated': datetime.now().isoformat()
        }
        
        self.storage.save_encrypted(f'baseline_{self.user_id}.json', data)
    
    def calculate_anomaly_score(self, current_behavior):
        """
        Calculate how much current behavior deviates from baseline
        
        Args:
            current_behavior: Dict of current behavior metrics
            
        Returns:
            Anomaly score (0-1, where 1 = very anomalous)
        """
        if not self.baseline_stats:
            return 0.0  # No baseline yet
        
        anomaly_scores = []
        
        for feature, current_value in current_behavior.items():
            if feature in self.baseline_stats:
                stats = self.baseline_stats[feature]
                mean = stats['mean']
                std = stats['std']
                
                if std > 0:
                    # Z-score
                    z_score = abs(current_value - mean) / std
                    
                    # Convert to 0-1 score (z > 3 is very anomalous)
                    anomaly = min(z_score / 3, 1.0)
                    anomaly_scores.append(anomaly)
        
        if anomaly_scores:
            # Average anomaly across all features
            return float(np.mean(anomaly_scores))
        
        return 0.0
    
    def is_behavior_normal(self, current_behavior, threshold=0.7):
        """
        Check if current behavior is within normal range
        
        Args:
            current_behavior: Dict of current metrics
            threshold: Anomaly threshold (above this = abnormal)
            
        Returns:
            (is_normal, anomaly_score, deviating_features)
        """
        anomaly_score = self.calculate_anomaly_score(current_behavior)
        
        # Find which features are deviating
        deviating_features = []
        
        if self.baseline_stats:
            for feature, current_value in current_behavior.items():
                if feature in self.baseline_stats:
                    stats = self.baseline_stats[feature]
                    mean = stats['mean']
                    std = stats['std']
                    
                    if std > 0:
                        z_score = abs(current_value - mean) / std
                        
                        if z_score > 2:  # More than 2 std deviations
                            deviating_features.append({
                                'feature': feature,
                                'current': current_value,
                                'expected': mean,
                                'deviation': z_score
                            })
        
        is_normal = anomaly_score < threshold
        
        return is_normal, anomaly_score, deviating_features
    
    def train_lstm_baseline(self):
        """
        Train LSTM model on historical behavior for anomaly detection
        """
        if not KERAS_AVAILABLE:
            print("[WARNING] Keras not available - LSTM baseline disabled")
            return
        
        if len(self.behavior_history) < 20:
            print("[WARNING] Need at least 20 days of data to train LSTM baseline")
            return
        
        # Prepare sequences
        features = ['typing_entropy', 'mouse_entropy', 'gaze_presence', 
                   'app_focus', 'emotion_focus']
        
        # Convert history to feature matrix
        X_data = []
        for day in self.behavior_history:
            vector = [day.get(f, 0.5) for f in features]
            X_data.append(vector)
        
        X_data = np.array(X_data)
        
        # Create sequences
        X = []
        y = []
        
        for i in range(len(X_data) - self.sequence_length):
            X.append(X_data[i:i+self.sequence_length])
            y.append(X_data[i+self.sequence_length])  # Predict next day
        
        X = np.array(X)
        y = np.array(y)
        
        # Build autoencoder model
        model = Sequential([
            LSTM(32, input_shape=(self.sequence_length, len(features)), return_sequences=True),
            Dropout(0.2),
            LSTM(16),
            Dropout(0.2),
            Dense(len(features), activation='sigmoid')
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train
        model.fit(X, y, epochs=50, batch_size=4, validation_split=0.2, verbose=0)
        
        # Save model
        try:
            model.save(self.model_path)
            self.model = model
            print(f"[OK] Trained LSTM baseline model for user {self.user_id}")
        except Exception as e:
            print(f"[WARNING] Could not save baseline model: {e}")
    
    def get_baseline_summary(self):
        """Get summary of baseline data"""
        return {
            'user_id': self.user_id,
            'days_of_data': len(self.behavior_history),
            'baseline_established': self.baseline_stats is not None,
            'baseline_stats': self.baseline_stats,
            'last_updated': self.behavior_history[-1]['timestamp'] if self.behavior_history else None
        }
