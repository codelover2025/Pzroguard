"""
Anomaly Result Model — stores ML analysis results per monitoring cycle.

Each row captures a snapshot of the extracted feature vector, the ML-derived
anomaly score, final suspicion score, and whether the cycle was flagged.
"""

import json
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

# Import the shared db instance used across the application
# This will be the same `db` object created in app.py
try:
    from app import db
except ImportError:
    # Fallback for standalone testing or circular import avoidance
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()


class AnomalyResult(db.Model):
    """Stores per-cycle ML analysis results for historical review."""

    __tablename__ = 'anomaly_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Serialised feature vector (JSON string)
    feature_vector = db.Column(db.Text, nullable=False)

    # ML outputs
    anomaly_score = db.Column(db.Float, nullable=False, default=0.0)
    suspicion_score = db.Column(db.Float, nullable=False, default=0.0)
    risk_level = db.Column(db.String(16), nullable=False, default='low')
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)

    # Optional: dominant reason text
    primary_reason = db.Column(db.String(256), nullable=True)

    def set_features(self, features: dict) -> None:
        """Serialize a feature dict to JSON for storage."""
        self.feature_vector = json.dumps(features)

    def get_features(self) -> dict:
        """Deserialize the stored feature vector."""
        try:
            return json.loads(self.feature_vector)
        except (json.JSONDecodeError, TypeError):
            return {}

    def __repr__(self) -> str:
        return (
            f"<AnomalyResult user={self.user_id} score={self.suspicion_score:.0f} "
            f"flagged={self.is_flagged} at={self.timestamp}>"
        )
