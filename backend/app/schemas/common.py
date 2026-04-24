from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    code: int = 0
    msg: str = "ok"
    data: DataT

    model_config = ConfigDict(extra="forbid")


class HealthPayload(BaseModel):
    service: str
    status: str
