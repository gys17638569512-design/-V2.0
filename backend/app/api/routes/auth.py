from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service, get_bearer_token, get_current_user
from app.schemas.auth import (
    AuthTokenPayload,
    LoginRequest,
    LogoutPayload,
    RefreshTokenRequest,
    UserProfile,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse[AuthTokenPayload], summary="User login")
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[AuthTokenPayload]:
    return ApiResponse(data=auth_service.authenticate(payload.username, payload.password))


@router.post("/refresh", response_model=ApiResponse[AuthTokenPayload], summary="Refresh token")
def refresh(
    payload: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[AuthTokenPayload]:
    return ApiResponse(data=auth_service.refresh(payload.refresh_token))


@router.post("/logout", response_model=ApiResponse[LogoutPayload], summary="Logout current user")
def logout(
    token: str = Depends(get_bearer_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[LogoutPayload]:
    auth_service.logout(token)
    return ApiResponse(data=LogoutPayload(logged_out=True))


@router.get("/me", response_model=ApiResponse[UserProfile], summary="Current user")
def me(current_user=Depends(get_current_user)) -> ApiResponse[UserProfile]:
    return ApiResponse(
        data=UserProfile(
            id=current_user.id,
            username=current_user.username,
            role=current_user.role,
            name=current_user.full_name,
        )
    )
