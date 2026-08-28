from uuid import uuid4

from fastapi.testclient import TestClient


def create_supplier(client: TestClient) -> int:
    unique_id = uuid4().hex[:8]
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": f"Analysis Supplier {unique_id}",
            "code": f"ANALYSIS-SUP-{unique_id}",
            "email": f"{unique_id}@example.com",
            "country": "Lebanon",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_product(client: TestClient) -> int:
    unique_id = uuid4().hex[:8]
    response = client.post(
        "/api/v1/products",
        json={
            "name": f"Analysis Product {unique_id}",
            "sku": f"ANALYSIS-PROD-{unique_id}",
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


def get_analysis(client: TestClient, product_id: int) -> dict:
    response = client.get(
        f"/api/v1/products/{product_id}/procurement-analysis"
    )

    assert response.status_code == 200
    return response.json()


def test_analysis_for_product_with_one_quote(client: TestClient):
    product_id = create_product(client)
    supplier_id = create_supplier(client)
    quote = create_quote(client, supplier_id, product_id, 100)

    analysis = get_analysis(client, product_id)
    currency_analysis = analysis["currency_analyses"][0]

    assert currency_analysis["number_of_quotes"] == 1
    assert currency_analysis["lowest_price"] == 100
    assert currency_analysis["highest_price"] == 100
    assert currency_analysis["cheapest_quote"]["quote_id"] == quote["id"]
    assert currency_analysis["most_expensive_quote"]["quote_id"] == quote["id"]


def test_analysis_for_multiple_quotes_calculates_price_metrics(
    client: TestClient,
):
    product_id = create_product(client)
    supplier_one_id = create_supplier(client)
    supplier_two_id = create_supplier(client)
    create_quote(client, supplier_one_id, product_id, 720)
    create_quote(client, supplier_two_id, product_id, 680)

    currency_analysis = get_analysis(client, product_id)[
        "currency_analyses"
    ][0]

    assert currency_analysis["number_of_quotes"] == 2
    assert currency_analysis["lowest_price"] == 680
    assert currency_analysis["highest_price"] == 720
    assert currency_analysis["average_price"] == 700
    assert currency_analysis["price_difference"] == 40


def test_analysis_calculates_savings_amount_and_percentage(
    client: TestClient,
):
    product_id = create_product(client)
    create_quote(client, create_supplier(client), product_id, 720)
    create_quote(client, create_supplier(client), product_id, 680)

    currency_analysis = get_analysis(client, product_id)[
        "currency_analyses"
    ][0]

    assert currency_analysis["potential_savings"] == 40
    assert currency_analysis["savings_percentage"] == 5.555555555555555
    assert currency_analysis["price_difference_percentage"] == 5.555555555555555


def test_multiple_currencies_are_analyzed_independently(client: TestClient):
    product_id = create_product(client)
    supplier_one_id = create_supplier(client)
    supplier_two_id = create_supplier(client)
    create_quote(client, supplier_one_id, product_id, 100, "USD")
    create_quote(client, supplier_two_id, product_id, 80, "USD")
    create_quote(client, supplier_one_id, product_id, 300, "EUR")
    create_quote(client, supplier_two_id, product_id, 250, "EUR")

    analyses = {
        analysis["currency"]: analysis
        for analysis in get_analysis(client, product_id)["currency_analyses"]
    }

    assert analyses["USD"]["lowest_price"] == 80
    assert analyses["USD"]["highest_price"] == 100
    assert analyses["EUR"]["lowest_price"] == 250
    assert analyses["EUR"]["highest_price"] == 300


def test_analysis_for_nonexistent_product_returns_404(client: TestClient):
    response = client.get(
        "/api/v1/products/999999/procurement-analysis"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_analysis_for_product_with_no_quotes_is_empty(client: TestClient):
    product_id = create_product(client)

    analysis = get_analysis(client, product_id)

    assert analysis["currency_analyses"] == []


def test_zero_price_does_not_cause_division_by_zero(client: TestClient):
    product_id = create_product(client)
    create_quote(client, create_supplier(client), product_id, 0)

    currency_analysis = get_analysis(client, product_id)[
        "currency_analyses"
    ][0]

    assert currency_analysis["price_difference_percentage"] == 0
    assert currency_analysis["savings_percentage"] == 0


def test_inactive_quotes_are_excluded_from_analysis(client: TestClient):
    product_id = create_product(client)
    active_quote = create_quote(
        client,
        create_supplier(client),
        product_id,
        100,
    )
    inactive_quote = create_quote(
        client,
        create_supplier(client),
        product_id,
        50,
    )
    response = client.put(
        f"/api/v1/supplier-quotes/{inactive_quote['id']}",
        json={"is_active": False},
    )

    assert response.status_code == 200

    currency_analysis = get_analysis(client, product_id)[
        "currency_analyses"
    ][0]

    assert currency_analysis["number_of_quotes"] == 1
    assert currency_analysis["lowest_price"] == 100
    assert currency_analysis["cheapest_quote"]["quote_id"] == active_quote["id"]
