"""
Improved extraction endpoints with clean architecture
"""

import asyncio
import time
from typing import Optional
import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from src.api.schemas_v2 import (
    RawDataRequest, RawDataResponse, ValidationRequest, ValidationResponse,
    DataSourcesResponse, DataSourceInfo, ProcessingStatus, ExportFormat
)
from src.core.interfaces import IDataSourceFactory, IProcessingService, IJobStorage
from src.core.data_sources.factory import DataSourceFactory
from src.core.services.processing_service import RawDataProcessingService
from src.core.storage.job_storage import InMemoryJobStorage
from src.utils.exceptions import AtlasException, ValidationError, ProcessingError
from src.utils.geometry import geojson_to_shapely_polygon
from src.core.config import get_settings
from src.utils.logging_config import log_request_separator
from src.core.processors.buildings_cleaner import (
    BuildingsCleaner,
    BuildingsCleanerConfig,
)
from src.core.processors.roads_cleaner import (
    RoadsCleaner,
    RoadsCleanerConfig,
)

router = APIRouter()
_JOB_STORAGE = InMemoryJobStorage()  # Shared singleton for this process
logger = logging.getLogger(__name__)


# Dependency injection setup
def get_data_source_factory() -> IDataSourceFactory:
    """Get data source factory instance"""
    return DataSourceFactory()


def get_job_storage() -> IJobStorage:
    """Get job storage instance (shared singleton)."""
    # In production, this could return RedisJobStorage
    return _JOB_STORAGE


def get_processing_service(
    factory: IDataSourceFactory = Depends(get_data_source_factory)
) -> IProcessingService:
    """Get processing service instance"""
    return RawDataProcessingService(factory)


