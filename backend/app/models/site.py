from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Computed, ForeignKey, Index, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.equipment import Equipment


class Site(BaseModel):
    """Customer sites with active-state soft delete semantics."""

    __tablename__ = "sites"
    __table_args__ = (
        Index("uq_sites_active_customer_id_name", "customer_id", "active_name", unique=True),
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
    active_name: Mapped[str | None] = mapped_column(
        String(128),
        Computed(
            "CASE WHEN is_active = 1 THEN name ELSE NULL END",
            persisted=True,
        ),
        nullable=True,
    )

    customer: Mapped["Customer"] = relationship(back_populates="sites")
    equipments: Mapped[list["Equipment"]] = relationship(back_populates="site")
