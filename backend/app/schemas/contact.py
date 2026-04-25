from pydantic import BaseModel, ConfigDict, Field


class ContactCreateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    mobile: str = Field(min_length=1, max_length=32)
    phone: str | None = Field(default=None, max_length=32)
    position: str | None = Field(default=None, max_length=64)
    is_primary: bool = False
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")


class ContactUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    mobile: str = Field(min_length=1, max_length=32)
    phone: str | None = Field(default=None, max_length=32)
    position: str | None = Field(default=None, max_length=64)
    is_primary: bool = False
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")


class ContactPayload(BaseModel):
    id: int
    customer_id: int
    name: str | None
    mobile: str
    phone: str | None
    position: str | None
    is_primary: bool
    remark: str | None

    model_config = ConfigDict(extra="forbid")


class ContactDeletePayload(BaseModel):
    deleted: bool

    model_config = ConfigDict(extra="forbid")
