from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import pytest

from app.core.exceptions import ApiException
from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models import Contact, Customer, User
from app.models.enums import UserRole
from app.services.contact_service import ContactService


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


def _create_contact(
    *,
    customer_id: int,
    mobile: str,
    name: str | None = None,
    phone: str | None = None,
    position: str | None = None,
    is_primary: bool = False,
    remark: str | None = None,
    is_active: bool = True,
) -> dict[str, int | str | bool | None]:
    session = get_session_factory()()
    try:
        result = session.execute(
            text(
                """
                INSERT INTO contacts (
                    customer_id,
                    name,
                    mobile,
                    phone,
                    position,
                    is_primary,
                    remark,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (
                    :customer_id,
                    :name,
                    :mobile,
                    :phone,
                    :position,
                    :is_primary,
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
                "mobile": mobile,
                "phone": phone,
                "position": position,
                "is_primary": is_primary,
                "remark": remark,
                "is_active": is_active,
            },
        )
        session.commit()
        return {
            "id": result.lastrowid,
            "customer_id": customer_id,
            "name": name,
            "mobile": mobile,
            "phone": phone,
            "position": position,
            "is_primary": is_primary,
            "remark": remark,
            "is_active": is_active,
        }
    finally:
        session.close()


def _get_contact_by_id(contact_id: int) -> Contact | None:
    session = get_session_factory()()
    try:
        return session.get(Contact, contact_id)
    finally:
        session.close()


def test_list_contacts_requires_authentication(auth_client, seeded_user) -> None:
    customer = _create_customer(name="联系人客户", manager_id=seeded_user["id"])

    response = auth_client.get(f"/api/v1/customers/{customer['id']}/contacts?page=1&page_size=20")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }


def test_admin_can_list_customer_contacts_with_pagination(auth_client, seeded_user) -> None:
    customer = _create_customer(name="宝武钢铁", manager_id=seeded_user["id"])
    first_contact = _create_contact(
        customer_id=customer["id"],
        name="张厂长",
        mobile="13800000001",
        phone="0731-1001",
        position="厂长",
        is_primary=True,
        remark="总负责人",
    )
    second_contact = _create_contact(
        customer_id=customer["id"],
        name="李经理",
        mobile="13800000002",
        phone="0731-1002",
        position="设备经理",
        remark="设备接口人",
    )
    _create_contact(
        customer_id=customer["id"],
        name="已删除联系人",
        mobile="13800000003",
        is_active=False,
    )

    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/contacts?page=1&page_size=2",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "items": [
                {
                    "id": first_contact["id"],
                    "customer_id": customer["id"],
                    "name": "张厂长",
                    "mobile": "13800000001",
                    "phone": "0731-1001",
                    "position": "厂长",
                    "is_primary": True,
                    "remark": "总负责人",
                },
                {
                    "id": second_contact["id"],
                    "customer_id": customer["id"],
                    "name": "李经理",
                    "mobile": "13800000002",
                    "phone": "0731-1002",
                    "position": "设备经理",
                    "is_primary": False,
                    "remark": "设备接口人",
                },
            ],
            "total": 2,
            "page": 1,
            "page_size": 2,
        },
    }


def test_manager_can_list_contacts_for_owned_customer_only(auth_client) -> None:
    manager = _create_user(
        username="contact-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    own_customer = _create_customer(name="我的客户", manager_id=manager["id"])
    contact = _create_contact(
        customer_id=own_customer["id"],
        name="王主管",
        mobile="13800000011",
        position="主管",
    )

    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.get(
        f"/api/v1/customers/{own_customer['id']}/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "items": [
                {
                    "id": contact["id"],
                    "customer_id": own_customer["id"],
                    "name": "王主管",
                    "mobile": "13800000011",
                    "phone": None,
                    "position": "主管",
                    "is_primary": False,
                    "remark": None,
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
        },
    }


def test_manager_cannot_list_contacts_for_other_managers_customer(auth_client) -> None:
    manager = _create_user(
        username="contact-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="contact-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    other_customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    _create_contact(
        customer_id=other_customer["id"],
        name="隔离联系人",
        mobile="13800000021",
    )

    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.get(
        f"/api/v1/customers/{other_customer['id']}/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_list_contacts_returns_404_for_missing_or_inactive_customer(auth_client, seeded_user) -> None:
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
        "/api/v1/customers/999/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    inactive_response = auth_client.get(
        f"/api/v1/customers/{inactive_customer['id']}/contacts?page=1&page_size=20",
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


def test_list_contacts_excludes_soft_deleted_contacts(auth_client, seeded_user) -> None:
    customer = _create_customer(name="软删除客户", manager_id=seeded_user["id"])
    _create_contact(
        customer_id=customer["id"],
        name="有效联系人",
        mobile="13800000031",
    )
    _create_contact(
        customer_id=customer["id"],
        name="已软删除联系人",
        mobile="13800000032",
        is_active=False,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["total"] == 1
    assert len(response.json()["data"]["items"]) == 1
    assert response.json()["data"]["items"][0]["mobile"] == "13800000031"


def test_same_customer_cannot_have_two_primary_contacts(auth_client, seeded_user) -> None:
    customer = _create_customer(name="主联系人约束客户", manager_id=seeded_user["id"])
    _create_contact(
        customer_id=customer["id"],
        name="主联系人A",
        mobile="13800000041",
        is_primary=True,
    )

    with pytest.raises(IntegrityError):
        _create_contact(
            customer_id=customer["id"],
            name="主联系人B",
            mobile="13800000042",
            is_primary=True,
        )


def test_inactive_primary_contact_allows_new_primary_contact_via_orm(auth_client, seeded_user) -> None:
    customer = _create_customer(name="主联系人轮换客户", manager_id=seeded_user["id"])
    session = get_session_factory()()
    try:
        first_primary = Contact(
            customer_id=customer["id"],
            name="主联系人A",
            mobile="13800000051",
            is_primary=True,
            is_active=True,
        )
        session.add(first_primary)
        session.commit()
        session.refresh(first_primary)
        assert first_primary.active_primary_customer_id == customer["id"]

        first_primary.is_active = False
        session.add(first_primary)
        session.commit()
        session.refresh(first_primary)
        assert first_primary.active_primary_customer_id is None

        replacement_primary = Contact(
            customer_id=customer["id"],
            name="主联系人B",
            mobile="13800000052",
            is_primary=True,
            is_active=True,
        )
        session.add(replacement_primary)
        session.commit()
        session.refresh(replacement_primary)

        assert replacement_primary.active_primary_customer_id == customer["id"]
    finally:
        session.close()


def test_forbidden_role_cannot_list_contacts(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁用角色客户", manager_id=seeded_user["id"])
    tech_user = _create_user(
        username="contact-tech-user",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_contact_service_rejects_forbidden_role_without_router_guard(auth_client, seeded_user) -> None:
    customer = _create_customer(name="服务层收口客户", manager_id=seeded_user["id"])
    tech_user = _create_user(
        username="contact-service-tech",
        password="tech-pass",
        full_name="服务层工程师",
        role=UserRole.TECH,
    )

    session = get_session_factory()()
    try:
        current_user = session.get(User, tech_user["id"])
        assert current_user is not None

        service = ContactService(session)

        with pytest.raises(ApiException) as exc_info:
            service.list_page(
                customer_id=customer["id"],
                current_user=current_user,
                page=1,
                page_size=20,
            )

        assert exc_info.value.status_code == 403
        assert exc_info.value.message == "无权限"
    finally:
        session.close()


def test_admin_can_create_contact_for_active_customer(auth_client, seeded_user) -> None:
    customer = _create_customer(name="新增联系人客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "张接口",
            "mobile": "13800000061",
            "phone": "0731-2001",
            "position": "设备经理",
            "is_primary": True,
            "remark": "首要对接人",
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
            "name": "张接口",
            "mobile": "13800000061",
            "phone": "0731-2001",
            "position": "设备经理",
            "is_primary": True,
            "remark": "首要对接人",
        },
    }

    created = _get_contact_by_id(payload["data"]["id"])
    assert created is not None
    assert created.is_active is True


def test_manager_can_create_contact_for_owned_customer(auth_client) -> None:
    manager = _create_user(
        username="contact-post-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理客户", manager_id=manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "李接口",
            "mobile": "13800000062",
            "position": "主管",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": response.json()["data"]["id"],
            "customer_id": customer["id"],
            "name": "李接口",
            "mobile": "13800000062",
            "phone": None,
            "position": "主管",
            "is_primary": False,
            "remark": None,
        },
    }


def test_manager_cannot_create_contact_for_other_managers_customer(auth_client) -> None:
    manager = _create_user(
        username="contact-post-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="contact-post-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000063"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "客户不存在",
        "data": None,
    }


def test_forbidden_role_cannot_create_contact(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止新增联系人客户", manager_id=seeded_user["id"])
    tech_user = _create_user(
        username="contact-post-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000064"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_create_contact_missing_mobile_returns_unified_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="缺手机号客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "没手机号"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_create_contact_rejects_is_active_in_payload(auth_client, seeded_user) -> None:
    customer = _create_customer(name="非法字段客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "mobile": "13800000065",
            "is_active": False,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_create_contact_rejects_duplicate_mobile_with_unified_business_error(auth_client, seeded_user) -> None:
    customer = _create_customer(name="手机号重复客户", manager_id=seeded_user["id"])
    _create_contact(
        customer_id=customer["id"],
        name="旧联系人",
        mobile="13800000066",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新联系人",
            "mobile": "13800000066",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "同一客户下手机号不允许重复",
        "data": None,
    }


def test_create_contact_rejects_second_primary_with_unified_business_error(auth_client, seeded_user) -> None:
    customer = _create_customer(name="主联系人冲突客户", manager_id=seeded_user["id"])
    _create_contact(
        customer_id=customer["id"],
        name="旧主联系人",
        mobile="13800000067",
        is_primary=True,
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新主联系人",
            "mobile": "13800000068",
            "is_primary": True,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "同一客户最多只能有一个主联系人",
        "data": None,
    }


def test_created_contact_is_visible_in_list_and_active_by_default(auth_client, seeded_user) -> None:
    customer = _create_customer(name="新增后列表客户", manager_id=seeded_user["id"])
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    create_response = auth_client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": None,
            "mobile": "13800000069",
            "remark": "新增后应可见",
        },
    )
    list_response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 200
    created_id = create_response.json()["data"]["id"]
    created = _get_contact_by_id(created_id)
    assert created is not None
    assert created.is_active is True
    assert list_response.status_code == 200
    assert any(item["id"] == created_id for item in list_response.json()["data"]["items"])


def test_admin_can_update_contact(auth_client, seeded_user) -> None:
    customer = _create_customer(name="更新联系人客户", manager_id=seeded_user["id"])
    contact = _create_contact(
        customer_id=customer["id"],
        name="旧联系人",
        mobile="13800000071",
        phone="0731-3001",
        position="旧岗位",
        remark="旧备注",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新联系人",
            "mobile": "13800000072",
            "phone": "0731-3002",
            "position": "新岗位",
            "is_primary": True,
            "remark": "新备注",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": contact["id"],
            "customer_id": customer["id"],
            "name": "新联系人",
            "mobile": "13800000072",
            "phone": "0731-3002",
            "position": "新岗位",
            "is_primary": True,
            "remark": "新备注",
        },
    }


def test_manager_can_update_owned_customer_contact(auth_client) -> None:
    manager = _create_user(
        username="contact-put-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理客户", manager_id=manager["id"])
    contact = _create_contact(
        customer_id=customer["id"],
        name="经理旧联系人",
        mobile="13800000073",
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "经理新联系人",
            "mobile": "13800000074",
            "position": "主管",
            "is_primary": False,
            "remark": None,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {
            "id": contact["id"],
            "customer_id": customer["id"],
            "name": "经理新联系人",
            "mobile": "13800000074",
            "phone": None,
            "position": "主管",
            "is_primary": False,
            "remark": None,
        },
    }


def test_manager_cannot_update_other_managers_contact(auth_client) -> None:
    manager = _create_user(
        username="contact-put-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="contact-put-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000075")
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000076"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }


def test_forbidden_role_cannot_update_contact(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止更新联系人客户", manager_id=seeded_user["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000077")
    tech_user = _create_user(
        username="contact-put-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000078"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_update_contact_returns_404_for_missing_deleted_or_inactive_customer(auth_client, seeded_user) -> None:
    active_customer = _create_customer(name="活动客户", manager_id=seeded_user["id"])
    deleted_contact = _create_contact(
        customer_id=active_customer["id"],
        mobile="13800000079",
        is_active=False,
    )
    inactive_customer = _create_customer(
        name="停用客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    inactive_customer_contact = _create_contact(
        customer_id=inactive_customer["id"],
        mobile="13800000080",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.put(
        "/api/v1/contacts/999",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000081"},
    )
    deleted_response = auth_client.put(
        f"/api/v1/contacts/{deleted_contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000082"},
    )
    inactive_customer_response = auth_client.put(
        f"/api/v1/contacts/{inactive_customer_contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000083"},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }
    assert deleted_response.status_code == 404
    assert deleted_response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }
    assert inactive_customer_response.status_code == 404
    assert inactive_customer_response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }


def test_update_contact_rejects_customer_id_or_is_active_in_payload(auth_client, seeded_user) -> None:
    customer = _create_customer(name="非法更新字段客户", manager_id=seeded_user["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000084")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    customer_id_response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "mobile": "13800000085",
            "customer_id": 999,
        },
    )
    is_active_response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "mobile": "13800000086",
            "is_active": False,
        },
    )

    assert customer_id_response.status_code == 400
    assert customer_id_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }
    assert is_active_response.status_code == 400
    assert is_active_response.json() == {
        "code": 400,
        "msg": "参数错误",
        "data": None,
    }


def test_update_contact_rejects_duplicate_mobile_with_unified_business_error(auth_client, seeded_user) -> None:
    customer = _create_customer(name="更新手机号冲突客户", manager_id=seeded_user["id"])
    contact_a = _create_contact(customer_id=customer["id"], mobile="13800000087")
    contact_b = _create_contact(customer_id=customer["id"], mobile="13800000088")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/contacts/{contact_b['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": contact_a["mobile"]},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "同一客户下手机号不允许重复",
        "data": None,
    }


def test_update_contact_rejects_second_primary_with_unified_business_error(auth_client, seeded_user) -> None:
    customer = _create_customer(name="更新主联系人冲突客户", manager_id=seeded_user["id"])
    _create_contact(customer_id=customer["id"], mobile="13800000089", is_primary=True)
    second_contact = _create_contact(customer_id=customer["id"], mobile="13800000090", is_primary=False)
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.put(
        f"/api/v1/contacts/{second_contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "mobile": "13800000090",
            "is_primary": True,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "msg": "同一客户最多只能有一个主联系人",
        "data": None,
    }


def test_updated_contact_is_reflected_in_list(auth_client, seeded_user) -> None:
    customer = _create_customer(name="更新后列表客户", manager_id=seeded_user["id"])
    contact = _create_contact(
        customer_id=customer["id"],
        name="旧显示名",
        mobile="13800000091",
        position="旧岗位",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    update_response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "新显示名",
            "mobile": "13800000092",
            "position": "新岗位",
            "remark": "更新后可见",
        },
    )
    list_response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert update_response.status_code == 200
    assert list_response.status_code == 200
    assert any(
        item["id"] == contact["id"]
        and item["name"] == "新显示名"
        and item["mobile"] == "13800000092"
        and item["position"] == "新岗位"
        and item["remark"] == "更新后可见"
        for item in list_response.json()["data"]["items"]
    )


def test_admin_can_soft_delete_contact(auth_client, seeded_user) -> None:
    customer = _create_customer(name="删除联系人客户", manager_id=seeded_user["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000093")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.delete(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }


def test_manager_can_delete_owned_customer_contact(auth_client) -> None:
    manager = _create_user(
        username="contact-delete-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="经理删除客户", manager_id=manager["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000094")
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.delete(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }


def test_manager_cannot_delete_other_managers_contact(auth_client) -> None:
    manager = _create_user(
        username="contact-delete-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="contact-delete-manager-c",
        password="manager-pass",
        full_name="项目经理C",
        role=UserRole.MANAGER,
    )
    customer = _create_customer(name="别人的删除客户", manager_id=other_manager["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000095")
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    response = auth_client.delete(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }


def test_forbidden_role_cannot_delete_contact(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止删除联系人客户", manager_id=seeded_user["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000096")
    tech_user = _create_user(
        username="contact-delete-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    response = auth_client.delete(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": 403,
        "msg": "无权限",
        "data": None,
    }


def test_delete_contact_returns_404_for_missing_deleted_or_inactive_customer(auth_client, seeded_user) -> None:
    active_customer = _create_customer(name="活动删除客户", manager_id=seeded_user["id"])
    deleted_contact = _create_contact(
        customer_id=active_customer["id"],
        mobile="13800000097",
        is_active=False,
    )
    inactive_customer = _create_customer(
        name="停用删除客户",
        manager_id=seeded_user["id"],
        is_active=False,
    )
    inactive_customer_contact = _create_contact(
        customer_id=inactive_customer["id"],
        mobile="13800000098",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_response = auth_client.delete(
        "/api/v1/contacts/999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    deleted_response = auth_client.delete(
        f"/api/v1/contacts/{deleted_contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    inactive_customer_response = auth_client.delete(
        f"/api/v1/contacts/{inactive_customer_contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }
    assert deleted_response.status_code == 404
    assert deleted_response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }
    assert inactive_customer_response.status_code == 404
    assert inactive_customer_response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }


def test_deleted_contact_is_hidden_from_default_list(auth_client, seeded_user) -> None:
    customer = _create_customer(name="删除后隐藏客户", manager_id=seeded_user["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000099")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    list_response = auth_client.get(
        f"/api/v1/customers/{customer['id']}/contacts?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert all(item["id"] != contact["id"] for item in list_response.json()["data"]["items"])


def test_deleted_contact_cannot_be_updated(auth_client, seeded_user) -> None:
    customer = _create_customer(name="删除后不可更新客户", manager_id=seeded_user["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000100")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    update_response = auth_client.put(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"mobile": "13800000101"},
    )

    assert delete_response.status_code == 200
    assert update_response.status_code == 404
    assert update_response.json() == {
        "code": 404,
        "msg": "联系人不存在",
        "data": None,
    }


def test_soft_deleted_contact_record_still_exists_but_inactive(auth_client, seeded_user) -> None:
    customer = _create_customer(name="软删除记录客户", manager_id=seeded_user["id"])
    contact = _create_contact(customer_id=customer["id"], mobile="13800000102")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    response = auth_client.delete(
        f"/api/v1/contacts/{contact['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    deleted = _get_contact_by_id(contact["id"])
    assert deleted is not None
    assert deleted.is_active is False
