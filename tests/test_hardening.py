import pytest

from app.core.config import settings
from app.core.security import create_access_token


def test_negative_quote_price_is_rejected(client):
    response = client.post(
        "/api/v1/supplier-quotes",
        json={
            "supplier_id": 1,
            "product_id": 1,
            "unit_price": -1,
            "currency": "USD",
            "quantity": 1,
            "quote_date": "2026-08-28T16:00:00",
        },
    )

    assert response.status_code == 422


def test_zero_quote_quantity_is_rejected(client):
    response = client.post(
        "/api/v1/supplier-quotes",
        json={
            "supplier_id": 1,
            "product_id": 1,
            "unit_price": 100,
            "currency": "USD",
            "quantity": 0,
            "quote_date": "2026-08-28T16:00:00",
        },
    )

    assert response.status_code == 422


def test_empty_product_name_is_rejected(client):
    response = client.post(
        "/api/v1/products",
        json={"name": "", "sku": "VALID-SKU"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "query",
    ["skip=-1", "limit=0", "limit=1001"],
)
def test_invalid_product_pagination_is_rejected(client, query):
    response = client.get(f"/api/v1/products?{query}")

    assert response.status_code == 422


def test_missing_jwt_secret_fails_clearly(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", None)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_access_token(1)
