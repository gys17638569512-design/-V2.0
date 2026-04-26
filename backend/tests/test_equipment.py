from datetime import date

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models import Customer, Equipment, Site, User
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


def _create_customer(*, name: str, manager_id: int | None, is_active: bool = True) -> dict[str, int | str | bool | None]:
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
    is_active: bool = True,
) -> dict[str, int | str | bool]:
    session = get_session_factory()()
    try:
        site = Site(
            customer_id=customer_id,
            name=name,
            address=address,
            is_active=is_active,
        )
        session.add(site)
        session.commit()
        session.refresh(site)
        return {
            "id": site.id,
            "customer_id": site.customer_id,
            "name": site.name,
            "address": site.address,
            "is_active": site.is_active,
        }
    finally:
        session.close()


def _create_equipment(
    *,
    site_id: int,
    name: str,
    category: str = "桥式起重机",
    model: str = "QD50T",
    manufacturer: str | None = None,
    manufacture_date: date | None = None,
    factory_no: str | None = None,
    site_inner_no: str | None = None,
    owner_unit: str | None = None,
    use_unit: str | None = None,
    management_department: str | None = None,
    equipment_admin_name: str | None = None,
    equipment_admin_phone: str | None = None,
    workshop: str | None = None,
    track_no: str | None = None,
    location_detail: str | None = None,
    status: str | None = None,
    remark: str | None = None,
    is_active: bool = True,
) -> dict[str, int | str | bool | None]:
    session = get_session_factory()()
    try:
        equipment = Equipment(
            site_id=site_id,
            name=name,
            category=category,
            model=model,
            manufacturer=manufacturer,
            manufacture_date=manufacture_date,
            factory_no=factory_no,
            site_inner_no=site_inner_no,
            owner_unit=owner_unit,
            use_unit=use_unit,
            management_department=management_department,
            equipment_admin_name=equipment_admin_name,
            equipment_admin_phone=equipment_admin_phone,
            workshop=workshop,
            track_no=track_no,
            location_detail=location_detail,
            status=status,
            remark=remark,
            is_active=is_active,
        )
        session.add(equipment)
        session.commit()
        session.refresh(equipment)
        return {
            "id": equipment.id,
            "site_id": equipment.site_id,
            "system_no": equipment.system_no,
            "name": equipment.name,
            "category": equipment.category,
            "model": equipment.model,
            "manufacturer": equipment.manufacturer,
            "manufacture_date": equipment.manufacture_date.isoformat() if equipment.manufacture_date else None,
            "factory_no": equipment.factory_no,
            "site_inner_no": equipment.site_inner_no,
            "owner_unit": equipment.owner_unit,
            "use_unit": equipment.use_unit,
            "management_department": equipment.management_department,
            "equipment_admin_name": equipment.equipment_admin_name,
            "equipment_admin_phone": equipment.equipment_admin_phone,
            "workshop": equipment.workshop,
            "track_no": equipment.track_no,
            "location_detail": equipment.location_detail,
            "status": equipment.status,
            "remark": equipment.remark,
            "is_active": equipment.is_active,
        }
    finally:
        session.close()


def _get_equipment_by_id(equipment_id: int) -> Equipment | None:
    session = get_session_factory()()
    try:
        return session.get(Equipment, equipment_id)
    finally:
        session.close()


def _update_site_active(site_id: int, *, is_active: bool) -> None:
    session = get_session_factory()()
    try:
        site = session.get(Site, site_id)
        assert site is not None
        site.is_active = is_active
        session.add(site)
        session.commit()
    finally:
        session.close()


def _update_customer_active(customer_id: int, *, is_active: bool) -> None:
    session = get_session_factory()()
    try:
        customer = session.get(Customer, customer_id)
        assert customer is not None
        customer.is_active = is_active
        session.add(customer)
        session.commit()
    finally:
        session.close()


def _equipment_create_payload(site_id: int) -> dict[str, object]:
    return {
        "site_id": site_id,
        "name": "A2桥机",
        "category": "桥式起重机",
        "model": "QD50T",
        "manufacturer": "智造机械",
        "manufacture_date": "2024-01-15",
        "factory_no": "F-001",
        "site_inner_no": "N-001",
        "owner_unit": "宝武钢铁",
        "use_unit": "一炼钢",
        "management_department": "设备部",
        "equipment_admin_name": "张主管",
        "equipment_admin_phone": "13800001001",
        "workshop": "炼钢车间",
        "track_no": "TR-01",
        "location_detail": "跨一北侧",
        "status": "RUNNING",
        "remark": "首台设备",
    }


