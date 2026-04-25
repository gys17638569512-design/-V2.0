import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-bootstrap-secret")

from app.core.config import get_settings
from app.db.session import get_session_factory, reset_db_state
from app.main import create_app
from app.models import User
from app.models.enums import UserRole

TEST_PASSWORD = "secret123"
TEST_PASSWORD_HASH = "$2b$12$CKu7RfyESAEhzIzMsrbs4u7w/U7OIcKZaAjvVZhmifVpZ8gi1GxQ2"


def _reset_runtime_state() -> None:
    get_settings.cache_clear()
    reset_db_state()


def _build_alembic_config() -> Config:
    alembic_ini_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    return Config(str(alembic_ini_path))


@pytest.fixture
def auth_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "m03_auth.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    _reset_runtime_state()
    command.upgrade(_build_alembic_config(), "head")

    app = create_app()
    client = TestClient(app)

    try:
        yield client
    finally:
        _reset_runtime_state()


@pytest.fixture
def seeded_user() -> dict[str, str | int]:
    session = get_session_factory()()
    try:
        user = User(
            username="admin",
            password_hash=TEST_PASSWORD_HASH,
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role.value,
            "name": user.full_name,
            "password": TEST_PASSWORD,
            "token_version": user.token_version,
        }
    finally:
        session.close()
