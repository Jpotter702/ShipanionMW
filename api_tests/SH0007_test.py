#!/usr/bin/env python3
"""
Test script for FedEx Ship API - Test Case SH0007
US to US, FEDEX_GROUND, YOUR_PACKAGING, SENDER, URL_ONLY, PAPER_LETTER
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_sh0007():
    """Test case SH0007"""
    print("\n=== Testing SH0007: US to US, FEDEX_GROUND, YOUR_PACKAGING ===\n")
    
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
        "service_type": "FEDEX_GROUND",
        "shipper": {
            "name": "Shipper Name",
            "street": "123 Shipper Street",
            "city": "Memphis",
            "state": "TN",
            "zip_code": "38117",
            "country": "US",
            "phone": "9018328595",
            "company": "Shipper Company"
        },
        "recipient": {
            "name": "Recipient Name",
            "street": "456 Recipient Street",
            "city": "Atlanta",
            "state": "GA",
            "zip_code": "30339",
            "country": "US",
            "phone": "9018328595",
            "company": "Recipient Company"
        },
        "package": {
            "weight": 20.0,
            "dimensions": {
                "length": 20.0,
                "width": 15.0,
                "height": 10.0
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
    result = test_sh0007()
    if result:
        print("\n✅ SH0007 test passed!")
    else:
        print("\n❌ SH0007 test failed!")
