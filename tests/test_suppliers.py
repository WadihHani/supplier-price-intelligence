def test_create_supplier(client):
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Test Supplier",
            "code": "TEST-001",
            "email": "test@example.com",
            "phone": "+96170000000",
            "country": "Lebanon",
            "website": "https://example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Supplier"
    assert data["code"] == "TEST-001"
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


def test_duplicate_supplier_code(client):
    client.post(
        "/api/v1/suppliers",
        json={
            "name": "Original Supplier",
            "code": "DUPLICATE-001",
            "email": "original@example.com",
        },
    )

    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Duplicate Supplier",
            "code": "DUPLICATE-001",
            "email": "duplicate@example.com",
        },
    )

    assert response.status_code == 409


def test_get_supplier(client):
    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Get Test Supplier",
            "code": "GET-001",
            "email": "get@example.com",
        },
    )

    assert create_response.status_code == 201

    supplier_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/suppliers/{supplier_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == supplier_id


def test_supplier_not_found(client):
    response = client.get("/api/v1/suppliers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found."


def test_update_supplier(client):
    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Update Test Supplier",
            "code": "UPDATE-001",
            "email": "update@example.com",
        },
    )

    assert create_response.status_code == 201

    supplier_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/suppliers/{supplier_id}",
        json={
            "phone": "+96171111111",
        },
    )

    assert response.status_code == 200
    assert response.json()["phone"] == "+96171111111"
    assert response.json()["name"] == "Update Test Supplier"


def test_delete_supplier(client):
    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Delete Test Supplier",
            "code": "DELETE-001",
            "email": "delete@example.com",
        },
    )

    assert create_response.status_code == 201

    supplier_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/suppliers/{supplier_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/suppliers/{supplier_id}"
    )

    assert get_response.status_code == 404
