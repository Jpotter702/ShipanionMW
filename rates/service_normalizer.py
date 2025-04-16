from enum import Enum
from typing import Dict

class ServiceTier(str, Enum):
    GROUND = "ground"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    SAVER = "saver"

class ServiceNormalizer:
    def __init__(self):
        self._mappings = {
            'fedex': {
                'FEDEX_GROUND': ServiceTier.GROUND,
                'FEDEX_2_DAY': ServiceTier.EXPRESS,
                'FEDEX_OVERNIGHT': ServiceTier.OVERNIGHT,
                'FEDEX_EXPRESS_SAVER': ServiceTier.SAVER
            },
            'ups': {
                'GND': ServiceTier.GROUND,
                '2DA': ServiceTier.EXPRESS,
                '1DA': ServiceTier.OVERNIGHT,
                '3DS': ServiceTier.SAVER
            }
        }

    def normalize_service(self, carrier: str, service_code: str) -> ServiceTier:
        """
        Normalize carrier-specific service codes to standard tiers.
        """
        return self._mappings.get(carrier, {}).get(service_code, ServiceTier.GROUND)
