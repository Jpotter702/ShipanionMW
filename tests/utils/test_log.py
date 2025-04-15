import json
import logging
from utils.log import CustomJSONFormatter, setup_logging

def test_json_formatter():
    """Test JSON formatter output"""
    formatter = CustomJSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    assert "timestamp" in data
    assert data["level"] == "INFO"
    assert data["message"] == "Test message"
    assert data["module"] == "test"
    assert data["function"] == "<module>"
    assert data["line"] == 1

def test_json_formatter_with_exception():
    """Test JSON formatter with exception"""
    formatter = CustomJSONFormatter()
    try:
        raise ValueError("Test error")
    except ValueError as e:
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error occurred",
            args=(),
            exc_info=(type(e), e, e.__traceback__)
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert "exception" in data
        assert "ValueError: Test error" in data["exception"]

def test_setup_logging():
    """Test logging setup"""
    setup_logging("DEBUG")
    logger = logging.getLogger("shipvox")
    
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0].formatter, CustomJSONFormatter)
    assert not logger.propagate 