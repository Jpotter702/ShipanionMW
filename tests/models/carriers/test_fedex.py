import pytest
from datetime import datetime
from models.carriers.fedex import (
    FedExAddress,
    FedExWeight,
    FedExDimensions,
    FedExRequestedPackageLineItem,
    FedExRateRequest,
    FedExServiceOption
)

def test_fedex_address_validation():
    """Test FedEx address validation"""
    # Valid address
    addr = FedExAddress(
        streetLines=["123 Main St"],
        city="Test City",
        stateOrProvinceCode="CA",
        postalCode="12345"
    )
    assert addr.countryCode == "US"
    assert addr.postalCode == "12345"
    
    # Valid address with multiple street lines
    addr = FedExAddress(
        streetLines=["123 Main St", "Suite 100"],
        city="Test City",
        stateOrProvinceCode="CA",
        postalCode="12345"
    )
    assert len(addr.streetLines) == 2

def test_fedex_weight_validation():
    """Test FedEx weight validation"""
    # Valid weight
    weight = FedExWeight(value=10.0)
    assert weight.value == 10.0
    assert weight.units == "LB"

def test_fedex_dimensions_validation():
    """Test FedEx dimensions validation"""
    # Valid dimensions
    dims = FedExDimensions(
        length=10.0,
        width=10.0,
        height=10.0
    )
    assert dims.length == 10.0
    assert dims.units == "IN"

def test_fedex_package_line_item_validation():
    """Test FedEx package line item validation"""
    # Valid package with weight only
    weight = FedExWeight(value=10.0)
    pkg = FedExRequestedPackageLineItem(weight=weight)
    assert pkg.weight == weight
    assert pkg.dimensions is None
    assert pkg.groupPackageCount == 1
    
    # Valid package with dimensions
    dims = FedExDimensions(
        length=10.0,
        width=10.0,
        height=10.0
    )
    pkg = FedExRequestedPackageLineItem(
        weight=weight,
        dimensions=dims
    )
    assert pkg.dimensions == dims

def test_fedex_rate_request_validation():
    """Test FedEx rate request validation"""
    origin = FedExAddress(
        streetLines=["123 Main St"],
        city="Origin City",
        stateOrProvinceCode="CA",
        postalCode="12345"
    )
    
    destination = FedExAddress(
        streetLines=["456 Main St"],
        city="Dest City",
        stateOrProvinceCode="NY",
        postalCode="54321"
    )
    
    # Valid request
    request = FedExRateRequest(
        origin=origin,
        destination=destination
    )
    assert request.requestedShipment["rateRequestType"] == ["LIST"]
    assert request.requestedShipment["preferredCurrency"] == "USD"

def test_fedex_service_option_validation():
    """Test FedEx service option validation"""
    # Valid service option
    option = FedExServiceOption(
        serviceType="FEDEX_GROUND",
        serviceName="FedEx Ground",
        packagingType="YOUR_PACKAGING",
        rateDetail={"totalNetCharge": 10.0},
        actualRateType="PAYOR_ACCOUNT_PACKAGE",
        ratedShipmentDetails=[{"totalNetCharge": 10.0}]
    )
    assert option.serviceType == "FEDEX_GROUND"
    assert option.deliveryTimestamp is None 