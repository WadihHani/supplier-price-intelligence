from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ai import MockAIProvider, OpenAIProvider
from app.services.procurement_recommendation import (
    ProcurementRecommendationService,
    get_procurement_recommendation_service,
)


class FailingAIProvider:

    def generate_procurement_explanation(self, analysis: dict) -> str:
        raise RuntimeError("Provider unavailable")


class StaticAIProvider:

    def __init__(self, explanation: str):
        self.explanation = explanation
        self.analyses: list[dict] = []

    def generate_procurement_explanation(self, analysis: dict) -> str:
        self.analyses.append(analysis)
        return self.explanation


@pytest.fixture(autouse=True)
def mock_ai_provider():
    app.dependency_overrides[get_procurement_recommendation_service] = (
        lambda: ProcurementRecommendationService(MockAIProvider())
    )
    yield
    app.dependency_overrides.pop(get_procurement_recommendation_service, None)


def set_ai_provider(provider) -> None:
    app.dependency_overrides[get_procurement_recommendation_service] = (
        lambda: ProcurementRecommendationService(provider)
    )


def create_supplier(
    client: TestClient,
    reliability_score: float | None = None,
    delivery_score: float | None = None,
) -> tuple[int, str]:
    unique_id = uuid4().hex[:8]
    name = f"Recommendation Supplier {unique_id}"
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": name,
            "code": f"RECOMMENDATION-SUP-{unique_id}",
            "email": f"{unique_id}@example.com",
            "reliability_score": reliability_score,
            "delivery_score": delivery_score,
        },
    )

    assert response.status_code == 201
    return response.json()["id"], name


