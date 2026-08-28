from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.products import router as product_router
from app.api.v1.suppliers import router as supplier_router
from app.api.v1.supplier_quotes import router as supplier_quote_router


app = FastAPI(
    title="Supplier Price Intelligence API",
    description=(
        "AI-powered procurement intelligence platform for "
        "supplier quote analysis, product matching, "
        "price comparison, and supplier recommendations."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    supplier_router,
    prefix="/api/v1",
)

app.include_router(
    product_router,
    prefix="/api/v1",
)

app.include_router(
    supplier_quote_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "application": "Supplier Price Intelligence",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
