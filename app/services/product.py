from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.product import product_repository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def create_product(
        self,
        db: Session,
        product_data: ProductCreate,
    ):
        existing_product = product_repository.get_by_sku(
            db,
            product_data.sku,
        )

        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this SKU already exists.",
            )

        return product_repository.create(
            db,
            product_data,
        )

    def get_product(
        self,
        db: Session,
        product_id: int,
    ):
        product = product_repository.get_by_id(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return product

    def get_products(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ):
        return product_repository.get_all(
            db,
            skip=skip,
            limit=limit,
        )

    def update_product(
        self,
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
    ):
        product = self.get_product(
            db,
            product_id,
        )

        if product_data.sku is not None:
            existing_product = product_repository.get_by_sku(
                db,
                product_data.sku,
            )

            if (
                existing_product
                and existing_product.id != product.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A product with this SKU already exists.",
                )

        return product_repository.update(
            db,
            product,
            product_data,
        )

    def delete_product(
        self,
        db: Session,
        product_id: int,
    ) -> None:
        product = self.get_product(
            db,
            product_id,
        )

        product_repository.delete(
            db,
            product,
        )


product_service = ProductService()
