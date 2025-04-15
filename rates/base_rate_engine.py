from abc import ABC, abstractmethod
from models.rate_request import RateRequest
from models.rate_response import RateOption
from typing import List

class BaseRateEngine(ABC):
    @abstractmethod
    async def get_rates(self, request: RateRequest) -> List[RateOption]:
        """
        Get shipping rates from the carrier.
        
        Args:
            request: RateRequest containing shipping details
            
        Returns:
            List of RateOption objects with carrier-specific rates
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate carrier API credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass 