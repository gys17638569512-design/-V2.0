from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_field_option_service, require_roles
from app.models import UserRole
from app.schemas.common import ApiResponse, PagePayload
from app.schemas.field_option import (
    DeletePayload,
    FieldOptionCreateRequest,
    FieldOptionPayload,
    FieldOptionUpdateRequest,
)
from app.services.field_option_service import FieldOptionService

router = APIRouter(prefix="/field-options", tags=["field-options"])


@router.get("", response_model=ApiResponse[PagePayload[FieldOptionPayload]], summary="List field options")
def list_field_options(
    field_key: str | None = None,
    include_inactive: bool = False,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    _current_user=Depends(get_current_user),
    field_option_service: FieldOptionService = Depends(get_field_option_service),
) -> ApiResponse[PagePayload[FieldOptionPayload]]:
    return ApiResponse(
        data=field_option_service.list_page(
            field_key=field_key,
            include_inactive=include_inactive,
            page=page,
            page_size=page_size,
        )
    )


@router.post(
    "",
    response_model=ApiResponse[FieldOptionPayload],
    summary="Create field option",
)
def create_field_option(
    payload: FieldOptionCreateRequest,
    _current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    field_option_service: FieldOptionService = Depends(get_field_option_service),
) -> ApiResponse[FieldOptionPayload]:
    return ApiResponse(data=field_option_service.create(payload))


@router.put(
    "/{field_option_id}",
    response_model=ApiResponse[FieldOptionPayload],
    summary="Update field option",
)
def update_field_option(
    field_option_id: int,
    payload: FieldOptionUpdateRequest,
    _current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    field_option_service: FieldOptionService = Depends(get_field_option_service),
) -> ApiResponse[FieldOptionPayload]:
    return ApiResponse(data=field_option_service.update(field_option_id, payload))


@router.delete(
    "/{field_option_id}",
    response_model=ApiResponse[DeletePayload],
    summary="Delete field option",
)
def delete_field_option(
    field_option_id: int,
    _current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    field_option_service: FieldOptionService = Depends(get_field_option_service),
) -> ApiResponse[DeletePayload]:
    field_option_service.delete(field_option_id)
    return ApiResponse(data=DeletePayload(deleted=True))
