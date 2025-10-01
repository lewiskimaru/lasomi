"""
Health check endpoints for monitoring service status
"""

import time
import asyncio
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException, Request

from src.api.api_schemas import HealthStatus, DataSourceHealth
from src.core.data_sources.google_earth_engine import GoogleEarthEngineConnector
from src.core.data_sources.openstreetmap import OpenStreetMapConnector
from src.api.api_schemas import DataSourceType, DataSourceConfig
from src.core.config import get_settings, debug_environment_variables
from src.utils.logging_config import log_request_separator

router = APIRouter()
settings = get_settings()

# Service start time for uptime calculation
SERVICE_START_TIME = time.time()

# Logger for health endpoints
import logging
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthStatus)
async def health_check(http_request: Request):
    """Basic health check endpoint"""
    
    # Log request separator for debugging
    log_request_separator(logger, http_request.method, str(http_request.url.path))
    
    uptime = time.time() - SERVICE_START_TIME
    
    return HealthStatus(
        status="healthy",
        version=settings.version,
        timestamp=datetime.utcnow(),
        uptime=uptime
    )


@router.get("/health/ready")
async def readiness_check(http_request: Request):
    """Kubernetes readiness probe endpoint"""
    
    # Log request separator for debugging
    log_request_separator(logger, http_request.method, str(http_request.url.path))
    
    # Basic readiness checks
    try:
        # Check if we can import required modules
        import geopandas
        import shapely
        
        return {"status": "ready", "timestamp": datetime.utcnow()}
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get("/health/live")
async def liveness_check(http_request: Request):
    """Kubernetes liveness probe endpoint"""
    
    # Log request separator for debugging
    log_request_separator(logger, http_request.method, str(http_request.url.path))
    
    return {"status": "alive", "timestamp": datetime.utcnow()}


@router.get("/health/data-sources", response_model=DataSourceHealth)
async def data_sources_health(http_request: Request):
    """Check health of external data sources"""
    
    try:
        # Log request separator for debugging
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        # Test data source connections concurrently
        gee_task = asyncio.create_task(_test_google_earth_engine())
        osm_task = asyncio.create_task(_test_overpass_api())
        
        # Wait for both tests with timeout
        gee_healthy, osm_healthy = await asyncio.gather(
            gee_task, osm_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(gee_healthy, Exception):
            gee_healthy = False
        if isinstance(osm_healthy, Exception):
            osm_healthy = False
        
        return DataSourceHealth(
            google_earth_engine=gee_healthy,
            overpass_api=osm_healthy,
            last_checked=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to check data source health: {str(e)}"
        )


async def _test_google_earth_engine() -> bool:
    """Test Google Earth Engine connectivity"""
    
    try:
        # Create a test connector
        config = DataSourceConfig(enabled=True, timeout=10)
        connector = GoogleEarthEngineConnector(DataSourceType.MICROSOFT_BUILDINGS, config)
        
        # Test connection
        return await connector.test_connection()
        
    except Exception:
        return False


async def _test_overpass_api() -> bool:
    """Test Overpass API connectivity"""
    
    try:
        # Create a test connector
        config = DataSourceConfig(enabled=True, timeout=10)
        connector = OpenStreetMapConnector(DataSourceType.OSM_BUILDINGS, config)
        
        # Test connection
        return await connector.test_connection()
        
    except Exception:
        return False


@router.get("/health/detailed")
async def detailed_health(http_request: Request):
    """Detailed health check with system information"""
    
    try:
        # Log request separator for debugging
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        import psutil
        import sys
        
        # Get system information
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk_info = psutil.disk_usage('/')
        
        # Get Python information
        python_version = sys.version
        
        # Get data source health
        data_sources = await data_sources_health()
        
        uptime = time.time() - SERVICE_START_TIME
        
        return {
            "service": {
                "status": "healthy",
                "version": settings.version,
                "uptime_seconds": uptime,
                "python_version": python_version
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory_info.total / (1024**3), 2),
                    "available_gb": round(memory_info.available / (1024**3), 2),
                    "percent_used": memory_info.percent
                },
                "disk": {
                    "total_gb": round(disk_info.total / (1024**3), 2),
                    "free_gb": round(disk_info.free / (1024**3), 2),
                    "percent_used": round((disk_info.used / disk_info.total) * 100, 1)
                }
            },
            "data_sources": data_sources.dict(),
            "configuration": {
                "max_aoi_area_km2": settings.max_aoi_area_km2,
                "request_timeout": settings.request_timeout,
                "debug_mode": settings.debug,
                "overpass_rate_limit": settings.overpass_rate_limit,
                "overpass_timeout": settings.overpass_timeout
            },
            "timestamp": datetime.utcnow()
        }
        
    except ImportError:
        # psutil not available, return basic health
        return await health_check()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detailed health check failed: {str(e)}"
        )


