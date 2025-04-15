# Log
# TODO: Implement this module

import logging
import json
from datetime import datetime
from typing import Any, Dict

class CustomJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """Format log records as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(log_level: str = "INFO") -> None:
    """Configure application-wide logging"""
    # Create logger
    logger = logging.getLogger("shipvox")
    logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter and add it to the handler
    formatter = CustomJSONFormatter()
    console_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
