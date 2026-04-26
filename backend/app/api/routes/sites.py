from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_site_service, require_roles
from app.models import UserRole
from app.schemas.common import ApiResponse, PagePayload
from app.schemas.site import SiteCreateRequest, SiteDeletePayload, SitePayload, SiteUpdateRequest
from app.services.site_service import SiteService

router = APIRouter(tags=["sites"])


@router.get(
    "/customers/{customer_id}/sites",
    response_model=ApiResponse[PagePayload[SitePayload]],
    summary="List customer sites",
)
def list_customer_sites(
    customer_id: int,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    site_service: SiteService = Depends(get_site_service),
) -> ApiResponse[PagePayload[SitePayload]]:
    return ApiResponse(
        data=site_service.list_page(
            customer_id=customer_id,
            current_user=current_user,
            page=page,
            page_size=page_size,
        )
    )


@router.post(
    "/customers/{customer_id}/sites",
    response_model=ApiResponse[SitePayload],
    summary="Create customer site",
)
def create_customer_site(
    customer_id: int,
    payload: SiteCreateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    site_service: SiteService = Depends(get_site_service),
) -> ApiResponse[SitePayload]:
    return ApiResponse(
        data=site_service.create(
            customer_id=customer_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.put(
    "/sites/{site_id}",
    response_model=ApiResponse[SitePayload],
    summary="Update site",
)
def update_site(
    site_id: int,
    payload: SiteUpdateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    site_service: SiteService = Depends(get_site_service),
) -> ApiResponse[SitePayload]:
    return ApiResponse(
        data=site_service.update(
            site_id=site_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.delete(
    "/sites/{site_id}",
    response_model=ApiResponse[SiteDeletePayload],
    summary="Delete site",
)
def delete_site(
    site_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    site_service: SiteService = Depends(get_site_service),
) -> ApiResponse[SiteDeletePayload]:
    return ApiResponse(
        data=site_service.delete(
            site_id=site_id,
            current_user=current_user,
        )
    )
