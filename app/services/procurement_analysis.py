from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.repositories.product import product_repository
from app.repositories.supplier_quote import supplier_quote_repository


class ProcurementAnalysisService:

    def analyze_product_quotes(
        self,
        db: Session,
        product_id: int,
    ) -> dict:
        product = product_repository.get_by_id(
            db,
            product_id,
        )

        if not product:
            return {
                "product_id": product_id,
                "product_name": None,
                "currency_analyses": [],
            }

        quotes = supplier_quote_repository.get_by_product(
            db,
            product_id,
            active_only=True,
        )

        if not quotes:
            return {
                "product_id": product.id,
                "product_name": product.name,
                "currency_analyses": [],
            }

        suppliers = {
            supplier.id: supplier
            for supplier in (
                db.query(Supplier)
                .filter(
                    Supplier.id.in_(
                        {quote.supplier_id for quote in quotes}
                    )
                )
                .all()
            )
        }
        quotes_by_currency = defaultdict(list)

        for quote in quotes:
            quotes_by_currency[quote.currency].append(quote)

        currency_analyses = []

        for currency, currency_quotes in quotes_by_currency.items():
            sorted_quotes = sorted(
                currency_quotes,
                key=lambda quote: quote.unit_price,
            )
            cheapest_quote = sorted_quotes[0]
            most_expensive_quote = sorted_quotes[-1]
            lowest_price = cheapest_quote.unit_price
            highest_price = most_expensive_quote.unit_price
            price_difference = highest_price - lowest_price
            price_difference_percentage = (
                (price_difference / highest_price) * 100
                if highest_price != 0
                else 0
            )

            currency_analyses.append(
                {
                    "currency": currency,
                    "number_of_quotes": len(sorted_quotes),
                    "lowest_price": lowest_price,
                    "highest_price": highest_price,
                    "average_price": sum(
                        quote.unit_price for quote in sorted_quotes
                    ) / len(sorted_quotes),
                    "price_difference": price_difference,
                    "price_difference_percentage": (
                        price_difference_percentage
                    ),
                    "potential_savings": price_difference,
                    "savings_percentage": price_difference_percentage,
                    "cheapest_quote": self._serialize_quote(
                        cheapest_quote,
                        suppliers,
                    ),
                    "most_expensive_quote": self._serialize_quote(
                        most_expensive_quote,
                        suppliers,
                    ),
                }
            )

        return {
            "product_id": product.id,
            "product_name": product.name,
            "currency_analyses": currency_analyses,
        }

    @staticmethod
    def _serialize_quote(
        quote,
        suppliers: dict[int, Supplier],
    ) -> dict:
        supplier = suppliers.get(quote.supplier_id)

        return {
            "quote_id": quote.id,
            "supplier_id": quote.supplier_id,
            "supplier_name": supplier.name if supplier else None,
            "unit_price": quote.unit_price,
            "quantity": quote.quantity,
        }


procurement_analysis_service = ProcurementAnalysisService()
