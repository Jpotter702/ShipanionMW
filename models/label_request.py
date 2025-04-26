
from pydantic import BaseModel
from typing import Literal, Optional
from models.shipping import Address, Package, SpecialServices

class LabelRequest(BaseModel):
    carrier: Literal["fedex", "ups"]
    shipper: Address
    recipient: Address
    package: Package
    service_type: str  # e.g., FEDEX_GROUND, FEDEX_2_DAY_AM
    special_services: Optional[SpecialServices] = None
