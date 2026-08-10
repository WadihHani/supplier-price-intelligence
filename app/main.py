from fastapi import FastAPI

from app.api.v1.suppliers import router as supplier_router


app = FastAPI(
    title="Supplier Price Intelligence API",
    description=(
        "AI-powered procurement intelligence platform for "
        "supplier quote analysis, product matching, "
        "price comparison, and supplier recommendations."
    ),
    version="0.1.0",
)


app.include_router(
    supplier_router,
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
