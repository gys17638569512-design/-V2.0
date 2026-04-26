from pydantic import BaseModel, ConfigDict, Field, model_validator


class SiteCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    address: str = Field(min_length=1, max_length=255)
    contact_name: str | None = Field(default=None, max_length=128)
    contact_phone: str | None = Field(default=None, max_length=32)
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")


class SiteUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    contact_name: str | None = Field(default=None, max_length=128)
    contact_phone: str | None = Field(default=None, max_length=32)
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_not_empty(self) -> "SiteUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("empty payload")
        return self


class SitePayload(BaseModel):
    id: int
    customer_id: int
    name: str
    address: str
    contact_name: str | None
    contact_phone: str | None
    remark: str | None

    model_config = ConfigDict(extra="forbid")


class SiteDeletePayload(BaseModel):
    deleted: bool

    model_config = ConfigDict(extra="forbid")
