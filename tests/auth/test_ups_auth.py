import pytest
from unittest.mock import AsyncMock, patch
from auth.ups_auth import UPSAuth
from auth.token_manager import TokenManager

@pytest.fixture
def ups_auth():
    with patch.dict('os.environ', {
        'UPS_CLIENT_ID': 'test_client_id',
        'UPS_CLIENT_SECRET': 'test_client_secret',
        'UPS_REDIRECT_URI': 'http://localhost/callback',
        'UPS_API_URL': 'https://test.ups.com'
    }):
        return UPSAuth()

@pytest.mark.asyncio
async def test_get_token_cached(ups_auth):
    """Test getting a cached token"""
    with patch.object(TokenManager, 'get_valid_token', new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = 'cached_token'
        token = await ups_auth.get_token()
        assert token == 'cached_token'
        mock_get_token.assert_called_once()

@pytest.mark.asyncio
async def test_get_token_refresh(ups_auth):
    """Test refreshing an expired token"""
    with patch.object(TokenManager, 'get_valid_token', new_callable=AsyncMock) as mock_get_token:
        with patch.object(TokenManager, 'get_refresh_token', new_callable=AsyncMock) as mock_get_refresh:
            with patch.object(UPSAuth, '_refresh_token', new_callable=AsyncMock) as mock_refresh:
                mock_get_token.return_value = None
                mock_get_refresh.return_value = 'refresh_token'
                mock_refresh.return_value = 'new_token'
                
                token = await ups_auth.get_token()
                assert token == 'new_token'
                mock_refresh.assert_called_once_with('refresh_token')

@pytest.mark.asyncio
async def test_get_token_new(ups_auth):
    """Test getting a new token when no cached or refresh token exists"""
    with patch.object(TokenManager, 'get_valid_token', new_callable=AsyncMock) as mock_get_token:
        with patch.object(TokenManager, 'get_refresh_token', new_callable=AsyncMock) as mock_get_refresh:
            with patch.object(UPSAuth, '_get_new_token', new_callable=AsyncMock) as mock_new_token:
                mock_get_token.return_value = None
                mock_get_refresh.return_value = None
                mock_new_token.return_value = 'new_token'
                
                token = await ups_auth.get_token()
                assert token == 'new_token'
                mock_new_token.assert_called_once()

@pytest.mark.asyncio
async def test_get_new_token(ups_auth):
    """Test getting a new token from UPS"""
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'new_token',
            'refresh_token': 'refresh_token',
            'expires_in': 3600
        }
        
        with patch.object(TokenManager, 'save_tokens', new_callable=AsyncMock) as mock_save:
            token = await ups_auth._get_new_token()
            assert token == 'new_token'
            mock_save.assert_called_once_with('new_token', 'refresh_token', 3600)

@pytest.mark.asyncio
async def test_refresh_token(ups_auth):
    """Test refreshing a token"""
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'refreshed_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 3600
        }
        
        with patch.object(TokenManager, 'save_tokens', new_callable=AsyncMock) as mock_save:
            token = await ups_auth._refresh_token('old_refresh_token')
            assert token == 'refreshed_token'
            mock_save.assert_called_once_with('refreshed_token', 'new_refresh_token', 3600) 