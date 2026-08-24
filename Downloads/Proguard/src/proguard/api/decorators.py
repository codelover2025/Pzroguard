"""
Reusable API decorators (RBAC and request guards).
"""

from functools import wraps
from flask import jsonify
from flask_login import current_user


def roles_required(*allowed_roles):
    """Require the current user to have one of the given role enums."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "authentication_required"}), 401
            if current_user.role not in allowed_roles:
                return jsonify({"error": "forbidden"}), 403
            return func(*args, **kwargs)

        return wrapper

    return decorator

