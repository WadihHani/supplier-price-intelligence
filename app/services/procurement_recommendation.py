from sqlalchemy.orm import Session

from app.services.ai import AIProvider, get_ai_provider
from app.services.procurement_analysis import procurement_analysis_service
from app.services.quote_comparison import quote_comparison_service
from app.services.supplier_scoring import supplier_scoring_service


class ProcurementRecommendationService:

    def __init__(self, ai_provider: AIProvider | None = None):
        self.ai_provider = ai_provider or get_ai_provider()

    def generate_recommendation(
        self,
        db: Session,
        product_id: int,
    ) -> dict:
        comparison = quote_comparison_service.compare_product_quotes(
            db,
            product_id,
        )
        procurement_analysis = (
            procurement_analysis_service.analyze_product_quotes(
                db,
                product_id,
            )
        )
        supplier_scoring = supplier_scoring_service.analyze_supplier_options(
            db,
            product_id,
        )
        quotes_by_id = {
            quote["quote_id"]: quote
            for quote in comparison["quotes"]
        }
        analyses_by_currency = {
            analysis["currency"]: analysis
            for analysis in procurement_analysis["currency_analyses"]
        }
        recommendations = []

        for currency_ranking in supplier_scoring["currency_rankings"]:
            recommendation = currency_ranking["recommendation"]
            facts = self._build_procurement_facts(
                supplier_scoring,
                currency_ranking,
                analyses_by_currency.get(currency_ranking["currency"]),
                quotes_by_id,
            )

            try:
                explanation = self.ai_provider.generate_procurement_explanation(
                    facts
                )
            except Exception:
                explanation = self._fallback_explanation(facts)

            recommendations.append(
                {
                    "currency": currency_ranking["currency"],
                    "supplier_id": recommendation["supplier_id"],
                    "supplier_name": recommendation["supplier_name"],
                    "final_score": recommendation["final_score"],
                    "unit_price": recommendation["unit_price"],
                    "explanation": explanation,
                }
            )

        return {
            "product_id": supplier_scoring["product_id"],
            "product_name": supplier_scoring["product_name"],
            "recommendations": recommendations,
        }

    @staticmethod
    def _build_procurement_facts(
        supplier_scoring: dict,
        currency_ranking: dict,
        currency_analysis: dict | None,
        quotes_by_id: dict[int, dict],
    ) -> dict:
        recommendation = currency_ranking["recommendation"]

        return {
            "product": {
                "id": supplier_scoring["product_id"],
                "name": supplier_scoring["product_name"],
            },
            "currency": currency_ranking["currency"],
            "suppliers": [
                {
                    "supplier_name": score["supplier_name"],
                    "unit_price": score["unit_price"],
                    "quantity": quotes_by_id[score["quote_id"]]["quantity"],
                    "price_score": score["price_score"],
                    "reliability_score": score["reliability_score"],
                    "delivery_score": score["delivery_score"],
                    "activity_score": score["activity_score"],
                    "final_score": score["final_score"],
                }
                for score in currency_ranking["ranked_suppliers"]
            ],
            "price_difference": (
                currency_analysis["price_difference"]
                if currency_analysis
                else None
            ),
            "recommendation": {
                "supplier_name": recommendation["supplier_name"],
                "unit_price": recommendation["unit_price"],
                "reliability_score": recommendation["reliability_score"],
                "delivery_score": recommendation["delivery_score"],
                "final_score": recommendation["final_score"],
                "reason": "Highest overall supplier score",
            },
        }

    @staticmethod
    def _fallback_explanation(facts: dict) -> str:
        recommendation = facts["recommendation"]

        return (
            f"{recommendation['supplier_name']} is recommended based on the "
            f"highest overall supplier score of "
            f"{recommendation['final_score']}. Its unit price is "
            f"{recommendation['unit_price']} {facts['currency']} and it has "
            f"a reliability score of {recommendation['reliability_score']} "
            f"and delivery score of {recommendation['delivery_score']}."
        )


def get_procurement_recommendation_service() -> ProcurementRecommendationService:
    return ProcurementRecommendationService()
