from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.supplier import supplier_repository
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierService:
    def create_supplier(
        self,
        db: Session,
        supplier_data: SupplierCreate,
    ):
        existing_supplier = supplier_repository.get_by_code(
            db,
            supplier_data.code,
        )

        if existing_supplier:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A supplier with this code already exists.",
            )

        return supplier_repository.create(
            db,
            supplier_data,
        )

    def get_supplier(
        self,
        db: Session,
        supplier_id: int,
    ):
        supplier = supplier_repository.get_by_id(
            db,
            supplier_id,
        )

        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found.",
            )

        return supplier

    def get_suppliers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ):
        return supplier_repository.get_all(
            db,
            skip=skip,
            limit=limit,
        )

    def update_supplier(
        self,
        db: Session,
        supplier_id: int,
        supplier_data: SupplierUpdate,
    ):
        supplier = self.get_supplier(
            db,
            supplier_id,
        )

        if supplier_data.code is not None:
            existing_supplier = supplier_repository.get_by_code(
                db,
                supplier_data.code,
            )

            if (
                existing_supplier
                and existing_supplier.id != supplier.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A supplier with this code already exists.",
                )

        return supplier_repository.update(
            db,
            supplier,
            supplier_data,
        )

    def delete_supplier(
        self,
        db: Session,
        supplier_id: int,
    ) -> None:
        supplier = self.get_supplier(
            db,
            supplier_id,
        )

        supplier_repository.delete(
            db,
            supplier,
        )


supplier_service = SupplierService()
