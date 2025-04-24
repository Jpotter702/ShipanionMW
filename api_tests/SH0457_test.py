#!/usr/bin/env python3
"""
Test script for FedEx Ship API - Test Case SH0457
US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING, SENDER, URL_ONLY, PAPER_LETTER
With Email Notification
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_sh0457():
    """Test case SH0457"""
    print("\n=== Testing SH0457: US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING with Email Notification ===\n")
    
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
        "service_type": "PRIORITY_OVERNIGHT",
        "shipper": {
            "name": "Shipper Name",
            "street": "123 Shipper Street",
            "city": "Memphis",
            "state": "TN",
            "zip_code": "38117",
            "country": "US",
            "phone": "9018328595",
            "company": "Shipper Company",
            "email": "shipper@example.com"
        },
        "recipient": {
            "name": "Recipient Name",
            "street": "456 Recipient Street",
            "city": "Atlanta",
            "state": "GA",
            "zip_code": "30339",
            "country": "US",
            "phone": "9018328595",
            "company": "Recipient Company",
            "email": "recipient@example.com"
        },
        "package": {
            "weight": 5.0,
            "dimensions": {
                "length": 10.0,
                "width": 8.0,
                "height": 6.0
            },
            "packaging_type": "YOUR_PACKAGING"
        },
        "special_services": {
            "email_notification": {
                "recipients": [
                    {
                        "email": "recipient@example.com",
                        "notification_types": ["SHIPMENT", "DELIVERY"]
                    },
                    {
                        "email": "shipper@example.com",
                        "notification_types": ["SHIPMENT"]
                    }
                ]
            }
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
    result = test_sh0457()
    if result:
        print("\n✅ SH0457 test passed!")
    else:
        print("\n❌ SH0457 test failed!")
