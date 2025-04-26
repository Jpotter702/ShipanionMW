#!/usr/bin/env python3
"""
Test script to directly use the FedExRateEngine class to get rates.
"""

import asyncio
import os
from dotenv import load_dotenv
from rates.fedex_rates import FedExRateEngine
from models.rate_request import RateRequest, Dimensions

async def test_fedex_rate_engine():
    """Test FedEx rate engine directly"""
    print("\n=== Testing FedEx Rate Engine ===\n")

    # Load environment variables
    load_dotenv()

    # Print FedEx credentials (first few characters only for security)
    client_id = os.getenv('FEDEX_CLIENT_ID')
    client_secret = os.getenv('FEDEX_CLIENT_SECRET')
    account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')
    api_url = os.getenv('FEDEX_API_URL', 'https://apis-sandbox.fedex.com')

    print(f"FedEx API URL: {api_url}")
    print(f"FedEx Client ID: {client_id[:5]}..." if client_id else "FedEx Client ID: Not set")
    print(f"FedEx Client Secret: {client_secret[:5]}..." if client_secret else "FedEx Client Secret: Not set")
    print(f"FedEx Account Number: {account_number[:5]}..." if account_number else "FedEx Account Number: Not set")

    # Create rate request
    dimensions = Dimensions(length=12, width=10, height=8)
    request = RateRequest(
        origin_zip="90210",
        destination_zip="10001",
        weight=5.0,
        dimensions=dimensions
    )

    # Create rate engine
    rate_engine = FedExRateEngine()

    try:
        # Get rates
        print("\nGetting rates from FedEx rate engine...")
        rates = await rate_engine.get_rates(request)

        # Print rates
        print(f"\nGot {len(rates)} rates from FedEx:")
        for i, rate in enumerate(rates):
            print(f"Rate {i+1}:")
            print(f"  Carrier: {rate.carrier}")
            print(f"  Service: {rate.service_name}")
            print(f"  Cost: ${rate.cost}")
            print(f"  Delivery: {rate.estimated_delivery}")
            print(f"  Transit days: {rate.transit_days}")

        return True
    except Exception as e:
        print(f"\n❌ Error getting rates: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fedex_rate_engine())
    if result:
        print("\n✅ FedEx rate engine test passed!")
    else:
        print("\n❌ FedEx rate engine test failed!")
