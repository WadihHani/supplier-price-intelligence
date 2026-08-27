from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def create(
        self,
        db: Session,
        product_data: ProductCreate,
    ) -> Product:
        product = Product(**product_data.model_dump())

        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    def get_by_id(
        self,
        db: Session,
        product_id: int,
    ) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id
        )

        return db.scalar(statement)

    def get_by_sku(
        self,
        db: Session,
        sku: str,
    ) -> Product | None:
        statement = select(Product).where(
            Product.sku == sku
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        statement = (
            select(Product)
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        product: Product,
        product_data: ProductUpdate,
    ) -> Product:
        update_data = product_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)

        return product

    def delete(
        self,
        db: Session,
        product: Product,
    ) -> None:
        db.delete(product)
        db.commit()


product_repository = ProductRepository()
