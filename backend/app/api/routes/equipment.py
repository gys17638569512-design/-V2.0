from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_equipment_service, require_roles
from app.models import UserRole
from app.schemas.common import ApiResponse, PagePayload
from app.schemas.equipment import (
    EquipmentCreateRequest,
    EquipmentDeletePayload,
    EquipmentPayload,
    EquipmentUpdateRequest,
)
from app.services.equipment_service import EquipmentService

router = APIRouter(tags=["equipment"])


@router.get(
    "/equipment",
    response_model=ApiResponse[PagePayload[EquipmentPayload]],
    summary="List equipment",
)
def list_equipment(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    site_id: int | None = None,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    equipment_service: EquipmentService = Depends(get_equipment_service),
) -> ApiResponse[PagePayload[EquipmentPayload]]:
    return ApiResponse(
        data=equipment_service.list_page(
            current_user=current_user,
            page=page,
            page_size=page_size,
            site_id=site_id,
        )
    )


@router.post(
    "/equipment",
    response_model=ApiResponse[EquipmentPayload],
    summary="Create equipment",
)
def create_equipment(
    payload: EquipmentCreateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    equipment_service: EquipmentService = Depends(get_equipment_service),
) -> ApiResponse[EquipmentPayload]:
    return ApiResponse(
        data=equipment_service.create(
            payload=payload,
            current_user=current_user,
        )
    )


@router.get(
    "/equipment/{equipment_id}",
    response_model=ApiResponse[EquipmentPayload],
    summary="Get equipment detail",
)
def get_equipment_detail(
    equipment_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    equipment_service: EquipmentService = Depends(get_equipment_service),
) -> ApiResponse[EquipmentPayload]:
    return ApiResponse(
        data=equipment_service.get_detail(
            equipment_id=equipment_id,
            current_user=current_user,
        )
    )


@router.put(
    "/equipment/{equipment_id}",
    response_model=ApiResponse[EquipmentPayload],
    summary="Update equipment",
)
def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    equipment_service: EquipmentService = Depends(get_equipment_service),
) -> ApiResponse[EquipmentPayload]:
    return ApiResponse(
        data=equipment_service.update(
            equipment_id=equipment_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.delete(
    "/equipment/{equipment_id}",
    response_model=ApiResponse[EquipmentDeletePayload],
    summary="Delete equipment",
)
def delete_equipment(
    equipment_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    equipment_service: EquipmentService = Depends(get_equipment_service),
) -> ApiResponse[EquipmentDeletePayload]:
    return ApiResponse(
        data=equipment_service.delete(
            equipment_id=equipment_id,
            current_user=current_user,
        )
    )
