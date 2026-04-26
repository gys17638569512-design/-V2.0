from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_certificate_service, require_roles
from app.models import UserRole
from app.schemas.certificate import (
    EquipmentCertificateCreateRequest,
    EquipmentCertificateDeletePayload,
    EquipmentCertificatePayload,
    EquipmentCertificateUpdateRequest,
)
from app.schemas.common import ApiResponse, PagePayload
from app.services.certificate_service import EquipmentCertificateService

router = APIRouter(tags=["equipment-certificates"])


@router.get(
    "/equipment-certificates",
    response_model=ApiResponse[PagePayload[EquipmentCertificatePayload]],
    summary="List equipment certificates",
)
def list_equipment_certificates(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    equipment_id: int | None = None,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    certificate_service: EquipmentCertificateService = Depends(get_certificate_service),
) -> ApiResponse[PagePayload[EquipmentCertificatePayload]]:
    return ApiResponse(
        data=certificate_service.list_page(
            current_user=current_user,
            page=page,
            page_size=page_size,
            equipment_id=equipment_id,
        )
    )


@router.post(
    "/equipment-certificates",
    response_model=ApiResponse[EquipmentCertificatePayload],
    summary="Create equipment certificate",
)
def create_equipment_certificate(
    payload: EquipmentCertificateCreateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    certificate_service: EquipmentCertificateService = Depends(get_certificate_service),
) -> ApiResponse[EquipmentCertificatePayload]:
    return ApiResponse(
        data=certificate_service.create(
            payload=payload,
            current_user=current_user,
        )
    )


@router.get(
    "/equipment-certificates/{certificate_id}",
    response_model=ApiResponse[EquipmentCertificatePayload],
    summary="Get equipment certificate detail",
)
def get_equipment_certificate_detail(
    certificate_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    certificate_service: EquipmentCertificateService = Depends(get_certificate_service),
) -> ApiResponse[EquipmentCertificatePayload]:
    return ApiResponse(
        data=certificate_service.get_detail(
            certificate_id=certificate_id,
            current_user=current_user,
        )
    )


@router.put(
    "/equipment-certificates/{certificate_id}",
    response_model=ApiResponse[EquipmentCertificatePayload],
    summary="Update equipment certificate",
)
def update_equipment_certificate(
    certificate_id: int,
    payload: EquipmentCertificateUpdateRequest,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    certificate_service: EquipmentCertificateService = Depends(get_certificate_service),
) -> ApiResponse[EquipmentCertificatePayload]:
    return ApiResponse(
        data=certificate_service.update(
            certificate_id=certificate_id,
            payload=payload,
            current_user=current_user,
        )
    )


@router.delete(
    "/equipment-certificates/{certificate_id}",
    response_model=ApiResponse[EquipmentCertificateDeletePayload],
    summary="Delete equipment certificate",
)
def delete_equipment_certificate(
    certificate_id: int,
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER)),
    certificate_service: EquipmentCertificateService = Depends(get_certificate_service),
) -> ApiResponse[EquipmentCertificateDeletePayload]:
    return ApiResponse(
        data=certificate_service.delete(
            certificate_id=certificate_id,
            current_user=current_user,
        )
    )
