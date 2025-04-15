from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class Dimensions(BaseModel):
    length: float = Field(..., gt=0, description="Length in inches")
    width: float = Field(..., gt=0, description="Width in inches")
    height: float = Field(..., gt=0, description="Height in inches")

class RateRequest(BaseModel):
    origin_zip: str = Field(..., description="Origin ZIP code")
    destination_zip: str = Field(..., description="Destination ZIP code")
    weight: float = Field(..., gt=0, description="Weight in pounds")
    dimensions: Optional[Dimensions] = Field(None, description="Package dimensions in inches")
    pickup_requested: bool = Field(False, description="Whether pickup is requested")

    @validator('origin_zip', 'destination_zip')
    def validate_zip_code(cls, v):
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid ZIP code format')
        return v

    @validator('weight')
    def validate_weight(cls, v):
        if v > 150:  # Maximum weight limit in pounds
            raise ValueError('Weight exceeds maximum limit of 150 pounds')
        return v 