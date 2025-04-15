# Exceptions
# TODO: Implement this module

class ShipVoxBaseException(Exception):
    """Base exception for all ShipVox errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AuthenticationError(ShipVoxBaseException):
    """Authentication related errors"""
    pass

class ValidationError(ShipVoxBaseException):
    """Data validation errors"""
    pass

class CarrierAPIError(ShipVoxBaseException):
    """Carrier API related errors"""
    pass

class ConfigurationError(ShipVoxBaseException):
    """Configuration related errors"""
    pass
