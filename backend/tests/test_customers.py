from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models import Customer, User
from app.models.enums import UserRole


def _login_and_get_access_token(auth_client, username: str, password: str) -> str:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def _create_user(*, username: str, password: str, full_name: str, role: UserRole) -> dict[str, int | str]:
    session = get_session_factory()()
    try:
        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return {
            "id": user.id,
            "username": user.username,
            "password": password,
            "role": user.role.value,
            "name": user.full_name,
        }
    finally:
        session.close()


def _create_customer(*, name: str, manager_id: int | None, is_active: bool = True) -> dict[str, int | str | bool]:
    session = get_session_factory()()
    try:
        customer = Customer(
            name=name,
            manager_id=manager_id,
            is_active=is_active,
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return {
            "id": customer.id,
            "name": customer.name,
            "manager_id": customer.manager_id,
            "is_active": customer.is_active,
        }
    finally:
        session.close()


def _get_customer_by_id(customer_id: int) -> Customer | None:
    session = get_session_factory()()
    try:
        return session.get(Customer, customer_id)
    finally:
        session.close()


def test_list_customers_requires_authentication(auth_client) -> None:
    response = auth_client.get("/api/v1/customers?page=1&page_size=20")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }


def test_admin_can_list_customers_with_pagination(auth_client, seeded_user) -> None:
    _create_customer(name="宝武钢铁", manager_id=seeded_user["id"])
    _create_customer(name="中联重科", manager_id=seeded_user["id"])
    _create_customer(name="三一重工", manager_id=None)
    _create_customer(name="停用客户", manager_id=seeded_user["id"], is_active=False)

    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.get(
        "/api/v1/customers?page=1&page_size=2",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "items": [
                {
                    "id": 1,
                    "name": "宝武钢铁",
                    "manager_id": seeded_user["id"],
                },
                {
                    "id": 2,
                    "name": "中联重科",
                    "manager_id": seeded_user["id"],
                },
            ],
            "total": 3,
            "page": 1,
            "page_size": 2,
        },
    }


def test_manager_only_sees_owned_customers_in_list(auth_client) -> None:
    manager = _create_user(
        username="manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )

    _create_customer(name="我的客户A", manager_id=manager["id"])
    _create_customer(name="别人的客户", manager_id=other_manager["id"])
    _create_customer(name="我的停用客户", manager_id=manager["id"], is_active=False)

    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.get(
        "/api/v1/customers?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "items": [
                {
                    "id": 1,
                    "name": "我的客户A",
                    "manager_id": manager["id"],
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
        },
    }


def test_admin_can_get_customer_detail(auth_client, seeded_user) -> None:
    customer = _create_customer(name="长沙起重机厂", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": customer["id"],
            "name": "长沙起重机厂",
            "manager_id": seeded_user["id"],
        },
    }


