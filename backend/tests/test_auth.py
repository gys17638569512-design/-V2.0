from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.main import create_app
from app.models import User


def _build_access_token_without_claim(
    seeded_user: dict[str, str | int],
    missing_claim: str,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(seeded_user["id"]),
        "role": seeded_user["role"],
        "type": "access",
        "ver": seeded_user["token_version"],
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=30),
    }
    payload.pop(missing_claim)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def test_settings_require_secret_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SECRET_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        get_settings()

    get_settings.cache_clear()


def test_login_returns_access_and_refresh_tokens(auth_client, seeded_user) -> None:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "username": seeded_user["username"],
            "password": seeded_user["password"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["msg"] == "ok"
    assert payload["data"]["token_type"] == "bearer"
    assert payload["data"]["access_token"]
    assert payload["data"]["refresh_token"]
    assert payload["data"]["expires_in"] > 0
    assert payload["data"]["user"] == {
        "id": seeded_user["id"],
        "username": seeded_user["username"],
        "role": seeded_user["role"],
        "name": seeded_user["name"],
    }


def test_login_rejects_invalid_password_with_unified_401(auth_client, seeded_user) -> None:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "username": seeded_user["username"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "用户名或密码错误",
        "data": None,
    }


def test_me_returns_current_user_from_access_token(auth_client, seeded_user) -> None:
    login_response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "username": seeded_user["username"],
            "password": seeded_user["password"],
        },
    )
    access_token = login_response.json()["data"]["access_token"]

    response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": seeded_user["id"],
            "username": seeded_user["username"],
            "role": seeded_user["role"],
            "name": seeded_user["name"],
        },
    }


def test_refresh_rotates_tokens_for_valid_refresh_token(auth_client, seeded_user) -> None:
    login_response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "username": seeded_user["username"],
            "password": seeded_user["password"],
        },
    )
    login_payload = login_response.json()["data"]

    response = auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_payload["refresh_token"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["msg"] == "ok"
    assert payload["data"]["token_type"] == "bearer"
    assert payload["data"]["access_token"]
    assert payload["data"]["refresh_token"]
    assert payload["data"]["access_token"] != login_payload["access_token"]
    assert payload["data"]["refresh_token"] != login_payload["refresh_token"]
    assert payload["data"]["user"]["username"] == seeded_user["username"]


def test_refresh_rejects_replayed_refresh_token(auth_client, seeded_user) -> None:
    login_response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "username": seeded_user["username"],
            "password": seeded_user["password"],
        },
    )
    original_refresh_token = login_response.json()["data"]["refresh_token"]

    first_refresh_response = auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )
    assert first_refresh_response.status_code == 200

    replay_response = auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )

    assert replay_response.status_code == 401
    assert replay_response.json() == {
        "code": 401,
        "msg": "登录状态已失效",
        "data": None,
    }


@pytest.mark.parametrize("missing_claim", ["exp", "iat", "jti"])
def test_access_token_requires_critical_claims(
    auth_client,
    seeded_user,
    missing_claim: str,
) -> None:
    access_token = _build_access_token_without_claim(seeded_user, missing_claim)

    response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "登录状态已失效",
        "data": None,
    }


def test_logout_invalidates_existing_access_and_refresh_tokens(auth_client, seeded_user) -> None:
    login_response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "username": seeded_user["username"],
            "password": seeded_user["password"],
        },
    )
    login_payload = login_response.json()["data"]

    logout_response = auth_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {login_payload['access_token']}"},
    )

    assert logout_response.status_code == 200
    assert logout_response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"logged_out": True},
    }

    me_response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_payload['access_token']}"},
    )
    assert me_response.status_code == 401
    assert me_response.json() == {
        "code": 401,
        "msg": "登录状态已失效",
        "data": None,
    }

    refresh_response = auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_payload["refresh_token"]},
    )
    assert refresh_response.status_code == 401
    assert refresh_response.json() == {
        "code": 401,
        "msg": "登录状态已失效",
        "data": None,
    }


def test_login_with_corrupted_password_hash_returns_unified_401(auth_client, seeded_user) -> None:
    session = get_session_factory()()
    try:
        user = session.get(User, seeded_user["id"])
        assert user is not None
        user.password_hash = "not-a-valid-bcrypt-hash"
        session.add(user)
        session.commit()
    finally:
        session.close()

    response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "username": seeded_user["username"],
            "password": seeded_user["password"],
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "用户名或密码错误",
        "data": None,
    }


def test_unhandled_exception_returns_unified_500_response() -> None:
    app = create_app()
    router = APIRouter()

    @router.get("/__m03_boom")
    def boom() -> None:
        raise RuntimeError("boom")

    app.include_router(router, prefix="/api/v1")
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/api/v1/__m03_boom")

    assert response.status_code == 500
    assert response.json() == {
        "code": 500,
        "msg": "服务器错误",
        "data": None,
    }
