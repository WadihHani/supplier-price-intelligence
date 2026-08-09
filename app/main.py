from fastapi import FastAPI

app = FastAPI(
    title="Supplier Price Intelligence API",
    description=(
        "AI-powered procurement intelligence platform for "
        "supplier quote analysis, product matching, "
        "price comparison, and supplier recommendations."
    ),
    version="0.1.0",
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