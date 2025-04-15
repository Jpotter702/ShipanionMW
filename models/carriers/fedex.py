from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class FedExAddress(BaseModel):
    """FedEx address format"""
    streetLines: List[str]
    city: str
    stateOrProvinceCode: str
    postalCode: str
    countryCode: str = "US"

class FedExWeight(BaseModel):
    """FedEx weight format"""
    value: float
    units: str = "LB"

class FedExDimensions(BaseModel):
    """FedEx dimensions format"""
    length: float
    width: float
    height: float
    units: str = "IN"

class FedExRequestedPackageLineItem(BaseModel):
    """FedEx package details"""
    weight: FedExWeight
    dimensions: Optional[FedExDimensions] = None
    groupPackageCount: int = 1

class FedExRateRequest(BaseModel):
    """FedEx rate request format"""
    accountNumber: Optional[str] = None
    requestedShipment: dict = Field(
        default_factory=lambda: {
            "rateRequestType": ["LIST"],
            "preferredCurrency": "USD"
        }
    )
    origin: FedExAddress
    destination: FedExAddress
    shippingChargesPayment: dict = Field(
        default_factory=lambda: {
            "paymentType": "SENDER"
        }
    )
    rateRequestControlParameters: dict = Field(
        default_factory=lambda: {
            "returnTransitTimes": True,
            "servicesNeededOnRateFailure": True
        }
    )

class FedExServiceOption(BaseModel):
    """FedEx service option details"""
    serviceType: str
    serviceName: str
    packagingType: str
    rateDetail: dict
    deliveryDayOfWeek: Optional[str] = None
    deliveryTimestamp: Optional[datetime] = None
    transitTime: Optional[str] = None
    signatureOption: Optional[str] = None
    actualRateType: str
    ratedShipmentDetails: List[dict] 