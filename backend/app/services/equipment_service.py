from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ApiException
from app.models import Equipment, User, UserRole
from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.common import PagePayload
from app.schemas.equipment import (
    EquipmentCreateRequest,
    EquipmentDeletePayload,
    EquipmentPayload,
    EquipmentUpdateRequest,
)


class EquipmentService:
    def __init__(
        self,
        session: Session,
        repository: EquipmentRepository | None = None,
        site_repository: SiteRepository | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or EquipmentRepository()
        self.site_repository = site_repository or SiteRepository()

    def list_page(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        site_id: int | None = None,
    ) -> PagePayload[EquipmentPayload]:
        manager_scope = self._resolve_manager_scope(current_user)
        items, total = self.repository.list_page(
            self.session,
            manager_id=manager_scope,
            site_id=site_id,
            page=page,
            page_size=page_size,
        )
        return PagePayload(
            items=[self._to_payload(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_detail(self, *, equipment_id: int, current_user: User) -> EquipmentPayload:
        equipment = self._get_equipment_or_404(
            equipment_id=equipment_id,
            current_user=current_user,
        )
        return self._to_payload(equipment)

    def create(self, *, payload: EquipmentCreateRequest, current_user: User) -> EquipmentPayload:
        site = self._get_site_or_404(
            site_id=payload.site_id,
            current_user=current_user,
        )
        equipment = Equipment(
            site_id=site.id,
            name=payload.name,
            category=payload.category,
            model=payload.model,
            manufacturer=payload.manufacturer,
            manufacture_date=payload.manufacture_date,
            factory_no=payload.factory_no,
            site_inner_no=payload.site_inner_no,
            owner_unit=payload.owner_unit,
            use_unit=payload.use_unit,
            management_department=payload.management_department,
            equipment_admin_name=payload.equipment_admin_name,
            equipment_admin_phone=payload.equipment_admin_phone,
            workshop=payload.workshop,
            track_no=payload.track_no,
            location_detail=payload.location_detail,
            status=payload.status,
            remark=payload.remark,
            is_active=True,
        )
        try:
            created = self.repository.create(self.session, equipment=equipment)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc
        return self._to_payload(created)

    def update(
        self,
        *,
        equipment_id: int,
        payload: EquipmentUpdateRequest,
        current_user: User,
    ) -> EquipmentPayload:
        equipment = self._get_equipment_or_404(
            equipment_id=equipment_id,
            current_user=current_user,
        )
        updates = payload.model_dump(exclude_unset=True)

        if "site_id" in updates:
            site = self._get_site_or_404(
                site_id=updates["site_id"],
                current_user=current_user,
            )
            equipment.site_id = site.id
        if "name" in updates:
            equipment.name = updates["name"]
        if "category" in updates:
            equipment.category = updates["category"]
        if "model" in updates:
            equipment.model = updates["model"]
        if "manufacturer" in updates:
            equipment.manufacturer = updates["manufacturer"]
        if "manufacture_date" in updates:
            equipment.manufacture_date = updates["manufacture_date"]
        if "factory_no" in updates:
            equipment.factory_no = updates["factory_no"]
        if "site_inner_no" in updates:
            equipment.site_inner_no = updates["site_inner_no"]
        if "owner_unit" in updates:
            equipment.owner_unit = updates["owner_unit"]
        if "use_unit" in updates:
            equipment.use_unit = updates["use_unit"]
        if "management_department" in updates:
            equipment.management_department = updates["management_department"]
        if "equipment_admin_name" in updates:
            equipment.equipment_admin_name = updates["equipment_admin_name"]
        if "equipment_admin_phone" in updates:
            equipment.equipment_admin_phone = updates["equipment_admin_phone"]
        if "workshop" in updates:
            equipment.workshop = updates["workshop"]
        if "track_no" in updates:
            equipment.track_no = updates["track_no"]
        if "location_detail" in updates:
            equipment.location_detail = updates["location_detail"]
        if "status" in updates:
            equipment.status = updates["status"]
        if "remark" in updates:
            equipment.remark = updates["remark"]

        try:
            updated = self.repository.update(self.session, equipment=equipment)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc
        return self._to_payload(updated)

    def delete(self, *, equipment_id: int, current_user: User) -> EquipmentDeletePayload:
        equipment = self._get_equipment_or_404(
            equipment_id=equipment_id,
            current_user=current_user,
        )
        self.repository.delete(self.session, equipment=equipment)
        return EquipmentDeletePayload(deleted=True)

    def _resolve_manager_scope(self, current_user: User) -> int | None:
        if current_user.role in {UserRole.SUPER_ADMIN, UserRole.ADMIN}:
            return None
        if current_user.role == UserRole.MANAGER:
            return current_user.id
        raise ApiException(403, "无权限")

    def _get_site_or_404(self, *, site_id: int, current_user: User):
        manager_scope = self._resolve_manager_scope(current_user)
        site = self.site_repository.get_by_id(
            self.session,
            site_id,
            manager_id=manager_scope,
        )
        if site is None:
            raise ApiException(404, "厂区不存在")
        return site

    def _get_equipment_or_404(self, *, equipment_id: int, current_user: User) -> Equipment:
        manager_scope = self._resolve_manager_scope(current_user)
        equipment = self.repository.get_by_id(
            self.session,
            equipment_id,
            manager_id=manager_scope,
        )
        if equipment is None:
            raise ApiException(404, "设备不存在")
        return equipment

    def _translate_integrity_error(self, exc: IntegrityError) -> ApiException:
        message = str(exc.orig)
        if "equipment.system_no" in message or "uq_equipment_system_no" in message:
            return ApiException(400, "设备系统编号冲突")
        raise ApiException(400, "设备数据冲突")

    def _to_payload(self, equipment: Equipment) -> EquipmentPayload:
        return EquipmentPayload(
            id=equipment.id,
            site_id=equipment.site_id,
            system_no=equipment.system_no,
            name=equipment.name,
            category=equipment.category,
            model=equipment.model,
            manufacturer=equipment.manufacturer,
            manufacture_date=equipment.manufacture_date,
            factory_no=equipment.factory_no,
            site_inner_no=equipment.site_inner_no,
            owner_unit=equipment.owner_unit,
            use_unit=equipment.use_unit,
            management_department=equipment.management_department,
            equipment_admin_name=equipment.equipment_admin_name,
            equipment_admin_phone=equipment.equipment_admin_phone,
            workshop=equipment.workshop,
            track_no=equipment.track_no,
            location_detail=equipment.location_detail,
            status=equipment.status,
            remark=equipment.remark,
        )
