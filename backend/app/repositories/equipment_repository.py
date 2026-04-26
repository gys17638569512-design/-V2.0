from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Customer, Equipment, Site


class EquipmentRepository:
    def create(self, session: Session, *, equipment: Equipment) -> Equipment:
        session.add(equipment)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(equipment)
        session.expunge(equipment)
        return equipment

    def update(self, session: Session, *, equipment: Equipment) -> Equipment:
        session.add(equipment)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(equipment)
        session.expunge(equipment)
        return equipment

    def delete(self, session: Session, *, equipment: Equipment) -> Equipment:
        equipment.is_active = False
        return self.update(session, equipment=equipment)

    def get_by_id(
        self,
        session: Session,
        equipment_id: int,
        *,
        manager_id: int | None,
    ) -> Equipment | None:
        statement = (
            select(Equipment)
            .join(Site, Equipment.site_id == Site.id)
            .join(Customer, Site.customer_id == Customer.id)
            .where(
                Equipment.id == equipment_id,
                Equipment.is_active.is_(True),
                Site.is_active.is_(True),
                Customer.is_active.is_(True),
            )
        )
        if manager_id is not None:
            statement = statement.where(Customer.manager_id == manager_id)
        return session.scalar(statement)

    def get_by_system_no(
        self,
        session: Session,
        system_no: str,
    ) -> Equipment | None:
        statement = select(Equipment).where(Equipment.system_no == system_no)
        return session.scalar(statement)

    def list_page(
        self,
        session: Session,
        *,
        manager_id: int | None,
        site_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Equipment], int]:
        statement = (
            select(Equipment)
            .join(Site, Equipment.site_id == Site.id)
            .join(Customer, Site.customer_id == Customer.id)
            .where(
                Equipment.is_active.is_(True),
                Site.is_active.is_(True),
                Customer.is_active.is_(True),
            )
        )
        count_statement = (
            select(func.count())
            .select_from(Equipment)
            .join(Site, Equipment.site_id == Site.id)
            .join(Customer, Site.customer_id == Customer.id)
            .where(
                Equipment.is_active.is_(True),
                Site.is_active.is_(True),
                Customer.is_active.is_(True),
            )
        )

        if manager_id is not None:
            statement = statement.where(Customer.manager_id == manager_id)
            count_statement = count_statement.where(Customer.manager_id == manager_id)
        if site_id is not None:
            statement = statement.where(Equipment.site_id == site_id)
            count_statement = count_statement.where(Equipment.site_id == site_id)

        statement = statement.order_by(Equipment.id.asc()).offset((page - 1) * page_size).limit(page_size)

        items = list(session.scalars(statement))
        total = session.scalar(count_statement) or 0
        return items, total
