from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ApiException
from app.models import Equipment, EquipmentCertificate, User, UserRole
from app.repositories.certificate_repository import EquipmentCertificateRepository
from app.repositories.equipment_repository import EquipmentRepository
from app.schemas.certificate import (
    EquipmentCertificateCreateRequest,
    EquipmentCertificateDeletePayload,
    EquipmentCertificatePayload,
    EquipmentCertificateUpdateRequest,
)
from app.schemas.common import PagePayload


class EquipmentCertificateService:
    def __init__(
        self,
        session: Session,
        repository: EquipmentCertificateRepository | None = None,
        equipment_repository: EquipmentRepository | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or EquipmentCertificateRepository()
        self.equipment_repository = equipment_repository or EquipmentRepository()

    def list_page(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        equipment_id: int | None = None,
    ) -> PagePayload[EquipmentCertificatePayload]:
        manager_scope = self._resolve_manager_scope(current_user)
        items, total = self.repository.list_page(
            self.session,
            manager_id=manager_scope,
            equipment_id=equipment_id,
            page=page,
            page_size=page_size,
        )
        return PagePayload(
            items=[self._to_payload(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_detail(self, *, certificate_id: int, current_user: User) -> EquipmentCertificatePayload:
        certificate = self._get_certificate_or_404(
            certificate_id=certificate_id,
            current_user=current_user,
        )
        return self._to_payload(certificate)

    def create(
        self,
        *,
        payload: EquipmentCertificateCreateRequest,
        current_user: User,
    ) -> EquipmentCertificatePayload:
        equipment = self._get_equipment_or_404(
            equipment_id=payload.equipment_id,
            current_user=current_user,
        )
        certificate = EquipmentCertificate(
            equipment_id=equipment.id,
            name=payload.name,
            certificate_no=payload.certificate_no,
            issuer=payload.issuer,
            issued_date=payload.issued_date,
            expiry_date=payload.expiry_date,
            remark=payload.remark,
            is_active=True,
        )
        try:
            created = self.repository.create(self.session, certificate=certificate)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc
        return self._to_payload(created)

    def update(
        self,
        *,
        certificate_id: int,
        payload: EquipmentCertificateUpdateRequest,
        current_user: User,
    ) -> EquipmentCertificatePayload:
        certificate = self._get_certificate_or_404(
            certificate_id=certificate_id,
            current_user=current_user,
        )
        updates = payload.model_dump(exclude_unset=True)

        if "equipment_id" in updates:
            equipment = self._get_equipment_or_404(
                equipment_id=updates["equipment_id"],
                current_user=current_user,
            )
            certificate.equipment_id = equipment.id
        if "name" in updates:
            certificate.name = updates["name"]
        if "certificate_no" in updates:
            certificate.certificate_no = updates["certificate_no"]
        if "issuer" in updates:
            certificate.issuer = updates["issuer"]
        if "issued_date" in updates:
            certificate.issued_date = updates["issued_date"]
        if "expiry_date" in updates:
            certificate.expiry_date = updates["expiry_date"]
        if "remark" in updates:
            certificate.remark = updates["remark"]

        try:
            updated = self.repository.update(self.session, certificate=certificate)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc
        return self._to_payload(updated)

    def delete(self, *, certificate_id: int, current_user: User) -> EquipmentCertificateDeletePayload:
        certificate = self._get_certificate_or_404(
            certificate_id=certificate_id,
            current_user=current_user,
        )
        self.repository.delete(self.session, certificate=certificate)
        return EquipmentCertificateDeletePayload(deleted=True)

    def _resolve_manager_scope(self, current_user: User) -> int | None:
        if current_user.role in {UserRole.SUPER_ADMIN, UserRole.ADMIN}:
            return None
        if current_user.role == UserRole.MANAGER:
            return current_user.id
        raise ApiException(403, "无权限")

    def _get_equipment_or_404(self, *, equipment_id: int, current_user: User) -> Equipment:
        manager_scope = self._resolve_manager_scope(current_user)
        equipment = self.equipment_repository.get_by_id(
            self.session,
            equipment_id,
            manager_id=manager_scope,
        )
        if equipment is None:
            raise ApiException(404, "设备不存在")
        return equipment

    def _get_certificate_or_404(self, *, certificate_id: int, current_user: User) -> EquipmentCertificate:
        manager_scope = self._resolve_manager_scope(current_user)
        certificate = self.repository.get_by_id(
            self.session,
            certificate_id,
            manager_id=manager_scope,
        )
        if certificate is None:
            raise ApiException(404, "设备证书不存在")
        return certificate

    def _to_payload(self, certificate: EquipmentCertificate) -> EquipmentCertificatePayload:
        return EquipmentCertificatePayload(
            id=certificate.id,
            equipment_id=certificate.equipment_id,
            name=certificate.name,
            certificate_no=certificate.certificate_no,
            issuer=certificate.issuer,
            issued_date=certificate.issued_date,
            expiry_date=certificate.expiry_date,
            remark=certificate.remark,
        )

    def _translate_integrity_error(self, exc: IntegrityError) -> ApiException:
        _ = str(exc.orig)
        return ApiException(400, "设备证书数据冲突")
