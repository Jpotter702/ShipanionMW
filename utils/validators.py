# Validators
# TODO: Implement this module

import re
from typing import Dict, Optional
from .exceptions import ValidationError

class InputValidator:
    ZIP_CODE_PATTERN = r'^\d{5}(-\d{4})?$'
    
    @staticmethod
    def validate_zip(zip_code: str) -> bool:
        """Validate ZIP code format"""
        if not re.match(InputValidator.ZIP_CODE_PATTERN, zip_code):
            raise ValidationError(f"Invalid ZIP code format: {zip_code}")
        return True
    
    @staticmethod
    def validate_weight(weight: float) -> bool:
        """Validate weight is positive and within limits"""
        if weight <= 0:
            raise ValidationError("Weight must be positive")
        if weight > 150:  # Assuming 150 lbs is max weight
            raise ValidationError("Weight exceeds maximum limit of 150 lbs")
        return True
    
    @staticmethod
    def validate_dimensions(dimensions: Dict[str, float]) -> bool:
        """Validate package dimensions"""
        required_fields = {"length", "width", "height"}
        if not all(field in dimensions for field in required_fields):
            raise ValidationError("Dimensions must include length, width, and height")
        
        for dim, value in dimensions.items():
            if value <= 0:
                raise ValidationError(f"{dim} must be positive")
            if value > 108:  # Assuming 108 inches is max dimension
                raise ValidationError(f"{dim} exceeds maximum limit of 108 inches")
        
        return True
    
    @staticmethod
    def validate_package_data(
        weight: float,
        dimensions: Optional[Dict[str, float]] = None
    ) -> bool:
        """Validate complete package data"""
        InputValidator.validate_weight(weight)
        if dimensions:
            InputValidator.validate_dimensions(dimensions)
        return True