@router.post("/extract", response_model=RawDataResponse)
async def extract_raw_data(
    request: RawDataRequest,
    http_request: Request,
    processing_service: IProcessingService = Depends(get_processing_service),
    job_storage: IJobStorage = Depends(get_job_storage)
):
    """
    Extract raw geospatial data from multiple sources.
    
    **Simplified API focused on essential parameters:**
    - `aoi_boundary`: Area of interest polygon (required)
    - `sources`: Simple enable/disable for each data source
    - `export_format`: Optional immediate export format
    
    **Raw Data Promise:**
    - No sampling, filtering, or coordinate modification
    - Data delivered exactly as received from sources
    - Each source maintains complete independence
    
    **Stateless Design:**
    - Jobs stored with TTL for download access
    - No server-side state dependencies
    - Horizontally scalable architecture
    """
    
    job_id = uuid4()
    start_time = time.time()
    
    try:
        # Log request
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        logger.info(f"Starting raw data extraction job {job_id}")
        
        # Convert AOI to Shapely polygon
        aoi_polygon = geojson_to_shapely_polygon(request.aoi_boundary)
        
        # Prepare source configurations
        source_configs = {}
        for source_type, selection in request.sources.items():
            if selection.enabled:
                source_configs[source_type] = {
                    'enabled': True,
                    'timeout': selection.timeout or 30
                }
        
        # Process extraction request
        results = await processing_service.process_extraction_request(aoi_polygon, source_configs)

        # Optional per-source cleaning for building datasets
        if request.clean:
            logger.info(f"Geometry cleaning enabled with config: {request.cleaning_config}")

            # Determine which cleaner to use based on configuration
            cleaning_config = request.cleaning_config or {}

            # Use unified BuildingsCleaner exclusively
            try:
                logger.info("Using unified BuildingsCleaner (source-specific)")
                b_cleaner = BuildingsCleaner()
                b_cfg = BuildingsCleanerConfig(
                    min_area_m2=cleaning_config.get('min_area_m2', 8.0),
                    overlap_threshold=cleaning_config.get('overlap_threshold', 0.30),
                    edge_buffer_m=cleaning_config.get('edge_buffer_m', 0.5),
                    strategy=cleaning_config.get('strategy', 'highest_confidence'),
                    simplify_tolerance_m=cleaning_config.get('simplify_tolerance_m'),
                    make_valid=cleaning_config.get('make_valid', True),
                    google_min_confidence=cleaning_config.get('google_min_confidence', 0.65),
                    min_width_m=cleaning_config.get('min_width_m', 2.0),
                    min_compactness=cleaning_config.get('min_compactness', 0.08),
                    max_elongation=cleaning_config.get('max_elongation', 8.0),
                )

                from src.api.schemas_v2 import DataSourceType
                for source_type, result in list(results.items()):
                    if result.data and source_type in {DataSourceType.GOOGLE_BUILDINGS, DataSourceType.MICROSOFT_BUILDINGS, DataSourceType.OSM_BUILDINGS}:
                        original_count = len(result.data.features or [])
                        cleaned_fc = b_cleaner.clean(source_type, result.data, aoi_polygon, b_cfg)
                        result.data = cleaned_fc
                        try:
                            new_count = len(cleaned_fc.features or [])
                            result.stats.count = new_count
                            logger.info(f"Unified cleaning for {source_type.value}: {original_count} → {new_count}")
                        except Exception:
                            pass
            except Exception:
                logger.exception("Unified BuildingsCleaner failed; returning raw results for cleaning step")
        else:
            logger.info("Geometry cleaning disabled (clean=False)")

        # Optional roads clipping
        if getattr(request, 'clean_roads', False):
            try:
                logger.info("Roads clipping enabled (clean_roads=True)")
                r_cleaner = RoadsCleaner()
                r_cfg = RoadsCleanerConfig()
                from src.api.schemas_v2 import DataSourceType
                for source_type, result in list(results.items()):
                    if source_type == DataSourceType.OSM_ROADS and result.data:
                        original_count = len(result.data.features or [])
                        cleaned_fc = r_cleaner.clean_osm_roads(result.data, aoi_polygon, r_cfg)
                        result.data = cleaned_fc
                        try:
                            new_count = len(cleaned_fc.features or [])
                            result.stats.count = new_count
                            logger.info(f"Roads clipped for {source_type.value}: {original_count} → {new_count}")
                        except Exception:
                            pass
            except Exception:
                logger.exception("Roads clipping step failed; continuing with original roads data")
        
        # Calculate overall statistics
        processing_time = time.time() - start_time
        total_features = sum(result.stats.count for result in results.values())
        successful_sources = sum(1 for result in results.values() if result.status == ProcessingStatus.COMPLETED)
        
        # Determine overall status
        if successful_sources == 0:
            status = ProcessingStatus.FAILED
        elif successful_sources == len(results):
            status = ProcessingStatus.COMPLETED
        else:
            status = ProcessingStatus.PARTIAL
        
        # Create response
        response = RawDataResponse(
            job_id=job_id,
            status=status,
            processing_time=processing_time,
            results=results,
            total_features=total_features,
            successful_sources=successful_sources
        )
        
        # Handle immediate export if requested
        if request.export_format:
            export_data = await _export_data_immediately(response, request.export_format)
            response.export_data = export_data
        else:
            # Generate download URLs
            response.download_urls = {
                ExportFormat.GEOJSON: f"/api/v2/download/{job_id}/geojson",
                ExportFormat.KML: f"/api/v2/download/{job_id}/kml",
                ExportFormat.KMZ: f"/api/v2/download/{job_id}/kmz",
                ExportFormat.CSV: f"/api/v2/download/{job_id}/csv"
            }
        
        # Store job result for later access
        await job_storage.store_job_result(job_id, response, ttl_seconds=3600)
        
        logger.info(
            f"Job {job_id} completed in {processing_time:.2f}s: "
            f"{total_features} features from {successful_sources}/{len(results)} sources"
        )
        
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error for job {job_id}: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    
    except ProcessingError as e:
        logger.error(f"Processing error for job {job_id}: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
    
    except Exception as e:
        processing_time = time.time() - start_time
        logger.exception(f"Job {job_id} failed after {processing_time:.2f}s")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during data extraction"
        )


@router.post("/validate", response_model=ValidationResponse)
async def validate_aoi(request: ValidationRequest, http_request: Request):
    """
    Validate Area of Interest and provide processing estimates.
    
    **Fast validation without heavy processing:**
    - Geometry validation
    - Area calculations
    - Basic feasibility checks
    """
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        logger.info("Validating AOI geometry")
        
        # Convert to Shapely for validation
        aoi_polygon = geojson_to_shapely_polygon(request.aoi_boundary)
        
        # Import validation function
        from src.utils.geometry import validate_aoi_polygon
        settings = get_settings()
        
        is_valid, area_km2, errors = validate_aoi_polygon(
            request.aoi_boundary,
            settings.max_aoi_area_km2
        )
        
        # Create basic response
        response = ValidationResponse(
            valid=is_valid,
            area_km2=area_km2,
            errors=errors if not is_valid else [],
            warnings=[]
        )
        
        # Add performance warnings
        if area_km2 > 50:
            response.warnings.append(f"Large AOI ({area_km2:.1f} km²) may take longer to process")
        
        if area_km2 > 10:
            response.estimated_processing_time = min(area_km2 * 2, 300)  # Rough estimate
        else:
            response.estimated_processing_time = 30
        
        logger.info(f"AOI validation completed: valid={is_valid}, area={area_km2:.2f} km²")
        return response
        
    except Exception as e:
        logger.exception("Error during AOI validation")
        raise HTTPException(
            status_code=500,
            detail=f"AOI validation failed: {str(e)}"
        )


