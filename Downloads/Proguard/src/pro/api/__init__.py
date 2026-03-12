"""
ProGuard API Package

This package contains all API blueprints and routes for the ProGuard application.
"""

from flask import Blueprint


def register_blueprints(app):
    """
    Register all API blueprints with the Flask application.

    The original scaffold referenced several blueprints (vendor, manager,
    admin, reports, charts, swagger_ui) that are not actually implemented
    in this repository, which caused import errors as soon as the package
    was imported.  To keep the package importable and the app runnable,
    we only register the existing authentication blueprint here.
    """
    from .auth import auth_bp

    # Core auth endpoints
    app.register_blueprint(auth_bp)


__all__ = ["register_blueprints"]

