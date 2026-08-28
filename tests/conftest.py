import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
from app.api.dependencies import get_current_admin, get_current_user
from app.main import app
from app.models.user import User


TEST_DATABASE_URL = "sqlite:///./supplier_intelligence_test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    test_admin = User(
        id=1,
        email="test-admin@example.com",
        hashed_password="not-used-in-tests",
        is_active=True,
        is_admin=True,
    )
    app.dependency_overrides[get_current_user] = lambda: test_admin
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=test_engine)
