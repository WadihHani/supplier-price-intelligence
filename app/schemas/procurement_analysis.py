from pydantic import BaseModel


class AnalyzedQuote(BaseModel):
    quote_id: int
    supplier_id: int
    supplier_name: str | None
    unit_price: float
    quantity: int


class CurrencyAnalysis(BaseModel):
    currency: str
    number_of_quotes: int
    lowest_price: float
    highest_price: float
    average_price: float
    price_difference: float
    price_difference_percentage: float
    potential_savings: float
    savings_percentage: float
    cheapest_quote: AnalyzedQuote
    most_expensive_quote: AnalyzedQuote


class ProcurementAnalysisResponse(BaseModel):
    product_id: int
    product_name: str
    currency_analyses: list[CurrencyAnalysis]
