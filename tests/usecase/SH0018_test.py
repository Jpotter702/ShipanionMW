#!/usr/bin/env python3
"""
Test script for FedEx Ship API - Test Case SH0018
US to Canada, INTERNATIONAL_PRIORITY, YOUR_PACKAGING, SENDER, URL_ONLY, PAPER_LETTER
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_sh0018():
    """Test case SH0018"""
    print("\n=== Testing SH0018: US to Canada, INTERNATIONAL_PRIORITY, YOUR_PACKAGING ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Get FedEx credentials
    account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')
    
    # API endpoint - either direct to FedEx or through our API
    # url = "https://apis-sandbox.fedex.com/ship/v1/shipments"  # Direct to FedEx
    url = "http://localhost:8000/api/labels"  # Through our API
    
    # Create test request payload
    payload = {
        "carrier": "fedex",
        "service_type": "INTERNATIONAL_PRIORITY",
        "shipper": {
            "name": "Shipper Name",
            "street": "123 Shipper Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "US",
            "phone": "2125551212",
            "company": "Shipper Company"
        },
        "recipient": {
            "name": "Recipient Name",
            "street": "456 Recipient Street",
            "city": "Toronto",
            "state": "ON",
            "zip_code": "M5V 2N4",
            "country": "CA",
            "phone": "4165551212",
            "company": "Recipient Company"
        },
        "package": {
            "weight": 5.0,
            "dimensions": {
                "length": 12.0,
                "width": 8.0,
                "height": 6.0
            },
            "packaging_type": "YOUR_PACKAGING"
        },
        "customs": {
            "document_only": False,
            "customs_value": 100.0,
            "currency": "USD",
            "commodities": [
                {
                    "description": "Electronics",
                    "quantity": 1,
                    "unit_price": 100.0,
                    "weight": 5.0,
                    "country_of_manufacture": "US"
                }
            ]
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
            label_url = f"http://localhost:8000{data['label_url']}"
            print(f"\nFull Label URL: {label_url}")
            
            if data.get('fallback_qr_code_url'):
                qr_url = f"http://localhost:8000{data['fallback_qr_code_url']}"
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
    result = test_sh0018()
    if result:
        print("\n✅ SH0018 test passed!")
    else:
        print("\n❌ SH0018 test failed!")