@router.get("/health/debug-env")
async def debug_environment(http_request: Request):
    """Debug endpoint to inspect environment variables (only available in debug mode)"""

    # Log request separator for debugging
    log_request_separator(logger, http_request.method, str(http_request.url.path))

    if not settings.debug:
        raise HTTPException(
            status_code=404,
            detail="Debug endpoints are only available when DEBUG=true"
        )

    try:
        debug_info = debug_environment_variables()

        return {
            "message": "Environment variable debug information",
            "debug_info": debug_info,
            "current_settings": {
                "service_name": settings.service_name,
                "version": settings.version,
                "debug": settings.debug,
                "log_level": settings.log_level,
                "max_aoi_area_km2": settings.max_aoi_area_km2,
                "request_timeout": settings.request_timeout,
                "overpass_rate_limit": settings.overpass_rate_limit,
                "overpass_timeout": settings.overpass_timeout,
                "overpass_api_url": settings.overpass_api_url,
                "google_cloud_project": settings.google_cloud_project,
                "google_service_account_email": settings.google_service_account_email,
                "allowed_origins": settings.allowed_origins
            },
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Environment debug failed: {str(e)}"
        )


@router.get("/health/debug-gee")
async def debug_google_earth_engine():
    """Debug endpoint for Google Earth Engine authentication (only available in debug mode)"""

    if not settings.debug:
        raise HTTPException(
            status_code=404,
            detail="Debug endpoints are only available when DEBUG=true"
        )

    try:
        from src.utils.gee_auth import validate_service_account_setup, test_earth_engine_connection

        # Validate service account setup
        validation_results = validate_service_account_setup()

        # Test connection if validation passes
        connection_test = False
        if validation_results['valid']:
            connection_test = test_earth_engine_connection()

        return {
            "message": "Google Earth Engine debug information",
            "service_account_validation": validation_results,
            "connection_test_passed": connection_test,
            "configuration": {
                "google_cloud_project": settings.google_cloud_project,
                "google_service_account_email": settings.google_service_account_email,
                "credentials_configured": bool(settings.google_cloud_project and settings.google_service_account_email)
            },
            "troubleshooting_guide": {
                "common_oauth_issues": [
                    "Service account missing 'Earth Engine Resource Viewer' role",
                    "Project not registered for Earth Engine access",
                    "Earth Engine API not enabled in Google Cloud Console",
                    "Permissions still propagating (can take up to 24 hours)"
                ],
                "next_steps": [
                    "1. Go to Google Cloud Console > IAM & Admin > IAM",
                    "2. Find your service account and add 'Earth Engine Resource Viewer' role",
                    "3. Enable Earth Engine API in APIs & Services",
                    "4. Register project at https://earthengine.google.com/",
                    "5. Wait for permissions to propagate"
                ]
            },
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Google Earth Engine debug failed: {str(e)}"
        )


