"""
Enhanced Demo Data Generator
----------------------------

This script provides a convenient entry point for generating rich demo
data for the ProGuard/Attendo application.

The original version of this file had a large, partially duplicated
implementation that had become syntactically invalid. To keep things
robust and easy to maintain, this version simply delegates to the
single, well‑tested implementation in ``demo_data.create_demo_data``.
"""

from __future__ import annotations

from typing import Any

import models
from models import (  # noqa: F401  (re-exported for convenience when exploring)
    User,
    Vendor,
    Manager,
    DailyStatus,
    SwipeRecord,
    Holiday,
    MismatchRecord,
    NotificationLog,
    AuditLog,
    SystemConfiguration,
    LeaveRecord,
    WFHRecord,
    UserRole,
    AttendanceStatus,
    ApprovalStatus,
)


def create_enhanced_demo_data(*args: Any, **kwargs: Any) -> bool:
    """
    Populate the database with demo data.

    For now this function is a thin wrapper around the canonical
    ``demo_data.create_demo_data`` function located at the project root.
    It returns ``True`` on success and ``False`` if an exception occurs.
    """
    from demo_data import create_demo_data as _create_demo_data
    from app import app

    with app.app_context():
        try:
            # Let the central demo_data module handle all inserts
            _create_demo_data(*args, **kwargs)
            print("✅ Enhanced demo data created successfully (via demo_data.create_demo_data).")
            return True
        except Exception as exc:  # pragma: no cover - best-effort logging
            models.db.session.rollback()
            print(f"❌ Error creating enhanced demo data: {exc}")
            return False


if __name__ == "__main__":
    create_enhanced_demo_data()


