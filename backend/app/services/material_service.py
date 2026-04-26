from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ApiException
from app.models import Material, User, UserRole
from app.repositories.material_repository import MaterialRepository
from app.schemas.common import PagePayload
from app.schemas.material import (
    MaterialCreateRequest,
    MaterialDeletePayload,
    MaterialPayload,
    MaterialUpdateRequest,
)


class MaterialService:
    def __init__(
        self,
        session: Session,
        repository: MaterialRepository | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or MaterialRepository()

    def list_page(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
    ) -> PagePayload[MaterialPayload]:
        self._ensure_shared_material_access(current_user)
        items, total = self.repository.list_page(
            self.session,
            page=page,
            page_size=page_size,
        )
        return PagePayload(
            items=[self._to_payload(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_detail(self, *, material_id: int, current_user: User) -> MaterialPayload:
        material = self._get_material_or_404(material_id=material_id, current_user=current_user)
        return self._to_payload(material)

    def create(self, *, payload: MaterialCreateRequest, current_user: User) -> MaterialPayload:
        self._ensure_shared_material_access(current_user)
        material = Material(
            name=payload.name,
            specification=payload.specification,
            equipment_category=payload.equipment_category,
            sale_price=payload.sale_price,
            unit=payload.unit,
            cost_price=payload.cost_price,
            stock_qty=payload.stock_qty,
            min_stock_qty=payload.min_stock_qty,
            manufacturer=payload.manufacturer,
            remark=payload.remark,
            is_active=True,
        )
        try:
            created = self.repository.create(self.session, material=material)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc
        return self._to_payload(created)

    def update(
        self,
        *,
        material_id: int,
        payload: MaterialUpdateRequest,
        current_user: User,
    ) -> MaterialPayload:
        self._ensure_shared_material_access(current_user)
        material = self._get_material_or_404(material_id=material_id, current_user=current_user)
        updates = payload.model_dump(exclude_unset=True)

        if "name" in updates:
            material.name = updates["name"]
        if "specification" in updates:
            material.specification = updates["specification"]
        if "equipment_category" in updates:
            material.equipment_category = updates["equipment_category"]
        if "sale_price" in updates:
            material.sale_price = updates["sale_price"]
        if "unit" in updates:
            material.unit = updates["unit"]
        if "cost_price" in updates:
            material.cost_price = updates["cost_price"]
        if "stock_qty" in updates:
            material.stock_qty = updates["stock_qty"]
        if "min_stock_qty" in updates:
            material.min_stock_qty = updates["min_stock_qty"]
        if "manufacturer" in updates:
            material.manufacturer = updates["manufacturer"]
        if "remark" in updates:
            material.remark = updates["remark"]

        try:
            updated = self.repository.update(self.session, material=material)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc
        return self._to_payload(updated)

    def delete(self, *, material_id: int, current_user: User) -> MaterialDeletePayload:
        self._ensure_shared_material_access(current_user)
        material = self._get_material_or_404(material_id=material_id, current_user=current_user)
        self.repository.delete(self.session, material=material)
        return MaterialDeletePayload(deleted=True)

    def _ensure_shared_material_access(self, current_user: User) -> None:
        if current_user.role not in {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER}:
            raise ApiException(403, "无权限")

    def _get_material_or_404(self, *, material_id: int, current_user: User) -> Material:
        self._ensure_shared_material_access(current_user)
        material = self.repository.get_by_id(
            self.session,
            material_id,
        )
        if material is None:
            raise ApiException(404, "物料不存在")
        return material

    def _translate_integrity_error(self, exc: IntegrityError) -> ApiException:
        message = str(exc.orig)
        if "materials.system_no" in message or "uq_materials_system_no" in message:
            return ApiException(400, "物料系统编号冲突")
        raise ApiException(400, "物料数据冲突")

    def _to_payload(self, material: Material) -> MaterialPayload:
        return MaterialPayload(
            id=material.id,
            system_no=material.system_no,
            name=material.name,
            specification=material.specification,
            equipment_category=material.equipment_category,
            sale_price=self._decimal_to_float(material.sale_price),
            unit=material.unit,
            cost_price=self._decimal_to_float(material.cost_price),
            stock_qty=self._decimal_to_float(material.stock_qty),
            min_stock_qty=self._decimal_to_float(material.min_stock_qty),
            manufacturer=material.manufacturer,
            remark=material.remark,
        )

    def _decimal_to_float(self, value: Decimal | float | None) -> float | None:
        if value is None:
            return None
        return float(value)
