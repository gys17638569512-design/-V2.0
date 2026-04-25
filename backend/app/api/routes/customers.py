from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_customer_service, require_roles
from app.models import UserRole
from app.schemas.common import ApiResponse, PagePayload
from app.schemas.customer import (
    CustomerCreateRequest,
    CustomerDeletePayload,
    CustomerPayload,
    CustomerUpdateRequest,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=ApiResponse[CustomerPayload], summary="Create customer")
def create_customer(
    payload: CustomerCreateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    customer_service: CustomerService = Depends(get_customer_service),
) -> ApiResponse[CustomerPayload]:
    return ApiResponse(data=customer_service.create(payload=payload, current_user=current_user))


@router.get("", response_model=ApiResponse[PagePayload[CustomerPayload]], summary="List customers")
def list_customers(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    customer_service: CustomerService = Depends(get_customer_service),
) -> ApiResponse[PagePayload[CustomerPayload]]:
    return ApiResponse(
        data=customer_service.list_page(
            current_user=current_user,
            page=page,
            page_size=page_size,
        )
    )


@router.get(
    "/{customer_id}",
    response_model=ApiResponse[CustomerPayload],
    summary="Get customer detail",
)
def get_customer_detail(
    customer_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    customer_service: CustomerService = Depends(get_customer_service),
) -> ApiResponse[CustomerPayload]:
    return ApiResponse(
        data=customer_service.get_detail(
            customer_id=customer_id,
            current_user=current_user,
        )
    )


@router.put(
    "/{customer_id}",
    response_model=ApiResponse[CustomerPayload],
    summary="Update customer",
)
def update_customer(
    customer_id: int,
    payload: CustomerUpdateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    customer_service: CustomerService = Depends(get_customer_service),
) -> ApiResponse[CustomerPayload]:
    return ApiResponse(
        data=customer_service.update(
            customer_id=customer_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.delete(
    "/{customer_id}",
    response_model=ApiResponse[CustomerDeletePayload],
    summary="Delete customer",
)
def delete_customer(
    customer_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    customer_service: CustomerService = Depends(get_customer_service),
) -> ApiResponse[CustomerDeletePayload]:
    return ApiResponse(data=customer_service.delete(customer_id=customer_id, current_user=current_user))
