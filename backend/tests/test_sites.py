from sqlalchemy import text
import pytest

from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models import Customer, Site, User
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


def _create_site(
    *,
    customer_id: int,
    name: str,
    address: str,
    contact_name: str | None = None,
    contact_phone: str | None = None,
    remark: str | None = None,
    is_active: bool = True,
) -> dict[str, int | str | bool | None]:
    session = get_session_factory()()
    try:
        result = session.execute(
            text(
                """
                INSERT INTO sites (
                    customer_id,
                    name,
                    address,
                    contact_name,
                    contact_phone,
                    remark,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (
                    :customer_id,
                    :name,
                    :address,
                    :contact_name,
                    :contact_phone,
                    :remark,
                    :is_active,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                """
            ),
            {
                "customer_id": customer_id,
                "name": name,
                "address": address,
                "contact_name": contact_name,
                "contact_phone": contact_phone,
                "remark": remark,
                "is_active": is_active,
            },
        )
        session.commit()
        return {
            "id": result.lastrowid,
            "customer_id": customer_id,
            "name": name,
            "address": address,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "remark": remark,
            "is_active": is_active,
        }
    finally:
        session.close()


def _get_site_by_id(site_id: int) -> Site | None:
    session = get_session_factory()()
    try:
        return session.get(Site, site_id)
    finally:
        session.close()


def test_list_sites_requires_authentication(auth_client, seeded_user) -> None:
    customer = _create_customer(name="厂区客户", manager_id=seeded_user["id"])

    response = auth_client.get(f"/api/v1/customers/{customer['id']}/sites?page=1&page_size=20")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }


def test_admin_can_list_customer_sites_with_pagination(auth_client, seeded_user) -> None:
    customer = _create_customer(name="宝武钢铁", manager_id=seeded_user["id"])
    first_site = _create_site(
        customer_id=customer["id"],
        name="一号厂区",
        address="长沙市岳麓区厂区路1号",
        contact_name="张厂长",
        contact_phone="13800000101",
        remark="主厂区",
    )
    second_site = _create_site(
        customer_id=customer["id"],
        name="二号厂区",
        address="长沙市岳麓区厂区路2号",
        contact_name="李主管",
        contact_phone="13800000102",
    )
    _create_site(
        customer_id=customer["id"],
        name="已删除厂区",
        address="长沙市岳麓区厂区路3号",
        is_active=False,
    )

    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/sites?page=1&page_size=2",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "items": [
                {
                    "id": first_site["id"],
                    "customer_id": customer["id"],
                    "name": "一号厂区",
                    "address": "长沙市岳麓区厂区路1号",
                    "contact_name": "张厂长",
                    "contact_phone": "13800000101",
                    "remark": "主厂区",
                },
                {
                    "id": second_site["id"],
                    "customer_id": customer["id"],
                    "name": "二号厂区",
                    "address": "长沙市岳麓区厂区路2号",
                    "contact_name": "李主管",
                    "contact_phone": "13800000102",
                    "remark": None,
                },
            ],
            "total": 2,
            "page": 1,
            "page_size": 2,
        },
    }


def test_manager_can_list_sites_for_owned_customer_only(auth_client) -> None:
    manager = _create_user(
        username="site-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="我的客户", manager_id=manager["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="我的厂区",
        address="株洲市厂区一路",
    )

    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/sites?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "items": [
                {
                    "id": site["id"],
                    "customer_id": customer["id"],
                    "name": "我的厂区",
                    "address": "株洲市厂区一路",
                    "contact_name": None,
                    "contact_phone": None,
                    "remark": None,
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
        },
    }


