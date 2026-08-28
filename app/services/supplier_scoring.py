from collections import defaultdict

from sqlalchemy.orm import Session, object_session

from app.models.supplier import Supplier
from app.models.supplier_quote import SupplierQuote
from app.repositories.product import product_repository
from app.repositories.supplier import supplier_repository
from app.repositories.supplier_quote import supplier_quote_repository


class SupplierScoringService:

    def calculate_supplier_score(
        self,
        supplier: Supplier,
        quote: SupplierQuote,
    ) -> dict:
        db = object_session(quote)

        if db is None:
            raise ValueError("Quote must be attached to a database session.")

        comparison_quotes = [
            comparison_quote
            for comparison_quote in supplier_quote_repository.get_by_product(
                db,
                quote.product_id,
                active_only=True,
            )
            if comparison_quote.currency == quote.currency
        ]
        lowest_price = min(
            comparison_quote.unit_price
            for comparison_quote in comparison_quotes
        )

        if quote.unit_price == lowest_price:
            price_score = 100.0
        elif quote.unit_price == 0:
            price_score = 100.0
        else:
            price_score = (lowest_price / quote.unit_price) * 100

        price_score = max(0.0, min(price_score, 100.0))
        reliability_score = (
            supplier.reliability_score
            if supplier.reliability_score is not None
            else 50.0
        )
        delivery_score = (
            supplier.delivery_score
            if supplier.delivery_score is not None
            else 50.0
        )
        activity_score = 100.0 if supplier.is_active else 0.0
        final_score = round(
            (price_score * 0.50)
            + (reliability_score * 0.20)
            + (delivery_score * 0.15)
            + (activity_score * 0.15),
            2,
        )

        return {
            "supplier_id": supplier.id,
            "supplier_name": supplier.name,
            "quote_id": quote.id,
            "product_id": quote.product_id,
            "unit_price": quote.unit_price,
            "currency": quote.currency,
            "price_score": price_score,
            "reliability_score": reliability_score,
            "delivery_score": delivery_score,
            "activity_score": activity_score,
            "final_score": final_score,
        }

    def analyze_supplier_options(
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
                "currency_rankings": [],
            }

        quotes = supplier_quote_repository.get_by_product(
            db,
            product_id,
            active_only=True,
        )
        quotes_by_currency = defaultdict(list)

        for quote in quotes:
            quotes_by_currency[quote.currency].append(quote)

        currency_rankings = []

        for currency, currency_quotes in quotes_by_currency.items():
            scored_quotes = []

            for quote in currency_quotes:
                supplier = supplier_repository.get_by_id(
                    db,
                    quote.supplier_id,
                )

                if supplier:
                    scored_quotes.append(
                        self.calculate_supplier_score(supplier, quote)
                    )

            ranked_suppliers = sorted(
                scored_quotes,
                key=lambda score: score["final_score"],
                reverse=True,
            )

            for rank, score in enumerate(ranked_suppliers, start=1):
                score["rank"] = rank

            if ranked_suppliers:
                currency_rankings.append(
                    {
                        "currency": currency,
                        "ranked_suppliers": ranked_suppliers,
                        "recommendation": ranked_suppliers[0],
                    }
                )

        return {
            "product_id": product.id,
            "product_name": product.name,
            "currency_rankings": currency_rankings,
        }


supplier_scoring_service = SupplierScoringService()
