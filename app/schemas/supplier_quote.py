from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SupplierQuoteBase(BaseModel):
    supplier_id: int
    product_id: int
    unit_price: float
    currency: str = "USD"
    quantity: int = 1
    quote_date: datetime
    valid_until: datetime | None = None
    notes: str | None = None


class SupplierQuoteCreate(SupplierQuoteBase):
    pass


class SupplierQuoteUpdate(BaseModel):
    supplier_id: int | None = None
    product_id: int | None = None
    unit_price: float | None = None
    currency: str | None = None
    quantity: int | None = None
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
