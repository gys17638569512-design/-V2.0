from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FieldOptionCreateRequest(BaseModel):
    field_key: str = Field(min_length=1, max_length=64)
    option_value: str = Field(min_length=1, max_length=64)
    option_label: str = Field(min_length=1, max_length=128)
    sort_order: int = 0
    is_active: bool = True

    model_config = ConfigDict(extra="forbid")


class FieldOptionUpdateRequest(BaseModel):
    field_key: str | None = Field(default=None, min_length=1, max_length=64)
    option_value: str | None = Field(default=None, min_length=1, max_length=64)
    option_label: str | None = Field(default=None, min_length=1, max_length=128)
    sort_order: int | None = None
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


class FieldOptionPayload(BaseModel):
    id: int
    field_key: str
    option_value: str
    option_label: str
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DeletePayload(BaseModel):
    deleted: bool
