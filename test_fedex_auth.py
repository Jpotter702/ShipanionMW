#!/usr/bin/env python3
"""
Test script to verify FedEx authentication is working properly.
"""

import asyncio
import os
from auth.fedex_auth import FedExAuth
from dotenv import load_dotenv

async def test_fedex_auth():
    """Test FedEx authentication"""
    print("Testing FedEx authentication...")
    
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
    
    # Create FedEx auth instance
    auth = FedExAuth()
    
    try:
        # Get token
        print("\nAttempting to get FedEx token...")
        token = await auth.get_token()
        print(f"Successfully got token: {token[:15]}...")
        
        # Try to get the token again (should use cached token)
        print("\nAttempting to get token again (should use cached token)...")
        token2 = await auth.get_token()
        print(f"Successfully got token again: {token2[:15]}...")
        
        # Verify tokens match
        if token == token2:
            print("✅ Tokens match - caching is working")
        else:
            print("❌ Tokens don't match - caching is not working")
        
        return True
    except Exception as e:
        print(f"❌ Error getting FedEx token: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fedex_auth())
    if result:
        print("\n✅ FedEx authentication test passed!")
    else:
        print("\n❌ FedEx authentication test failed!")