def _assert_equipment_payload_matches(payload: dict[str, object], expected: dict[str, object]) -> None:
    assert payload["id"] == expected["id"]
    assert payload["site_id"] == expected["site_id"]
    assert isinstance(payload["system_no"], str)
    assert payload["system_no"]
    assert payload["name"] == expected["name"]
    assert payload["category"] == expected["category"]
    assert payload["model"] == expected["model"]
    assert payload["manufacturer"] == expected["manufacturer"]
    assert payload["manufacture_date"] == expected["manufacture_date"]
    assert payload["factory_no"] == expected["factory_no"]
    assert payload["site_inner_no"] == expected["site_inner_no"]
    assert payload["owner_unit"] == expected["owner_unit"]
    assert payload["use_unit"] == expected["use_unit"]
    assert payload["management_department"] == expected["management_department"]
    assert payload["equipment_admin_name"] == expected["equipment_admin_name"]
    assert payload["equipment_admin_phone"] == expected["equipment_admin_phone"]
    assert payload["workshop"] == expected["workshop"]
    assert payload["track_no"] == expected["track_no"]
    assert payload["location_detail"] == expected["location_detail"]
    assert payload["status"] == expected["status"]
    assert payload["remark"] == expected["remark"]


def test_list_equipment_requires_authentication(auth_client, seeded_user) -> None:
    customer = _create_customer(name="设备客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="一号厂区", address="长沙市厂区路1号")
    _create_equipment(site_id=site["id"], name="设备A")

    response = auth_client.get("/api/v1/equipment?page=1&page_size=20")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }


