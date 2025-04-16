# Ups Rates
# TODO: Implement this module

from typing import List
from datetime import datetime, timedelta
from models.rate_request import RateRequest
from models.rate_response import RateOption
from rates.base_rate_engine import BaseRateEngine
from utils.service_normalizer import ServiceTier, ServiceNormalizer
from auth.ups_auth import UPSAuth
import httpx
import os

class UPSRateEngine(BaseRateEngine):
    def __init__(self):
        super().__init__()
        # Store credentials for mock mode check
        self._client_id = os.getenv('UPS_CLIENT_ID')
        self._client_secret = os.getenv('UPS_CLIENT_SECRET')
        self._auth = UPSAuth()
        self._normalizer = ServiceNormalizer()
        self._base_url = os.getenv('UPS_API_URL', 'https://onlinetools.ups.com')
        self._client = httpx.AsyncClient()

    async def validate_credentials(self) -> bool:
        try:
            token = await self._auth.get_token()
            return bool(token)
        except Exception:
            return False

    async def get_rates(self, request: RateRequest) -> List[RateOption]:
        """Get shipping rates from UPS."""
        try:
            # Check if we're in mock mode (no API credentials)
            # Use environment variables directly to avoid attribute errors
            if not os.getenv('UPS_CLIENT_ID') or not os.getenv('UPS_CLIENT_SECRET'):
                # Return mock data for testing
                return self._get_mock_rates(request)
        except Exception as e:
            # If there's any issue with the check, use mock data
            print(f"Error checking UPS credentials: {str(e)}. Using mock data.")
            return self._get_mock_rates(request)

        try:
            # Since UPS is disabled, just return an empty list
            # This will be skipped anyway due to the ENABLE_UPS flag
            return []
        except Exception as e:
            from utils.exceptions import RateError
            raise RateError(f"Failed to get UPS rates: {str(e)}")

    def _get_mock_rates(self, request: RateRequest) -> List[RateOption]:
        """Return mock rates for testing"""
        # Calculate a simple rate based on weight and distance
        # This is just for testing purposes
        base_rate = 12.0  # UPS is slightly more expensive in our mock
        try:
            weight_factor = request.weight * 0.6
        except (TypeError, AttributeError):
            # Default if there's an issue with the weight
            weight_factor = 3.0  # Default for a 5 lb package

        # Simple distance calculation based on ZIP codes
        # This is very crude and just for testing
        try:
            origin_prefix = int(request.origin_zip[:1])
            dest_prefix = int(request.destination_zip[:1])
            distance_factor = abs(origin_prefix - dest_prefix) * 2.2
        except (ValueError, IndexError, TypeError):
            # Default if there's an issue with the ZIP codes
            distance_factor = 5.5  # Default distance factor

        # Create mock rates for different service levels
        delivery_date = datetime.now() + timedelta(days=3)
        overnight_date = datetime.now() + timedelta(days=1)

        return [
            RateOption(
                carrier='ups',
                service_name='UPS Ground',
                service_tier=ServiceTier.GROUND,
                cost=base_rate + weight_factor + distance_factor,
                estimated_delivery=delivery_date,
                transit_days=3
            ),
            RateOption(
                carrier='ups',
                service_name='UPS 3 Day Select',
                service_tier=ServiceTier.SAVER,
                cost=(base_rate + weight_factor + distance_factor) * 1.3,
                estimated_delivery=delivery_date - timedelta(days=1),
                transit_days=2
            ),
            RateOption(
                carrier='ups',
                service_name='UPS Next Day Air',
                service_tier=ServiceTier.OVERNIGHT,
                cost=(base_rate + weight_factor + distance_factor) * 2.7,
                estimated_delivery=overnight_date,
                transit_days=1
            )
        ]

    def _prepare_rate_request(self, request: RateRequest) -> dict:
        """Prepare UPS-specific rate request payload"""
        return {
            "Request": {
                "RequestOption": "Shop",
                "TransactionReference": {
                    "CustomerContext": "Rate Request"
                }
            },
            "Shipment": {
                "Shipper": {
                    "Address": {
                        "PostalCode": request.origin_zip,
                        "CountryCode": "US"
                    }
                },
                "ShipTo": {
                    "Address": {
                        "PostalCode": request.destination_zip,
                        "CountryCode": "US"
                    }
                },
                "ShipFrom": {
                    "Address": {
                        "PostalCode": request.origin_zip,
                        "CountryCode": "US"
                    }
                },
                "Package": {
                    "PackagingType": {
                        "Code": "02"  # Customer Supplied Package
                    },
                    "PackageWeight": {
                        "UnitOfMeasurement": {
                            "Code": "LBS"
                        },
                        "Weight": str(request.weight)
                    }
                }
            }
        }

    def _parse_rate_response(self, response: dict) -> List[RateOption]:
        """Parse UPS rate response into RateOption objects"""
        options = []

        for service in response.get('RateResponse', {}).get('RatedShipment', []):
            service_code = service.get('Service', {}).get('Code')
            if not service_code:
                continue

            # Calculate estimated delivery
            transit_days = int(service.get('GuaranteedDaysToDelivery', 1))
            estimated_delivery = datetime.now() + timedelta(days=transit_days)

            # Get service tier
            service_tier = self._normalizer.normalize_service('ups', service_code)

            options.append(RateOption(
                carrier='ups',
                service_name=service.get('Service', {}).get('Description', ''),
                service_tier=service_tier,
                cost=float(service.get('TotalCharges', {}).get('MonetaryValue', 0)),
                estimated_delivery=estimated_delivery,
                transit_days=transit_days
            ))

        return options
