from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Material


class MaterialRepository:
    def create(self, session: Session, *, material: Material) -> Material:
        session.add(material)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(material)
        session.expunge(material)
        return material

    def update(self, session: Session, *, material: Material) -> Material:
        session.add(material)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(material)
        session.expunge(material)
        return material

    def delete(self, session: Session, *, material: Material) -> Material:
        material.is_active = False
        return self.update(session, material=material)

    def get_by_id(
        self,
        session: Session,
        material_id: int,
    ) -> Material | None:
        statement = select(Material).where(
            Material.id == material_id,
            Material.is_active.is_(True),
        )
        return session.scalar(statement)

    def list_page(
        self,
        session: Session,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Material], int]:
        statement = select(Material).where(Material.is_active.is_(True))
        count_statement = select(func.count()).select_from(Material).where(Material.is_active.is_(True))

        statement = statement.order_by(Material.id.asc()).offset((page - 1) * page_size).limit(page_size)

        items = list(session.scalars(statement))
        total = session.scalar(count_statement) or 0
        return items, total
