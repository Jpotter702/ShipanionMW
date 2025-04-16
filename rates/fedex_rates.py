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
import json

class FedExRateEngine(BaseRateEngine):
    def __init__(self):
        super().__init__()
        # Store credentials for mock mode check
        self._client_id = os.getenv('FEDEX_CLIENT_ID')
        self._client_secret = os.getenv('FEDEX_CLIENT_SECRET')
        self._auth = FedExAuth()
        # Use sandbox URL for development/testing
        self._base_url = os.getenv('FEDEX_API_URL', 'https://apis-sandbox.fedex.com')
        self._account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')
        self._client = httpx.AsyncClient()
        self._normalizer = ServiceNormalizer()

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

    async def get_rates(self, request: RateRequest) -> List[RateOption]:
        """
        Get shipping rates from FedEx.
        """
        try:
            # Check if we're in mock mode (no API credentials)
            # Use environment variables directly to avoid attribute errors
            if not os.getenv('FEDEX_CLIENT_ID') or not os.getenv('FEDEX_CLIENT_SECRET'):
                # Return mock data for testing
                return self._get_mock_rates(request)
        except Exception as e:
            # If there's any issue with the check, use mock data
            print(f"Error checking FedEx credentials: {str(e)}. Using mock data.")
            return self._get_mock_rates(request)

        try:
            print("FedExRateEngine: Getting token from auth service")
            token = await self._auth.get_token()
            print(f"FedExRateEngine: Got token: {token[:10]}..." if token else "FedExRateEngine: No token received")

            print("FedExRateEngine: Preparing rate request")
            request_data = self._prepare_rate_request({
                'origin': {'postal_code': request.origin_zip, 'country_code': 'US'},
                'destination': {'postal_code': request.destination_zip, 'country_code': 'US'},
                'packages': [{
                    'weight': request.weight,
                    'length': request.dimensions.length if request.dimensions else 12,
                    'width': request.dimensions.width if request.dimensions else 12,
                    'height': request.dimensions.height if request.dimensions else 12
                }]
            })
            print(f"FedExRateEngine: Request data prepared: {json.dumps(request_data, indent=2)}")
            print(f"FedExRateEngine: Using account number: {self._account_number}")

            rate_url = f"{self._base_url}/rate/v1/rates/quotes"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-locale": "en_US"  # Added as per FedEx API requirements
            }

            print(f"FedExRateEngine: Sending rate request to {rate_url}")
            print(f"FedExRateEngine: Headers: {headers}")

            try:
                response = await self._client.post(
                    rate_url,
                    json=request_data,
                    headers=headers
                )
                print(f"FedExRateEngine: Rate response status: {response.status_code}")
                response.raise_for_status()
            except httpx.HTTPError as e:
                error_msg = f"FedExRateEngine: HTTP error: {str(e)}"
                print(error_msg)
                if hasattr(e, 'response') and e.response is not None:
                    print(f"FedExRateEngine: Error response status: {e.response.status_code}")
                    print(f"FedExRateEngine: Error response: {e.response.text}")

                # For 400 errors, let's try with a specific service type as fallback
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 400:
                    print("FedExRateEngine: Trying fallback with specific service type (FEDEX_GROUND)")
                    # Create a new request with a specific service type
                    fallback_request_data = self._prepare_rate_request_with_service({
                        'origin': {'postal_code': request.origin_zip, 'country_code': 'US'},
                        'destination': {'postal_code': request.destination_zip, 'country_code': 'US'},
                        'packages': [{
                            'weight': request.weight,
                            'length': request.dimensions.length if request.dimensions else 12,
                            'width': request.dimensions.width if request.dimensions else 12,
                            'height': request.dimensions.height if request.dimensions else 12
                        }]
                    }, "FEDEX_GROUND")

                    try:
                        fallback_response = await self._client.post(
                            rate_url,
                            json=fallback_request_data,
                            headers=headers
                        )
                        print(f"FedExRateEngine: Fallback response status: {fallback_response.status_code}")
                        fallback_response.raise_for_status()
                        response = fallback_response  # Use the fallback response
                    except httpx.HTTPError as fallback_e:
                        print(f"FedExRateEngine: Fallback request also failed: {str(fallback_e)}")
                        if hasattr(fallback_e, 'response') and fallback_e.response is not None:
                            print(f"FedExRateEngine: Fallback error response: {fallback_e.response.text}")
                        raise fallback_e
                else:
                    raise

            # Print response for debugging
            try:
                response_data = response.json()
                print(f"FedEx API Response: {json.dumps(response_data, indent=2)}")
            except Exception as e:
                print(f"FedExRateEngine: Error parsing response JSON: {str(e)}")
                print(f"FedExRateEngine: Raw response: {response.text}")
                raise RateError(f"Error parsing FedEx response JSON: {str(e)}")

            try:
                rates = self._parse_rate_response(response_data)
                return [
                    RateOption(
                        carrier='fedex',
                        service_name=rate['service_name'] or 'FedEx Service',
                        service_tier=self._normalizer.normalize_service('fedex', rate['service_code']),
                        cost=float(rate['total_charge']) if rate['total_charge'] else 0.0,
                        estimated_delivery=datetime.fromisoformat(rate['delivery_date']) if rate['delivery_date'] else None,
                        transit_days=int(rate['transit_days']) if rate['transit_days'] else 1
                    )
                    for rate in rates
                ]
            except Exception as e:
                print(f"Error parsing FedEx response: {str(e)}")
                raise RateError(f"Error parsing FedEx response: {str(e)}")
        except Exception as e:
            raise RateError(f"Failed to get FedEx rates: {str(e)}")

    def _get_mock_rates(self, request: RateRequest) -> List[RateOption]:
        """Return mock rates for testing"""
        # Calculate a simple rate based on weight and distance
        # This is just for testing purposes
        base_rate = 10.0
        try:
            weight_factor = request.weight * 0.5
        except (TypeError, AttributeError):
            # Default if there's an issue with the weight
            weight_factor = 2.5  # Default for a 5 lb package

        # Simple distance calculation based on ZIP codes
        # This is very crude and just for testing
        try:
            origin_prefix = int(request.origin_zip[:1])
            dest_prefix = int(request.destination_zip[:1])
            distance_factor = abs(origin_prefix - dest_prefix) * 2
        except (ValueError, IndexError, TypeError):
            # Default if there's an issue with the ZIP codes
            distance_factor = 5  # Default distance factor

        # Create mock rates for different service levels
        delivery_date = datetime.now() + timedelta(days=3)
        overnight_date = datetime.now() + timedelta(days=1)

        return [
            RateOption(
                carrier='fedex',
                service_name='FedEx Ground',
                service_tier=ServiceTier.GROUND,
                cost=base_rate + weight_factor + distance_factor,
                estimated_delivery=delivery_date,
                transit_days=3
            ),
            RateOption(
                carrier='fedex',
                service_name='FedEx Express Saver',
                service_tier=ServiceTier.SAVER,
                cost=(base_rate + weight_factor + distance_factor) * 1.2,
                estimated_delivery=delivery_date - timedelta(days=1),
                transit_days=2
            ),
            RateOption(
                carrier='fedex',
                service_name='FedEx Overnight',
                service_tier=ServiceTier.OVERNIGHT,
                cost=(base_rate + weight_factor + distance_factor) * 2.5,
                estimated_delivery=overnight_date,
                transit_days=1
            )
        ]

    def _prepare_rate_request(self, shipment: Dict) -> Dict:
        """
        Prepare the rate request payload for FedEx API without specifying a service type.
        This will return rates for all available services.

        Args:
            shipment: Shipment details

        Returns:
            Dict: Formatted request payload
        """
        return self._prepare_rate_request_with_service(shipment)

    def _prepare_rate_request_with_service(self, shipment: Dict, service_type: str = None) -> Dict:
        """
        Prepare the rate request payload for FedEx API with an optional service type.

        Args:
            shipment: Shipment details
            service_type: Optional FedEx service type (e.g., FEDEX_GROUND, FEDEX_EXPRESS_SAVER)

        Returns:
            Dict: Formatted request payload
        """
        request = {
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

        # Add service type if specified
        if service_type:
            request["requestedShipment"]["serviceType"] = service_type

        return request

    def _parse_rate_response(self, response: Dict) -> List[Dict]:
        """
        Parse the FedEx rate response into our standard format.

        Args:
            response: Raw API response

        Returns:
            List[Dict]: List of normalized rates
        """
        rates = []

        # Check if response has the expected structure
        if not isinstance(response, dict):
            print(f"Unexpected response type: {type(response)}")
            return rates

        output = response.get('output')
        if not output or not isinstance(output, dict):
            print(f"Missing or invalid 'output' in response: {response}")
            return rates

        rate_details = output.get('rateReplyDetails', [])
        if not rate_details or not isinstance(rate_details, list):
            print(f"Missing or invalid 'rateReplyDetails' in response: {output}")
            return rates

        for quote in rate_details:
            try:
                # Get rated shipment details safely
                rated_details = quote.get('ratedShipmentDetails', [])
                if not rated_details or not isinstance(rated_details, list) or len(rated_details) == 0:
                    print(f"Missing or invalid 'ratedShipmentDetails' in quote: {quote}")
                    continue

                # Get total net charge safely - it's a float value in the response, not a dict
                total_net_charge = rated_details[0].get('totalNetCharge')
                if total_net_charge is None:
                    print(f"Missing 'totalNetCharge' in rated details: {rated_details[0]}")
                    continue

                # Get currency from the rated shipment details
                currency = rated_details[0].get('currency', 'USD')

                # Get service type for transit day calculation
                service_type = quote.get('serviceType', '')

                # Set realistic transit days based on service type
                # These are more realistic values for cross-country shipping
                if service_type in ['FIRST_OVERNIGHT', 'PRIORITY_OVERNIGHT']:
                    transit_days = 1  # Overnight services
                elif service_type == 'STANDARD_OVERNIGHT':
                    transit_days = 1  # Standard overnight
                elif service_type in ['FEDEX_2_DAY', 'FEDEX_2_DAY_AM']:
                    transit_days = 2  # 2-day services
                elif service_type == 'FEDEX_EXPRESS_SAVER':
                    transit_days = 3  # Express saver is typically 3 days
                elif service_type == 'FEDEX_GROUND':
                    transit_days = 5  # Ground is typically 5 days for cross-country
                else:
                    transit_days = 3  # Default fallback

                # Calculate an estimated delivery date based on transit days
                delivery_date = datetime.now() + timedelta(days=transit_days)

                # Check if there's an operational detail with transit information
                # Only use API transit days if they seem reasonable
                if 'operationalDetail' in quote:
                    transit_info = quote.get('operationalDetail', {})
                    if transit_info.get('transitDays'):
                        try:
                            api_transit_days = int(transit_info.get('transitDays'))
                            # Only use API transit days if they're reasonable for the service type
                            if api_transit_days > 0 and api_transit_days <= 10:
                                transit_days = api_transit_days
                                # Update delivery date based on actual transit days
                                delivery_date = datetime.now() + timedelta(days=transit_days)
                        except (ValueError, TypeError):
                            # Keep the default if conversion fails
                            pass

                # Create the rate dictionary
                rate = {
                    'carrier': 'fedex',
                    'service_code': quote.get('serviceType', ''),
                    'service_name': quote.get('serviceName', 'FedEx Service'),
                    'total_charge': total_net_charge,  # Now using the float value directly
                    'currency': currency,
                    'transit_days': transit_days,
                    'delivery_date': delivery_date.isoformat(),  # Convert to ISO format string
                    'guaranteed': quote.get('serviceDescription', {}).get('serviceId', '') != ''
                }
                rates.append(rate)
            except Exception as e:
                print(f"Error parsing rate quote: {str(e)}")
                continue
        return rates
