from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import ApiResponse, HealthPayload

router = APIRouter(tags=["system"])


@router.get("/health", response_model=ApiResponse[HealthPayload], summary="Health check")
def health_check() -> ApiResponse[HealthPayload]:
    settings = get_settings()
    return ApiResponse(
        data=HealthPayload(
            service=settings.app_name,
            status="ok",
        )
    )
