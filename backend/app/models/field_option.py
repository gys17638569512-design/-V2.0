from sqlalchemy import Boolean, Integer, String, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class FieldOption(BaseModel):
    __tablename__ = "field_options"
    __table_args__ = (
        UniqueConstraint("field_key", "option_value", name="uq_field_options_field_key_option_value"),
    )

    field_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    option_value: Mapped[str] = mapped_column(String(64), nullable=False)
    option_label: Mapped[str] = mapped_column(String(128), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
        index=True,
    )
