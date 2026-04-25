from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def get_by_username(self, session: Session, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return session.scalar(statement)

    def get_by_id(self, session: Session, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        return session.scalar(statement)

    def increment_token_version(self, session: Session, user: User) -> User:
        user.token_version += 1
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
