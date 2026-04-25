from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import FieldOption


class FieldOptionRepository:
    def list_page(
        self,
        session: Session,
        *,
        field_key: str | None,
        include_inactive: bool,
        page: int,
        page_size: int,
    ) -> tuple[list[FieldOption], int]:
        statement = select(FieldOption)
        count_statement = select(func.count()).select_from(FieldOption)

        if field_key is not None:
            statement = statement.where(FieldOption.field_key == field_key)
            count_statement = count_statement.where(FieldOption.field_key == field_key)

        if not include_inactive:
            statement = statement.where(FieldOption.is_active.is_(True))
            count_statement = count_statement.where(FieldOption.is_active.is_(True))

        statement = statement.order_by(
            FieldOption.field_key.asc(),
            FieldOption.sort_order.asc(),
            FieldOption.id.asc(),
        ).offset((page - 1) * page_size).limit(page_size)

        items = list(session.scalars(statement))
        total = session.scalar(count_statement) or 0
        return items, total

    def get_by_id(self, session: Session, field_option_id: int) -> FieldOption | None:
        return session.get(FieldOption, field_option_id)

    def get_by_field_and_value(
        self,
        session: Session,
        *,
        field_key: str,
        option_value: str,
    ) -> FieldOption | None:
        statement = select(FieldOption).where(
            FieldOption.field_key == field_key,
            FieldOption.option_value == option_value,
        )
        return session.scalar(statement)

    def create(self, session: Session, *, field_option: FieldOption) -> FieldOption:
        session.add(field_option)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(field_option)
        session.expunge(field_option)
        return field_option

    def update(self, session: Session, *, field_option: FieldOption) -> FieldOption:
        session.add(field_option)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(field_option)
        session.expunge(field_option)
        return field_option

    def delete(self, session: Session, *, field_option: FieldOption) -> FieldOption:
        field_option.is_active = False
        return self.update(session, field_option=field_option)
