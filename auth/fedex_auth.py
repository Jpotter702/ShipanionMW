# Fedex Auth
# TODO: Implement this module

import os
from typing import Dict, Any, Optional
import httpx
from auth.base_auth import BaseAuthProvider, TokenData
from utils.exceptions import AuthenticationError
from auth.token_manager import TokenManager

class FedExAuth(BaseAuthProvider):
    def __init__(self):
        self._client_id = os.getenv('FEDEX_CLIENT_ID')
        self._client_secret = os.getenv('FEDEX_CLIENT_SECRET')
        super().__init__(client_id=self._client_id, client_secret=self._client_secret)
        self._base_url = os.getenv('FEDEX_API_URL', 'https://apis-sandbox.fedex.com')
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
        print(f"FedExAuth: Getting token with client_id: {self._client_id[:5]}... and client_secret: {self._client_secret[:5]}...")
        token = await self._token_manager.get_valid_token()
        if token:
            print(f"FedExAuth: Using existing token: {token[:10]}...")
            return token

        # Try to refresh token
        print("FedExAuth: No existing token, trying to refresh")
        refresh_token = await self._token_manager.get_refresh_token()
        if refresh_token:
            try:
                print("FedExAuth: Refresh token found, refreshing")
                new_token = await self._refresh_token(refresh_token)
                print(f"FedExAuth: Successfully refreshed token: {new_token[:10]}...")
                return new_token
            except Exception as e:
                print(f"FedExAuth: Failed to refresh token: {str(e)}")
                pass

        # If no valid token and refresh failed, get new token
        print("FedExAuth: Getting new token")
        new_token = await self._get_new_token()
        print(f"FedExAuth: Got new token: {new_token[:10]}...")
        return new_token

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
            print(f"FedExAuth: Requesting new token from {token_url}")
            print(f"FedExAuth: Request data: {data}")
            response = await self._client.post(token_url, data=data)
            print(f"FedExAuth: Token response status: {response.status_code}")
            response.raise_for_status()

            token_data = response.json()
            print(f"FedExAuth: Token response data: {token_data}")
            await self._token_manager.save_tokens(
                token_data['access_token'],
                token_data.get('refresh_token'),
                token_data.get('expires_in', 3600)
            )

            return token_data['access_token']
        except httpx.HTTPError as e:
            error_msg = f"Failed to get FedEx token: {str(e)}"
            print(f"FedExAuth: {error_msg}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"FedExAuth: Error response: {e.response.text}")
            raise AuthenticationError(error_msg)

    async def refresh_token(self) -> None:
        """Implement abstract method from BaseAuthProvider"""
        refresh_token = await self._token_manager.get_refresh_token()
        if refresh_token:
            await self._refresh_token(refresh_token)
        else:
            await self._get_new_token()

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
