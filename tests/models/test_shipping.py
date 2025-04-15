import pytest
from datetime import datetime
from models.shipping import (
    Dimensions,
    Package,
    Address,
    RateRequest,
    ServiceOption,
    RateResponse
)

def test_dimensions_validation():
    """Test dimensions validation"""
    # Valid dimensions
    dims = Dimensions(length=10.0, width=10.0, height=10.0)
    assert dims.length == 10.0
    
    # Invalid dimensions
    with pytest.raises(ValueError):
        Dimensions(length=0.0, width=10.0, height=10.0)
    
    with pytest.raises(ValueError):
        Dimensions(length=109.0, width=10.0, height=10.0)

def test_package_validation():
    """Test package validation"""
    # Valid package without dimensions
    pkg = Package(weight=10.0)
    assert pkg.weight == 10.0
    assert pkg.dimensions is None
    
    # Valid package with dimensions
    dims = Dimensions(length=10.0, width=10.0, height=10.0)
    pkg = Package(weight=10.0, dimensions=dims)
    assert pkg.dimensions == dims
    
    # Invalid weight
    with pytest.raises(ValueError):
        Package(weight=0.0)
    
    with pytest.raises(ValueError):
        Package(weight=151.0)

def test_address_validation():
    """Test address validation"""
    # Valid address
    addr = Address(
        name="Test Name",
        street="123 Main St",
        city="Test City",
        state="CA",
        zip_code="12345"
    )
    assert addr.zip_code == "12345"
    
    # Valid address with ZIP+4
    addr = Address(
        name="Test Name",
        street="123 Main St",
        city="Test City",
        state="CA",
        zip_code="12345-6789"
    )
    assert addr.zip_code == "12345-6789"
    
    # Invalid ZIP code
    with pytest.raises(ValueError):
        Address(
            name="Test Name",
            street="123 Main St",
            city="Test City",
            state="CA",
            zip_code="1234"
        )

def test_rate_request_validation():
    """Test rate request validation"""
    origin = Address(
        name="Origin",
        street="123 Main St",
        city="Origin City",
        state="CA",
        zip_code="12345"
    )
    
    destination = Address(
        name="Destination",
        street="456 Main St",
        city="Dest City",
        state="NY",
        zip_code="54321"
    )
    
    package = Package(weight=10.0)
    
    # Valid request
    request = RateRequest(
        origin=origin,
        destination=destination,
        package=package
    )
    assert request.pickup_requested is False
    assert request.carrier_preferences is None
    
    # Valid request with preferences
    request = RateRequest(
        origin=origin,
        destination=destination,
        package=package,
        pickup_requested=True,
        carrier_preferences=["fedex", "ups"]
    )
    assert request.pickup_requested is True
    assert request.carrier_preferences == ["fedex", "ups"]

def test_service_option_validation():
    """Test service option validation"""
    # Valid service option
    option = ServiceOption(
        carrier="fedex",
        service_name="Ground",
        service_code="FEDEX_GROUND",
        cost=10.0,
        estimated_delivery=datetime.now(),
        guaranteed_delivery=True
    )
    assert option.carrier == "fedex"
    assert option.guaranteed_delivery is True

def test_rate_response_validation():
    """Test rate response validation"""
    service_option = ServiceOption(
        carrier="fedex",
        service_name="Ground",
        service_code="FEDEX_GROUND",
        cost=10.0
    )
    
    # Valid response
    response = RateResponse(
        request_id="test123",
        options=[service_option],
        cheapest_option=service_option
    )
    assert response.request_id == "test123"
    assert len(response.options) == 1
    assert response.errors is None
    
    # Valid response with errors
    response = RateResponse(
        request_id="test123",
        options=[service_option],
        cheapest_option=service_option,
        errors=["Test error"]
    )
    assert response.errors == ["Test error"] 