from datetime import timedelta

import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import ApiException
from app.core.security import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, create_token, verify_password
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthTokenPayload, TokenClaims, UserProfile


class AuthService:
    def __init__(
        self,
        session: Session,
        user_repository: UserRepository | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.user_repository = user_repository or UserRepository()
        self.settings = settings or get_settings()

    def authenticate(self, username: str, password: str) -> AuthTokenPayload:
        user = self.user_repository.get_by_username(self.session, username)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            raise ApiException(401, "用户名或密码错误")
        return self._build_auth_payload(user)

    def refresh(self, refresh_token: str) -> AuthTokenPayload:
        user, claims = self._get_user_and_claims_from_token(
            refresh_token,
            expected_token_type=REFRESH_TOKEN_TYPE,
        )
        user = self.user_repository.increment_token_version_if_matches(
            self.session,
            user_id=user.id,
            expected_version=claims.ver,
        )
        if user is None:
            raise ApiException(401, "登录状态已失效")
        return self._build_auth_payload(user)

    def logout(self, access_token: str) -> None:
        user, claims = self._get_user_and_claims_from_token(
            access_token,
            expected_token_type=ACCESS_TOKEN_TYPE,
        )
        invalidated_user = self.user_repository.increment_token_version_if_matches(
            self.session,
            user_id=user.id,
            expected_version=claims.ver,
        )
        if invalidated_user is None:
            raise ApiException(401, "登录状态已失效")

    def get_current_user(self, access_token: str) -> User:
        return self.get_user_from_token(access_token, expected_token_type=ACCESS_TOKEN_TYPE)

    def get_user_from_token(self, token: str, *, expected_token_type: str) -> User:
        user, _claims = self._get_user_and_claims_from_token(
            token,
            expected_token_type=expected_token_type,
        )
        return user

    def _get_user_and_claims_from_token(
        self,
        token: str,
        *,
        expected_token_type: str,
    ) -> tuple[User, TokenClaims]:
        try:
            claims = TokenClaims.model_validate(self._decode_token(token))
            user_id = int(claims.sub)
        except (jwt.InvalidTokenError, ValidationError, ValueError):
            raise ApiException(401, "登录状态已失效") from None

        if claims.type != expected_token_type:
            raise ApiException(401, "登录状态已失效")

        user = self.user_repository.get_by_id(self.session, user_id)
        if user is None or not user.is_active or user.token_version != claims.ver:
            raise ApiException(401, "登录状态已失效")
        return user, claims

    def _build_auth_payload(self, user: User) -> AuthTokenPayload:
        access_token = create_token(
            settings=self.settings,
            user_id=user.id,
            role=user.role.value,
            token_type=ACCESS_TOKEN_TYPE,
            token_version=user.token_version,
            expires_delta=timedelta(minutes=self.settings.access_token_expire_minutes),
        )
        refresh_token = create_token(
            settings=self.settings,
            user_id=user.id,
            role=user.role.value,
            token_type=REFRESH_TOKEN_TYPE,
            token_version=user.token_version,
            expires_delta=timedelta(days=self.settings.refresh_token_expire_days),
        )
        return AuthTokenPayload(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.settings.access_token_expire_minutes * 60,
            user=self._build_user_profile(user),
        )

    def _build_user_profile(self, user: User) -> UserProfile:
        return UserProfile(
            id=user.id,
            username=user.username,
            role=user.role,
            name=user.full_name,
        )

    def _decode_token(self, token: str) -> dict[str, object]:
        from app.core.security import decode_token

        return decode_token(token, self.settings)
