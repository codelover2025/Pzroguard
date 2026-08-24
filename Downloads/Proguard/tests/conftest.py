import os
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from proguard import create_app
from proguard.models import db
from proguard.models.user import User, UserRole


@pytest.fixture()
def app():
    os.environ["FLASK_ENV"] = "testing"
    flask_app = create_app("testing")
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    with app.app_context():
        account = User(
            username="alice",
            email="alice@example.com",
            role=UserRole.ADMIN,
            is_active=True,
        )
        account.set_password("StrongPass123")
        db.session.add(account)
        db.session.commit()
        return account

