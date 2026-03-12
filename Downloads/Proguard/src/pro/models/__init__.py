"""
Attendo Models Package
----------------------

The Attendo package reuses the same ORM models as the core ProGuard
package. To avoid maintaining duplicate model definitions, this module
simply re-exports everything from ``proguard.models``.
"""

from proguard.models import (  # type: ignore[F401]
    db,
    User,
    UserRole,
    Vendor,
    Manager,
    DailyStatus,
    AttendanceStatus,
    ApprovalStatus,
    SwipeRecord,
    Holiday,
    MismatchRecord,
    NotificationLog,
    AuditLog,
    SystemConfiguration,
    LeaveRecord,
    WFHRecord,
)

__all__ = [
    "db",
    "User",
    "UserRole",
    "Vendor",
    "Manager",
    "DailyStatus",
    "AttendanceStatus",
    "ApprovalStatus",
    "SwipeRecord",
    "Holiday",
    "MismatchRecord",
    "NotificationLog",
    "AuditLog",
    "SystemConfiguration",
    "LeaveRecord",
    "WFHRecord",
]
