"""
Demo Data Service for ProGuard
------------------------------

This module provides a hook for the enterprise-style application factory
(`src/proguard/core/application.py`) to create demo data *if desired*.

To keep the dependency graph clean and avoid mixing different
`SQLAlchemy` instances, this implementation keeps things deliberately
minimal and does **not** reuse the top-level `demo_data.py` module that
is wired to the monolithic `models.py` setup.
"""

from typing import Any


def create_demo_data(*args: Any, **kwargs: Any) -> None:
    """
    Populate the database with demo data for the packaged ProGuard app.

    Currently this is a no-op seed hook – the tables are created by
    ``create_database_tables`` and you can add your own seeding logic
    here later, using ``src.proguard.models`` and its ``db`` instance.
    """
    # Intentionally left minimal to avoid cross‑wiring different db
    # instances; real seeding can be implemented here if needed.
    return None


__all__ = ["create_demo_data"]


