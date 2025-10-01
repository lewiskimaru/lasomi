"""
Logging configuration for Atlas API
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a structured logger"""
    return structlog.get_logger(name)


def log_request_separator(logger: logging.Logger, method: str, endpoint: str) -> None:
    """
    Log a visual separator for new API requests to improve debugging.
    
    Args:
        logger: The logger instance to use
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = f"===== NEW REQUEST: {method} {endpoint} at {timestamp} ====="
    logger.info(separator)