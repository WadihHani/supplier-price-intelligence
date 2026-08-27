def test_create_product(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Test Laptop",
            "sku": "TEST-LAP-001",
            "description": "Test product",
            "category": "Electronics",
            "unit": "piece",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Laptop"
    assert data["sku"] == "TEST-LAP-001"
    assert data["category"] == "Electronics"
    assert data["unit"] == "piece"
    assert data["is_active"] is True


def test_duplicate_product_sku(client):
    client.post(
        "/api/v1/products",
        json={
            "name": "Original Product",
            "sku": "DUPLICATE-SKU-001",
            "category": "Electronics",
        },
    )

    response = client.post(
        "/api/v1/products",
        json={
            "name": "Duplicate Product",
            "sku": "DUPLICATE-SKU-001",
            "category": "Electronics",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A product with this SKU already exists."
    )


def test_get_product(client):
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Get Test Product",
            "sku": "GET-PRODUCT-001",
            "category": "Electronics",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/products/{product_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["sku"] == "GET-PRODUCT-001"


def test_product_not_found(client):
    response = client.get(
        "/api/v1/products/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_update_product(client):
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Update Test Product",
            "sku": "UPDATE-PRODUCT-001",
            "category": "Electronics",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Updated Product",
            "category": "Computers",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Product"
    assert data["category"] == "Computers"
    assert data["sku"] == "UPDATE-PRODUCT-001"


def test_delete_product(client):
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Delete Test Product",
            "sku": "DELETE-PRODUCT-001",
            "category": "Electronics",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/products/{product_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/products/{product_id}"
    )

    assert get_response.status_code == 404
