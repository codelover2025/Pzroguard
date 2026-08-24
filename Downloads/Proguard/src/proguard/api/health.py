"""
Operational health endpoints.
"""

from datetime import datetime
from flask import Blueprint, jsonify

from ..models import db

health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("/", methods=["GET"])
def health():
    """Basic health endpoint with lightweight DB liveness check."""
    db.session.execute(db.text("SELECT 1"))
    return jsonify(
        {
            "status": "ok",
            "service": "proguard",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        }
    ), 200

