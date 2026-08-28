from pydantic import BaseModel


class QuoteComparisonItem(BaseModel):
    quote_id: int
    supplier_id: int
    supplier_name: str | None
    product_id: int
    product_name: str
    unit_price: float
    currency: str
    quantity: int
    rank: int


class QuoteComparisonResponse(BaseModel):
    product_id: int
    product_name: str
    quotes: list[QuoteComparisonItem]
    recommendations: list[QuoteComparisonItem]
