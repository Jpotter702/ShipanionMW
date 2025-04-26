from typing import Dict, Optional
from enum import Enum
from utils.exceptions import ValidationError  # Changed from relative to absolute import

class ServiceTier(Enum):
    """
    Standardized shipping service tiers based on delivery time.

    These are used for internal comparison only. The original carrier-specific
    service names should be displayed to the user and sent back to ElevenLabs.
    """
    # Internal enum values for comparison
    DAY1_AM = "1Day_AM"         # Next Business Day (Early Morning)
    DAY1_NOON = "1Day_Noon"     # Next Business Day (Mid-Morning)
    DAY1_EOD = "1Day_EOD"       # Next Business Day (Afternoon)
    DAY2_AM = "2Day_AM"         # 2 Business Days (Early Morning)
    DAY2_EOD = "2Day_EOD"       # 2 Business Days
    DAY3_EOD = "3day_EOD"       # 3 Business Days
    GROUND_EOD = "Ground_EOD"   # 1-5 Business Days (Business or Residential)

class ServiceNormalizer:
    def __init__(self):
        self._mappings: Dict[str, Dict[str, ServiceTier]] = {
            "fedex": {
                # Next Business Day services
                "FIRST_OVERNIGHT": ServiceTier.DAY1_AM,       # FedEx First Overnight
                "PRIORITY_OVERNIGHT": ServiceTier.DAY1_NOON,  # FedEx Priority Overnight
                "STANDARD_OVERNIGHT": ServiceTier.DAY1_EOD,   # FedEx Standard Overnight

                # 2-Day services
                "FEDEX_2_DAY_AM": ServiceTier.DAY2_AM,        # FedEx 2Day A.M.
                "FEDEX_2_DAY": ServiceTier.DAY2_EOD,          # FedEx 2Day

                # 3-Day services
                "FEDEX_EXPRESS_SAVER": ServiceTier.DAY3_EOD,  # FedEx Express Saver

                # Ground services
                "FEDEX_GROUND": ServiceTier.GROUND_EOD,       # FedEx Ground
                "FEDEX_HOME_DELIVERY": ServiceTier.GROUND_EOD # FedEx Home Delivery
            },
            "ups": {
                # Next Business Day services
                "01": ServiceTier.DAY1_AM,      # UPS Next Day Air Early
                "02": ServiceTier.DAY1_NOON,    # UPS Next Day Air
                "13": ServiceTier.DAY1_EOD,     # UPS Next Day Air Saver

                # 2-Day services
                "59": ServiceTier.DAY2_AM,      # UPS 2nd Day Air A.M.
                "02DA": ServiceTier.DAY2_EOD,   # UPS 2nd Day Air

                # 3-Day services
                "12": ServiceTier.DAY3_EOD,     # UPS 3 Day Select

                # Ground services
                "GND": ServiceTier.GROUND_EOD   # UPS Ground
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
