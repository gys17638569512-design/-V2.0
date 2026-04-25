from pydantic import BaseModel, ConfigDict, Field, model_validator


class CustomerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    manager_id: int | None = None

    model_config = ConfigDict(extra="forbid")


class CustomerUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    manager_id: int | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_not_empty(self) -> "CustomerUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("empty payload")
        return self


class CustomerPayload(BaseModel):
    id: int
    name: str
    manager_id: int | None


class CustomerDeletePayload(BaseModel):
    deleted: bool
