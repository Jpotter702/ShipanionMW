# Fedex Auth
# TODO: Implement this module

import os
from typing import Dict, Any, Optional
import httpx
from .base_auth import BaseAuthProvider, TokenData
from ..utils.exceptions import AuthenticationError
from auth.base_auth import BaseAuth
from auth.token_manager import TokenManager

class FedExAuth(BaseAuth):
    def __init__(self):
        super().__init__()
        self._client_id = os.getenv('FEDEX_CLIENT_ID')
        self._client_secret = os.getenv('FEDEX_CLIENT_SECRET')
        self._base_url = os.getenv('FEDEX_API_URL', 'https://apis.fedex.com')
        self._token_manager = TokenManager('fedex')
        self._client = httpx.AsyncClient()

    async def get_token(self) -> str:
        """
        Get a valid access token, either from cache or by refreshing.
        
        Returns:
            str: Valid access token
            
        Raises:
            AuthenticationError: If token cannot be obtained
        """
        token = await self._token_manager.get_valid_token()
        if token:
            return token

        # Try to refresh token
        refresh_token = await self._token_manager.get_refresh_token()
        if refresh_token:
            try:
                new_token = await self._refresh_token(refresh_token)
                return new_token
            except Exception:
                pass

        # If no valid token and refresh failed, get new token
        return await self._get_new_token()

    async def _get_new_token(self) -> str:
        """
        Get a new access token using client credentials.
        
        Returns:
            str: New access token
            
        Raises:
            AuthenticationError: If token request fails
        """
        token_url = f"{self._base_url}/oauth/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        
        try:
            response = await self._client.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            await self._token_manager.save_tokens(
                token_data['access_token'],
                token_data.get('refresh_token'),
                token_data.get('expires_in', 3600)
            )
            
            return token_data['access_token']
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Failed to get FedEx token: {str(e)}")

    async def _refresh_token(self, refresh_token: str) -> str:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            str: New access token
            
        Raises:
            AuthenticationError: If refresh fails
        """
        token_url = f"{self._base_url}/oauth/token"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        
        try:
            response = await self._client.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            await self._token_manager.save_tokens(
                token_data['access_token'],
                token_data.get('refresh_token'),
                token_data.get('expires_in', 3600)
            )
            
            return token_data['access_token']
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Failed to refresh FedEx token: {str(e)}")
