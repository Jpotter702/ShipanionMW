from typing import Dict, Optional
from .base_auth import BaseAuthProvider
from utils.exceptions import AuthenticationError

class TokenManager:
    def __init__(self, provider_name=None):
        self._providers: Dict[str, BaseAuthProvider] = {}
        self._tokens = {}
        self._refresh_tokens = {}
        self._provider_name = provider_name
        print(f"TokenManager: Initialized with provider_name: {provider_name}")

    def register_provider(self, name: str, provider: BaseAuthProvider) -> None:
        """Register a new auth provider"""
        self._providers[name] = provider

    async def get_token(self, provider_name: str) -> str:
        """Get a valid token for the specified provider"""
        provider = self._providers.get(provider_name)
        if not provider:
            raise AuthenticationError(f"Provider {provider_name} not registered")

        return await provider.get_token()

    def get_provider(self, provider_name: str) -> Optional[BaseAuthProvider]:
        """Get a provider instance by name"""
        return self._providers.get(provider_name)

    async def get_valid_token(self) -> Optional[str]:
        """Get a valid token for the current provider"""
        if not self._provider_name:
            print("TokenManager: No provider name set, cannot get token")
            return None
        token = self._tokens.get(self._provider_name)
        if token:
            print(f"TokenManager: Found token for {self._provider_name}: {token[:10]}...")
        else:
            print(f"TokenManager: No token found for {self._provider_name}")
        return token

    async def get_refresh_token(self) -> Optional[str]:
        """Get a refresh token for the current provider"""
        if not self._provider_name:
            print("TokenManager: No provider name set, cannot get refresh token")
            return None
        refresh_token = self._refresh_tokens.get(self._provider_name)
        if refresh_token:
            print(f"TokenManager: Found refresh token for {self._provider_name}")
        else:
            print(f"TokenManager: No refresh token found for {self._provider_name}")
        return refresh_token

    async def save_tokens(self, access_token: str, refresh_token: Optional[str], expires_in: int) -> None:
        """Save tokens for the current provider"""
        if not self._provider_name:
            print("TokenManager: No provider name set, cannot save tokens")
            return
        print(f"TokenManager: Saving token for {self._provider_name}: {access_token[:10]}...")
        self._tokens[self._provider_name] = access_token
        if refresh_token:
            print(f"TokenManager: Saving refresh token for {self._provider_name}")
            self._refresh_tokens[self._provider_name] = refresh_token
        print(f"TokenManager: Token saved for {self._provider_name}, expires in {expires_in} seconds")