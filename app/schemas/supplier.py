from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
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
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
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
