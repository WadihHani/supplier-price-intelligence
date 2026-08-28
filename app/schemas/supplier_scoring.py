from pydantic import BaseModel


class SupplierScoreBreakdown(BaseModel):
    rank: int
    supplier_id: int
    supplier_name: str
    quote_id: int
    product_id: int
    unit_price: float
    currency: str
    price_score: float
    reliability_score: float
    delivery_score: float
    activity_score: float
    final_score: float


class CurrencySupplierRanking(BaseModel):
    currency: str
    ranked_suppliers: list[SupplierScoreBreakdown]
    recommendation: SupplierScoreBreakdown


class SupplierScoringResponse(BaseModel):
    product_id: int
    product_name: str
    currency_rankings: list[CurrencySupplierRanking]
