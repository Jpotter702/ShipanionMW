from typing import Optional, Dict, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

class Dimensions(BaseModel):
    """Package dimensions in inches"""
    length: float = Field(..., gt=0, le=108, description="Length in inches")
    width: float = Field(..., gt=0, le=108, description="Width in inches")
    height: float = Field(..., gt=0, le=108, description="Height in inches")

class Package(BaseModel):
    """Package details"""
    weight: float = Field(..., gt=0, le=150, description="Weight in pounds")
    dimensions: Optional[Dimensions] = None

class Address(BaseModel):
    """Shipping address"""
    name: str
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        import re
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid ZIP code format')
        return v

class RateRequest(BaseModel):
    """Rate request model"""
    origin: Address
    destination: Address
    package: Package
    pickup_requested: bool = False
    carrier_preferences: Optional[List[str]] = None

class ServiceOption(BaseModel):
    """Shipping service option"""
    carrier: str
    service_name: str
    service_code: str
    cost: float
    estimated_delivery: Optional[datetime] = None
    guaranteed_delivery: bool = False

class RateResponse(BaseModel):
    """Rate response model"""
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    options: List[ServiceOption]
    cheapest_option: ServiceOption
    fastest_option: Optional[ServiceOption] = None
    errors: Optional[List[str]] = None 