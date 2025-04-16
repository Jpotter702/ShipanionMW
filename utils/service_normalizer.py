from typing import Dict, Optional
from enum import Enum
from utils.exceptions import ValidationError  # Changed from relative to absolute import

class ServiceTier(Enum):
    """Standardized shipping service tiers"""
    GROUND = "GROUND"
    EXPEDITED = "EXPEDITED"
    EXPRESS = "EXPRESS"
    PRIORITY = "PRIORITY"
    SAME_DAY = "SAME_DAY"

class ServiceNormalizer:
    def __init__(self):
        self._mappings: Dict[str, Dict[str, ServiceTier]] = {
            "fedex": {
                "FEDEX_GROUND": ServiceTier.GROUND,
                "FEDEX_HOME_DELIVERY": ServiceTier.GROUND,
                "FEDEX_2_DAY": ServiceTier.EXPEDITED,
                "FEDEX_2_DAY_AM": ServiceTier.EXPEDITED,
                "FEDEX_EXPRESS_SAVER": ServiceTier.EXPEDITED,
                "STANDARD_OVERNIGHT": ServiceTier.EXPRESS,
                "PRIORITY_OVERNIGHT": ServiceTier.PRIORITY,
                "FIRST_OVERNIGHT": ServiceTier.PRIORITY,
                "SAME_DAY": ServiceTier.SAME_DAY,
                "SAME_DAY_CITY": ServiceTier.SAME_DAY
            }
        }
    
    def normalize_service(self, carrier: str, service_code: str) -> ServiceTier:
        """Normalize a carrier-specific service code to a standard tier"""
        if carrier not in self._mappings:
            raise ValidationError(f"Unsupported carrier: {carrier}")
        
        carrier_mappings = self._mappings[carrier]
        if service_code not in carrier_mappings:
            raise ValidationError(
                f"Unknown service code {service_code} for carrier {carrier}"
            )
        
        return carrier_mappings[service_code]
    
    def get_carrier_services(self, carrier: str, tier: ServiceTier) -> list:
        """Get all service codes for a carrier that match a specific tier"""
        if carrier not in self._mappings:
            raise ValidationError(f"Unsupported carrier: {carrier}")
        
        return [
            code for code, service_tier in self._mappings[carrier].items()
            if service_tier == tier
        ]
    
    def add_mapping(
        self,
        carrier: str,
        service_code: str,
        tier: ServiceTier
    ) -> None:
        """Add a new service mapping"""
        if carrier not in self._mappings:
            self._mappings[carrier] = {}
        
        self._mappings[carrier][service_code] = tier 
