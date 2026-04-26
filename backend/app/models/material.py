from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean, Index, Numeric, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


def _generate_placeholder_system_no() -> str:
    return f"MT-TMP-{uuid4().hex.upper()}"


class Material(BaseModel):
    """Material master data foundation for M10 CRUD."""

    __tablename__ = "materials"
    __table_args__ = (
        Index("uq_materials_system_no", "system_no", unique=True),
    )

    system_no: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default=_generate_placeholder_system_no,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    specification: Mapped[str] = mapped_column(String(255), nullable=False)
    equipment_category: Mapped[str] = mapped_column(String(128), nullable=False)
    sale_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    cost_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    stock_qty: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    min_stock_qty: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
