from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Computed, ForeignKey, Index, Integer, String, Text, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.customer import Customer


class Contact(BaseModel):
    """Customer contacts with DB-enforced active primary uniqueness."""

    __tablename__ = "contacts"
    __table_args__ = (
        Index("ix_contacts_customer_id_mobile", "customer_id", "mobile", unique=True),
        Index("uq_contacts_active_primary_customer_id", "active_primary_customer_id", unique=True),
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mobile: Mapped[str] = mapped_column(String(32), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    position: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
    active_primary_customer_id: Mapped[int | None] = mapped_column(
        Integer,
        Computed(
            "CASE WHEN is_primary = 1 AND is_active = 1 THEN customer_id ELSE NULL END",
            persisted=True,
        ),
        nullable=True,
    )

    customer: Mapped["Customer"] = relationship(back_populates="contacts")
