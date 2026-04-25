from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Contact, Customer


class ContactRepository:
    def create(self, session: Session, *, contact: Contact) -> Contact:
        session.add(contact)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(contact)
        session.expunge(contact)
        return contact

    def update(self, session: Session, *, contact: Contact) -> Contact:
        session.add(contact)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(contact)
        session.expunge(contact)
        return contact

    def delete(self, session: Session, *, contact: Contact) -> Contact:
        contact.is_active = False
        return self.update(session, contact=contact)

    def get_by_id(
        self,
        session: Session,
        contact_id: int,
        *,
        manager_id: int | None,
    ) -> Contact | None:
        statement = (
            select(Contact)
            .join(Customer, Contact.customer_id == Customer.id)
            .where(
                Contact.id == contact_id,
                Contact.is_active.is_(True),
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
    ) -> tuple[list[Contact], int]:
        statement = (
            select(Contact)
            .where(
                Contact.customer_id == customer_id,
                Contact.is_active.is_(True),
            )
            .order_by(Contact.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        count_statement = select(func.count()).select_from(Contact).where(
            Contact.customer_id == customer_id,
            Contact.is_active.is_(True),
        )

        items = list(session.scalars(statement))
        total = session.scalar(count_statement) or 0
        return items, total
