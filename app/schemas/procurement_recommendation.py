from pydantic import BaseModel


class ProcurementRecommendationItem(BaseModel):
    currency: str
    supplier_id: int
    supplier_name: str
    final_score: float
    unit_price: float
    explanation: str


class ProcurementRecommendationResponse(BaseModel):
    product_id: int
    product_name: str
    recommendations: list[ProcurementRecommendationItem]
