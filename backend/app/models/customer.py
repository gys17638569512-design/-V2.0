from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class Customer(BaseModel):
    """Minimum customer foundation table for upcoming business modules."""

    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    manager: Mapped["User | None"] = relationship(back_populates="customers_managed")
