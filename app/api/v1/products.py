from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.procurement_analysis import ProcurementAnalysisResponse
from app.schemas.procurement_recommendation import (
    ProcurementRecommendationResponse,
)
from app.schemas.quote_comparison import QuoteComparisonResponse
from app.schemas.supplier_scoring import SupplierScoringResponse
from app.services.product import product_service
from app.services.procurement_analysis import procurement_analysis_service
from app.services.procurement_recommendation import (
    ProcurementRecommendationService,
    get_procurement_recommendation_service,
)
from app.services.quote_comparison import quote_comparison_service
from app.services.supplier_scoring import supplier_scoring_service


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    return product_service.create_product(
        db,
        product_data,
    )


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return product_service.get_products(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{product_id}/price-comparison",
    response_model=QuoteComparisonResponse,
)
def get_product_price_comparison(
    product_id: int,
    db: Session = Depends(get_db),
):
    product_service.get_product(
        db,
        product_id,
    )

    return quote_comparison_service.compare_product_quotes(
        db,
        product_id,
    )


@router.get(
    "/{product_id}/procurement-analysis",
    response_model=ProcurementAnalysisResponse,
)
def get_product_procurement_analysis(
    product_id: int,
    db: Session = Depends(get_db),
):
    product_service.get_product(
        db,
        product_id,
    )

    return procurement_analysis_service.analyze_product_quotes(
        db,
        product_id,
    )


@router.get(
    "/{product_id}/supplier-ranking",
    response_model=SupplierScoringResponse,
)
def get_product_supplier_ranking(
    product_id: int,
    db: Session = Depends(get_db),
):
    product_service.get_product(
        db,
        product_id,
    )

    return supplier_scoring_service.analyze_supplier_options(
        db,
        product_id,
    )


@router.get(
    "/{product_id}/ai-recommendation",
    response_model=ProcurementRecommendationResponse,
)
def get_product_ai_recommendation(
    product_id: int,
    db: Session = Depends(get_db),
    recommendation_service: ProcurementRecommendationService = Depends(
        get_procurement_recommendation_service
    ),
):
    product_service.get_product(
        db,
        product_id,
    )

    return recommendation_service.generate_recommendation(
        db,
        product_id,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    return product_service.get_product(
        db,
        product_id,
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    return product_service.update_product(
        db,
        product_id,
        product_data,
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product_service.delete_product(
        db,
        product_id,
    )

    return None
