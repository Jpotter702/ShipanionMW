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
        token = await self._auth.get_token()
        
        # Prepare UPS rate request
        payload = self._prepare_rate_request(request)
        
        # Make API call
        response = await self._client.post(
            f"{self._base_url}/api/rating/v1/Shop",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()
        
        # Parse and normalize response
        return self._parse_rate_response(response.json())

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
