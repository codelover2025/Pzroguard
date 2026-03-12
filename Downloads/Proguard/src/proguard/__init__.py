"""
ProGuard - Work Authenticity Analytics Platform

A comprehensive enterprise-grade system with behavioral analytics, explainable insights,
and privacy-focused monitoring for remote work authenticity.

Version: 1.0.0
Author: ProGuard Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "ProGuard Team"
__email__ = "team@proguard.ai"

from .core.application import create_app

__all__ = ["create_app"]
