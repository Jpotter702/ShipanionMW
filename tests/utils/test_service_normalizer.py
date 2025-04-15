import pytest
from utils.service_normalizer import ServiceNormalizer, ServiceTier

def test_normalize_service():
    """Test service normalization"""
    normalizer = ServiceNormalizer()
    
    # Test known FedEx services
    assert normalizer.normalize_service("fedex", "FEDEX_GROUND") == ServiceTier.GROUND
    assert normalizer.normalize_service("fedex", "FEDEX_2_DAY") == ServiceTier.EXPEDITED
    assert normalizer.normalize_service("fedex", "STANDARD_OVERNIGHT") == ServiceTier.EXPRESS
    assert normalizer.normalize_service("fedex", "PRIORITY_OVERNIGHT") == ServiceTier.PRIORITY
    assert normalizer.normalize_service("fedex", "SAME_DAY") == ServiceTier.SAME_DAY
    
    # Test unknown carrier
    with pytest.raises(ValidationError):
        normalizer.normalize_service("unknown", "SERVICE")
    
    # Test unknown service
    with pytest.raises(ValidationError):
        normalizer.normalize_service("fedex", "UNKNOWN_SERVICE")

def test_get_carrier_services():
    """Test getting carrier services by tier"""
    normalizer = ServiceNormalizer()
    
    # Test known tiers
    ground_services = normalizer.get_carrier_services("fedex", ServiceTier.GROUND)
    assert "FEDEX_GROUND" in ground_services
    assert "FEDEX_HOME_DELIVERY" in ground_services
    
    expedited_services = normalizer.get_carrier_services("fedex", ServiceTier.EXPEDITED)
    assert "FEDEX_2_DAY" in expedited_services
    assert "FEDEX_EXPRESS_SAVER" in expedited_services
    
    # Test unknown carrier
    with pytest.raises(ValidationError):
        normalizer.get_carrier_services("unknown", ServiceTier.GROUND)

def test_add_mapping():
    """Test adding new service mappings"""
    normalizer = ServiceNormalizer()
    
    # Add new carrier
    normalizer.add_mapping("new_carrier", "NEW_SERVICE", ServiceTier.GROUND)
    assert normalizer.normalize_service("new_carrier", "NEW_SERVICE") == ServiceTier.GROUND
    
    # Add new service to existing carrier
    normalizer.add_mapping("fedex", "NEW_FEDEX_SERVICE", ServiceTier.EXPRESS)
    assert normalizer.normalize_service("fedex", "NEW_FEDEX_SERVICE") == ServiceTier.EXPRESS 