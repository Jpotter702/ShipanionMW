from typing import List
from models.rate_request import RateRequest
from models.rate_response import RateResponse
from rates.fedex_rates import FedExRateEngine
from rates.ups_rates import UPSRateEngine
from rates.rate_comparer import RateComparer
from utils.exceptions import ValidationError
import asyncio
import os

class RateService:
    def __init__(self):
        self._fedex_engine = FedExRateEngine()
        self._ups_engine = UPSRateEngine()
        self._comparer = RateComparer()
        # Flag to control whether UPS is enabled
        self._ups_enabled = os.getenv('ENABLE_UPS', 'false').lower() == 'true'

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
        print("RateService: Getting rates from enabled carriers")
        # Get rates from enabled carriers
        tasks = [self._fedex_engine.get_rates(request)]

        # Only add UPS if it's enabled
        if self._ups_enabled:
            print("RateService: UPS is enabled, adding to tasks")
            tasks.append(self._ups_engine.get_rates(request))
        else:
            print("RateService: UPS is disabled, skipping")

        print(f"RateService: Executing {len(tasks)} tasks")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"RateService: Got {len(results)} results")

        all_options = []
        errors = []

        # Process FedEx results (always first)
        print(f"RateService: Processing FedEx results: {type(results[0])}")
        if isinstance(results[0], Exception):
            error_msg = f"FedEx error: {str(results[0])}"
            print(f"RateService: {error_msg}")
            errors.append(error_msg)
        elif isinstance(results[0], list):
            print(f"RateService: FedEx returned {len(results[0])} options")
            all_options.extend(results[0])
        else:
            print(f"RateService: Unexpected FedEx result type: {type(results[0])}")

        # Process UPS results if enabled
        if self._ups_enabled and len(results) > 1:
            print(f"RateService: Processing UPS results: {type(results[1])}")
            if isinstance(results[1], Exception):
                error_msg = f"UPS error: {str(results[1])}"
                print(f"RateService: {error_msg}")
                errors.append(error_msg)
            elif isinstance(results[1], list):
                print(f"RateService: UPS returned {len(results[1])} options")
                all_options.extend(results[1])
            else:
                print(f"RateService: Unexpected UPS result type: {type(results[1])}")

        print(f"RateService: Total options found: {len(all_options)}")
        if not all_options:
            error_msg = f"No valid shipping rates found. Errors: {'; '.join(errors)}"
            print(f"RateService: {error_msg}")
            raise ValidationError(error_msg)

        # Compare and return best options
        print("RateService: Comparing rates to find best options")
        result = self._comparer.compare_rates(all_options)
        print(f"RateService: Found cheapest option: {result.cheapest_option.carrier} {result.cheapest_option.service_name} ${result.cheapest_option.cost}")
        if result.fastest_option:
            print(f"RateService: Found fastest option: {result.fastest_option.carrier} {result.fastest_option.service_name} ${result.fastest_option.cost}")
        else:
            print("RateService: No separate fastest option found (cheapest is also fastest)")
        return result

    async def validate_carriers(self) -> dict:
        """
        Validate carrier API credentials.

        Returns:
            Dictionary with carrier status
        """
        fedex_status = await self._fedex_engine.validate_credentials()

        result = {
            "fedex": fedex_status,
        }

        # Only validate UPS if it's enabled
        if self._ups_enabled:
            ups_status = await self._ups_engine.validate_credentials()
            result["ups"] = ups_status
        else:
            result["ups"] = False  # UPS is disabled

        return result
