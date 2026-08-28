from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    name: str
    code: str
    email: EmailStr | None = None
    phone: str | None = None
    country: str | None = None
    website: str | None = None
    reliability_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    delivery_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    country: str | None = None
    website: str | None = None
    is_active: bool | None = None
    reliability_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    delivery_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
