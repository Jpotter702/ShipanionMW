#!/usr/bin/env python3
"""
Test script to verify FedEx label creation functionality.
"""

import asyncio
import os
from dotenv import load_dotenv
from models.shipping import Address, Package, Dimensions
from models.label_request import LabelRequest
from labels.fedex_ship import FedExShipEngine

async def test_fedex_label():
    """Test FedEx label creation"""
    print("\n=== Testing FedEx Label Creation ===\n")
    
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
    
    # Create test addresses
    shipper = Address(
        name="Shipper Name",
        street="123 Shipper Street",
        city="Memphis",
        state="TN",
        zip_code="38117",
        country="US"
    )
    
    recipient = Address(
        name="Recipient Name",
        street="456 Recipient Street",
        city="Atlanta",
        state="GA",
        zip_code="30339",
        country="US"
    )
    
    # Create test package
    dimensions = Dimensions(
        length=10.0,
        width=8.0,
        height=6.0
    )
    
    package = Package(
        weight=5.0,
        dimensions=dimensions
    )
    
    # Create label request
    request = LabelRequest(
        carrier="fedex",
        shipper=shipper,
        recipient=recipient,
        package=package,
        service_type="FEDEX_GROUND"
    )
    
    # Create FedEx ship engine
    engine = FedExShipEngine()
    
    try:
        # Create label
        print("\nCreating FedEx label...")
        response = await engine.create_label(request)
        
        # Print response
        print("\nLabel created successfully!")
        print(f"Tracking Number: {response.tracking_number}")
        print(f"Label URL: {response.label_url}")
        print(f"Native QR Code: {'Available' if response.native_qr_code_base64 else 'Not available'}")
        print(f"Fallback QR Code URL: {response.fallback_qr_code_url or 'Not generated yet'}")
        print(f"Estimated Delivery: {response.estimated_delivery}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error creating label: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fedex_label())
    if result:
        print("\n✅ FedEx label creation test passed!")
    else:
        print("\n❌ FedEx label creation test failed!")
