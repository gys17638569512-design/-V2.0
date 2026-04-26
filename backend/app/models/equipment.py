from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Date, ForeignKey, Index, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.certificate import EquipmentCertificate
    from app.models.site import Site


def _generate_placeholder_system_no() -> str:
    return f"EQ-TMP-{uuid4().hex.upper()}"


class Equipment(BaseModel):
    """Equipment archive foundation for M08 CRUD."""

    __tablename__ = "equipment"
    __table_args__ = (
        Index("uq_equipment_system_no", "system_no", unique=True),
    )

    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    system_no: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default=_generate_placeholder_system_no,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    manufacture_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    factory_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    site_inner_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    owner_unit: Mapped[str | None] = mapped_column(String(128), nullable=True)
    use_unit: Mapped[str | None] = mapped_column(String(128), nullable=True)
    management_department: Mapped[str | None] = mapped_column(String(128), nullable=True)
    equipment_admin_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    equipment_admin_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    workshop: Mapped[str | None] = mapped_column(String(128), nullable=True)
    track_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    location_detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    site: Mapped["Site"] = relationship(back_populates="equipments")
    certificates: Mapped[list["EquipmentCertificate"]] = relationship(back_populates="equipment")
