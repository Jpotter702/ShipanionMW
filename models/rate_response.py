from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from utils.service_normalizer import ServiceTier

class RateOption(BaseModel):
    carrier: str = Field(..., description="Carrier name (e.g., 'fedex', 'ups')")
    service_name: str = Field(..., description="Carrier-specific service name")
    service_tier: ServiceTier = Field(..., description="Normalized service tier")
    cost: float = Field(..., gt=0, description="Shipping cost in USD")
    estimated_delivery: datetime = Field(..., description="Estimated delivery date and time")
    transit_days: int = Field(..., ge=1, description="Number of transit days")

class RateResponse(BaseModel):
    cheapest_option: RateOption = Field(..., description="Cheapest available shipping option")
    fastest_option: Optional[RateOption] = Field(None, description="Fastest reasonably priced option")
    all_options: list[RateOption] = Field(default_factory=list, description="All available shipping options") 