def test_manager_cannot_get_other_managers_customer_detail(auth_client) -> None:
    manager = _create_user(
        username="manager-detail-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="manager-detail-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="隔离客户", manager_id=other_manager["id"])

    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_customer_detail_returns_404_for_missing_or_inactive_customer(auth_client, seeded_user) -> None:
    inactive_customer = _create_customer(
        name="已停用客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.get(
        "/api/v1/customers/999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    inactive_response = auth_client.get(
        f"/api/v1/customers/{inactive_customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }
    assert inactive_response.status_code == 404
    assert inactive_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_tech_cannot_list_customers(auth_client) -> None:
    tech_user = _create_user(
        username="tech-user",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.get(
        "/api/v1/customers?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_dealer_cannot_list_customers(auth_client) -> None:
    dealer_user = _create_user(
        username="dealer-user",
        password="dealer-pass",
        full_name="发展商用户",
        role=UserRole.DEALER,
    )
    access_token = _login_and_get_access_token(auth_client, dealer_user["username"], dealer_user["password"])

    response = auth_client.get(
        "/api/v1/customers?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_client_cannot_get_customer_detail(auth_client, seeded_user) -> None:
    customer = _create_customer(name="客户详情样本", manager_id=seeded_user["id"])
    client_user = _create_user(
        username="client-user",
        password="client-pass",
        full_name="客户门户用户",
        role=UserRole.CLIENT,
    )
    access_token = _login_and_get_access_token(auth_client, client_user["username"], client_user["password"])

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_admin_can_create_customer(auth_client) -> None:
    manager = _create_user(
        username="post-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    admin = _create_user(
        username="post-admin-a",
        password="admin-pass",
        full_name="管理员A",
        role=UserRole.ADMIN,
    )
    access_token = _login_and_get_access_token(auth_client, admin["username"], admin["password"])

    response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新增客户A",
            "manager_id": manager["id"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": payload["data"]["id"],
            "name": "新增客户A",
            "manager_id": manager["id"],
        },
    }

    customer = _get_customer_by_id(payload["data"]["id"])
    assert customer is not None
    assert customer.name == "新增客户A"
    assert customer.manager_id == manager["id"]
    assert customer.is_active is True


def test_manager_can_create_customer_for_self(auth_client) -> None:
    manager = _create_user(
        username="post-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "经理自建客户"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": payload["data"]["id"],
            "name": "经理自建客户",
            "manager_id": manager["id"],
        },
    }

    customer = _get_customer_by_id(payload["data"]["id"])
    assert customer is not None
    assert customer.manager_id == manager["id"]
    assert customer.is_active is True


def test_manager_cannot_create_customer_for_other_manager(auth_client) -> None:
    manager = _create_user(
        username="post-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="post-manager-d",
        password="manager-pass",
        full_name="项目经理D",
        role=UserRole.MANAGER,
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "越权客户",
            "manager_id": other_manager["id"],
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_tech_cannot_create_customer(auth_client) -> None:
    tech_user = _create_user(
        username="post-tech-user",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "技术人员不能创建"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_create_customer_invalid_payload_returns_unified_400(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_name_response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"manager_id": seeded_user["id"]},
    )
    extra_field_response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "非法载荷客户",
            "unknown_field": "x",
        },
    )

    assert missing_name_response.status_code == 400
    assert missing_name_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }
    assert extra_field_response.status_code == 400
    assert extra_field_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_admin_cannot_create_customer_with_missing_manager_user(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "无效负责人客户",
            "manager_id": 999,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "客户负责人必须是有效的项目经理",
        "data": None,
    }


def test_admin_cannot_create_customer_with_non_manager_user(auth_client, seeded_user) -> None:
    tech_user = _create_user(
        username="post-invalid-tech-user",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "非经理负责人客户",
            "manager_id": tech_user["id"],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "客户负责人必须是有效的项目经理",
        "data": None,
    }


def test_admin_can_update_customer_name(auth_client, seeded_user) -> None:
    customer = _create_customer(name="旧客户名", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "新客户名"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": customer["id"],
            "name": "新客户名",
            "manager_id": seeded_user["id"],
        },
    }

    updated_customer = _get_customer_by_id(customer["id"])
    assert updated_customer is not None
    assert updated_customer.name == "新客户名"


def test_admin_can_update_customer_manager_id(auth_client, seeded_user) -> None:
    old_manager = _create_user(
        username="put-manager-old",
        password="manager-pass",
        full_name="旧经理",
        role=UserRole.MANAGER,
    )
    new_manager = _create_user(
        username="put-manager-new",
        password="manager-pass",
        full_name="新经理",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="可调经理客户", manager_id=old_manager["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"manager_id": new_manager["id"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": customer["id"],
            "name": "可调经理客户",
            "manager_id": new_manager["id"],
        },
    }

    updated_customer = _get_customer_by_id(customer["id"])
    assert updated_customer is not None
    assert updated_customer.manager_id == new_manager["id"]


def test_manager_can_update_owned_customer_name(auth_client) -> None:
    manager = _create_user(
        username="put-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理旧客户名", manager_id=manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "经理新客户名"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": customer["id"],
            "name": "经理新客户名",
            "manager_id": manager["id"],
        },
    }


