import pytest
from utils.validators import InputValidator
from utils.exceptions import ValidationError

def test_validate_zip_valid():
    """Test valid ZIP code validation"""
    assert InputValidator.validate_zip("12345")
    assert InputValidator.validate_zip("12345-6789")

def test_validate_zip_invalid():
    """Test invalid ZIP code validation"""
    with pytest.raises(ValidationError):
        InputValidator.validate_zip("1234")
    with pytest.raises(ValidationError):
        InputValidator.validate_zip("12345-678")
    with pytest.raises(ValidationError):
        InputValidator.validate_zip("abcde")

def test_validate_weight_valid():
    """Test valid weight validation"""
    assert InputValidator.validate_weight(1.0)
    assert InputValidator.validate_weight(150.0)

def test_validate_weight_invalid():
    """Test invalid weight validation"""
    with pytest.raises(ValidationError):
        InputValidator.validate_weight(0.0)
    with pytest.raises(ValidationError):
        InputValidator.validate_weight(-1.0)
    with pytest.raises(ValidationError):
        InputValidator.validate_weight(151.0)

def test_validate_dimensions_valid():
    """Test valid dimensions validation"""
    dimensions = {
        "length": 10.0,
        "width": 10.0,
        "height": 10.0
    }
    assert InputValidator.validate_dimensions(dimensions)

def test_validate_dimensions_invalid():
    """Test invalid dimensions validation"""
    # Missing required field
    with pytest.raises(ValidationError):
        InputValidator.validate_dimensions({
            "length": 10.0,
            "width": 10.0
        })
    
    # Negative dimension
    with pytest.raises(ValidationError):
        InputValidator.validate_dimensions({
            "length": -10.0,
            "width": 10.0,
            "height": 10.0
        })
    
    # Exceeds maximum
    with pytest.raises(ValidationError):
        InputValidator.validate_dimensions({
            "length": 109.0,
            "width": 10.0,
            "height": 10.0
        })

def test_validate_package_data_valid():
    """Test valid package data validation"""
    assert InputValidator.validate_package_data(10.0)
    assert InputValidator.validate_package_data(
        10.0,
        {"length": 10.0, "width": 10.0, "height": 10.0}
    )

def test_validate_package_data_invalid():
    """Test invalid package data validation"""
    with pytest.raises(ValidationError):
        InputValidator.validate_package_data(0.0)
    
    with pytest.raises(ValidationError):
        InputValidator.validate_package_data(
            10.0,
            {"length": -10.0, "width": 10.0, "height": 10.0}
        ) 