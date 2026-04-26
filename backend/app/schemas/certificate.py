from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EquipmentCertificateCreateRequest(BaseModel):
    equipment_id: int
    name: str = Field(min_length=1, max_length=128)
    certificate_no: str | None = Field(default=None, max_length=128)
    issuer: str | None = Field(default=None, max_length=128)
    issued_date: date | None = None
    expiry_date: date | None = None
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")


class EquipmentCertificateUpdateRequest(BaseModel):
    equipment_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=128)
    certificate_no: str | None = Field(default=None, max_length=128)
    issuer: str | None = Field(default=None, max_length=128)
    issued_date: date | None = None
    expiry_date: date | None = None
    remark: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_not_empty(self) -> "EquipmentCertificateUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("empty payload")
        return self


class EquipmentCertificatePayload(BaseModel):
    id: int
    equipment_id: int
    name: str
    certificate_no: str | None
    issuer: str | None
    issued_date: date | None
    expiry_date: date | None
    remark: str | None

    model_config = ConfigDict(extra="forbid")


class EquipmentCertificateDeletePayload(BaseModel):
    deleted: bool

    model_config = ConfigDict(extra="forbid")
