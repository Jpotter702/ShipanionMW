# Fedex Rates
# TODO: Implement this module

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models.rate_request import RateRequest
from models.rate_response import RateOption
from rates.base_rate_engine import BaseRateEngine
from utils.service_normalizer import ServiceTier, ServiceNormalizer
from auth.fedex_auth import FedExAuth
from utils.exceptions import RateError
import httpx
import os

class FedExRateEngine(BaseRateEngine):
    def __init__(self):
        super().__init__()
        self._auth = FedExAuth()
        self._base_url = os.getenv('FEDEX_API_URL', 'https://apis.fedex.com')
        self._account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')
        self._client = httpx.AsyncClient()

    async def validate_credentials(self) -> bool:
        """
        Validate FedEx API credentials by attempting to get a token.
        
        Returns:
            bool: True if credentials are valid
            
        Raises:
            RateError: If credentials are invalid
        """
        try:
            await self._auth.get_token()
            return True
        except Exception as e:
            raise RateError(f"Invalid FedEx credentials: {str(e)}")

    async def get_rates(self, shipment: Dict) -> List[Dict]:
        """
        Get shipping rates from FedEx.
        
        Args:
            shipment: Shipment details including origin, destination, and package info
            
        Returns:
            List[Dict]: List of available rates
            
        Raises:
            RateError: If rate request fails
        """
        try:
            token = await self._auth.get_token()
            request_data = self._prepare_rate_request(shipment)
            
            response = await self._client.post(
                f"{self._base_url}/rate/v1/rates/quotes",
                json=request_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            
            return self._parse_rate_response(response.json())
        except httpx.HTTPError as e:
            raise RateError(f"Failed to get FedEx rates: {str(e)}")

    def _prepare_rate_request(self, shipment: Dict) -> Dict:
        """
        Prepare the rate request payload for FedEx API.
        
        Args:
            shipment: Shipment details
            
        Returns:
            Dict: Formatted request payload
        """
        return {
            "accountNumber": {
                "value": self._account_number
            },
            "requestedShipment": {
                "shipper": {
                    "address": {
                        "postalCode": shipment['origin']['postal_code'],
                        "countryCode": shipment['origin']['country_code']
                    }
                },
                "recipient": {
                    "address": {
                        "postalCode": shipment['destination']['postal_code'],
                        "countryCode": shipment['destination']['country_code']
                    }
                },
                "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
                "serviceType": "FEDEX_GROUND",
                "packagingType": "YOUR_PACKAGING",
                "rateRequestType": ["LIST"],
                "preferredCurrency": "USD",
                "requestedPackageLineItems": [
                    {
                        "weight": {
                            "value": package['weight'],
                            "units": "LB"
                        },
                        "dimensions": {
                            "length": package['length'],
                            "width": package['width'],
                            "height": package['height'],
                            "units": "IN"
                        }
                    }
                    for package in shipment['packages']
                ]
            }
        }

    def _parse_rate_response(self, response: Dict) -> List[Dict]:
        """
        Parse the FedEx rate response into our standard format.
        
        Args:
            response: Raw API response
            
        Returns:
            List[Dict]: List of normalized rates
        """
        rates = []
        for quote in response.get('output', {}).get('rateReplyDetails', []):
            rate = {
                'carrier': 'fedex',
                'service_code': quote.get('serviceType'),
                'service_name': quote.get('serviceName'),
                'total_charge': quote.get('ratedShipmentDetails', [{}])[0].get('totalNetCharge', {}).get('amount', 0),
                'currency': quote.get('ratedShipmentDetails', [{}])[0].get('totalNetCharge', {}).get('currency', 'USD'),
                'transit_days': quote.get('transitTime'),
                'delivery_date': quote.get('deliveryTimestamp'),
                'guaranteed': quote.get('guaranteed', False)
            }
            rates.append(rate)
        return rates
