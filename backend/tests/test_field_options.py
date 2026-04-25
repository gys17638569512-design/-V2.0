from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models import User
from app.models.enums import UserRole


def _login_and_get_access_token(auth_client, username: str, password: str) -> str:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_get_field_options_returns_seeded_device_categories(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.get(
        "/api/v1/field-options?field_key=device_category&page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["msg"] == "ok"
    assert payload["data"]["page"] == 1
    assert payload["data"]["page_size"] == 20
    assert payload["data"]["total"] >= 3

    items = payload["data"]["items"]
    assert [item["option_value"] for item in items[:3]] == [
        "BRIDGE_CRANE",
        "GANTRY_CRANE",
        "ELECTRIC_HOIST",
    ]
    assert [item["option_label"] for item in items[:3]] == [
        "桥式起重机",
        "门式起重机",
        "电动葫芦",
    ]


def test_admin_can_create_update_and_delete_field_option(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    create_response = auth_client.post(
        "/api/v1/field-options",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "field_key": "industry_type",
            "option_value": "CHEMICAL",
            "option_label": "化工",
            "sort_order": 30,
            "is_active": True,
        },
    )

    assert create_response.status_code == 200
    created_item = create_response.json()["data"]
    assert created_item["field_key"] == "industry_type"
    assert created_item["option_value"] == "CHEMICAL"
    assert created_item["option_label"] == "化工"

    update_response = auth_client.put(
        f"/api/v1/field-options/{created_item['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "option_label": "化工行业",
            "sort_order": 35,
            "is_active": True,
        },
    )

    assert update_response.status_code == 200
    updated_item = update_response.json()["data"]
    assert updated_item["option_label"] == "化工行业"
    assert updated_item["sort_order"] == 35
    assert updated_item["is_active"] is True

    delete_response = auth_client.delete(
        f"/api/v1/field-options/{created_item['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }

    list_response = auth_client.get(
        "/api/v1/field-options?field_key=industry_type&page=1&page_size=100",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    listed_values = [item["option_value"] for item in list_response.json()["data"]["items"]]
    assert "CHEMICAL" not in listed_values

    inactive_list_response = auth_client.get(
        "/api/v1/field-options?field_key=industry_type&include_inactive=true&page=1&page_size=100",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    inactive_items = inactive_list_response.json()["data"]["items"]
    deleted_item = next(item for item in inactive_items if item["option_value"] == "CHEMICAL")
    assert deleted_item["is_active"] is False


def test_duplicate_field_option_returns_unified_400(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        "/api/v1/field-options",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "field_key": "device_category",
            "option_value": "BRIDGE_CRANE",
            "option_label": "桥式起重机-重复",
            "sort_order": 99,
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "同一字段分类下的选项值不能重复",
        "data": None,
    }


def test_non_admin_cannot_modify_field_options(auth_client, seeded_user) -> None:
    session = get_session_factory()()
    try:
        manager = User(
            username="manager-user",
            password_hash=hash_password("manager-pass"),
            full_name="项目经理",
            role=UserRole.MANAGER,
            is_active=True,
        )
        session.add(manager)
        session.commit()
    finally:
        session.close()

    access_token = _login_and_get_access_token(auth_client, "manager-user", "manager-pass")

    response = auth_client.post(
        "/api/v1/field-options",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "field_key": "industry_type",
            "option_value": "TEXTILE",
            "option_label": "纺织",
            "sort_order": 40,
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_list_field_options_requires_authentication(auth_client) -> None:
    response = auth_client.get("/api/v1/field-options?field_key=device_category&page=1&page_size=20")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }
