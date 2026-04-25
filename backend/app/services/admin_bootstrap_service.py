from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository


class AdminBootstrapService:
    def __init__(
        self,
        session: Session,
        user_repository: UserRepository | None = None,
    ) -> None:
        self.session = session
        self.user_repository = user_repository or UserRepository()

    def create_initial_admin(self, *, username: str, password: str, full_name: str) -> User:
        if self.user_repository.get_first_admin(self.session) is not None:
            raise ValueError("初始管理员已存在，不能重复创建")

        if self.user_repository.get_by_username(self.session, username) is not None:
            raise ValueError("用户名已存在，请更换后重试")

        return self.user_repository.create(
            self.session,
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
        )