def test_manager_cannot_list_sites_for_other_managers_customer(auth_client) -> None:
    manager = _create_user(
        username="site-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="site-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    _create_site(
        customer_id=customer["id"],
        name="隔离厂区",
        address="湘潭市厂区二路",
    )

    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/sites?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_forbidden_role_cannot_list_sites(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁用角色客户", manager_id=seeded_user["id"])
    tech_user = _create_user(
        username="site-tech-user",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/sites?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_list_sites_returns_404_for_missing_or_inactive_customer(auth_client, seeded_user) -> None:
    inactive_customer = _create_customer(
        name="停用客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.get(
        "/api/v1/customers/999/sites?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    inactive_response = auth_client.get(
        f"/api/v1/customers/{inactive_customer['id']}/sites?page=1&page_size=20",
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


def test_admin_can_create_site_for_active_customer(auth_client, seeded_user) -> None:
    customer = _create_customer(name="新增厂区客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "主厂区",
            "address": "长沙市岳麓区科技路1号",
            "contact_name": "张接口",
            "contact_phone": "13800000103",
            "remark": "主要维保厂区",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": payload["data"]["id"],
            "customer_id": customer["id"],
            "name": "主厂区",
            "address": "长沙市岳麓区科技路1号",
            "contact_name": "张接口",
            "contact_phone": "13800000103",
            "remark": "主要维保厂区",
        },
    }

    created = _get_site_by_id(payload["data"]["id"])
    assert created is not None
    assert created.is_active is True


def test_manager_can_create_site_for_owned_customer(auth_client) -> None:
    manager = _create_user(
        username="site-post-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理客户", manager_id=manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新厂区",
            "address": "株洲市天元区厂区大道8号",
            "contact_name": "李接口",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": response.json()["data"]["id"],
            "customer_id": customer["id"],
            "name": "新厂区",
            "address": "株洲市天元区厂区大道8号",
            "contact_name": "李接口",
            "contact_phone": None,
            "remark": None,
        },
    }


def test_manager_cannot_create_site_for_other_managers_customer(auth_client) -> None:
    manager = _create_user(
        username="site-post-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="site-post-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "越权厂区",
            "address": "湘潭市厂区大道1号",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_forbidden_role_cannot_create_site(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止新增厂区客户", manager_id=seeded_user["id"])
    tech_user = _create_user(
        username="site-post-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "禁用角色厂区",
            "address": "常德市厂区大道2号",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_create_site_invalid_payload_returns_unified_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="参数错误客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_address_response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "没地址厂区"},
    )
    invalid_field_response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "非法字段厂区",
            "address": "长沙市高新区1号",
            "is_active": False,
        },
    )

    assert missing_address_response.status_code == 400
    assert missing_address_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }
    assert invalid_field_response.status_code == 400
    assert invalid_field_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_create_site_rejects_duplicate_active_name_with_unified_business_error(auth_client, seeded_user) -> None:
    customer = _create_customer(name="名称重复客户", manager_id=seeded_user["id"])
    _create_site(
        customer_id=customer["id"],
        name="重名厂区",
        address="长沙市厂区一号",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "重名厂区",
            "address": "长沙市厂区二号",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "同一客户下厂区名称不允许重复",
        "data": None,
    }


def test_admin_can_update_site(auth_client, seeded_user) -> None:
    customer = _create_customer(name="更新厂区客户", manager_id=seeded_user["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="旧厂区",
        address="长沙市旧地址1号",
        contact_name="旧联系人",
        contact_phone="13800000104",
        remark="旧备注",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新厂区",
            "address": "长沙市新地址2号",
            "contact_name": "新联系人",
            "contact_phone": "13800000105",
            "remark": "新备注",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": site["id"],
            "customer_id": customer["id"],
            "name": "新厂区",
            "address": "长沙市新地址2号",
            "contact_name": "新联系人",
            "contact_phone": "13800000105",
            "remark": "新备注",
        },
    }


def test_manager_can_update_owned_customer_site(auth_client) -> None:
    manager = _create_user(
        username="site-put-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理客户", manager_id=manager["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="经理旧厂区",
        address="株洲市旧厂区一路",
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.put(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "经理新厂区",
            "remark": "仅更新部分字段",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": site["id"],
            "customer_id": customer["id"],
            "name": "经理新厂区",
            "address": "株洲市旧厂区一路",
            "contact_name": None,
            "contact_phone": None,
            "remark": "仅更新部分字段",
        },
    }


def test_manager_cannot_update_other_managers_site(auth_client) -> None:
    manager = _create_user(
        username="site-put-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="site-put-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="隔离厂区",
        address="湘潭市旧厂区一路",
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.put(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "越权修改厂区"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }


def test_forbidden_role_cannot_update_site(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止更新厂区客户", manager_id=seeded_user["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="禁止更新厂区",
        address="常德市旧厂区三路",
    )
    tech_user = _create_user(
        username="site-put-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.put(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "禁用角色修改"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_update_site_returns_404_for_missing_deleted_or_inactive_customer(auth_client, seeded_user) -> None:
    active_customer = _create_customer(name="活动客户", manager_id=seeded_user["id"])
    deleted_site = _create_site(
        customer_id=active_customer["id"],
        name="已删厂区",
        address="长沙市已删厂区一路",
        is_active=False,
    )
    inactive_customer = _create_customer(
        name="停用客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    inactive_customer_site = _create_site(
        customer_id=inactive_customer["id"],
        name="停用客户厂区",
        address="长沙市停用厂区一路",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.put(
        "/api/v1/sites/999",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "缺失厂区"},
    )
    deleted_response = auth_client.put(
        f"/api/v1/sites/{deleted_site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "已删厂区重命名"},
    )
    inactive_customer_response = auth_client.put(
        f"/api/v1/sites/{inactive_customer_site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "停用客户厂区重命名"},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }
    assert deleted_response.status_code == 404
    assert deleted_response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }
    assert inactive_customer_response.status_code == 404
    assert inactive_customer_response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }


def test_update_site_invalid_payload_returns_unified_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="非法更新字段客户", manager_id=seeded_user["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="待更新厂区",
        address="长沙市待更新一路",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    empty_payload_response = auth_client.put(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )
    invalid_field_response = auth_client.put(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新厂区名",
            "customer_id": 999,
        },
    )

    assert empty_payload_response.status_code == 400
    assert empty_payload_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }
    assert invalid_field_response.status_code == 400
    assert invalid_field_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_update_site_rejects_duplicate_active_name_with_unified_business_error(auth_client, seeded_user) -> None:
    customer = _create_customer(name="更新名称冲突客户", manager_id=seeded_user["id"])
    first_site = _create_site(
        customer_id=customer["id"],
        name="一号厂区",
        address="长沙市一号地址",
    )
    second_site = _create_site(
        customer_id=customer["id"],
        name="二号厂区",
        address="长沙市二号地址",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/sites/{second_site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": first_site["name"]},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "同一客户下厂区名称不允许重复",
        "data": None,
    }


def test_admin_can_soft_delete_site(auth_client, seeded_user) -> None:
    customer = _create_customer(name="删除厂区客户", manager_id=seeded_user["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="待删除厂区",
        address="长沙市待删除一路",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.delete(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }


def test_manager_can_delete_owned_customer_site(auth_client) -> None:
    manager = _create_user(
        username="site-delete-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理删除客户", manager_id=manager["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="经理待删厂区",
        address="株洲市删除厂区一路",
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.delete(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }


def test_manager_cannot_delete_other_managers_site(auth_client) -> None:
    manager = _create_user(
        username="site-delete-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="site-delete-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的删除客户", manager_id=other_manager["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="隔离删除厂区",
        address="湘潭市删除厂区一路",
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.delete(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }


def test_forbidden_role_cannot_delete_site(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止删除厂区客户", manager_id=seeded_user["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="禁止删除厂区",
        address="常德市删除厂区一路",
    )
    tech_user = _create_user(
        username="site-delete-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.delete(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_delete_site_returns_404_for_missing_deleted_or_inactive_customer(auth_client, seeded_user) -> None:
    active_customer = _create_customer(name="活动删除客户", manager_id=seeded_user["id"])
    deleted_site = _create_site(
        customer_id=active_customer["id"],
        name="已删厂区",
        address="长沙市已删厂区二路",
        is_active=False,
    )
    inactive_customer = _create_customer(
        name="停用删除客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    inactive_customer_site = _create_site(
        customer_id=inactive_customer["id"],
        name="停用客户厂区",
        address="长沙市停用删除一路",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.delete(
        "/api/v1/sites/999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    deleted_response = auth_client.delete(
        f"/api/v1/sites/{deleted_site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    inactive_customer_response = auth_client.delete(
        f"/api/v1/sites/{inactive_customer_site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }
    assert deleted_response.status_code == 404
    assert deleted_response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }
    assert inactive_customer_response.status_code == 404
    assert inactive_customer_response.json() == {
        "code": 404,
        "msg": "厂区不存在",
        "data": None,
    }


def test_soft_deleted_site_is_hidden_from_list_and_record_still_exists(auth_client, seeded_user) -> None:
    customer = _create_customer(name="删除后隐藏客户", manager_id=seeded_user["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="删除后隐藏厂区",
        address="长沙市隐藏厂区一路",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    list_response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/sites?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert all(item["id"] != site["id"] for item in list_response.json()["data"]["items"])
    deleted = _get_site_by_id(site["id"])
    assert deleted is not None
    assert deleted.is_active is False


def test_soft_deleted_site_allows_recreate_same_name(auth_client, seeded_user) -> None:
    customer = _create_customer(name="重建同名客户", manager_id=seeded_user["id"])
    site = _create_site(
        customer_id=customer["id"],
        name="可复用厂区名",
        address="长沙市老地址",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/sites/{site['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    recreate_response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/sites",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "可复用厂区名",
            "address": "长沙市新地址",
        },
    )

    assert delete_response.status_code == 200
    assert recreate_response.status_code == 200
    assert recreate_response.json()["data"]["name"] == "可复用厂区名"
    assert recreate_response.json()["data"]["address"] == "长沙市新地址"
