"""
ProGuard API Package

This package contains all API blueprints and routes for the ProGuard application.
"""

def register_blueprints(app):
    """
    Register all API blueprints with the Flask application.

    For now only the authentication blueprint is wired up here.
    The stub imports for vendor/manager/admin/report/chart APIs were
    referring to modules that do not exist in the codebase, which caused
    import errors as soon as the package was imported.
    """
    from .auth import auth_bp
    from .health import health_bp

    # Core auth endpoints
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)


__all__ = ["register_blueprints"]

