from pydantic import BaseModel, ConfigDict, Field, model_validator


class MaterialCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    specification: str = Field(min_length=1, max_length=255)
    equipment_category: str = Field(min_length=1, max_length=128)
    sale_price: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=32)
    cost_price: float | None = Field(default=None, ge=0)
    stock_qty: float | None = Field(default=None, ge=0)
    min_stock_qty: float | None = Field(default=None, ge=0)
    manufacturer: str | None = Field(default=None, max_length=128)
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")


class MaterialUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    specification: str | None = Field(default=None, min_length=1, max_length=255)
    equipment_category: str | None = Field(default=None, min_length=1, max_length=128)
    sale_price: float | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=32)
    cost_price: float | None = Field(default=None, ge=0)
    stock_qty: float | None = Field(default=None, ge=0)
    min_stock_qty: float | None = Field(default=None, ge=0)
    manufacturer: str | None = Field(default=None, max_length=128)
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_not_empty(self) -> "MaterialUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("empty payload")
        return self


class MaterialPayload(BaseModel):
    id: int
    system_no: str
    name: str
    specification: str
    equipment_category: str
    sale_price: float
    unit: str
    cost_price: float | None
    stock_qty: float | None
    min_stock_qty: float | None
    manufacturer: str | None
    remark: str | None

    model_config = ConfigDict(extra="forbid")


class MaterialDeletePayload(BaseModel):
    deleted: bool

    model_config = ConfigDict(extra="forbid")
