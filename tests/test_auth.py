from uuid import uuid4

import pytest

from app.api.dependencies import get_current_admin, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.user import User
from app.repositories.user import user_repository
from tests.conftest import TestSessionLocal


@pytest.fixture()
def auth_client(client, monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", "test-jwt-secret")
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_current_admin, None)
    return client


def user_credentials() -> dict:
    unique_id = uuid4().hex[:8]
    return {
        "email": f"user-{unique_id}@example.com",
        "password": "SecurePass123",
    }


def register_user(client) -> dict:
    credentials = user_credentials()
    response = client.post("/api/v1/auth/register", json=credentials)

    assert response.status_code == 201
    return credentials


def login_user(client, credentials: dict) -> str:
    response = client.post("/api/v1/auth/login", json=credentials)

    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_user_registration_succeeds(auth_client):
    credentials = user_credentials()

    response = auth_client.post("/api/v1/auth/register", json=credentials)

    assert response.status_code == 201
    assert response.json()["email"] == credentials["email"]
    assert "hashed_password" not in response.json()
    assert "password" not in response.json()


def test_password_is_hashed(auth_client):
    credentials = register_user(auth_client)
    db = TestSessionLocal()

    try:
        user = user_repository.get_by_email(db, credentials["email"])
        assert user is not None
        assert user.hashed_password != credentials["password"]
        assert user.hashed_password.startswith("$2")
    finally:
        db.close()


def test_plaintext_password_is_not_stored(auth_client):
    credentials = register_user(auth_client)
    db = TestSessionLocal()

    try:
        user = user_repository.get_by_email(db, credentials["email"])
        assert credentials["password"] not in user.hashed_password
    finally:
        db.close()


def test_duplicate_email_is_rejected(auth_client):
    credentials = register_user(auth_client)

    response = auth_client.post("/api/v1/auth/register", json=credentials)

    assert response.status_code == 409


def test_login_succeeds_with_correct_credentials(auth_client):
    credentials = register_user(auth_client)

    response = auth_client.post("/api/v1/auth/login", json=credentials)

    assert response.status_code == 200


def test_login_fails_with_incorrect_password(auth_client):
    credentials = register_user(auth_client)

    response = auth_client.post(
        "/api/v1/auth/login",
        json={**credentials, "password": "IncorrectPass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_fails_for_unknown_email(auth_client):
    response = auth_client.post(
        "/api/v1/auth/login",
        json=user_credentials(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_inactive_user_cannot_authenticate(auth_client):
    credentials = register_user(auth_client)
    db = TestSessionLocal()

    try:
        user = user_repository.get_by_email(db, credentials["email"])
        user.is_active = False
        db.commit()
    finally:
        db.close()

    response = auth_client.post("/api/v1/auth/login", json=credentials)

    assert response.status_code == 401


def test_successful_login_returns_jwt(auth_client):
    token = login_user(auth_client, register_user(auth_client))

    assert isinstance(token, str)
    assert token.count(".") == 2


def test_authenticated_request_succeeds(auth_client):
    token = login_user(auth_client, register_user(auth_client))

    response = auth_client.get(
        "/api/v1/suppliers",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_missing_token_returns_401(auth_client):
    response = auth_client.get("/api/v1/suppliers")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_invalid_token_returns_401(auth_client):
    response = auth_client.get(
        "/api/v1/suppliers",
        headers=auth_headers("invalid-token"),
    )

    assert response.status_code == 401


def test_expired_token_returns_401(auth_client, monkeypatch):
    credentials = register_user(auth_client)
    db = TestSessionLocal()

    try:
        user = user_repository.get_by_email(db, credentials["email"])
        monkeypatch.setattr(settings, "jwt_access_token_expire_minutes", -1)
        expired_token = create_access_token(user.id)
    finally:
        db.close()

    response = auth_client.get(
        "/api/v1/suppliers",
        headers=auth_headers(expired_token),
    )

    assert response.status_code == 401


def test_normal_user_cannot_perform_admin_delete(auth_client):
    token = login_user(auth_client, register_user(auth_client))
    response = auth_client.post(
        "/api/v1/products",
        headers=auth_headers(token),
        json={"name": "Admin Test Product", "sku": "ADMIN-TEST-001"},
    )
    product_id = response.json()["id"]

    response = auth_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_admin_can_perform_admin_delete(auth_client):
    credentials = register_user(auth_client)
    token = login_user(auth_client, credentials)
    db = TestSessionLocal()

    try:
        user = user_repository.get_by_email(db, credentials["email"])
        user.is_admin = True
        db.commit()
    finally:
        db.close()

    response = auth_client.post(
        "/api/v1/products",
        headers=auth_headers(token),
        json={"name": "Admin Delete Product", "sku": "ADMIN-DELETE-001"},
    )
    product_id = response.json()["id"]

    response = auth_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 204


def test_public_root_endpoint_remains_accessible(auth_client):
    assert auth_client.get("/").status_code == 200


def test_public_health_endpoint_remains_accessible(auth_client):
    assert auth_client.get("/health").status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/suppliers",
        "/api/v1/products",
        "/api/v1/supplier-quotes",
        "/api/v1/products/1/price-comparison",
        "/api/v1/products/1/procurement-analysis",
        "/api/v1/products/1/supplier-ranking",
        "/api/v1/products/1/ai-recommendation",
    ],
)
def test_protected_endpoints_reject_unauthenticated_requests(
    auth_client,
    path,
):
    response = auth_client.get(path)

    assert response.status_code == 401