def test_forbidden_role_cannot_access_equipment_endpoints(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止角色客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="一号厂区", address="株洲市厂区路1号")
    equipment = _create_equipment(site_id=site["id"], name="设备A")
    tech_user = _create_user(
        username="equipment-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    list_response = auth_client.get(
        "/api/v1/equipment?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    create_response = auth_client.post(
        "/api/v1/equipment",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_equipment_create_payload(site["id"]),
    )
    detail_response = auth_client.get(
        f"/api/v1/equipment/{equipment['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    for response in (list_response, create_response, detail_response):
        assert response.status_code == 403
        assert response.json() == {
            "code": 403,
            "msg": "无权限",
            "data": None,
        }


def test_admin_happy_path_for_equipment_crud(auth_client, seeded_user) -> None:
    customer = _create_customer(name="宝武钢铁", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="一号厂区", address="长沙市岳麓区厂区路1号")
    existing = _create_equipment(
        site_id=site["id"],
        name="先有设备",
        manufacturer="先有厂家",
        manufacture_date=date(2023, 5, 20),
        status="IDLE",
    )
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    list_response = auth_client.get(
        "/api/v1/equipment?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["code"] == 0
    assert list_response.json()["data"]["total"] == 1
    _assert_equipment_payload_matches(list_response.json()["data"]["items"][0], existing)

    create_response = auth_client.post(
        "/api/v1/equipment",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_equipment_create_payload(site["id"]),
    )
    assert create_response.status_code == 200
    created_payload = create_response.json()["data"]
    assert created_payload["system_no"]
    created_id = created_payload["id"]

    detail_response = auth_client.get(
        f"/api/v1/equipment/{created_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["id"] == created_id
    assert detail_response.json()["data"]["system_no"] == created_payload["system_no"]

    update_response = auth_client.put(
        f"/api/v1/equipment/{created_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "更新后设备",
            "manufacturer": "更新厂家",
            "status": "MAINTAINING",
            "remark": "更新备注",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["id"] == created_id
    assert update_response.json()["data"]["system_no"] == created_payload["system_no"]
    assert update_response.json()["data"]["name"] == "更新后设备"
    assert update_response.json()["data"]["manufacturer"] == "更新厂家"
    assert update_response.json()["data"]["status"] == "MAINTAINING"
    assert update_response.json()["data"]["remark"] == "更新备注"

    delete_response = auth_client.delete(
        f"/api/v1/equipment/{created_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }

    deleted = _get_equipment_by_id(created_id)
    assert deleted is not None
    assert deleted.is_active is False

    after_delete_list_response = auth_client.get(
        "/api/v1/equipment?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert after_delete_list_response.status_code == 200
    returned_ids = [item["id"] for item in after_delete_list_response.json()["data"]["items"]]
    assert created_id not in returned_ids
    assert existing["id"] in returned_ids


def test_manager_only_sees_owned_customer_equipment_and_cross_scope_returns_404(auth_client) -> None:
    manager = _create_user(
        username="equipment-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="equipment-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    own_customer = _create_customer(name="我的客户", manager_id=manager["id"])
    own_site = _create_site(customer_id=own_customer["id"], name="我的厂区", address="株洲市厂区一路")
    own_equipment = _create_equipment(site_id=own_site["id"], name="我的设备")
    other_customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    other_site = _create_site(customer_id=other_customer["id"], name="别人的厂区", address="湘潭市厂区二路")
    other_equipment = _create_equipment(site_id=other_site["id"], name="别人的设备")
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    list_response = auth_client.get(
        "/api/v1/equipment?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1
    assert list_response.json()["data"]["items"][0]["id"] == own_equipment["id"]

    detail_response = auth_client.get(
        f"/api/v1/equipment/{other_equipment['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    update_response = auth_client.put(
        f"/api/v1/equipment/{other_equipment['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "越权修改"},
    )
    delete_response = auth_client.delete(
        f"/api/v1/equipment/{other_equipment['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    for response in (detail_response, update_response, delete_response):
        assert response.status_code == 404
        assert response.json() == {
            "code": 404,
            "msg": "设备不存在",
            "data": None,
        }


def test_create_equipment_returns_404_for_missing_or_inactive_or_inaccessible_site(auth_client) -> None:
    manager = _create_user(
        username="equipment-create-manager",
        password="manager-pass",
        full_name="项目经理",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="equipment-create-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    own_customer = _create_customer(name="我的客户", manager_id=manager["id"])
    inactive_site = _create_site(customer_id=own_customer["id"], name="停用厂区", address="株洲市一路", is_active=False)
    inactive_customer = _create_customer(name="停用客户", manager_id=manager["id"], is_active=False)
    inactive_customer_site = _create_site(customer_id=inactive_customer["id"], name="停用客户厂区", address="株洲市二路")
    other_customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    other_site = _create_site(customer_id=other_customer["id"], name="别人的厂区", address="湘潭市一路")
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    for site_id in (999, inactive_site["id"], inactive_customer_site["id"], other_site["id"]):
        response = auth_client.post(
            "/api/v1/equipment",
            headers={"Authorization": f"Bearer {access_token}"},
            json=_equipment_create_payload(site_id),
        )
        assert response.status_code == 404
        assert response.json() == {
            "code": 404,
            "msg": "厂区不存在",
            "data": None,
        }


def test_create_equipment_invalid_payload_returns_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="参数错误客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="参数错误厂区", address="长沙市一路")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    missing_required_response = auth_client.post(
        "/api/v1/equipment",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"site_id": site["id"], "name": "缺必填"},
    )
    invalid_field_response = auth_client.post(
        "/api/v1/equipment",
        headers={"Authorization": f"Bearer {access_token}"},
        json={**_equipment_create_payload(site["id"]), "customer_id": 999},
    )

    for response in (missing_required_response, invalid_field_response):
        assert response.status_code == 400
        assert response.json() == {
            "code": 400,
            "msg": "参数错误",
            "data": None,
        }


def test_detail_update_delete_return_404_for_missing_deleted_inactive_site_or_customer(auth_client, seeded_user) -> None:
    active_customer = _create_customer(name="活动客户", manager_id=seeded_user["id"])
    active_site = _create_site(customer_id=active_customer["id"], name="活动厂区", address="长沙市一路")
    deleted_equipment = _create_equipment(site_id=active_site["id"], name="已删设备", is_active=False)

    inactive_site_customer = _create_customer(name="停用厂区客户", manager_id=seeded_user["id"])
    inactive_site = _create_site(customer_id=inactive_site_customer["id"], name="停用厂区", address="长沙市二路")
    inactive_site_equipment = _create_equipment(site_id=inactive_site["id"], name="停用厂区设备")
    _update_site_active(inactive_site["id"], is_active=False)

    inactive_customer = _create_customer(name="停用客户", manager_id=seeded_user["id"])
    inactive_customer_site = _create_site(customer_id=inactive_customer["id"], name="停用客户厂区", address="长沙市三路")
    inactive_customer_equipment = _create_equipment(site_id=inactive_customer_site["id"], name="停用客户设备")
    _update_customer_active(inactive_customer["id"], is_active=False)

    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    candidate_ids = [999, deleted_equipment["id"], inactive_site_equipment["id"], inactive_customer_equipment["id"]]

    for equipment_id in candidate_ids:
        detail_response = auth_client.get(
            f"/api/v1/equipment/{equipment_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        update_response = auth_client.put(
            f"/api/v1/equipment/{equipment_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"name": "不可访问"},
        )
        delete_response = auth_client.delete(
            f"/api/v1/equipment/{equipment_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        for response in (detail_response, update_response, delete_response):
            assert response.status_code == 404
            assert response.json() == {
                "code": 404,
                "msg": "设备不存在",
                "data": None,
            }


def test_update_equipment_invalid_payload_returns_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="更新参数客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="更新厂区", address="长沙市四路")
    equipment = _create_equipment(site_id=site["id"], name="待更新设备")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    empty_payload_response = auth_client.put(
        f"/api/v1/equipment/{equipment['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )
    invalid_field_response = auth_client.put(
        f"/api/v1/equipment/{equipment['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "非法字段更新", "is_active": False},
    )

    for response in (empty_payload_response, invalid_field_response):
        assert response.status_code == 400
        assert response.json() == {
            "code": 400,
            "msg": "参数错误",
            "data": None,
        }


def test_soft_deleted_equipment_is_hidden_from_default_list(auth_client, seeded_user) -> None:
    customer = _create_customer(name="软删除隐藏客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="软删除厂区", address="长沙市五路")
    visible_equipment = _create_equipment(site_id=site["id"], name="可见设备")
    hidden_equipment = _create_equipment(site_id=site["id"], name="待删除设备")
    access_token = _login_and_get_access_token(
        auth_client,
        seeded_user["username"],
        seeded_user["password"],
    )

    delete_response = auth_client.delete(
        f"/api/v1/equipment/{hidden_equipment['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    list_response = auth_client.get(
        "/api/v1/equipment?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert list_response.status_code == 200
    ids = [item["id"] for item in list_response.json()["data"]["items"]]
    assert hidden_equipment["id"] not in ids
    assert visible_equipment["id"] in ids
