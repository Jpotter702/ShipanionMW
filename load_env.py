#!/usr/bin/env python3
"""
Load environment variables from .env file and print them.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Print environment variables
print("Environment variables:")
print(f"FEDEX_CLIENT_ID: {os.getenv('FEDEX_CLIENT_ID')}")
print(f"FEDEX_CLIENT_SECRET: {os.getenv('FEDEX_CLIENT_SECRET')}")
print(f"FEDEX_ACCOUNT_NUMBER: {os.getenv('FEDEX_ACCOUNT_NUMBER')}")
print(f"FEDEX_METER_NUMBER: {os.getenv('FEDEX_METER_NUMBER')}")
print(f"FEDEX_API_URL: {os.getenv('FEDEX_API_URL')}")
