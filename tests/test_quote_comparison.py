from fastapi.testclient import TestClient


def create_supplier(client: TestClient, name: str) -> int:
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": name,
            "code": name.upper().replace(" ", "-"),
            "email": f"{name.lower().replace(' ', '.')}@example.com",
            "country": "Lebanon",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_product(client: TestClient) -> int:
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Comparison Product",
            "sku": "COMPARISON-PRODUCT",
            "unit": "piece",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_quote(
    client: TestClient,
    supplier_id: int,
    product_id: int,
    unit_price: float,
    currency: str = "USD",
) -> dict:
    response = client.post(
        "/api/v1/supplier-quotes",
        json={
            "supplier_id": supplier_id,
            "product_id": product_id,
            "unit_price": unit_price,
            "currency": currency,
            "quantity": 10,
            "quote_date": "2026-08-28T16:00:00",
        },
    )

    assert response.status_code == 201
    return response.json()


def get_comparison(client: TestClient, product_id: int) -> dict:
    response = client.get(
        f"/api/v1/products/{product_id}/price-comparison"
    )

    assert response.status_code == 200
    return response.json()


def test_comparison_for_product_with_one_quote(client: TestClient):
    product_id = create_product(client)
    supplier_id = create_supplier(client, "Single Quote Supplier")
    quote = create_quote(client, supplier_id, product_id, 100)

    comparison = get_comparison(client, product_id)

    assert comparison["product_id"] == product_id
    assert comparison["product_name"] == "Comparison Product"
    assert comparison["quotes"] == [
        {
            "quote_id": quote["id"],
            "supplier_id": supplier_id,
            "supplier_name": "Single Quote Supplier",
            "product_id": product_id,
            "product_name": "Comparison Product",
            "unit_price": 100.0,
            "currency": "USD",
            "quantity": 10,
            "rank": 1,
        }
    ]
    assert comparison["recommendations"] == comparison["quotes"]


def test_comparison_with_multiple_suppliers_ranks_lowest_price_first(
    client: TestClient,
):
    product_id = create_product(client)
    expensive_supplier_id = create_supplier(client, "Expensive Supplier")
    cheapest_supplier_id = create_supplier(client, "Cheapest Supplier")
    create_quote(client, expensive_supplier_id, product_id, 120)
    cheapest_quote = create_quote(client, cheapest_supplier_id, product_id, 90)

    comparison = get_comparison(client, product_id)

    assert [quote["supplier_id"] for quote in comparison["quotes"]] == [
        cheapest_supplier_id,
        expensive_supplier_id,
    ]
    assert [quote["rank"] for quote in comparison["quotes"]] == [1, 2]
    assert comparison["quotes"][0]["quote_id"] == cheapest_quote["id"]


def test_recommendations_contain_cheapest_quote_for_each_currency(
    client: TestClient,
):
    product_id = create_product(client)
    supplier_one_id = create_supplier(client, "Supplier One")
    supplier_two_id = create_supplier(client, "Supplier Two")
    create_quote(client, supplier_one_id, product_id, 100, "USD")
    cheapest_usd_quote = create_quote(
        client, supplier_two_id, product_id, 80, "USD"
    )
    cheapest_eur_quote = create_quote(
        client, supplier_one_id, product_id, 70, "EUR"
    )
    create_quote(client, supplier_two_id, product_id, 95, "EUR")

    comparison = get_comparison(client, product_id)

    assert {quote["quote_id"] for quote in comparison["recommendations"]} == {
        cheapest_usd_quote["id"],
        cheapest_eur_quote["id"],
    }


def test_different_currencies_are_ranked_separately(client: TestClient):
    product_id = create_product(client)
    supplier_one_id = create_supplier(client, "Currency Supplier One")
    supplier_two_id = create_supplier(client, "Currency Supplier Two")
    create_quote(client, supplier_one_id, product_id, 100, "USD")
    create_quote(client, supplier_two_id, product_id, 80, "USD")
    create_quote(client, supplier_one_id, product_id, 200, "EUR")
    create_quote(client, supplier_two_id, product_id, 250, "EUR")

    comparison = get_comparison(client, product_id)
    ranks_by_currency = {
        currency: [quote["rank"] for quote in comparison["quotes"] if quote["currency"] == currency]
        for currency in {quote["currency"] for quote in comparison["quotes"]}
    }

    assert ranks_by_currency == {"USD": [1, 2], "EUR": [1, 2]}


def test_comparison_for_nonexistent_product_returns_404(client: TestClient):
    response = client.get("/api/v1/products/999999/price-comparison")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_comparison_for_product_with_no_quotes_is_empty(client: TestClient):
    product_id = create_product(client)

    comparison = get_comparison(client, product_id)

    assert comparison == {
        "product_id": product_id,
        "product_name": "Comparison Product",
        "quotes": [],
        "recommendations": [],
    }
