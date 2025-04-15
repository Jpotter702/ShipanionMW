import pytest
from unittest.mock import AsyncMock
from auth.token_manager import TokenManager
from auth.fedex_auth import FedExAuthProvider
from utils.exceptions import AuthenticationError

@pytest.mark.asyncio
async def test_register_provider():
    """Test provider registration"""
    manager = TokenManager()
    provider = FedExAuthProvider("test_id", "test_secret")
    
    manager.register_provider("fedex", provider)
    assert manager.get_provider("fedex") == provider

@pytest.mark.asyncio
async def test_get_token_success():
    """Test successful token retrieval"""
    manager = TokenManager()
    provider = FedExAuthProvider("test_id", "test_secret")
    manager.register_provider("fedex", provider)
    
    with pytest.patch.object(provider, "get_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "test_token"
        token = await manager.get_token("fedex")
        assert token == "test_token"

@pytest.mark.asyncio
async def test_get_token_provider_not_found():
    """Test token retrieval with non-existent provider"""
    manager = TokenManager()
    
    with pytest.raises(AuthenticationError):
        await manager.get_token("nonexistent")

@pytest.mark.asyncio
async def test_get_provider():
    """Test provider retrieval"""
    manager = TokenManager()
    provider = FedExAuthProvider("test_id", "test_secret")
    
    manager.register_provider("fedex", provider)
    assert manager.get_provider("fedex") == provider
    assert manager.get_provider("nonexistent") is None 