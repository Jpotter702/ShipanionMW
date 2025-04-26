#!/usr/bin/env python3
"""
Test script for FedEx Ship API - Test Case SH0005
US to US, USE_SCHEDULED_PICKUP, PRIORITY_OVERNIGHT, YOUR_PACKAGING, SENDER, URL_ONLY, PAPER_LETTER
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_sh0005():
    """Test case SH0005"""
    print("\n=== Testing SH0005: US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING ===\n")

    # Load environment variables
    load_dotenv()

    # Get FedEx credentials
    account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')

    # API endpoint - either direct to FedEx or through our API
    # url = "https://apis-sandbox.fedex.com/ship/v1/shipments"  # Direct to FedEx
    use_remote = os.getenv('USE_REMOTE', 'true').lower() == 'true'
    if use_remote:
        url = "https://shipvox-backend.onrender.com/api/labels"  # Remote API
    else:
        api_port = os.getenv('API_PORT', '8000')
        url = f"http://localhost:{api_port}/api/labels"  # Local API

    # Create test request payload
    payload = {
        "carrier": "fedex",
        "service_type": "PRIORITY_OVERNIGHT",
        "shipper": {
            "name": "Shipper Name",
            "street": "123 Shipper Street",
            "city": "TAMPA",
            "state": "FL",
            "zip_code": "33610",
            "country": "US",
            "phone": "4152639685",
            "company": "Shipper Company"
        },
        "recipient": {
            "name": "Recipient Name",
            "street": "456 Recipient Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "US",
            "phone": "9018328595",
            "company": "Recipient Company"
        },
        "package": {
            "weight": 10.0,
            "dimensions": {
                "length": 12.0,
                "width": 10.0,
                "height": 8.0
            },
            "packaging_type": "YOUR_PACKAGING"
        }
    }

    # Send request
    print("Sending request to label API...")
    try:
        response = requests.post(url, json=payload)

        # Check response
        if response.status_code == 200:
            print("\nLabel created successfully!")
            data = response.json()
            print(f"Tracking Number: {data['tracking_number']}")
            print(f"Label URL: {data['label_url']}")
            print(f"Native QR Code: {'Available' if data.get('native_qr_code_base64') else 'Not available'}")
            print(f"Fallback QR Code URL: {data.get('fallback_qr_code_url', 'Not generated yet')}")
            print(f"Estimated Delivery: {data.get('estimated_delivery')}")

            # Construct full URL for label
            use_remote = os.getenv('USE_REMOTE', 'true').lower() == 'true'
            if use_remote:
                base_url = "https://shipvox-backend.onrender.com"
            else:
                api_port = os.getenv('API_PORT', '8000')
                base_url = f"http://localhost:{api_port}"

            label_url = f"{base_url}{data['label_url']}"
            print(f"\nFull Label URL: {label_url}")

            if data.get('fallback_qr_code_url'):
                qr_url = f"{base_url}{data['fallback_qr_code_url']}"
                print(f"Full QR Code URL: {qr_url}")

            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    result = test_sh0005()
    if result:
        print("\n✅ SH0005 test passed!")
    else:
        print("\n❌ SH0005 test failed!")
