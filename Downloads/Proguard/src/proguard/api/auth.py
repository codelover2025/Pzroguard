"""Authentication and session endpoints for the ProGuard API."""

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from ..models import db
from ..services.auth_service import (
    authenticate_user,
    can_attempt_login,
    record_failed_login,
    reset_failed_logins,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _bad_request(message: str):
    return jsonify({"error": "bad_request", "message": message}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login with username/password and start a secure session."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return _bad_request("username and password are required")

    max_attempts = current_app.config.get("AUTH_MAX_LOGIN_ATTEMPTS", 5)
    lockout_seconds = current_app.config.get("AUTH_LOCKOUT_SECONDS", 900)
    allowed, retry_after = can_attempt_login(username, max_attempts, lockout_seconds)
    if not allowed:
        return (
            jsonify(
                {
                    "error": "too_many_attempts",
                    "message": "account temporarily locked",
                    "retry_after_seconds": retry_after,
                }
            ),
            429,
        )

    user = authenticate_user(username, password)
    if not user:
        record_failed_login(username, max_attempts, lockout_seconds)
        return jsonify({"error": "invalid_credentials"}), 401

    login_user(user)
    reset_failed_logins(username)
    user.last_login = datetime.utcnow()
    db.session.commit()

    return (
        jsonify(
            {
                "message": "login_successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                },
            }
        ),
        200,
    )


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Terminate the current user session."""
    logout_user()
    return jsonify({"message": "logged_out"}), 200


@auth_bp.route("/status", methods=["GET"])
def auth_status():
    """Get simple authentication status for UI checks."""
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "username": current_user.username}), 200
    return jsonify({"authenticated": False}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """Return current authenticated user details."""
    return (
        jsonify(
            {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "role": current_user.role.value,
                "last_login": (
                    current_user.last_login.isoformat() + "Z"
                    if current_user.last_login
                    else None
                ),
            }
        ),
        200,
    )


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """Allow users to change password with current-password verification."""
    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not current_password or not new_password:
        return _bad_request("current_password and new_password are required")

    if not current_user.check_password(current_password):
        return jsonify({"error": "invalid_current_password"}), 401

    min_password_length = current_app.config.get("PASSWORD_MIN_LENGTH", 10)
    if len(new_password) < min_password_length:
        return (
            jsonify(
                {
                    "error": "weak_password",
                    "message": f"new password must be at least {min_password_length} characters",
                }
            ),
            400,
        )

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "password_updated"}), 200
