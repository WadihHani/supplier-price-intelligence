from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierRepository:
    def create(self, db: Session, supplier_data: SupplierCreate) -> Supplier:
        supplier = Supplier(**supplier_data.model_dump())

        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        return supplier

    def get_by_id(self, db: Session, supplier_id: int) -> Supplier | None:
        statement = select(Supplier).where(Supplier.id == supplier_id)

        return db.scalar(statement)

    def get_by_code(self, db: Session, code: str) -> Supplier | None:
        statement = select(Supplier).where(Supplier.code == code)

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Supplier]:
        statement = (
            select(Supplier)
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        supplier: Supplier,
        supplier_data: SupplierUpdate,
    ) -> Supplier:
        update_data = supplier_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(supplier, field, value)

        db.commit()
        db.refresh(supplier)

        return supplier

    def delete(self, db: Session, supplier: Supplier) -> None:
        db.delete(supplier)
        db.commit()


supplier_repository = SupplierRepository()
