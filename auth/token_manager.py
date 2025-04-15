from typing import Dict, Optional
from .base_auth import BaseAuthProvider
from ..utils.exceptions import AuthenticationError

class TokenManager:
    def __init__(self):
        self._providers: Dict[str, BaseAuthProvider] = {}
    
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