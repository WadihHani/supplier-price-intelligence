from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.supplier_quote import SupplierQuote
from app.repositories.supplier import supplier_repository
from app.repositories.product import product_repository
from app.repositories.supplier_quote import supplier_quote_repository
from app.schemas.supplier_quote import (
    SupplierQuoteCreate,
    SupplierQuoteUpdate,
)


class SupplierQuoteService:

    def create_quote(
        self,
        db: Session,
        quote_data: SupplierQuoteCreate,
    ) -> SupplierQuote:

        supplier = supplier_repository.get_by_id(
            db,
            quote_data.supplier_id,
        )

        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found.",
            )

        product = product_repository.get_by_id(
            db,
            quote_data.product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        quote = SupplierQuote(
            **quote_data.model_dump()
        )

        return supplier_quote_repository.create(
            db,
            quote,
        )

    def get_quote(
        self,
        db: Session,
        quote_id: int,
    ) -> SupplierQuote:

        quote = supplier_quote_repository.get_by_id(
            db,
            quote_id,
        )

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier quote not found.",
            )

        return quote

    def get_quotes(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SupplierQuote]:

        return supplier_quote_repository.get_all(
            db,
            skip=skip,
            limit=limit,
        )

    def update_quote(
        self,
        db: Session,
        quote_id: int,
        quote_data: SupplierQuoteUpdate,
    ) -> SupplierQuote:

        quote = self.get_quote(
            db,
            quote_id,
        )

        data = quote_data.model_dump(
            exclude_unset=True
        )

        if "supplier_id" in data:
            supplier = supplier_repository.get_by_id(
                db,
                data["supplier_id"],
            )

            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier not found.",
                )

        if "product_id" in data:
            product = product_repository.get_by_id(
                db,
                data["product_id"],
            )

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found.",
                )

        return supplier_quote_repository.update(
            db,
            quote,
            data,
        )

    def delete_quote(
        self,
        db: Session,
        quote_id: int,
    ) -> None:

        quote = self.get_quote(
            db,
            quote_id,
        )

        supplier_quote_repository.delete(
            db,
            quote,
        )


supplier_quote_service = SupplierQuoteService()
