from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.supplier_quote import (
    SupplierQuoteCreate,
    SupplierQuoteResponse,
    SupplierQuoteUpdate,
)
from app.services.supplier_quote import supplier_quote_service


router = APIRouter(
    prefix="/supplier-quotes",
    tags=["Supplier Quotes"],
)


@router.post(
    "",
    response_model=SupplierQuoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier_quote(
    quote_data: SupplierQuoteCreate,
    db: Session = Depends(get_db),
):
    return supplier_quote_service.create_quote(
        db,
        quote_data,
    )


@router.get(
    "",
    response_model=list[SupplierQuoteResponse],
)
def get_supplier_quotes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return supplier_quote_service.get_quotes(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{quote_id}",
    response_model=SupplierQuoteResponse,
)
def get_supplier_quote(
    quote_id: int,
    db: Session = Depends(get_db),
):
    return supplier_quote_service.get_quote(
        db,
        quote_id,
    )


@router.put(
    "/{quote_id}",
    response_model=SupplierQuoteResponse,
)
def update_supplier_quote(
    quote_id: int,
    quote_data: SupplierQuoteUpdate,
    db: Session = Depends(get_db),
):
    return supplier_quote_service.update_quote(
        db,
        quote_id,
        quote_data,
    )


@router.delete(
    "/{quote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_supplier_quote(
    quote_id: int,
    db: Session = Depends(get_db),
):
    supplier_quote_service.delete_quote(
        db,
        quote_id,
    )

    return None
