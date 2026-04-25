from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_contact_service, require_roles
from app.models import UserRole
from app.schemas.common import ApiResponse, PagePayload
from app.schemas.contact import (
    ContactCreateRequest,
    ContactDeletePayload,
    ContactPayload,
    ContactUpdateRequest,
)
from app.services.contact_service import ContactService

router = APIRouter(tags=["contacts"])


@router.post(
    "/customers/{customer_id}/contacts",
    response_model=ApiResponse[ContactPayload],
    summary="Create customer contact",
)
def create_customer_contact(
    customer_id: int,
    payload: ContactCreateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    contact_service: ContactService = Depends(get_contact_service),
) -> ApiResponse[ContactPayload]:
    return ApiResponse(
        data=contact_service.create(
            customer_id=customer_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.get(
    "/customers/{customer_id}/contacts",
    response_model=ApiResponse[PagePayload[ContactPayload]],
    summary="List customer contacts",
)
def list_customer_contacts(
    customer_id: int,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    contact_service: ContactService = Depends(get_contact_service),
) -> ApiResponse[PagePayload[ContactPayload]]:
    return ApiResponse(
        data=contact_service.list_page(
            customer_id=customer_id,
            current_user=current_user,
            page=page,
            page_size=page_size,
        )
    )


@router.put(
    "/contacts/{contact_id}",
    response_model=ApiResponse[ContactPayload],
    summary="Update contact",
)
def update_contact(
    contact_id: int,
    payload: ContactUpdateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    contact_service: ContactService = Depends(get_contact_service),
) -> ApiResponse[ContactPayload]:
    return ApiResponse(
        data=contact_service.update(
            contact_id=contact_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.delete(
    "/contacts/{contact_id}",
    response_model=ApiResponse[ContactDeletePayload],
    summary="Delete contact",
)
def delete_contact(
    contact_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    contact_service: ContactService = Depends(get_contact_service),
) -> ApiResponse[ContactDeletePayload]:
    return ApiResponse(
        data=contact_service.delete(
            contact_id=contact_id,
            current_user=current_user,
        )
    )
