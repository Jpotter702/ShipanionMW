#!/usr/bin/env python3
"""
Test script to verify the label API endpoint.
"""

import requests
import json
from dotenv import load_dotenv

def test_label_api():
    """Test the label API endpoint"""
    print("\n=== Testing Label API Endpoint ===\n")

    # Load environment variables
    load_dotenv()

    # API endpoint
    url = "http://localhost:8002/api/labels"

    # Create test request payload
    payload = {
        "carrier": "fedex",
        "shipper": {
            "name": "Shipper Name",
            "street": "123 Shipper Street",
            "city": "Memphis",
            "state": "TN",
            "zip_code": "38117",
            "country": "US"
        },
        "recipient": {
            "name": "Recipient Name",
            "street": "456 Recipient Street",
            "city": "Atlanta",
            "state": "GA",
            "zip_code": "30339",
            "country": "US"
        },
        "package": {
            "weight": 5.0,
            "dimensions": {
                "length": 10.0,
                "width": 8.0,
                "height": 6.0
            }
        },
        "service_type": "FEDEX_GROUND"
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
            label_url = f"http://localhost:8002{data['label_url']}"
            print(f"\nFull Label URL: {label_url}")

            if data.get('fallback_qr_code_url'):
                qr_url = f"http://localhost:8002{data['fallback_qr_code_url']}"
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
    result = test_label_api()
    if result:
        print("\n✅ Label API test passed!")
    else:
        print("\n❌ Label API test failed!")
