from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import BootstrapState

INITIAL_ADMIN_BOOTSTRAP_KEY = "initial_admin_created"


class BootstrapStateRepository:
    def create_initial_admin_marker(self, session: Session) -> bool:
        session.add(BootstrapState(key=INITIAL_ADMIN_BOOTSTRAP_KEY))
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            return False
        return True
