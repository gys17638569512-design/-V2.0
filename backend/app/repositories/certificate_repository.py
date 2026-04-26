from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Customer, Equipment, EquipmentCertificate, Site


class EquipmentCertificateRepository:
    def create(self, session: Session, *, certificate: EquipmentCertificate) -> EquipmentCertificate:
        session.add(certificate)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(certificate)
        session.expunge(certificate)
        return certificate

    def update(self, session: Session, *, certificate: EquipmentCertificate) -> EquipmentCertificate:
        session.add(certificate)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(certificate)
        session.expunge(certificate)
        return certificate

    def delete(self, session: Session, *, certificate: EquipmentCertificate) -> EquipmentCertificate:
        certificate.is_active = False
        return self.update(session, certificate=certificate)

    def get_by_id(
        self,
        session: Session,
        certificate_id: int,
        *,
        manager_id: int | None,
    ) -> EquipmentCertificate | None:
        statement = (
            select(EquipmentCertificate)
            .join(Equipment, EquipmentCertificate.equipment_id == Equipment.id)
            .join(Site, Equipment.site_id == Site.id)
            .join(Customer, Site.customer_id == Customer.id)
            .where(
                EquipmentCertificate.id == certificate_id,
                EquipmentCertificate.is_active.is_(True),
                Equipment.is_active.is_(True),
                Site.is_active.is_(True),
                Customer.is_active.is_(True),
            )
        )
        if manager_id is not None:
            statement = statement.where(Customer.manager_id == manager_id)
        return session.scalar(statement)

    def list_page(
        self,
        session: Session,
        *,
        manager_id: int | None,
        equipment_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[EquipmentCertificate], int]:
        statement = (
            select(EquipmentCertificate)
            .join(Equipment, EquipmentCertificate.equipment_id == Equipment.id)
            .join(Site, Equipment.site_id == Site.id)
            .join(Customer, Site.customer_id == Customer.id)
            .where(
                EquipmentCertificate.is_active.is_(True),
                Equipment.is_active.is_(True),
                Site.is_active.is_(True),
                Customer.is_active.is_(True),
            )
        )
        count_statement = (
            select(func.count())
            .select_from(EquipmentCertificate)
            .join(Equipment, EquipmentCertificate.equipment_id == Equipment.id)
            .join(Site, Equipment.site_id == Site.id)
            .join(Customer, Site.customer_id == Customer.id)
            .where(
                EquipmentCertificate.is_active.is_(True),
                Equipment.is_active.is_(True),
                Site.is_active.is_(True),
                Customer.is_active.is_(True),
            )
        )

        if manager_id is not None:
            statement = statement.where(Customer.manager_id == manager_id)
            count_statement = count_statement.where(Customer.manager_id == manager_id)
        if equipment_id is not None:
            statement = statement.where(EquipmentCertificate.equipment_id == equipment_id)
            count_statement = count_statement.where(EquipmentCertificate.equipment_id == equipment_id)

        statement = statement.order_by(EquipmentCertificate.id.asc()).offset((page - 1) * page_size).limit(page_size)

        items = list(session.scalars(statement))
        total = session.scalar(count_statement) or 0
        return items, total
