"""
Authentication service helpers.

Provides application-level authentication logic and in-memory
login throttling suitable for single-process development/test usage.
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple

from ..models.user import User


_FAILED_ATTEMPTS: Dict[str, Tuple[int, datetime]] = {}


def can_attempt_login(username: str, max_attempts: int, lockout_seconds: int) -> Tuple[bool, int]:
    """
    Check whether a user is currently allowed to attempt login.

    Returns:
        (is_allowed, retry_after_seconds)
    """
    now = datetime.utcnow()
    attempts, locked_until = _FAILED_ATTEMPTS.get(username, (0, now))

    if attempts < max_attempts:
        return True, 0

    if now >= locked_until:
        _FAILED_ATTEMPTS.pop(username, None)
        return True, 0

    retry_after = int((locked_until - now).total_seconds())
    return False, max(retry_after, 1)


def record_failed_login(username: str, max_attempts: int, lockout_seconds: int) -> None:
    """Track a failed login attempt and lock the account key if needed."""
    now = datetime.utcnow()
    attempts, _ = _FAILED_ATTEMPTS.get(username, (0, now))
    attempts += 1

    if attempts >= max_attempts:
        _FAILED_ATTEMPTS[username] = (attempts, now + timedelta(seconds=lockout_seconds))
        return

    _FAILED_ATTEMPTS[username] = (attempts, now)


def reset_failed_logins(username: str) -> None:
    """Reset failed login attempts after successful authentication."""
    _FAILED_ATTEMPTS.pop(username, None)


def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a username/password pair against the database."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    if not user.check_password(password):
        return None
    if not user.is_active:
        return None
    return user

