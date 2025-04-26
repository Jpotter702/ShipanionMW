import pytest
from unittest.mock import patch, AsyncMock
from auth.fedex_auth import FedExAuth
from utils.exceptions import AuthenticationError

@pytest.mark.asyncio
async def test_token_refresh_success(fedex_auth_provider):
    """Test successful token refresh"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_token",
        "token_type": "Bearer",
        "expires_in": 3600
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        await fedex_auth_provider.refresh_token()

        assert fedex_auth_provider._token_data is not None
        assert fedex_auth_provider._token_data.access_token == "test_token"
        assert fedex_auth_provider.is_token_valid

@pytest.mark.asyncio
async def test_token_refresh_failure(fedex_auth_provider):
    """Test token refresh failure"""
    mock_response = AsyncMock()
    mock_response.status_code = 401
    mock_response.text = "Invalid credentials"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError):
            await fedex_auth_provider.refresh_token()

@pytest.mark.asyncio
async def test_get_token_refreshes_when_invalid(fedex_auth_provider):
    """Test that get_token refreshes when token is invalid"""
    with patch.object(fedex_auth_provider, "refresh_token", new_callable=AsyncMock) as mock_refresh:
        await fedex_auth_provider.get_token()
        mock_refresh.assert_called_once()