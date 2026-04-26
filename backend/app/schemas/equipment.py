from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EquipmentCreateRequest(BaseModel):
    site_id: int
    name: str = Field(min_length=1, max_length=128)
    category: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    manufacturer: str | None = Field(default=None, max_length=128)
    manufacture_date: date | None = None
    factory_no: str | None = Field(default=None, max_length=64)
    site_inner_no: str | None = Field(default=None, max_length=64)
    owner_unit: str | None = Field(default=None, max_length=128)
    use_unit: str | None = Field(default=None, max_length=128)
    management_department: str | None = Field(default=None, max_length=128)
    equipment_admin_name: str | None = Field(default=None, max_length=128)
    equipment_admin_phone: str | None = Field(default=None, max_length=32)
    workshop: str | None = Field(default=None, max_length=128)
    track_no: str | None = Field(default=None, max_length=64)
    location_detail: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=64)
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")


class EquipmentUpdateRequest(BaseModel):
    site_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=128)
    category: str | None = Field(default=None, min_length=1, max_length=128)
    model: str | None = Field(default=None, min_length=1, max_length=128)
    manufacturer: str | None = Field(default=None, max_length=128)
    manufacture_date: date | None = None
    factory_no: str | None = Field(default=None, max_length=64)
    site_inner_no: str | None = Field(default=None, max_length=64)
    owner_unit: str | None = Field(default=None, max_length=128)
    use_unit: str | None = Field(default=None, max_length=128)
    management_department: str | None = Field(default=None, max_length=128)
    equipment_admin_name: str | None = Field(default=None, max_length=128)
    equipment_admin_phone: str | None = Field(default=None, max_length=32)
    workshop: str | None = Field(default=None, max_length=128)
    track_no: str | None = Field(default=None, max_length=64)
    location_detail: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=64)
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_not_empty(self) -> "EquipmentUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("empty payload")
        return self


class EquipmentPayload(BaseModel):
    id: int
    site_id: int
    system_no: str
    name: str
    category: str
    model: str
    manufacturer: str | None
    manufacture_date: date | None
    factory_no: str | None
    site_inner_no: str | None
    owner_unit: str | None
    use_unit: str | None
    management_department: str | None
    equipment_admin_name: str | None
    equipment_admin_phone: str | None
    workshop: str | None
    track_no: str | None
    location_detail: str | None
    status: str | None
    remark: str | None

    model_config = ConfigDict(extra="forbid")


class EquipmentDeletePayload(BaseModel):
    deleted: bool

    model_config = ConfigDict(extra="forbid")
