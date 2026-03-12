"""
ProGuard Application Entry Point

This is the main entry point for the ProGuard application using enterprise
application factory pattern for better organization and scalability.
"""

import os
import sys

# Add the project root src directory to Python path for proper imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from proguard import create_app
from proguard.services.notification_service import start_notification_scheduler

# Create application using factory pattern
app = create_app()

if __name__ == '__main__':
    # Start notification scheduler for development
    start_notification_scheduler()
    
    # Run the Flask app
    app.run(
        debug=app.config.get('DEBUG', False),
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000)
    )
