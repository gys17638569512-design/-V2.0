from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(extra="forbid")


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class UserProfile(BaseModel):
    id: int
    username: str
    role: UserRole
    name: str


class AuthTokenPayload(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserProfile


class LogoutPayload(BaseModel):
    logged_out: bool


class TokenClaims(BaseModel):
    sub: str
    role: UserRole
    type: Literal["access", "refresh"]
    ver: int
    jti: str
    iat: int
    exp: int
