from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import rates, labels
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Print environment variables for debugging
print("Environment variables loaded from .env:")
print(f"FEDEX_CLIENT_ID: {os.getenv('FEDEX_CLIENT_ID')}")
print(f"FEDEX_CLIENT_SECRET: {os.getenv('FEDEX_CLIENT_SECRET')}")
print(f"FEDEX_ACCOUNT_NUMBER: {os.getenv('FEDEX_ACCOUNT_NUMBER')}")
print(f"FEDEX_METER_NUMBER: {os.getenv('FEDEX_METER_NUMBER')}")
print(f"FEDEX_API_URL: {os.getenv('FEDEX_API_URL')}")

# Set environment variables explicitly
os.environ['FEDEX_CLIENT_ID'] = os.getenv('FEDEX_CLIENT_ID')
os.environ['FEDEX_CLIENT_SECRET'] = os.getenv('FEDEX_CLIENT_SECRET')
os.environ['FEDEX_ACCOUNT_NUMBER'] = os.getenv('FEDEX_ACCOUNT_NUMBER')
os.environ['FEDEX_METER_NUMBER'] = os.getenv('FEDEX_METER_NUMBER')
os.environ['FEDEX_API_URL'] = os.getenv('FEDEX_API_URL')

app = FastAPI(
    title="ShipVox API",
    description="Shipping rate aggregation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rates.router, prefix="/api", tags=["rates"])
app.include_router(labels.router, prefix="/api", tags=["labels"])

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to ShipVox API"}
