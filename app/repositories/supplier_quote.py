from sqlalchemy.orm import Session

from app.models.supplier_quote import SupplierQuote


class SupplierQuoteRepository:

    def create(
        self,
        db: Session,
        quote: SupplierQuote,
    ) -> SupplierQuote:
        db.add(quote)
        db.commit()
        db.refresh(quote)
        return quote

    def get_by_id(
        self,
        db: Session,
        quote_id: int,
    ) -> SupplierQuote | None:
        return (
            db.query(SupplierQuote)
            .filter(SupplierQuote.id == quote_id)
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SupplierQuote]:
        return (
            db.query(SupplierQuote)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_product(
        self,
        db: Session,
        product_id: int,
        active_only: bool = True,
    ) -> list[SupplierQuote]:
        query = (
            db.query(SupplierQuote)
            .filter(SupplierQuote.product_id == product_id)
        )

        if active_only:
            query = query.filter(
                SupplierQuote.is_active.is_(True)
            )

        return query.all()

    def update(
        self,
        db: Session,
        quote: SupplierQuote,
        data: dict,
    ) -> SupplierQuote:
        for field, value in data.items():
            setattr(quote, field, value)

        db.commit()
        db.refresh(quote)
        return quote

    def delete(
        self,
        db: Session,
        quote: SupplierQuote,
    ) -> None:
        db.delete(quote)
        db.commit()


supplier_quote_repository = SupplierQuoteRepository()
