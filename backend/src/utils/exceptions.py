"""
Custom exceptions for Atlas API
"""

from typing import Optional, Any


class AtlasException(Exception):
    """Base exception for Atlas API"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "ATLAS_ERROR",
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class ValidationError(AtlasException):
    """Raised when request validation fails"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class DataSourceError(AtlasException):
    """Raised when data source operations fail"""
    
    def __init__(self, source: str, message: str, details: Optional[Any] = None):
        super().__init__(
            message=f"Data source '{source}' error: {message}",
            status_code=502,
            error_code="DATA_SOURCE_ERROR",
            details=details
        )


class ProcessingError(AtlasException):
    """Raised when feature processing fails"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="PROCESSING_ERROR",
            details=details
        )


class ExportError(AtlasException):
    """Raised when export operations fail"""
    
    def __init__(self, format_name: str, message: str, details: Optional[Any] = None):
        super().__init__(
            message=f"Export to {format_name} failed: {message}",
            status_code=500,
            error_code="EXPORT_ERROR",
            details=details
        )


class AOITooLargeError(AtlasException):
    """Raised when AOI exceeds size limits"""
    
    def __init__(self, area_km2: float, max_area_km2: float):
        super().__init__(
            message=f"AOI area ({area_km2:.2f} km²) exceeds maximum allowed size ({max_area_km2} km²)",
            status_code=413,
            error_code="AOI_TOO_LARGE",
            details={"area_km2": area_km2, "max_area_km2": max_area_km2}
        )


class RateLimitError(AtlasException):
    """Raised when external API rate limits are exceeded"""
    
    def __init__(self, source: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for {source}",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"source": source, "retry_after": retry_after}
        )


class AuthenticationError(AtlasException):
    """Raised when authentication to external services fails"""
    
    def __init__(self, source: str, message: str):
        super().__init__(
            message=f"Authentication failed for {source}: {message}",
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details={"source": source}
        )


class TimeoutError(AtlasException):
    """Raised when operations timeout"""
    
    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(
            message=f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            status_code=408,
            error_code="TIMEOUT_ERROR",
            details={"operation": operation, "timeout_seconds": timeout_seconds}
        )