@router.get("/health/debug-gee-detailed")
async def debug_google_earth_engine_detailed():
    """Debug Google Earth Engine with comprehensive logging and raw API responses"""

    if not settings.debug:
        raise HTTPException(
            status_code=404,
            detail="Debug endpoints are only available when DEBUG=true"
        )

    try:
        from src.utils.gee_auth import validate_service_account_setup, test_earth_engine_connection
        import logging
        import io

        # Capture all log output for this request
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)

        # Add handler to all relevant loggers
        loggers = [
            logging.getLogger("src.utils.gee_auth"),
            logging.getLogger("urllib3.connectionpool"),
            logging.getLogger("google.auth.transport.requests"),
            logging.getLogger("google.auth._default"),
        ]

        for logger in loggers:
            logger.addHandler(handler)

        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "service_account_validation": None,
            "connection_test": None,
            "error": None,
            "detailed_logs": None,
            "troubleshooting": {
                "common_issues": [
                    "Missing roles/serviceusage.serviceUsageConsumer role",
                    "Service account lacks Earth Engine Resource Viewer role",
                    "Earth Engine API not enabled in Google Cloud Console",
                    "Project not registered for Earth Engine access",
                    "Invalid OAuth scopes or malformed credentials"
                ],
                "required_roles": [
                    "roles/earthengine.viewer",
                    "roles/serviceusage.serviceUsageConsumer"
                ],
                "setup_steps": [
                    "1. Enable Earth Engine API in Google Cloud Console",
                    "2. Add required roles to service account",
                    "3. Register project at https://earthengine.google.com/",
                    "4. Wait up to 24 hours for permissions to propagate"
                ]
            }
        }

        try:
            # Run validation and connection test
            debug_info["service_account_validation"] = validate_service_account_setup()
            debug_info["connection_test"] = test_earth_engine_connection()

        except Exception as e:
            debug_info["error"] = {
                "message": str(e),
                "type": type(e).__name__,
                "details": str(e)
            }

        finally:
            # Capture all logs
            debug_info["detailed_logs"] = log_capture.getvalue()

            # Remove handlers
            for logger in loggers:
                logger.removeHandler(handler)

        return debug_info

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detailed Google Earth Engine debug failed: {str(e)}"
        )


@router.get("/health/debug-gee-raw")
async def debug_google_earth_engine_raw():
    """Capture raw HTTP responses from Google APIs for debugging"""

    if not settings.debug:
        raise HTTPException(
            status_code=404,
            detail="Debug endpoints are only available when DEBUG=true"
        )

    try:
        import logging
        import io
        import urllib3
        from src.utils.gee_auth import initialize_earth_engine

        # Enable maximum verbosity for HTTP logging
        urllib3.disable_warnings()

        # Capture all HTTP traffic
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)

        # Enable debug logging for all HTTP-related loggers
        http_loggers = [
            "urllib3.connectionpool",
            "urllib3.util.retry",
            "urllib3.poolmanager",
            "requests.packages.urllib3.connectionpool",
            "google.auth.transport.requests",
            "google.auth.transport.urllib3",
            "google.auth._default",
            "google.oauth2.service_account",
            "src.utils.gee_auth"
        ]

        original_levels = {}
        for logger_name in http_loggers:
            logger = logging.getLogger(logger_name)
            original_levels[logger_name] = logger.level
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)

        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "initialization_result": None,
            "raw_http_logs": None,
            "error": None,
            "instructions": {
                "purpose": "This endpoint captures raw HTTP requests/responses from Google APIs",
                "what_to_look_for": [
                    "HTTP status codes (200, 400, 403, etc.)",
                    "OAuth error responses from Google",
                    "Specific error messages in response bodies",
                    "Request headers and authentication details"
                ],
                "common_patterns": {
                    "403_forbidden": "Usually indicates missing permissions or roles",
                    "400_bad_request": "Often OAuth scope or credential format issues",
                    "invalid_scope": "OAuth scope not allowed for this service account"
                }
            }
        }

        try:
            # Attempt to initialize Earth Engine (this will generate HTTP requests)
            debug_info["initialization_result"] = initialize_earth_engine()

        except Exception as e:
            debug_info["error"] = {
                "message": str(e),
                "type": type(e).__name__
            }

        finally:
            # Capture all HTTP logs
            debug_info["raw_http_logs"] = log_capture.getvalue()

            # Restore original logging levels and remove handlers
            for logger_name in http_loggers:
                logger = logging.getLogger(logger_name)
                logger.setLevel(original_levels[logger_name])
                logger.removeHandler(handler)

        return debug_info

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Raw HTTP debug failed: {str(e)}"
        )