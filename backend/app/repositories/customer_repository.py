from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Customer


class CustomerRepository:
    def create(self, session: Session, *, customer: Customer) -> Customer:
        session.add(customer)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(customer)
        session.expunge(customer)
        return customer

    def update(self, session: Session, *, customer: Customer) -> Customer:
        session.add(customer)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(customer)
        session.expunge(customer)
        return customer

    def delete(self, session: Session, *, customer: Customer) -> Customer:
        customer.is_active = False
        return self.update(session, customer=customer)

    def list_page(
        self,
        session: Session,
        *,
        manager_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Customer], int]:
        statement = select(Customer).where(Customer.is_active.is_(True))
        count_statement = select(func.count()).select_from(Customer).where(Customer.is_active.is_(True))

        if manager_id is not None:
            statement = statement.where(Customer.manager_id == manager_id)
            count_statement = count_statement.where(Customer.manager_id == manager_id)

        statement = statement.order_by(Customer.id.asc()).offset((page - 1) * page_size).limit(page_size)

        items = list(session.scalars(statement))
        total = session.scalar(count_statement) or 0
        return items, total

    def get_by_id(
        self,
        session: Session,
        customer_id: int,
        *,
        manager_id: int | None,
    ) -> Customer | None:
        statement = select(Customer).where(
            Customer.id == customer_id,
            Customer.is_active.is_(True),
        )
        if manager_id is not None:
            statement = statement.where(Customer.manager_id == manager_id)
        return session.scalar(statement)
