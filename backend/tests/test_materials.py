from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models import Material, User
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


def _create_material(
    *,
    name: str,
    specification: str = "380V/2.2kW",
    equipment_category: str = "电动葫芦",
    sale_price: float = 128.5,
    unit: str = "件",
    cost_price: float | None = 88.8,
    stock_qty: float | None = 12,
    min_stock_qty: float | None = 3,
    manufacturer: str | None = "湖南智造",
    remark: str | None = "基础物料",
    is_active: bool = True,
) -> dict[str, int | str | float | bool | None]:
    session = get_session_factory()()
    try:
        material = Material(
            name=name,
            specification=specification,
            equipment_category=equipment_category,
            sale_price=sale_price,
            unit=unit,
            cost_price=cost_price,
            stock_qty=stock_qty,
            min_stock_qty=min_stock_qty,
            manufacturer=manufacturer,
            remark=remark,
            is_active=is_active,
        )
        session.add(material)
        session.commit()
        session.refresh(material)
        return {
            "id": material.id,
            "system_no": material.system_no,
            "name": material.name,
            "specification": material.specification,
            "equipment_category": material.equipment_category,
            "sale_price": float(material.sale_price),
            "unit": material.unit,
            "cost_price": float(material.cost_price) if material.cost_price is not None else None,
            "stock_qty": float(material.stock_qty) if material.stock_qty is not None else None,
            "min_stock_qty": float(material.min_stock_qty) if material.min_stock_qty is not None else None,
            "manufacturer": material.manufacturer,
            "remark": material.remark,
            "is_active": material.is_active,
        }
    finally:
        session.close()


def _get_material_by_id(material_id: int) -> Material | None:
    session = get_session_factory()()
    try:
        return session.get(Material, material_id)
    finally:
        session.close()


def _material_create_payload() -> dict[str, object]:
    return {
        "name": "起升接触器",
        "specification": "CJX2-3210 220V",
        "equipment_category": "桥式起重机",
        "sale_price": 156.75,
        "unit": "件",
        "cost_price": 120.5,
        "stock_qty": 20,
        "min_stock_qty": 5,
        "manufacturer": "正泰",
        "remark": "常备件",
    }


def test_list_materials_requires_authentication(auth_client) -> None:
    response = auth_client.get("/api/v1/materials?page=1&page_size=20")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }


def test_forbidden_role_cannot_access_material_endpoints(auth_client) -> None:
    tech_user = _create_user(
        username="material-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    list_response = auth_client.get(
        "/api/v1/materials?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    create_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_material_create_payload(),
    )
    detail_response = auth_client.get(
        "/api/v1/materials/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    for response in (list_response, create_response, detail_response):
        assert response.status_code == 403
        assert response.json() == {
            "code": 403,
            "msg": "无权限",
            "data": None,
        }


def test_admin_happy_path_for_material_crud(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    create_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_material_create_payload(),
    )
    assert create_response.status_code == 200
    created_payload = create_response.json()["data"]
    material_id = created_payload["id"]
    assert created_payload["system_no"].startswith("MT-")
    assert created_payload == {
        "id": material_id,
        "system_no": created_payload["system_no"],
        "name": "起升接触器",
        "specification": "CJX2-3210 220V",
        "equipment_category": "桥式起重机",
        "sale_price": 156.75,
        "unit": "件",
        "cost_price": 120.5,
        "stock_qty": 20.0,
        "min_stock_qty": 5.0,
        "manufacturer": "正泰",
        "remark": "常备件",
    }

    list_response = auth_client.get(
        "/api/v1/materials?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1
    assert list_response.json()["data"]["items"][0] == created_payload

    detail_response = auth_client.get(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["data"] == created_payload

    update_response = auth_client.put(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "sale_price": 168.0,
            "stock_qty": 18,
            "remark": "调价后库存修正",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"] == {
        "id": material_id,
        "system_no": created_payload["system_no"],
        "name": "起升接触器",
        "specification": "CJX2-3210 220V",
        "equipment_category": "桥式起重机",
        "sale_price": 168.0,
        "unit": "件",
        "cost_price": 120.5,
        "stock_qty": 18.0,
        "min_stock_qty": 5.0,
        "manufacturer": "正泰",
        "remark": "调价后库存修正",
    }

    delete_response = auth_client.delete(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }

    material = _get_material_by_id(material_id)
    assert material is not None
    assert material.is_active is False


def test_manager_can_access_shared_materials(auth_client) -> None:
    manager = _create_user(
        username="material-manager",
        password="manager-pass",
        full_name="项目经理",
        role=UserRole.MANAGER,
    )
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    create_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_material_create_payload(),
    )
    assert create_response.status_code == 200
    material_id = create_response.json()["data"]["id"]

    list_response = auth_client.get(
        "/api/v1/materials?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    detail_response = auth_client.get(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    update_response = auth_client.put(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"manufacturer": "德力西"},
    )
    delete_response = auth_client.delete(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1
    assert list_response.json()["data"]["items"][0]["id"] == material_id
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["id"] == material_id
    assert update_response.status_code == 200
    assert update_response.json()["data"]["manufacturer"] == "德力西"
    assert delete_response.status_code == 200


def test_manager_can_access_shared_materials_created_by_admin_and_other_managers(
    auth_client,
    seeded_user,
) -> None:
    manager = _create_user(
        username="material-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="material-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    own_material = _create_material(name="我的物料")
    other_material = _create_material(name="别人的物料")
    admin_material = _create_material(name="管理员物料")

    manager_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])
    admin_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    manager_list_response = auth_client.get(
        "/api/v1/materials?page=1&page_size=20",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert manager_list_response.status_code == 200
    assert manager_list_response.json()["data"]["total"] == 3
    assert {item["id"] for item in manager_list_response.json()["data"]["items"]} == {
        own_material["id"],
        other_material["id"],
        admin_material["id"],
    }

    admin_list_response = auth_client.get(
        "/api/v1/materials?page=1&page_size=20",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_list_response.status_code == 200
    assert admin_list_response.json()["data"]["total"] == 3

    for target_id in (other_material["id"], admin_material["id"]):
        detail_response = auth_client.get(
            f"/api/v1/materials/{target_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        update_response = auth_client.put(
            f"/api/v1/materials/{target_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={"remark": "共享库修改"},
        )
        delete_response = auth_client.delete(
            f"/api/v1/materials/{target_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )

        assert detail_response.status_code == 200
        assert detail_response.json()["data"]["id"] == target_id
        assert update_response.status_code == 200
        assert update_response.json()["data"]["remark"] == "共享库修改"
        assert delete_response.status_code == 200
        assert delete_response.json() == {
            "code": 0,
            "msg": "ok",
            "data": {"deleted": True},
        }


def test_material_invalid_payload_returns_400(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    missing_required_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "缺字段物料"},
    )
    extra_field_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={**_material_create_payload(), "unknown_field": "x"},
    )
    invalid_number_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={**_material_create_payload(), "sale_price": -1},
    )

    create_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_material_create_payload(),
    )
    assert create_response.status_code == 200
    material_id = create_response.json()["data"]["id"]

    empty_update_response = auth_client.put(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )
    invalid_update_field_response = auth_client.put(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"is_active": False},
    )

    for response in (
        missing_required_response,
        extra_field_response,
        invalid_number_response,
        empty_update_response,
        invalid_update_field_response,
    ):
        assert response.status_code == 400
        assert response.json() == {
            "code": 400,
            "msg": "参数错误",
            "data": None,
        }


def test_material_detail_update_delete_return_404_for_missing_or_deleted(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    create_response = auth_client.post(
        "/api/v1/materials",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_material_create_payload(),
    )
    assert create_response.status_code == 200
    material_id = create_response.json()["data"]["id"]

    delete_response = auth_client.delete(
        f"/api/v1/materials/{material_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 200

    for target_id in (999, material_id):
        detail_response = auth_client.get(
            f"/api/v1/materials/{target_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        update_response = auth_client.put(
            f"/api/v1/materials/{target_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"remark": "不可访问"},
        )
        delete_again_response = auth_client.delete(
            f"/api/v1/materials/{target_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        for response in (detail_response, update_response, delete_again_response):
            assert response.status_code == 404
            assert response.json() == {
                "code": 404,
                "msg": "物料不存在",
                "data": None,
            }


def test_soft_deleted_material_is_hidden_from_default_list(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])
    visible_material = _create_material(name="可见物料")
    hidden_material = _create_material(name="待删除物料")

    delete_response = auth_client.delete(
        f"/api/v1/materials/{hidden_material['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    list_response = auth_client.get(
        "/api/v1/materials?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert list_response.status_code == 200
    ids = [item["id"] for item in list_response.json()["data"]["items"]]
    assert hidden_material["id"] not in ids
    assert visible_material["id"] in ids
