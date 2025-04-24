#!/usr/bin/env python3
"""
Test script for FedEx Ship API - Test Case SH0473
US to US, FEDEX_GROUND, YOUR_PACKAGING, SENDER, URL_ONLY, PAPER_LETTER
With Multiple Packages
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_sh0473():
    """Test case SH0473"""
    print("\n=== Testing SH0473: US to US, FEDEX_GROUND, YOUR_PACKAGING with Multiple Packages ===\n")
    
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
        "packages": [
            {
                "weight": 5.0,
                "dimensions": {
                    "length": 10.0,
                    "width": 8.0,
                    "height": 6.0
                },
                "packaging_type": "YOUR_PACKAGING",
                "sequence_number": 1,
                "reference": "PKG1"
            },
            {
                "weight": 7.0,
                "dimensions": {
                    "length": 12.0,
                    "width": 10.0,
                    "height": 8.0
                },
                "packaging_type": "YOUR_PACKAGING",
                "sequence_number": 2,
                "reference": "PKG2"
            },
            {
                "weight": 3.0,
                "dimensions": {
                    "length": 8.0,
                    "width": 6.0,
                    "height": 4.0
                },
                "packaging_type": "YOUR_PACKAGING",
                "sequence_number": 3,
                "reference": "PKG3"
            }
        ],
        "total_package_count": 3
    }
    
    # Send request
    print("Sending request to label API...")
    try:
        response = requests.post(url, json=payload)
        
        # Check response
        if response.status_code == 200:
            print("\nLabels created successfully!")
            data = response.json()
            
            if isinstance(data, list):
                # Multiple labels returned
                for i, label in enumerate(data):
                    print(f"\nPackage {i+1}:")
                    print(f"Tracking Number: {label['tracking_number']}")
                    print(f"Label URL: {label['label_url']}")
                    print(f"Native QR Code: {'Available' if label.get('native_qr_code_base64') else 'Not available'}")
                    print(f"Fallback QR Code URL: {label.get('fallback_qr_code_url', 'Not generated yet')}")
                    print(f"Estimated Delivery: {label.get('estimated_delivery')}")
                    
                    # Construct full URL for label
                    label_url = f"http://localhost:8000{label['label_url']}"
                    print(f"Full Label URL: {label_url}")
                    
                    if label.get('fallback_qr_code_url'):
                        qr_url = f"http://localhost:8000{label['fallback_qr_code_url']}"
                        print(f"Full QR Code URL: {qr_url}")
            else:
                # Single label or master label returned
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
    result = test_sh0473()
    if result:
        print("\n✅ SH0473 test passed!")
    else:
        print("\n❌ SH0473 test failed!")