@router.get("/sources", response_model=DataSourcesResponse)
async def list_data_sources(
    http_request: Request,
    factory: IDataSourceFactory = Depends(get_data_source_factory)
):
    """
    List available data sources with essential information.
    
    **Focused information:**
    - What data sources are available
    - Basic coverage and feature type info
    - No complex configuration options
    """
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        # Get supported sources
        supported_sources = factory.get_supported_sources()
        
        # Define source information
        source_details = {
            "microsoft_buildings": DataSourceInfo(
                name="Microsoft Building Footprints",
                description="Global building footprints dataset with 1.4B+ buildings",
                provider="Microsoft",
                coverage="Global (varies by country)",
                feature_types=["buildings"],
                update_frequency="Monthly",
                license="Open Data Commons Open Database License (ODbL)"
            ),
            "google_buildings": DataSourceInfo(
                name="Google Open Buildings",
                description="Building detections dataset with 1.8B+ buildings",
                provider="Google Research",
                coverage="Global South regions (Africa, Latin America, South-East Asia)",
                feature_types=["buildings"],
                update_frequency="Periodic",
                license="Creative Commons Attribution 4.0 License"
            ),
            "osm_buildings": DataSourceInfo(
                name="OpenStreetMap Buildings",
                description="Crowdsourced building data with real-time updates",
                provider="OpenStreetMap Community",
                coverage="Global (quality varies by region)",
                feature_types=["buildings"],
                update_frequency="Real-time",
                license="Open Database License (ODbL)"
            ),
            "osm_roads": DataSourceInfo(
                name="OpenStreetMap Roads",
                description="Comprehensive road network data",
                provider="OpenStreetMap Community",
                coverage="Global (quality varies by region)",
                feature_types=["roads", "highways"],
                update_frequency="Real-time",
                license="Open Database License (ODbL)"
            ),
            "osm_railways": DataSourceInfo(
                name="OpenStreetMap Railways",
                description="Railway and transit infrastructure data",
                provider="OpenStreetMap Community",
                coverage="Global (quality varies by region)",
                feature_types=["railways", "rail_stations"],
                update_frequency="Real-time",
                license="Open Database License (ODbL)"
            ),
            "osm_landmarks": DataSourceInfo(
                name="OpenStreetMap Landmarks",
                description="Points of interest and landmark data",
                provider="OpenStreetMap Community",
                coverage="Global (quality varies by region)",
                feature_types=["amenities", "tourism", "shops"],
                update_frequency="Real-time",
                license="Open Database License (ODbL)"
            ),
            "osm_natural": DataSourceInfo(
                name="OpenStreetMap Natural Features",
                description="Natural and land use features",
                provider="OpenStreetMap Community", 
                coverage="Global (quality varies by region)",
                feature_types=["natural", "landuse"],
                update_frequency="Real-time",
                license="Open Database License (ODbL)"
            )
        }
        
        # Filter to only supported sources
        filtered_details = {
            source_type: source_details[source_type.value]
            for source_type in supported_sources
            if source_type.value in source_details
        }
        
        return DataSourcesResponse(
            available_sources=supported_sources,
            source_details=filtered_details,
            processing_info={
                "raw_data_extraction": "All data delivered without processing or filtering",
                "coordinate_preservation": "Full precision maintained from original sources",
                "concurrent_processing": "All sources processed simultaneously for speed"
            }
        )
        
    except Exception as e:
        logger.exception("Error listing data sources")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve data source information"
        )


async def _export_data_immediately(response: RawDataResponse, format: str) -> bytes:
    """Export data immediately in requested format"""
    from src.core.services.export_service import RawDataExportService
    
    export_service = RawDataExportService()
    return await export_service.export_data(response, format)

