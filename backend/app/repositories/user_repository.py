from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import User
from app.models.enums import UserRole


class UserRepository:
    def get_by_username(self, session: Session, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return session.scalar(statement)

    def get_by_id(self, session: Session, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        return session.scalar(statement)

    def get_first_admin(self, session: Session) -> User | None:
        statement = (
            select(User)
            .where(User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
            .order_by(User.id.asc())
            .limit(1)
        )
        return session.scalar(statement)

    def create(
        self,
        session: Session,
        *,
        username: str,
        password_hash: str,
        full_name: str,
        role: UserRole,
        is_active: bool,
    ) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=is_active,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def increment_token_version_if_matches(
        self,
        session: Session,
        *,
        user_id: int,
        expected_version: int,
    ) -> User | None:
        statement = (
            update(User)
            .where(User.id == user_id, User.token_version == expected_version)
            .values(token_version=User.token_version + 1)
        )
        result = session.execute(statement)
        if result.rowcount != 1:
            session.rollback()
            return None

        session.commit()
        user = self.get_by_id(session, user_id)
        if user is None:
            return None
        session.refresh(user)
        session.expunge(user)
        return user
