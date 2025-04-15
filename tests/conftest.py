import pytest
from fastapi.testclient import TestClient
from app.main import app
from auth.token_manager import TokenManager
from auth.fedex_auth import FedExAuthProvider

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def token_manager():
    return TokenManager()

@pytest.fixture
def fedex_auth_provider():
    return FedExAuthProvider(
        client_id="test_client_id",
        client_secret="test_client_secret"
    ) 