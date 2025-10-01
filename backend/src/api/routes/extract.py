"""
Feature extraction endpoints
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from src.api.api_schemas import (
    ExtractFeaturesRequest, ExtractFeaturesResponse,
    ValidationRequest, ValidationResponse, DataSourceType
)
from src.core.processors.feature_aggregator import FeatureAggregator
from src.core.processors.aoi_processor import AOIProcessor
from src.utils.exceptions import AtlasException, ValidationError, ProcessingError
from src.core.config import get_settings
from src.utils.logging_config import log_request_separator
from src.core.processors.buildings_cleaner import BuildingsCleaner, BuildingsCleanerConfig
from src.utils.geometry import geojson_to_shapely_polygon

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize processors
feature_aggregator = FeatureAggregator()
aoi_processor = AOIProcessor()


@router.post("/extract-features", response_model=ExtractFeaturesResponse)
async def extract_features(
    request: ExtractFeaturesRequest,
    background_tasks: BackgroundTasks,
    http_request: Request
):
    """
    Extract geospatial features from multiple data sources for a given AOI.
    
    This endpoint processes the Area of Interest (AOI) across all enabled data sources
    and returns features organized by source type. Each data source maintains independence
    allowing users to toggle layers on/off in their applications.
    
    **New Single-Request Export:**
    - Use `output_format` parameter to specify desired format: `geojson`, `kml`, or `kmz`
    - Use `raw=true` to get formatted data directly in response `data` field
    - When both parameters are provided, no separate download request is needed
    
    **Processing Flow:**
    1. Validate AOI geometry and size constraints
    2. Query enabled data sources concurrently
    3. Process and filter features
    4. Apply format conversion if requested (output_format + raw=true)
    5. Generate export URLs for alternative formats
    
    **Data Sources:**
    - Microsoft Building Footprints: Global building dataset via Google Earth Engine
    - Google Open Buildings: Building detections via Google Earth Engine  
    - OpenStreetMap: Buildings, roads, railways, landmarks, and natural features
    
    **Response Organization:**
    Features are returned with source independence maintained, allowing frontend
    applications to create toggleable layers for each data source.
    
    **Usage Examples:**
    ```python
    # Traditional workflow (backward compatible)
    response = api.extract_features({"aoi_boundary": polygon, "data_sources": {...}})
    # Then: download via response.export_urls["geojson"]
    
    # New single-request workflow  
    response = api.extract_features({
        "aoi_boundary": polygon,
        "data_sources": {...},
        "output_format": "kmz",
        "raw": true
    })
    # Data available immediately in response.data (base64 for KMZ)
    ```
    """
    
    try:
        # Log request separator for debugging
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        logger.info(f"Starting feature extraction request")
        
        # Process the request
        response = await feature_aggregator.process_request(request)

        # Optional per-source cleaning for building datasets
        if getattr(request, 'clean', False):
            try:
                cleaner = BuildingsCleaner()
                cfg = BuildingsCleanerConfig(**(getattr(request, 'cleaning_config', None) or {}))
                aoi_polygon = geojson_to_shapely_polygon(request.aoi_boundary)
                from src.api.api_schemas import DataSourceType
                # results is Dict[DataSourceType, DataSourceResult]
                for source_type, result in list(response.results.items()):
                    if result.geojson and source_type in {DataSourceType.GOOGLE_BUILDINGS, DataSourceType.MICROSOFT_BUILDINGS, DataSourceType.OSM_BUILDINGS}:
                        cleaned_fc = cleaner.clean(source_type, result.geojson, aoi_polygon, cfg)
                        result.geojson = cleaned_fc
                        try:
                            result.stats.count = len(cleaned_fc.features or [])
                        except Exception:
                            pass
                # Recompute totals after cleaning
                response.total_features = sum(r.stats.count for r in response.results.values())
            except Exception:
                logger.exception("Geometry cleaning step failed; returning raw results")
        
        # Store job result for export access
        from src.api.routes.export import store_job_result
        store_job_result(response.job_id, response)
        
        # Schedule cleanup of temporary files (if any)
        background_tasks.add_task(_cleanup_temp_files, response.job_id)
        
        logger.info(f"Feature extraction completed: job_id={response.job_id}")
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    
    except ProcessingError as e:
        logger.error(f"Processing error: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
    
    except AtlasException as e:
        logger.error(f"Atlas error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    except Exception as e:
        logger.exception("Unexpected error during feature extraction")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during feature extraction"
        )


@router.post("/validate-aoi", response_model=ValidationResponse)
async def validate_aoi(request: ValidationRequest, http_request: Request):
    """
    Validate Area of Interest (AOI) geometry and provide processing estimates.
    
    This endpoint validates the provided AOI polygon and returns:
    - Geometry validation results
    - Area calculations
    - Estimated feature counts per data source
    - Estimated processing time
    - Optimization suggestions
    
    Use this endpoint before submitting extraction requests to ensure
    optimal performance and avoid errors.
    """
    
    try:
        # Log request separator for debugging
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        logger.info("Starting AOI validation")
        
        # Validate the AOI
        validation_result = aoi_processor.validate_aoi(request.aoi_boundary)
        
        logger.info(f"AOI validation completed: valid={validation_result.valid}, area={validation_result.area_km2:.2f} km²")
        return validation_result
        
    except Exception as e:
        logger.exception("Error during AOI validation")
        raise HTTPException(
            status_code=500,
            detail=f"AOI validation failed: {str(e)}"
        )


@router.get("/data-sources")
async def list_data_sources(http_request: Request):
    """
    List available data sources and their capabilities.
    
    Returns information about all supported data sources including:
    - Source identification and description
    - Available feature types
    - Coverage information
    - Usage guidelines
    """
    
    # Log request separator for debugging
    log_request_separator(logger, http_request.method, str(http_request.url.path))
    
    data_sources = {
        "microsoft_buildings": {
            "name": "Microsoft Building Footprints",
            "description": "Global building footprints dataset with 1.4B+ buildings",
            "provider": "Microsoft",
            "access_method": "Google Earth Engine",
            "coverage": "Global (varies by country)",
            "feature_types": ["buildings"],
            "attributes": ["confidence", "height_estimate"],
            "update_frequency": "Periodic",
            "documentation": "https://github.com/microsoft/GlobalMLBuildingFootprints",
            "license": "Open Data Commons Open Database License (ODbL)"
        },
        "google_buildings": {
            "name": "Google Open Buildings",
            "description": "Building detections dataset with 1.8B+ buildings",
            "provider": "Google Research",
            "access_method": "Google Earth Engine",
            "coverage": "Global South regions (Africa, Latin America, South-East Asia)",
            "feature_types": ["buildings"],
            "attributes": ["confidence"],
            "update_frequency": "Periodic",
            "documentation": "https://sites.research.google/open-buildings/",
            "license": "Creative Commons Attribution 4.0 License"
        },
        "openstreetmap": {
            "name": "OpenStreetMap",
            "description": "Crowdsourced geographic data with real-time updates",
            "provider": "OpenStreetMap Community",
            "access_method": "Overpass API",
            "coverage": "Global (quality varies by region)",
            "feature_types": [
                "buildings", "roads", "railways", "landmarks", "natural_features"
            ],
            "attributes": ["varies by feature type"],
            "update_frequency": "Real-time",
            "documentation": "https://wiki.openstreetmap.org/",
            "license": "Open Database License (ODbL)"
        }
    }
    
    return {
        "available_sources": list(DataSourceType),
        "source_details": data_sources,
        "usage_guidelines": {
            "max_aoi_area_km2": settings.max_aoi_area_km2,
            "request_timeout_seconds": settings.request_timeout,
            "rate_limits": {
                "google_earth_engine": "Managed by service account quotas",
                "overpass_api": f"{settings.overpass_rate_limit} requests/second"
            }
        },
        "recommendations": [
            "Start with smaller AOIs (< 10 km²) for testing",
            "Use validation endpoint before extraction",
            "Consider data source combinations based on your use case",
            "Microsoft Buildings: Best for building footprints in developed countries",
            "Google Buildings: Best for building detections in Global South",
            "OpenStreetMap: Best for roads, infrastructure, and local features"
        ]
    }


@router.get("/processing-limits")
async def get_processing_limits(http_request: Request):
    """
    Get current processing limits and constraints.
    
    Returns information about service limits to help users
    optimize their requests and understand constraints.
    """
    
    # Log request separator for debugging
    log_request_separator(logger, http_request.method, str(http_request.url.path))
    
    return {
        "aoi_constraints": {
            "max_area_km2": settings.max_aoi_area_km2,
            "recommended_max_km2": 25.0,
            "min_area_km2": 0.001,
            "max_coordinates": 1000
        },
        "performance_targets": {
            "small_aoi_seconds": 30,  # < 1 km²
            "medium_aoi_seconds": 120,  # 1-10 km²
            "large_aoi_seconds": 300,  # 10-100 km²
        },
        "timeout_settings": {
            "request_timeout_seconds": settings.request_timeout,
            "data_source_timeout_seconds": 30
        },
        "optimization_tips": [
            "Use rectangular AOIs when possible",
            "Avoid very elongated or complex polygons",
            "Enable only needed data sources",
            "Use appropriate filtering to reduce feature counts",
            "Consider breaking large areas into smaller chunks"
        ],
        "extraction_settings": {
            "max_features_per_source": settings.gee_max_features,
            "simplification_threshold": settings.gee_simplification_threshold,
            "sampling_threshold": settings.gee_sampling_threshold
        },
        "accuracy_notes": {
            "google_earth_engine": "Uses identical datasets and methods as manual Earth Engine queries",
            "data_versions": {
                "google_buildings": "v3/polygons (May 2023) - Latest available version",
                "microsoft_buildings": "Monthly updates - Most recent data available"
            },
            "processing_optimizations": [
                f"Features < {settings.gee_simplification_threshold}: Full precision extraction (no limits)",
                f"Features {settings.gee_simplification_threshold}-{settings.gee_sampling_threshold}: Geometry simplification applied",
                f"Features > {settings.gee_sampling_threshold}: Systematic sampling to max {settings.gee_max_features} features"
            ],
            "vs_manual_earth_engine": {
                "data_source": "Identical - same Earth Engine collections and versions",
                "processing": "API uses intelligent sampling for large datasets to prevent timeouts",
                "accuracy": "High fidelity maintained - manual GEE would face same memory limits",
                "recommendation": f"For >50k features, consider smaller AOI or accept sampling to {settings.gee_max_features} features"
            }
        }
    }


async def _cleanup_temp_files(job_id):
    """Background task to cleanup temporary files"""
    try:
        # Import here to avoid circular imports
        from src.exporters.manager import ExportManager
        
        export_manager = ExportManager()
        
        # Schedule cleanup after delay (give time for downloads)
        import asyncio
        await asyncio.sleep(3600)  # Wait 1 hour before cleanup
        
        export_manager.cleanup_exports(job_id)
        logger.info(f"Cleaned up temporary files for job {job_id}")
        
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary files for job {job_id}: {str(e)}")