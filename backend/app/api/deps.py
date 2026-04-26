from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ApiException
from app.db.session import get_db_session
from app.models import User, UserRole
from app.services.auth_service import AuthService
from app.services.certificate_service import EquipmentCertificateService
from app.services.contact_service import ContactService
from app.services.customer_service import CustomerService
from app.services.equipment_service import EquipmentService
from app.services.field_option_service import FieldOptionService
from app.services.site_service import SiteService

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(session: Session = Depends(get_db_session)) -> AuthService:
    return AuthService(session)


def get_field_option_service(session: Session = Depends(get_db_session)) -> FieldOptionService:
    return FieldOptionService(session)


def get_customer_service(session: Session = Depends(get_db_session)) -> CustomerService:
    return CustomerService(session)


def get_contact_service(session: Session = Depends(get_db_session)) -> ContactService:
    return ContactService(session)


def get_certificate_service(session: Session = Depends(get_db_session)) -> EquipmentCertificateService:
    return EquipmentCertificateService(session)


def get_site_service(session: Session = Depends(get_db_session)) -> SiteService:
    return SiteService(session)


def get_equipment_service(session: Session = Depends(get_db_session)) -> EquipmentService:
    return EquipmentService(session)


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiException(401, "未授权")
    return credentials.credentials


def get_current_user(
    token: str = Depends(get_bearer_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return auth_service.get_current_user(token)


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ApiException(403, "无权限")
        return current_user

    return dependency