def create_product(client: TestClient) -> int:
    unique_id = uuid4().hex[:8]
    response = client.post(
        "/api/v1/products",
        json={
            "name": f"Recommendation Product {unique_id}",
            "sku": f"RECOMMENDATION-PROD-{unique_id}",
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


def get_recommendations(client: TestClient, product_id: int) -> dict:
    response = client.get(
        f"/api/v1/products/{product_id}/ai-recommendation"
    )

    assert response.status_code == 200
    return response.json()


def test_recommendation_for_product_with_one_quote(client: TestClient):
    product_id = create_product(client)
    supplier_id, supplier_name = create_supplier(client)
    create_quote(client, supplier_id, product_id, 100)

    recommendation = get_recommendations(client, product_id)[
        "recommendations"
    ][0]

    assert recommendation["supplier_id"] == supplier_id
    assert recommendation["supplier_name"] == supplier_name


def test_highest_scoring_supplier_is_selected(client: TestClient):
    product_id = create_product(client)
    cheap_supplier_id, _ = create_supplier(client)
    high_score_supplier_id, _ = create_supplier(
        client,
        reliability_score=100,
        delivery_score=100,
    )
    create_quote(client, cheap_supplier_id, product_id, 80)
    create_quote(client, high_score_supplier_id, product_id, 90)

    recommendation = get_recommendations(client, product_id)[
        "recommendations"
    ][0]

    assert recommendation["supplier_id"] == high_score_supplier_id


def test_deterministic_score_and_unit_price_are_in_response(
    client: TestClient,
):
    product_id = create_product(client)
    supplier_id, _ = create_supplier(client)
    create_quote(client, supplier_id, product_id, 100)

    recommendation = get_recommendations(client, product_id)[
        "recommendations"
    ][0]

    assert recommendation["final_score"] == 82.5
    assert recommendation["unit_price"] == 100


def test_ai_explanation_appears_in_response(client: TestClient):
    product_id = create_product(client)
    create_quote(client, create_supplier(client)[0], product_id, 100)

    recommendation = get_recommendations(client, product_id)[
        "recommendations"
    ][0]

    assert "recommended" in recommendation["explanation"]


def test_multiple_currencies_produce_independent_recommendations(
    client: TestClient,
):
    product_id = create_product(client)
    supplier_one_id, _ = create_supplier(client)
    supplier_two_id, _ = create_supplier(client)
    create_quote(client, supplier_one_id, product_id, 80, "USD")
    create_quote(client, supplier_two_id, product_id, 100, "USD")
    create_quote(client, supplier_one_id, product_id, 300, "EUR")
    create_quote(client, supplier_two_id, product_id, 250, "EUR")

    recommendations = {
        recommendation["currency"]: recommendation
        for recommendation in get_recommendations(client, product_id)[
            "recommendations"
        ]
    }

    assert recommendations["USD"]["supplier_id"] == supplier_one_id
    assert recommendations["EUR"]["supplier_id"] == supplier_two_id


def test_different_currencies_are_never_compared(client: TestClient):
    product_id = create_product(client)
    usd_supplier_id, _ = create_supplier(client)
    eur_supplier_id, _ = create_supplier(client)
    create_quote(client, usd_supplier_id, product_id, 100, "USD")
    create_quote(client, eur_supplier_id, product_id, 1, "EUR")

    recommendations = get_recommendations(client, product_id)["recommendations"]

    assert {item["currency"] for item in recommendations} == {"USD", "EUR"}
    assert {item["supplier_id"] for item in recommendations} == {
        usd_supplier_id,
        eur_supplier_id,
    }


def test_nonexistent_product_returns_404(client: TestClient):
    response = client.get("/api/v1/products/999999/ai-recommendation")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_product_with_no_quotes_returns_empty_recommendations(
    client: TestClient,
):
    product_id = create_product(client)

    assert get_recommendations(client, product_id)["recommendations"] == []


def test_ai_provider_failure_uses_deterministic_fallback(client: TestClient):
    set_ai_provider(FailingAIProvider())
    product_id = create_product(client)
    supplier_id, supplier_name = create_supplier(client)
    create_quote(client, supplier_id, product_id, 100)

    recommendation = get_recommendations(client, product_id)[
        "recommendations"
    ][0]

    assert supplier_name in recommendation["explanation"]
    assert "82.5" in recommendation["explanation"]


def test_missing_ai_api_key_does_not_break_endpoint(client: TestClient):
    set_ai_provider(OpenAIProvider(api_key=None, model="test-model"))
    product_id = create_product(client)
    create_quote(client, create_supplier(client)[0], product_id, 100)

    assert get_recommendations(client, product_id)["recommendations"]


def test_inactive_quotes_are_excluded(client: TestClient):
    product_id = create_product(client)
    active_supplier_id, _ = create_supplier(client)
    inactive_supplier_id, _ = create_supplier(client)
    create_quote(client, active_supplier_id, product_id, 100)
    inactive_quote = create_quote(
        client,
        inactive_supplier_id,
        product_id,
        50,
    )
    response = client.put(
        f"/api/v1/supplier-quotes/{inactive_quote['id']}",
        json={"is_active": False},
    )

    assert response.status_code == 200
    recommendation = get_recommendations(client, product_id)[
        "recommendations"
    ][0]
    assert recommendation["supplier_id"] == active_supplier_id


def test_ai_response_cannot_override_deterministic_recommendation(
    client: TestClient,
):
    provider = StaticAIProvider("Choose Supplier B.")
    set_ai_provider(provider)
    product_id = create_product(client)
    preferred_supplier_id, _ = create_supplier(client)
    create_quote(client, preferred_supplier_id, product_id, 80)
    create_quote(client, create_supplier(client)[0], product_id, 100)

    recommendation = get_recommendations(client, product_id)[
        "recommendations"
    ][0]

    assert recommendation["supplier_id"] == preferred_supplier_id
    assert recommendation["explanation"] == "Choose Supplier B."


def test_ai_provider_receives_structured_procurement_facts(
    client: TestClient,
):
    provider = StaticAIProvider("Structured facts received.")
    set_ai_provider(provider)
    product_id = create_product(client)
    create_quote(client, create_supplier(client)[0], product_id, 100)

    get_recommendations(client, product_id)

    assert len(provider.analyses) == 1
    facts = provider.analyses[0]
    assert set(facts) == {
        "product",
        "currency",
        "suppliers",
        "price_difference",
        "recommendation",
    }
    assert facts["product"]["id"] == product_id
    assert facts["suppliers"][0]["quantity"] == 10


def test_ai_provider_does_not_receive_secrets(client: TestClient):
    provider = StaticAIProvider("No secrets received.")
    set_ai_provider(provider)
    product_id = create_product(client)
    create_quote(client, create_supplier(client)[0], product_id, 100)

    get_recommendations(client, product_id)

    facts = provider.analyses[0]
    assert "database_url" not in facts
    assert "api_key" not in facts
    assert "AI_API_KEY" not in facts
