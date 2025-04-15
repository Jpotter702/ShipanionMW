# Base Auth
# TODO: Implement this module

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

class TokenData(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    expires_at: datetime

class BaseAuthProvider(ABC):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token_data: Optional[TokenData] = None
    
    @abstractmethod
    async def get_token(self) -> str:
        """Get a valid token, refreshing if necessary"""
        if not self.is_token_valid:
            await self.refresh_token()
        return self._token_data.access_token
    
    @abstractmethod
    async def refresh_token(self) -> None:
        """Refresh the authentication token"""
        pass
    
    @property
    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        if not self._token_data:
            return False
        return datetime.now() < self._token_data.expires_at
    
    def _calculate_expiry(self, expires_in: int) -> datetime:
        """Calculate token expiry time"""
        return datetime.now() + timedelta(seconds=expires_in)