def test_manager_cannot_update_other_managers_customer(auth_client) -> None:
    manager = _create_user(
        username="put-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="put-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "试图越权修改"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_manager_cannot_reassign_owned_customer_to_other_manager(auth_client) -> None:
    manager = _create_user(
        username="put-manager-d",
        password="manager-pass",
        full_name="项目经理D",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="put-manager-e",
        password="manager-pass",
        full_name="项目经理E",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理自有客户", manager_id=manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"manager_id": other_manager["id"]},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_tech_cannot_update_customer(auth_client, seeded_user) -> None:
    customer = _create_customer(name="非允许角色更新客户", manager_id=seeded_user["id"])
    tech_user = _create_user(
        username="put-tech-user",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "不应成功"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_update_customer_returns_404_for_missing_or_inactive_customer(auth_client, seeded_user) -> None:
    inactive_customer = _create_customer(
        name="已停用客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.put(
        "/api/v1/customers/999",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "不存在客户"},
    )
    inactive_response = auth_client.put(
        f"/api/v1/customers/{inactive_customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "停用客户"},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }
    assert inactive_response.status_code == 404
    assert inactive_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_update_customer_invalid_payload_returns_unified_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="待更新客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    invalid_name_response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": ""},
    )
    extra_field_response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"is_active": False},
    )

    assert invalid_name_response.status_code == 400
    assert invalid_name_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }
    assert extra_field_response.status_code == 400
    assert extra_field_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_update_customer_empty_payload_returns_unified_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="空更新客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_admin_cannot_update_customer_with_missing_manager_user(auth_client, seeded_user) -> None:
    customer = _create_customer(name="待更新负责人客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"manager_id": 999},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "客户负责人必须是有效的项目经理",
        "data": None,
    }


def test_admin_cannot_update_customer_with_non_manager_user(auth_client, seeded_user) -> None:
    customer = _create_customer(name="待更新非经理负责人客户", manager_id=seeded_user["id"])
    admin_user = _create_user(
        username="put-invalid-admin-user",
        password="admin-pass",
        full_name="管理员用户",
        role=UserRole.ADMIN,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"manager_id": admin_user["id"]},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "客户负责人必须是有效的项目经理",
        "data": None,
    }


def test_admin_can_soft_delete_customer(auth_client, seeded_user) -> None:
    customer = _create_customer(name="待删除客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }

    deleted_customer = _get_customer_by_id(customer["id"])
    assert deleted_customer is not None
    assert deleted_customer.is_active is False


def test_manager_can_delete_owned_customer(auth_client) -> None:
    manager = _create_user(
        username="delete-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理自有待删除客户", manager_id=manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }


def test_manager_cannot_delete_other_managers_customer(auth_client) -> None:
    manager = _create_user(
        username="delete-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="delete-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的待删除客户", manager_id=other_manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_tech_cannot_delete_customer(auth_client, seeded_user) -> None:
    customer = _create_customer(name="非允许角色删除客户", manager_id=seeded_user["id"])
    tech_user = _create_user(
        username="delete-tech-user",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_delete_customer_returns_404_for_missing_or_inactive_customer(auth_client, seeded_user) -> None:
    inactive_customer = _create_customer(
        name="已停用待删除客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.delete(
        "/api/v1/customers/999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    inactive_response = auth_client.delete(
        f"/api/v1/customers/{inactive_customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }
    assert inactive_response.status_code == 404
    assert inactive_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_deleted_customer_is_hidden_from_default_list(auth_client, seeded_user) -> None:
    customer = _create_customer(name="列表隐藏客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    list_response = auth_client.get(
        "/api/v1/customers?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert all(item["id"] != customer["id"] for item in list_response.json()["data"]["items"])


def test_deleted_customer_detail_returns_404(auth_client, seeded_user) -> None:
    customer = _create_customer(name="详情隐藏客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    detail_response = auth_client.get(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert detail_response.status_code == 404
    assert detail_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_deleted_customer_cannot_be_updated(auth_client, seeded_user) -> None:
    customer = _create_customer(name="删除后不可更新客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    update_response = auth_client.put(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "不应成功"},
    )

    assert delete_response.status_code == 200
    assert update_response.status_code == 404
    assert update_response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_delete_customer_requires_authentication(auth_client, seeded_user) -> None:
    customer = _create_customer(name="未登录删除客户", manager_id=seeded_user["id"])

    response = auth_client.delete(f"/api/v1/customers/{customer['id']}")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }


def test_client_cannot_delete_customer(auth_client, seeded_user) -> None:
    customer = _create_customer(name="客户角色不能删除", manager_id=seeded_user["id"])
    client_user = _create_user(
        username="delete-client-user",
        password="client-pass",
        full_name="客户门户用户",
        role=UserRole.CLIENT,
    )
    access_token = _login_and_get_access_token(auth_client, client_user["username"], client_user["password"])

    response = auth_client.delete(
        f"/api/v1/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }
