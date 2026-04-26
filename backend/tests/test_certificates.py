from datetime import date

from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.core.exceptions import ApiException
from app.db.session import get_session_factory
from app.models import Customer, Equipment, EquipmentCertificate, Site, User
from app.models.enums import UserRole
from app.schemas.certificate import EquipmentCertificateCreateRequest, EquipmentCertificateUpdateRequest
from app.services.certificate_service import EquipmentCertificateService


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
    is_active: bool = True,
) -> dict[str, int | str | bool | None]:
    session = get_session_factory()()
    try:
        equipment = Equipment(
            site_id=site_id,
            name=name,
            category=category,
            model=model,
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
            "is_active": equipment.is_active,
        }
    finally:
        session.close()


def _update_equipment_active(equipment_id: int, *, is_active: bool) -> None:
    session = get_session_factory()()
    try:
        equipment = session.get(Equipment, equipment_id)
        assert equipment is not None
        equipment.is_active = is_active
        session.add(equipment)
        session.commit()
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


def _get_certificate_by_id(certificate_id: int) -> EquipmentCertificate | None:
    session = get_session_factory()()
    try:
        return session.get(EquipmentCertificate, certificate_id)
    finally:
        session.close()


def _certificate_create_payload(equipment_id: int) -> dict[str, object]:
    return {
        "equipment_id": equipment_id,
        "name": "特种设备使用登记证",
        "certificate_no": "CERT-2026-0001",
        "issuer": "长沙市市场监督管理局",
        "issued_date": "2024-06-01",
        "expiry_date": "2026-06-01",
        "remark": "首次建档",
    }


def test_list_certificates_requires_authentication(auth_client, seeded_user) -> None:
    response = auth_client.get("/api/v1/equipment-certificates?page=1&page_size=20")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "msg": "未授权",
        "data": None,
    }


def test_forbidden_role_cannot_access_certificate_endpoints(auth_client, seeded_user) -> None:
    customer = _create_customer(name="禁止角色客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="一号厂区", address="株洲市一路")
    equipment = _create_equipment(site_id=site["id"], name="设备A")
    tech_user = _create_user(
        username="certificate-tech",
        password="tech-pass",
        full_name="工程师用户",
        role=UserRole.TECH,
    )
    access_token = _login_and_get_access_token(auth_client, tech_user["username"], tech_user["password"])

    list_response = auth_client.get(
        "/api/v1/equipment-certificates?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    create_forbidden_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_certificate_create_payload(equipment["id"]),
    )
    detail_response = auth_client.get(
        "/api/v1/equipment-certificates/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    for response in (list_response, create_forbidden_response, detail_response):
        assert response.status_code == 403
        assert response.json() == {
            "code": 403,
            "msg": "无权限",
            "data": None,
        }


def test_admin_happy_path_for_certificate_crud(auth_client, seeded_user) -> None:
    customer = _create_customer(name="宝武钢铁", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="一号厂区", address="长沙市岳麓区厂区路1号")
    equipment = _create_equipment(site_id=site["id"], name="A2桥机")
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    create_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_certificate_create_payload(equipment["id"]),
    )
    assert create_response.status_code == 200
    created_payload = create_response.json()["data"]
    certificate_id = created_payload["id"]
    assert created_payload == {
        "id": certificate_id,
        "equipment_id": equipment["id"],
        "name": "特种设备使用登记证",
        "certificate_no": "CERT-2026-0001",
        "issuer": "长沙市市场监督管理局",
        "issued_date": "2024-06-01",
        "expiry_date": "2026-06-01",
        "remark": "首次建档",
    }

    list_response = auth_client.get(
        "/api/v1/equipment-certificates?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1
    assert list_response.json()["data"]["items"][0] == created_payload

    detail_response = auth_client.get(
        f"/api/v1/equipment-certificates/{certificate_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["data"] == created_payload

    update_response = auth_client.put(
        f"/api/v1/equipment-certificates/{certificate_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "起重机定期检验证",
            "issuer": "湖南省特检院",
            "expiry_date": "2027-06-01",
            "remark": "更新备注",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"] == {
        "id": certificate_id,
        "equipment_id": equipment["id"],
        "name": "起重机定期检验证",
        "certificate_no": "CERT-2026-0001",
        "issuer": "湖南省特检院",
        "issued_date": "2024-06-01",
        "expiry_date": "2027-06-01",
        "remark": "更新备注",
    }

    delete_response = auth_client.delete(
        f"/api/v1/equipment-certificates/{certificate_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "code": 0,
        "msg": "ok",
        "data": {"deleted": True},
    }

    after_delete_list_response = auth_client.get(
        "/api/v1/equipment-certificates?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert after_delete_list_response.status_code == 200
    assert after_delete_list_response.json()["data"]["total"] == 0
    assert after_delete_list_response.json()["data"]["items"] == []


def test_manager_only_sees_owned_customer_certificates_and_cross_scope_returns_404(auth_client) -> None:
    manager = _create_user(
        username="certificate-manager-a",
        password="manager-pass",
        full_name="项目经理A",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="certificate-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    own_customer = _create_customer(name="我的客户", manager_id=manager["id"])
    own_site = _create_site(customer_id=own_customer["id"], name="我的厂区", address="株洲市一路")
    own_equipment = _create_equipment(site_id=own_site["id"], name="我的设备")
    other_customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    other_site = _create_site(customer_id=other_customer["id"], name="别人的厂区", address="湘潭市一路")
    other_equipment = _create_equipment(site_id=other_site["id"], name="别人的设备")

    own_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])
    other_token = _login_and_get_access_token(auth_client, other_manager["username"], other_manager["password"])

    own_create_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {own_token}"},
        json=_certificate_create_payload(own_equipment["id"]),
    )
    assert own_create_response.status_code == 200

    other_create_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {other_token}"},
        json=_certificate_create_payload(other_equipment["id"]),
    )
    assert other_create_response.status_code == 200
    other_certificate_id = other_create_response.json()["data"]["id"]

    list_response = auth_client.get(
        "/api/v1/equipment-certificates?page=1&page_size=20",
        headers={"Authorization": f"Bearer {own_token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1
    assert list_response.json()["data"]["items"][0]["equipment_id"] == own_equipment["id"]

    detail_response = auth_client.get(
        f"/api/v1/equipment-certificates/{other_certificate_id}",
        headers={"Authorization": f"Bearer {own_token}"},
    )
    update_response = auth_client.put(
        f"/api/v1/equipment-certificates/{other_certificate_id}",
        headers={"Authorization": f"Bearer {own_token}"},
        json={"name": "越权修改"},
    )
    delete_response = auth_client.delete(
        f"/api/v1/equipment-certificates/{other_certificate_id}",
        headers={"Authorization": f"Bearer {own_token}"},
    )

    for response in (detail_response, update_response, delete_response):
        assert response.status_code == 404
        assert response.json() == {
            "code": 404,
            "msg": "设备证书不存在",
            "data": None,
        }


def test_create_certificate_returns_404_for_missing_inactive_or_inaccessible_equipment(auth_client) -> None:
    manager = _create_user(
        username="certificate-create-manager",
        password="manager-pass",
        full_name="项目经理",
        role=UserRole.MANAGER,
    )
    other_manager = _create_user(
        username="certificate-create-manager-b",
        password="manager-pass",
        full_name="项目经理B",
        role=UserRole.MANAGER,
    )
    own_customer = _create_customer(name="我的客户", manager_id=manager["id"])
    own_site = _create_site(customer_id=own_customer["id"], name="我的厂区", address="株洲市一路")
    inactive_equipment = _create_equipment(site_id=own_site["id"], name="停用设备")
    _update_equipment_active(inactive_equipment["id"], is_active=False)

    other_customer = _create_customer(name="别人的客户", manager_id=other_manager["id"])
    other_site = _create_site(customer_id=other_customer["id"], name="别人的厂区", address="湘潭市一路")
    other_equipment = _create_equipment(site_id=other_site["id"], name="别人的设备")
    access_token = _login_and_get_access_token(auth_client, manager["username"], manager["password"])

    for equipment_id in (999, inactive_equipment["id"], other_equipment["id"]):
        response = auth_client.post(
            "/api/v1/equipment-certificates",
            headers={"Authorization": f"Bearer {access_token}"},
            json=_certificate_create_payload(equipment_id),
        )
        assert response.status_code == 404
        assert response.json() == {
            "code": 404,
            "msg": "设备不存在",
            "data": None,
        }


def test_certificate_invalid_payload_returns_400(auth_client, seeded_user) -> None:
    customer = _create_customer(name="参数错误客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="参数错误厂区", address="长沙市一路")
    equipment = _create_equipment(site_id=site["id"], name="设备A")
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    create_missing_required_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"equipment_id": equipment["id"]},
    )
    create_invalid_field_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json={**_certificate_create_payload(equipment["id"]), "status": "EXTRA"},
    )

    create_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_certificate_create_payload(equipment["id"]),
    )
    assert create_response.status_code == 200
    certificate_id = create_response.json()["data"]["id"]

    update_empty_payload_response = auth_client.put(
        f"/api/v1/equipment-certificates/{certificate_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )
    update_invalid_field_response = auth_client.put(
        f"/api/v1/equipment-certificates/{certificate_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "更新证书", "is_active": False},
    )

    for response in (
        create_missing_required_response,
        create_invalid_field_response,
        update_empty_payload_response,
        update_invalid_field_response,
    ):
        assert response.status_code == 400
        assert response.json() == {
            "code": 400,
            "msg": "参数错误",
            "data": None,
        }


def test_certificate_detail_update_delete_return_404_for_missing_or_deleted(auth_client, seeded_user) -> None:
    customer = _create_customer(name="活动客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="活动厂区", address="长沙市一路")
    equipment = _create_equipment(site_id=site["id"], name="设备A")
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    create_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_certificate_create_payload(equipment["id"]),
    )
    assert create_response.status_code == 200
    certificate_id = create_response.json()["data"]["id"]

    delete_response = auth_client.delete(
        f"/api/v1/equipment-certificates/{certificate_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 200

    for target_id in (999, certificate_id):
        detail_response = auth_client.get(
            f"/api/v1/equipment-certificates/{target_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        update_response = auth_client.put(
            f"/api/v1/equipment-certificates/{target_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"name": "不可访问"},
        )
        delete_again_response = auth_client.delete(
            f"/api/v1/equipment-certificates/{target_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        for response in (detail_response, update_response, delete_again_response):
            assert response.status_code == 404
            assert response.json() == {
                "code": 404,
                "msg": "设备证书不存在",
                "data": None,
            }


def test_soft_deleted_certificate_is_hidden_from_default_list(auth_client, seeded_user) -> None:
    customer = _create_customer(name="软删除隐藏客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="软删除厂区", address="长沙市五路")
    equipment = _create_equipment(site_id=site["id"], name="设备A")
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    visible_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "equipment_id": equipment["id"],
            "name": "可见证书",
            "certificate_no": "VISIBLE-001",
            "issuer": "发证单位A",
            "issued_date": "2024-01-01",
            "expiry_date": "2026-01-01",
        },
    )
    hidden_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "equipment_id": equipment["id"],
            "name": "待删除证书",
            "certificate_no": "HIDDEN-001",
            "issuer": "发证单位B",
            "issued_date": "2024-02-01",
            "expiry_date": "2026-02-01",
        },
    )
    assert visible_response.status_code == 200
    assert hidden_response.status_code == 200
    hidden_id = hidden_response.json()["data"]["id"]
    visible_id = visible_response.json()["data"]["id"]

    delete_response = auth_client.delete(
        f"/api/v1/equipment-certificates/{hidden_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    list_response = auth_client.get(
        "/api/v1/equipment-certificates?page=1&page_size=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    assert list_response.status_code == 200
    ids = [item["id"] for item in list_response.json()["data"]["items"]]
    assert hidden_id not in ids
    assert visible_id in ids


def test_soft_deleted_certificate_row_still_exists_but_inactive(auth_client, seeded_user) -> None:
    customer = _create_customer(name="软删除保留客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="软删除保留厂区", address="长沙市六路")
    equipment = _create_equipment(site_id=site["id"], name="设备A")
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    create_response = auth_client.post(
        "/api/v1/equipment-certificates",
        headers={"Authorization": f"Bearer {access_token}"},
        json=_certificate_create_payload(equipment["id"]),
    )
    assert create_response.status_code == 200
    certificate_id = create_response.json()["data"]["id"]

    delete_response = auth_client.delete(
        f"/api/v1/equipment-certificates/{certificate_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 200
    certificate = _get_certificate_by_id(certificate_id)
    assert certificate is not None
    assert certificate.is_active is False


def test_certificate_becomes_inaccessible_when_parent_chain_is_inactive(auth_client, seeded_user) -> None:
    access_token = _login_and_get_access_token(auth_client, seeded_user["username"], seeded_user["password"])

    scenarios = []
    for suffix in ("equipment", "site", "customer"):
        customer = _create_customer(name=f"上游失活客户-{suffix}", manager_id=seeded_user["id"])
        site = _create_site(customer_id=customer["id"], name=f"上游失活厂区-{suffix}", address="长沙市七路")
        equipment = _create_equipment(site_id=site["id"], name=f"设备-{suffix}")
        create_response = auth_client.post(
            "/api/v1/equipment-certificates",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "equipment_id": equipment["id"],
                "name": f"证书-{suffix}",
                "certificate_no": f"CERT-{suffix}",
                "issuer": "发证单位",
                "issued_date": "2024-03-01",
                "expiry_date": "2026-03-01",
            },
        )
        assert create_response.status_code == 200
        scenarios.append(
            {
                "customer_id": customer["id"],
                "site_id": site["id"],
                "equipment_id": equipment["id"],
                "certificate_id": create_response.json()["data"]["id"],
                "suffix": suffix,
            }
        )

    _update_equipment_active(scenarios[0]["equipment_id"], is_active=False)
    _update_site_active(scenarios[1]["site_id"], is_active=False)
    _update_customer_active(scenarios[2]["customer_id"], is_active=False)

    list_response = auth_client.get(
        "/api/v1/equipment-certificates?page=1&page_size=50",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert list_response.status_code == 200
    returned_ids = {item["id"] for item in list_response.json()["data"]["items"]}

    for scenario in scenarios:
        certificate_id = scenario["certificate_id"]
        detail_response = auth_client.get(
            f"/api/v1/equipment-certificates/{certificate_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        update_response = auth_client.put(
            f"/api/v1/equipment-certificates/{certificate_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"remark": "上游失活后不可访问"},
        )
        delete_response = auth_client.delete(
            f"/api/v1/equipment-certificates/{certificate_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        for response in (detail_response, update_response, delete_response):
            assert response.status_code == 404
            assert response.json() == {
                "code": 404,
                "msg": "设备证书不存在",
                "data": None,
            }

        assert certificate_id not in returned_ids


def test_certificate_service_translates_integrity_errors_to_unified_400(auth_client, seeded_user) -> None:
    class FailingCertificateRepository:
        def create(self, session, *, certificate):
            raise IntegrityError("insert", {}, Exception("duplicate"))

        def update(self, session, *, certificate):
            raise IntegrityError("update", {}, Exception("duplicate"))

        def get_by_id(self, session, certificate_id, *, manager_id):
            return session.get(EquipmentCertificate, certificate_id)

        def delete(self, session, *, certificate):
            return certificate

        def list_page(self, session, *, manager_id, equipment_id, page, page_size):
            return [], 0

    customer = _create_customer(name="异常兜底客户", manager_id=seeded_user["id"])
    site = _create_site(customer_id=customer["id"], name="异常兜底厂区", address="长沙市八路")
    equipment = _create_equipment(site_id=site["id"], name="设备A")
    session = get_session_factory()()
    try:
        current_user = session.get(User, seeded_user["id"])
        assert current_user is not None
        service = EquipmentCertificateService(
            session,
            repository=FailingCertificateRepository(),
        )

        try:
            service.create(
                payload=EquipmentCertificateCreateRequest(**_certificate_create_payload(equipment["id"])),
                current_user=current_user,
            )
            raise AssertionError("expected create to raise ApiException")
        except ApiException as exc:
            assert exc.status_code == 400
            assert exc.message == "设备证书数据冲突"

        real_create_response = EquipmentCertificateService(session).create(
            payload=EquipmentCertificateCreateRequest(**_certificate_create_payload(equipment["id"])),
            current_user=current_user,
        )
        try:
            service.update(
                certificate_id=real_create_response.id,
                payload=EquipmentCertificateUpdateRequest(name="更新证书"),
                current_user=current_user,
            )
            raise AssertionError("expected update to raise ApiException")
        except ApiException as exc:
            assert exc.status_code == 400
            assert exc.message == "设备证书数据冲突"
    finally:
        session.close()
