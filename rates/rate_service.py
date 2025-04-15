from typing import List
from models.rate_request import RateRequest
from models.rate_response import RateResponse
from rates.fedex_rates import FedExRateEngine
from rates.ups_rates import UPSRateEngine
from rates.rate_comparer import RateComparer
from utils.exceptions import ValidationError
import asyncio

class RateService:
    def __init__(self):
        self._fedex_engine = FedExRateEngine()
        self._ups_engine = UPSRateEngine()
        self._comparer = RateComparer()

    async def get_rates(self, request: RateRequest) -> RateResponse:
        """
        Get shipping rates from all available carriers and return the best options.
        
        Args:
            request: RateRequest containing shipping details
            
        Returns:
            RateResponse with cheapest and fastest options
            
        Raises:
            ValidationError: If no valid rates are found
        """
        # Get rates from all carriers in parallel
        tasks = [
            self._fedex_engine.get_rates(request),
            self._ups_engine.get_rates(request)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect valid results
        all_options = []
        for result in results:
            if isinstance(result, list):
                all_options.extend(result)
            # Log errors but continue with available rates
        
        if not all_options:
            raise ValidationError("No valid shipping rates found")
            
        # Compare and return best options
        return self._comparer.compare_rates(all_options)

    async def validate_carriers(self) -> dict:
        """
        Validate carrier API credentials.
        
        Returns:
            Dictionary with carrier status
        """
        fedex_status = await self._fedex_engine.validate_credentials()
        ups_status = await self._ups_engine.validate_credentials()
        
        return {
            "fedex": fedex_status,
            "ups": ups_status
        } 