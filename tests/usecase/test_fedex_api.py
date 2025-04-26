#!/usr/bin/env python3
"""
Test script to verify FedEx API authentication and rate requests.
"""

import asyncio
import os
import json
import httpx
from dotenv import load_dotenv

async def test_fedex_auth():
    """Test FedEx authentication directly"""
    print("\n=== Testing FedEx Authentication ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Get FedEx credentials
    client_id = os.getenv('FEDEX_CLIENT_ID')
    client_secret = os.getenv('FEDEX_CLIENT_SECRET')
    account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')
    api_url = os.getenv('FEDEX_API_URL', 'https://apis-sandbox.fedex.com')
    
    print(f"FedEx API URL: {api_url}")
    print(f"FedEx Client ID: {client_id[:5]}..." if client_id else "FedEx Client ID: Not set")
    print(f"FedEx Client Secret: {client_secret[:5]}..." if client_secret else "FedEx Client Secret: Not set")
    print(f"FedEx Account Number: {account_number[:5]}..." if account_number else "FedEx Account Number: Not set")
    
    # Create HTTP client
    async with httpx.AsyncClient() as client:
        # Get token
        token_url = f"{api_url}/oauth/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        print(f"\nRequesting token from: {token_url}")
        print(f"Request data: {data}")
        
        try:
            response = await client.post(token_url, data=data)
            print(f"Token response status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data['access_token']
                print(f"Successfully got token: {token[:15]}...")
                return token
            else:
                print(f"Error response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting token: {str(e)}")
            return None

async def test_fedex_rates(token):
    """Test FedEx rate request"""
    print("\n=== Testing FedEx Rate Request ===\n")
    
    if not token:
        print("No token available, skipping rate request test")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Get FedEx credentials
    account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')
    api_url = os.getenv('FEDEX_API_URL', 'https://apis-sandbox.fedex.com')
    
    # Create HTTP client
    async with httpx.AsyncClient() as client:
        # Prepare rate request
        rate_url = f"{api_url}/rate/v1/rates/quotes"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-locale": "en_US"
        }
        
        request_data = {
            "accountNumber": {
                "value": account_number
            },
            "requestedShipment": {
                "shipper": {
                    "address": {
                        "postalCode": "90210",
                        "countryCode": "US"
                    }
                },
                "recipient": {
                    "address": {
                        "postalCode": "10001",
                        "countryCode": "US"
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
                            "value": 5.0,
                            "units": "LB"
                        },
                        "dimensions": {
                            "length": 12,
                            "width": 10,
                            "height": 8,
                            "units": "IN"
                        }
                    }
                ]
            }
        }
        
        print(f"Sending rate request to: {rate_url}")
        print(f"Headers: {headers}")
        print(f"Request data: {json.dumps(request_data, indent=2)}")
        
        try:
            response = await client.post(rate_url, json=request_data, headers=headers)
            print(f"Rate response status: {response.status_code}")
            
            if response.status_code == 200:
                rate_data = response.json()
                print(f"Rate response: {json.dumps(rate_data, indent=2)}")
                return True
            else:
                print(f"Error response: {response.text}")
                return False
        except Exception as e:
            print(f"Error getting rates: {str(e)}")
            return False

async def main():
    """Main test function"""
    token = await test_fedex_auth()
    if token:
        print("\n✅ FedEx authentication test passed!")
        
        rates_success = await test_fedex_rates(token)
        if rates_success:
            print("\n✅ FedEx rate request test passed!")
        else:
            print("\n❌ FedEx rate request test failed!")
    else:
        print("\n❌ FedEx authentication test failed!")

if __name__ == "__main__":
    asyncio.run(main())
