from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_material_service, require_roles
from app.models import UserRole
from app.schemas.common import ApiResponse, PagePayload
from app.schemas.material import (
    MaterialCreateRequest,
    MaterialDeletePayload,
    MaterialPayload,
    MaterialUpdateRequest,
)
from app.services.material_service import MaterialService

router = APIRouter(tags=["materials"])


@router.get(
    "/materials",
    response_model=ApiResponse[PagePayload[MaterialPayload]],
    summary="List materials",
)
def list_materials(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    material_service: MaterialService = Depends(get_material_service),
) -> ApiResponse[PagePayload[MaterialPayload]]:
    return ApiResponse(
        data=material_service.list_page(
            current_user=current_user,
            page=page,
            page_size=page_size,
        )
    )


@router.post(
    "/materials",
    response_model=ApiResponse[MaterialPayload],
    summary="Create material",
)
def create_material(
    payload: MaterialCreateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    material_service: MaterialService = Depends(get_material_service),
) -> ApiResponse[MaterialPayload]:
    return ApiResponse(
        data=material_service.create(
            payload=payload,
            current_user=current_user,
        )
    )


@router.get(
    "/materials/{material_id}",
    response_model=ApiResponse[MaterialPayload],
    summary="Get material detail",
)
def get_material_detail(
    material_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    material_service: MaterialService = Depends(get_material_service),
) -> ApiResponse[MaterialPayload]:
    return ApiResponse(
        data=material_service.get_detail(
            material_id=material_id,
            current_user=current_user,
        )
    )


@router.put(
    "/materials/{material_id}",
    response_model=ApiResponse[MaterialPayload],
    summary="Update material",
)
def update_material(
    material_id: int,
    payload: MaterialUpdateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    material_service: MaterialService = Depends(get_material_service),
) -> ApiResponse[MaterialPayload]:
    return ApiResponse(
        data=material_service.update(
            material_id=material_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.delete(
    "/materials/{material_id}",
    response_model=ApiResponse[MaterialDeletePayload],
    summary="Delete material",
)
def delete_material(
    material_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    material_service: MaterialService = Depends(get_material_service),
) -> ApiResponse[MaterialDeletePayload]:
    return ApiResponse(
        data=material_service.delete(
            material_id=material_id,
            current_user=current_user,
        )
    )
