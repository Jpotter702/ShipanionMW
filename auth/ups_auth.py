# Ups Auth
# TODO: Implement this module

from auth.base_auth import BaseAuth
from auth.token_manager import TokenManager
import os
import base64
import hashlib
import secrets
import httpx
from typing import Optional, Dict

class UPSAuth(BaseAuth):
    def __init__(self):
        super().__init__()
        self._client_id = os.getenv('UPS_CLIENT_ID')
        self._client_secret = os.getenv('UPS_CLIENT_SECRET')
        self._redirect_uri = os.getenv('UPS_REDIRECT_URI')
        self._base_url = os.getenv('UPS_API_URL', 'https://onlinetools.ups.com')
        self._token_manager = TokenManager('ups')
        self._client = httpx.AsyncClient()

    async def get_token(self) -> str:
        """
        Get a valid access token, either from cache or by refreshing.
        
        Returns:
            str: Valid access token
            
        Raises:
            Exception: If token cannot be obtained
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
        Get a new access token using PKCE flow.
        
        Returns:
            str: New access token
            
        Raises:
            Exception: If token request fails
        """
        # Generate PKCE values
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')

        # Get authorization code
        auth_url = f"{self._base_url}/security/v1/oauth/authorize"
        params = {
            'client_id': self._client_id,
            'redirect_uri': self._redirect_uri,
            'response_type': 'code',
            'scope': 'shipping',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Note: In a real implementation, this would redirect to UPS login
        # For backend service, we'll use client credentials
        token_url = f"{self._base_url}/security/v1/oauth/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        
        response = await self._client.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        await self._token_manager.save_tokens(
            token_data['access_token'],
            token_data.get('refresh_token'),
            token_data.get('expires_in', 3600)
        )
        
        return token_data['access_token']

    async def _refresh_token(self, refresh_token: str) -> str:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            str: New access token
            
        Raises:
            Exception: If refresh fails
        """
        token_url = f"{self._base_url}/security/v1/oauth/token"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        
        response = await self._client.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        await self._token_manager.save_tokens(
            token_data['access_token'],
            token_data.get('refresh_token'),
            token_data.get('expires_in', 3600)
        )
        
        return token_data['access_token']
