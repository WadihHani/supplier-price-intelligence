from uuid import uuid4

def create_supplier(client):
    unique_id = uuid4().hex[:8]

    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": f"Quote Test Supplier {unique_id}",
            "code": f"QUOTE-SUP-{unique_id}",
            "email": f"{unique_id}@example.com",
            "country": "Lebanon",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_product(client):
    unique_id = uuid4().hex[:8]

    response = client.post(
        "/api/v1/products",
        json={
            "name": f"Quote Test Product {unique_id}",
            "sku": f"QUOTE-PROD-{unique_id}",
            "category": "Electronics",
            "unit": "piece",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_quote(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    response = client.post(
        "/api/v1/supplier-quotes",
        json={
            "supplier_id": supplier_id,
            "product_id": product_id,
            "unit_price": 720.50,
            "currency": "USD",
            "quantity": 10,
            "quote_date": "2026-08-28T16:00:00",
            "valid_until": "2026-09-28T23:59:59",
            "notes": "Test quote",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_supplier_quote(client):
    quote = create_quote(client)

    assert quote["unit_price"] == 720.50
    assert quote["currency"] == "USD"
    assert quote["quantity"] == 10
    assert quote["is_active"] is True


def test_supplier_quote_supplier_not_found(client):
    product_id = create_product(client)

    response = client.post(
        "/api/v1/supplier-quotes",
        json={
            "supplier_id": 999999,
            "product_id": product_id,
            "unit_price": 700,
            "currency": "USD",
            "quantity": 1,
            "quote_date": "2026-08-28T16:00:00",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found."


def test_supplier_quote_product_not_found(client):
    supplier_id = create_supplier(client)

    response = client.post(
        "/api/v1/supplier-quotes",
        json={
            "supplier_id": supplier_id,
            "product_id": 999999,
            "unit_price": 700,
            "currency": "USD",
            "quantity": 1,
            "quote_date": "2026-08-28T16:00:00",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_get_supplier_quote(client):
    quote = create_quote(client)

    response = client.get(
        f"/api/v1/supplier-quotes/{quote['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == quote["id"]


def test_update_supplier_quote(client):
    quote = create_quote(client)

    response = client.put(
        f"/api/v1/supplier-quotes/{quote['id']}",
        json={
            "unit_price": 680.00,
            "quantity": 20,
            "notes": "Updated quote",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["unit_price"] == 680.00
    assert data["quantity"] == 20
    assert data["notes"] == "Updated quote"


def test_delete_supplier_quote(client):
    quote = create_quote(client)

    response = client.delete(
        f"/api/v1/supplier-quotes/{quote['id']}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/supplier-quotes/{quote['id']}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier quote not found."
