from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Customer, Site


class SiteRepository:
    def create(self, session: Session, *, site: Site) -> Site:
        session.add(site)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(site)
        session.expunge(site)
        return site

    def update(self, session: Session, *, site: Site) -> Site:
        session.add(site)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(site)
        session.expunge(site)
        return site

    def delete(self, session: Session, *, site: Site) -> Site:
        site.is_active = False
        return self.update(session, site=site)

    def get_by_id(
        self,
        session: Session,
        site_id: int,
        *,
        manager_id: int | None,
    ) -> Site | None:
        statement = (
            select(Site)
            .join(Customer, Site.customer_id == Customer.id)
            .where(
                Site.id == site_id,
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
        customer_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[Site], int]:
        statement = (
            select(Site)
            .where(
                Site.customer_id == customer_id,
                Site.is_active.is_(True),
            )
            .order_by(Site.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        count_statement = select(func.count()).select_from(Site).where(
            Site.customer_id == customer_id,
            Site.is_active.is_(True),
        )

        items = list(session.scalars(statement))
        total = session.scalar(count_statement) or 0
        return items, total
