from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SupplierQuoteBase(BaseModel):
    supplier_id: int
    product_id: int
    unit_price: float = Field(ge=0)
    currency: str = Field(default="USD", min_length=1, max_length=10)
    quantity: int = Field(default=1, ge=1)
    quote_date: datetime
    valid_until: datetime | None = None
    notes: str | None = None


class SupplierQuoteCreate(SupplierQuoteBase):
    pass


class SupplierQuoteUpdate(BaseModel):
    supplier_id: int | None = None
    product_id: int | None = None
    unit_price: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=1, max_length=10)
    quantity: int | None = Field(default=None, ge=1)
    quote_date: datetime | None = None
    valid_until: datetime | None = None
    notes: str | None = None
    is_active: bool | None = None


class SupplierQuoteResponse(SupplierQuoteBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
