import pytest
from fastapi.testclient import TestClient
from app.main import app
from auth.token_manager import TokenManager
from auth.fedex_auth import FedExAuth

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def token_manager():
    return TokenManager()

@pytest.fixture
def fedex_auth_provider():
    return FedExAuth()