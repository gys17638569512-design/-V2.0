from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ApiException
from app.models import FieldOption
from app.repositories.field_option_repository import FieldOptionRepository
from app.schemas.common import PagePayload
from app.schemas.field_option import (
    FieldOptionCreateRequest,
    FieldOptionPayload,
    FieldOptionUpdateRequest,
)


class FieldOptionService:
    def __init__(
        self,
        session: Session,
        repository: FieldOptionRepository | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or FieldOptionRepository()

    def list_page(
        self,
        *,
        field_key: str | None,
        include_inactive: bool,
        page: int,
        page_size: int,
    ) -> PagePayload[FieldOptionPayload]:
        items, total = self.repository.list_page(
            self.session,
            field_key=field_key,
            include_inactive=include_inactive,
            page=page,
            page_size=page_size,
        )
        return PagePayload(
            items=[self._to_payload(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create(self, payload: FieldOptionCreateRequest) -> FieldOptionPayload:
        field_option = FieldOption(
            field_key=payload.field_key,
            option_value=payload.option_value,
            option_label=payload.option_label,
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )
        try:
            created = self.repository.create(self.session, field_option=field_option)
        except IntegrityError:
            raise ApiException(400, "同一字段分类下的选项值不能重复") from None
        return self._to_payload(created)

    def update(self, field_option_id: int, payload: FieldOptionUpdateRequest) -> FieldOptionPayload:
        field_option = self.repository.get_by_id(self.session, field_option_id)
        if field_option is None:
            raise ApiException(404, "字段选项不存在")

        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(field_option, key, value)

        try:
            updated = self.repository.update(self.session, field_option=field_option)
        except IntegrityError:
            raise ApiException(400, "同一字段分类下的选项值不能重复") from None
        return self._to_payload(updated)

    def delete(self, field_option_id: int) -> None:
        field_option = self.repository.get_by_id(self.session, field_option_id)
        if field_option is None:
            raise ApiException(404, "字段选项不存在")
        self.repository.delete(self.session, field_option=field_option)

    def _to_payload(self, field_option: FieldOption) -> FieldOptionPayload:
        return FieldOptionPayload(
            id=field_option.id,
            field_key=field_option.field_key,
            option_value=field_option.option_value,
            option_label=field_option.option_label,
            sort_order=field_option.sort_order,
            is_active=field_option.is_active,
            created_at=field_option.created_at,
            updated_at=field_option.updated_at,
        )
