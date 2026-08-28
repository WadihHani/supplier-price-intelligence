from uuid import uuid4

from fastapi.testclient import TestClient


def create_supplier(
    client: TestClient,
    reliability_score: float | None = None,
    delivery_score: float | None = None,
) -> int:
    unique_id = uuid4().hex[:8]
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": f"Scoring Supplier {unique_id}",
            "code": f"SCORING-SUP-{unique_id}",
            "email": f"{unique_id}@example.com",
            "reliability_score": reliability_score,
            "delivery_score": delivery_score,
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_product(client: TestClient) -> int:
    unique_id = uuid4().hex[:8]
    response = client.post(
        "/api/v1/products",
        json={
            "name": f"Scoring Product {unique_id}",
            "sku": f"SCORING-PROD-{unique_id}",
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


def get_ranking(client: TestClient, product_id: int) -> dict:
    response = client.get(
        f"/api/v1/products/{product_id}/supplier-ranking"
    )

    assert response.status_code == 200
    return response.json()


def get_usd_scores(client: TestClient, product_id: int) -> list[dict]:
    return get_ranking(client, product_id)["currency_rankings"][0][
        "ranked_suppliers"
    ]


def test_lowest_price_supplier_receives_price_score_of_100(client: TestClient):
    product_id = create_product(client)
    cheapest_supplier_id = create_supplier(client)
    create_quote(client, cheapest_supplier_id, product_id, 80)
    create_quote(client, create_supplier(client), product_id, 100)

    scores = get_usd_scores(client, product_id)
    cheapest_score = next(
        score for score in scores if score["supplier_id"] == cheapest_supplier_id
    )

    assert cheapest_score["price_score"] == 100


def test_higher_priced_supplier_receives_lower_price_score(client: TestClient):
    product_id = create_product(client)
    create_quote(client, create_supplier(client), product_id, 80)
    expensive_supplier_id = create_supplier(client)
    create_quote(client, expensive_supplier_id, product_id, 100)

    scores = get_usd_scores(client, product_id)
    expensive_score = next(
        score for score in scores if score["supplier_id"] == expensive_supplier_id
    )

    assert expensive_score["price_score"] == 80


def test_reliability_score_affects_final_score(client: TestClient):
    product_id = create_product(client)
    reliable_supplier_id = create_supplier(client, reliability_score=90)
    neutral_supplier_id = create_supplier(client, reliability_score=50)
    create_quote(client, reliable_supplier_id, product_id, 100)
    create_quote(client, neutral_supplier_id, product_id, 100)

    scores = get_usd_scores(client, product_id)
    reliable_score = next(
        score for score in scores if score["supplier_id"] == reliable_supplier_id
    )
    neutral_score = next(
        score for score in scores if score["supplier_id"] == neutral_supplier_id
    )

    assert reliable_score["final_score"] > neutral_score["final_score"]


def test_delivery_score_affects_final_score(client: TestClient):
    product_id = create_product(client)
    fast_supplier_id = create_supplier(client, delivery_score=90)
    neutral_supplier_id = create_supplier(client, delivery_score=50)
    create_quote(client, fast_supplier_id, product_id, 100)
    create_quote(client, neutral_supplier_id, product_id, 100)

    scores = get_usd_scores(client, product_id)
    fast_score = next(
        score for score in scores if score["supplier_id"] == fast_supplier_id
    )
    neutral_score = next(
        score for score in scores if score["supplier_id"] == neutral_supplier_id
    )

    assert fast_score["final_score"] > neutral_score["final_score"]


def test_inactive_supplier_receives_zero_activity_score(client: TestClient):
    product_id = create_product(client)
    supplier_id = create_supplier(client)
    create_quote(client, supplier_id, product_id, 100)
    response = client.put(
        f"/api/v1/suppliers/{supplier_id}",
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert get_usd_scores(client, product_id)[0]["activity_score"] == 0


def test_missing_reliability_score_uses_neutral_value(client: TestClient):
    product_id = create_product(client)
    create_quote(client, create_supplier(client), product_id, 100)

    assert get_usd_scores(client, product_id)[0]["reliability_score"] == 50


def test_missing_delivery_score_uses_neutral_value(client: TestClient):
    product_id = create_product(client)
    create_quote(client, create_supplier(client), product_id, 100)

    assert get_usd_scores(client, product_id)[0]["delivery_score"] == 50


def test_final_score_uses_exact_weighting(client: TestClient):
    product_id = create_product(client)
    supplier_id = create_supplier(
        client,
        reliability_score=80,
        delivery_score=60,
    )
    create_quote(client, supplier_id, product_id, 100)

    assert get_usd_scores(client, product_id)[0]["final_score"] == 90


def test_suppliers_are_ranked_by_final_score_descending(client: TestClient):
    product_id = create_product(client)
    create_quote(client, create_supplier(client), product_id, 80)
    create_quote(
        client,
        create_supplier(client, reliability_score=100, delivery_score=100),
        product_id,
        90,
    )

    scores = get_usd_scores(client, product_id)

    assert [score["final_score"] for score in scores] == sorted(
        (score["final_score"] for score in scores),
        reverse=True,
    )
    assert [score["rank"] for score in scores] == [1, 2]


def test_different_currencies_are_ranked_independently(client: TestClient):
    product_id = create_product(client)
    supplier_one_id = create_supplier(client)
    supplier_two_id = create_supplier(client)
    create_quote(client, supplier_one_id, product_id, 80, "USD")
    create_quote(client, supplier_two_id, product_id, 100, "USD")
    create_quote(client, supplier_one_id, product_id, 300, "EUR")
    create_quote(client, supplier_two_id, product_id, 250, "EUR")

    rankings = {
        ranking["currency"]: ranking
        for ranking in get_ranking(client, product_id)["currency_rankings"]
    }

    assert rankings["USD"]["recommendation"]["supplier_id"] == supplier_one_id
    assert rankings["EUR"]["recommendation"]["supplier_id"] == supplier_two_id


def test_nonexistent_product_returns_404(client: TestClient):
    response = client.get("/api/v1/products/999999/supplier-ranking")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_product_with_no_quotes_returns_empty_ranking(client: TestClient):
    product_id = create_product(client)

    assert get_ranking(client, product_id)["currency_rankings"] == []


def test_inactive_quotes_are_excluded(client: TestClient):
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
    scores = get_usd_scores(client, product_id)
    assert len(scores) == 1
    assert scores[0]["quote_id"] == active_quote["id"]


def test_zero_price_does_not_cause_division_by_zero(client: TestClient):
    product_id = create_product(client)
    create_quote(client, create_supplier(client), product_id, 0)
    create_quote(client, create_supplier(client), product_id, 100)

    scores = get_usd_scores(client, product_id)

    assert scores[0]["price_score"] == 100
    assert scores[1]["price_score"] == 0


def test_scores_remain_between_zero_and_100(client: TestClient):
    product_id = create_product(client)
    create_quote(
        client,
        create_supplier(client, reliability_score=0, delivery_score=0),
        product_id,
        50,
    )
    create_quote(
        client,
        create_supplier(client, reliability_score=100, delivery_score=100),
        product_id,
        100,
    )

    for score in get_usd_scores(client, product_id):
        assert 0 <= score["price_score"] <= 100
        assert 0 <= score["reliability_score"] <= 100
        assert 0 <= score["delivery_score"] <= 100
        assert 0 <= score["activity_score"] <= 100
        assert 0 <= score["final_score"] <= 100
