from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import Supplier
from app.repositories.supplier_quote import supplier_quote_repository


class QuoteComparisonService:

    def compare_product_quotes(
        self,
        db: Session,
        product_id: int,
    ) -> dict:
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return {
                "product_id": product_id,
                "product_name": None,
                "quotes": [],
                "recommendations": [],
            }

        quotes = supplier_quote_repository.get_by_product(
            db,
            product_id,
        )

        if not quotes:
            return {
                "product_id": product_id,
                "product_name": product.name,
                "quotes": [],
                "recommendations": [],
            }

        supplier_ids = {
            quote.supplier_id
            for quote in quotes
        }

        suppliers = {
            supplier.id: supplier
            for supplier in (
                db.query(Supplier)
                .filter(Supplier.id.in_(supplier_ids))
                .all()
            )
        }

        quotes_by_currency = defaultdict(list)

        for quote in quotes:
            quotes_by_currency[quote.currency].append(quote)

        ranked_quotes = []

        for currency, currency_quotes in quotes_by_currency.items():
            sorted_quotes = sorted(
                currency_quotes,
                key=lambda quote: quote.unit_price,
            )

            for rank, quote in enumerate(sorted_quotes, start=1):
                supplier = suppliers.get(quote.supplier_id)

                ranked_quotes.append(
                    {
                        "quote_id": quote.id,
                        "supplier_id": quote.supplier_id,
                        "supplier_name": (
                            supplier.name
                            if supplier
                            else None
                        ),
                        "product_id": quote.product_id,
                        "product_name": product.name,
                        "unit_price": quote.unit_price,
                        "currency": currency,
                        "quantity": quote.quantity,
                        "rank": rank,
                    }
                )

        recommendations = [
            quote
            for quote in ranked_quotes
            if quote["rank"] == 1
        ]

        return {
            "product_id": product.id,
            "product_name": product.name,
            "quotes": ranked_quotes,
            "recommendations": recommendations,
        }


quote_comparison_service = QuoteComparisonService()
