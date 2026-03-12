"""
Demo Data Service for Attendo
-----------------------------

This module mirrors the ProGuard demo data service for the Attendo
package. It exists primarily as a stable import target for
`attendo.core.application`.

To avoid mixing multiple `SQLAlchemy` instances, this implementation
does **not** call the monolithic top-level ``demo_data.create_demo_data``
function. Instead it serves as a no-op seed hook that can be extended
later if you decide to add Attendo-specific demo data.
"""

from typing import Any


def create_demo_data(*args: Any, **kwargs: Any) -> None:
    """
    Populate the database with demo data for Attendo.

    Currently this is a no-op; real seeding can be added here later
    using the `attendo.models` (or `proguard.models`) package.
    """
    return None


__all__ = ["create_demo_data"]


