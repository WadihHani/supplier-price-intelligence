export interface Product { id: number; name: string; sku: string; description: string | null; category: string | null; unit: string; is_active: boolean; created_at: string; updated_at: string; }
export interface Supplier { id: number; name: string; code: string; email: string | null; phone: string | null; country: string | null; website: string | null; reliability_score: number | null; delivery_score: number | null; is_active: boolean; created_at: string; updated_at: string; }
export interface SupplierQuote { id: number; supplier_id: number; product_id: number; unit_price: number; currency: string; quantity: number; quote_date: string; valid_until: string | null; notes: string | null; is_active: boolean; created_at: string; updated_at: string; }
export interface PriceQuote { quote_id: number; supplier_id: number; supplier_name?: string | null; product_id: number; product_name: string; unit_price: number; currency: string; quantity: number; rank: number; }
export interface PriceComparisonResponse { product_id: number; product_name: string; quotes: PriceQuote[]; recommendations: PriceQuote[]; }
export interface AnalyzedQuote { quote_id: number; supplier_id: number; supplier_name: string | null; unit_price: number; quantity: number; }
export interface CurrencyAnalysis { currency: string; number_of_quotes: number; lowest_price: number; highest_price: number; average_price: number; price_difference: number; price_difference_percentage: number; potential_savings: number; savings_percentage: number; cheapest_quote: AnalyzedQuote; most_expensive_quote: AnalyzedQuote; }
export interface ProcurementAnalysisResponse { product_id: number; product_name: string; currency_analyses: CurrencyAnalysis[]; }
export interface SupplierScore { rank: number; supplier_id: number; supplier_name: string; quote_id: number; product_id: number; unit_price: number; currency: string; price_score: number; reliability_score: number; delivery_score: number; activity_score: number; final_score: number; }
export interface CurrencyRanking { currency: string; ranked_suppliers: SupplierScore[]; recommendation: SupplierScore; }
export interface SupplierScoringResponse { product_id: number; product_name: string; currency_rankings: CurrencyRanking[]; }
export interface ProcurementRecommendation { currency: string; supplier_id: number; supplier_name: string; final_score: number; unit_price: number; explanation: string; }
export interface ProcurementRecommendationResponse { product_id: number; product_name: string; recommendations: ProcurementRecommendation[]; }
export interface LoginResponse { access_token: string; token_type: string; }
