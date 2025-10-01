"""
Export endpoints for downloading processed data in multiple formats
"""

import os
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse

from src.api.api_schemas import ExportFormat, DataSourceType, ExportRequest
from src.exporters.manager import ExportManager
from src.utils.exceptions import ExportError
from src.core.config import get_settings
from src.utils.logging_config import log_request_separator

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize export manager
export_manager = ExportManager()

# DEPRECATED: Global cache removed for stateless design
# Job results now handled by proper IJobStorage implementations
# This maintains backward compatibility while encouraging migration to v2 API


@router.get("/export/{job_id}/{format}")
async def download_export(
    job_id: UUID,
    format: ExportFormat,
    http_request: Request,
    sources: Optional[List[DataSourceType]] = Query(None, description="Specific sources to include"),
    include_metadata: bool = Query(True, description="Include processing metadata")
):
    """
    Download processed data in the specified format.
    
    **Supported Formats:**
    - **geojson**: Standard GeoJSON for web applications and JavaScript mapping libraries
    - **kml**: KML format for Google Earth Desktop with folder organization by source
    - **kmz**: Compressed KML format for Google Earth Desktop  
    - **csv**: Tabular data with WKT geometry for spreadsheet analysis
    - **shapefile**: ESRI Shapefile format for professional GIS applications (QGIS, ArcGIS)
    - **dwg**: AutoCAD DWG format for architectural and engineering applications
    
    **File Organization:**
    - All formats maintain source independence with clear attribution
    - KML/KMZ files include folder hierarchy by data source and feature type
    - CSV includes source columns for filtering and analysis
    - Shapefiles are provided as ZIP archives with all required components
    
    **Parameters:**
    - `sources`: Filter to specific data sources (optional)
    - `include_metadata`: Include processing metadata and job information
    """
    
    try:
        # Log request separator for debugging
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        # Check if format is supported
        if not export_manager.is_format_supported(format):
            available_formats = [f.value for f in export_manager.get_available_formats()]
            raise HTTPException(
                status_code=400,
                detail=f"Export format '{format.value}' not supported. Available formats: {available_formats}"
            )
        
        # DEPRECATED: This v1 endpoint has stateless design issues
        # Please migrate to v2 API: /api/v2/download/{job_id}/{format}
        
        # For backward compatibility, attempt to retrieve from job storage
        from src.core.storage.job_storage import InMemoryJobStorage
        job_storage = InMemoryJobStorage()
        
        response_data = await job_storage.get_job_result(job_id)
        if not response_data:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found or has expired. Consider using v2 API for better reliability."
            )
        
        # Validate requested sources
        if sources:
            available_sources = list(response_data.results.keys())
            invalid_sources = [s for s in sources if s not in available_sources]
            if invalid_sources:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid sources: {invalid_sources}. Available sources: {[s.value for s in available_sources]}"
                )
        
        # Generate export file
        logger.info(f"Generating {format.value} export for job {job_id}")
        
        export_path = await export_manager.export_single_format(
            job_id=job_id,
            export_format=format,
            response_data=response_data,
            sources=sources,
            include_metadata=include_metadata
        )
        
        # Determine content type and filename
        content_type, filename = _get_export_content_type(format, job_id)
        
        # Return file response
        return FileResponse(
            path=export_path,
            media_type=content_type,
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Atlas-Job-ID": str(job_id),
                "X-Atlas-Export-Format": format.value
            }
        )
        
    except ExportError as e:
        logger.error(f"Export error: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
    
    except Exception as e:
        logger.exception(f"Unexpected error during export")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during export"
        )


@router.get("/export/{job_id}/formats")
async def list_available_exports(job_id: UUID, http_request: Request):
    """
    List available export formats for a completed job.
    
    Returns information about supported export formats and their characteristics.
    """
    
    try:
        # Log request separator for debugging
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        # DEPRECATED: This v1 endpoint has stateless design issues
        # Please migrate to v2 API for better reliability
        
        # For backward compatibility, attempt to retrieve from job storage
        from src.core.storage.job_storage import InMemoryJobStorage
        job_storage = InMemoryJobStorage()
        
        response_data = await job_storage.get_job_result(job_id)
        if not response_data:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found or has expired. Consider using v2 API."
            )
        available_sources = list(response_data.results.keys())
        
        # Get available formats
        available_formats = export_manager.get_available_formats()
        
        format_info = {}
        for format in available_formats:
            format_info[format.value] = {
                "description": _get_format_description(format),
                "content_type": _get_export_content_type(format, job_id)[0],
                "file_extension": _get_format_extension(format),
                "use_cases": _get_format_use_cases(format),
                "download_url": f"/api/v1/export/{job_id}/{format.value}"
            }
        
        return {
            "job_id": str(job_id),
            "available_formats": format_info,
            "available_sources": [source.value for source in available_sources],
            "total_features": response_data.total_features,
            "processing_status": response_data.status.value,
            "export_options": {
                "filter_by_sources": "Add ?sources=source1,source2 to URL",
                "include_metadata": "Add ?include_metadata=false to exclude metadata",
                "example_url": f"/api/v1/export/{job_id}/geojson?sources=osm_buildings,osm_roads&include_metadata=true"
            }
        }
        
    except Exception as e:
        logger.exception("Error listing available exports")
        raise HTTPException(
            status_code=500,
            detail="Failed to list available export formats"
        )


@router.delete("/export/{job_id}")
async def cleanup_job_exports(job_id: UUID, http_request: Request):
    """
    Clean up export files and cached data for a job.
    
    This endpoint allows manual cleanup of job data and temporary files.
    Jobs are automatically cleaned up after the configured retention period.
    """
    
    try:
        # Log request separator for debugging
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        # DEPRECATED: v1 endpoint - migrate to v2 for better architecture
        # For backward compatibility, attempt to clean up from job storage
        from src.core.storage.job_storage import InMemoryJobStorage
        job_storage = InMemoryJobStorage()
        
        # Remove from job storage
        await job_storage.delete_job_result(job_id)
        
        # Clean up export files
        success = export_manager.cleanup_exports(job_id)
        
        if success:
            return {
                "job_id": str(job_id),
                "status": "cleaned",
                "message": "Job data and export files have been cleaned up"
            }
        else:
            return {
                "job_id": str(job_id),
                "status": "partial",
                "message": "Job removed from cache, but some files may remain"
            }
        
    except Exception as e:
        logger.exception(f"Error cleaning up job {job_id}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cleanup job data"
        )


@router.get("/export/formats")
async def list_export_formats():
    """
    List all supported export formats and their characteristics.
    
    Returns detailed information about each export format including
    use cases, software compatibility, and technical specifications.
    """
    
    available_formats = export_manager.get_available_formats()
    
    format_details = {}
    for format in available_formats:
        format_details[format.value] = {
            "name": format.value.upper(),
            "description": _get_format_description(format),
            "content_type": _get_export_content_type(format, UUID("00000000-0000-0000-0000-000000000000"))[0],
            "file_extension": _get_format_extension(format),
            "use_cases": _get_format_use_cases(format),
            "software_compatibility": _get_software_compatibility(format),
            "features": _get_format_features(format)
        }
    
    return {
        "supported_formats": format_details,
        "usage_notes": {
            "source_independence": "All formats maintain separation between data sources",
            "metadata_inclusion": "Processing metadata can be included or excluded",
            "source_filtering": "Exports can be filtered to specific data sources",
            "file_organization": "Large exports may be split into multiple files"
        },
        "recommendations": {
            "web_applications": ["geojson"],
            "desktop_gis": ["shapefile", "geojson"],
            "google_earth": ["kml", "kmz"],
            "autocad": ["dwg"],
            "analysis": ["csv", "geojson"],
            "sharing": ["kmz", "geojson"]
        }
    }


def _get_export_content_type(format: ExportFormat, job_id: UUID) -> tuple:
    """Get content type and filename for export format"""
    
    content_types = {
        ExportFormat.GEOJSON: ("application/geo+json", f"atlas_export_{job_id}.geojson"),
        ExportFormat.KML: ("application/vnd.google-earth.kml+xml", f"atlas_export_{job_id}.kml"),
        ExportFormat.KMZ: ("application/vnd.google-earth.kmz", f"atlas_export_{job_id}.kmz"),
        ExportFormat.CSV: ("text/csv", f"atlas_export_{job_id}.csv"),
        ExportFormat.SHAPEFILE: ("application/zip", f"atlas_export_{job_id}_shapefile.zip"),
        ExportFormat.DWG: ("application/acad", f"atlas_export_{job_id}.dwg"),
    }
    
    return content_types.get(format, ("application/octet-stream", f"atlas_export_{job_id}.bin"))


def _get_format_description(format: ExportFormat) -> str:
    """Get description for export format"""
    
    descriptions = {
        ExportFormat.GEOJSON: "Standard GeoJSON format for web applications and JavaScript mapping libraries",
        ExportFormat.KML: "KML format for Google Earth Desktop with organized folder structure",
        ExportFormat.KMZ: "Compressed KML format for Google Earth Desktop (smaller file size)",
        ExportFormat.CSV: "Tabular data with WKT geometry for spreadsheet analysis and reporting",
        ExportFormat.SHAPEFILE: "ESRI Shapefile format for professional GIS applications",
        ExportFormat.DWG: "AutoCAD DWG format for architectural and engineering applications",
    }
    
    return descriptions.get(format, "Unknown format")


def _get_format_extension(format: ExportFormat) -> str:
    """Get file extension for format"""
    
    extensions = {
        ExportFormat.GEOJSON: ".geojson",
        ExportFormat.KML: ".kml",
        ExportFormat.KMZ: ".kmz",
        ExportFormat.CSV: ".csv",
        ExportFormat.SHAPEFILE: ".zip",
        ExportFormat.DWG: ".dwg",
    }
    
    return extensions.get(format, ".bin")


def _get_format_use_cases(format: ExportFormat) -> List[str]:
    """Get use cases for format"""
    
    use_cases = {
        ExportFormat.GEOJSON: [
            "Web mapping applications",
            "JavaScript visualization libraries",
            "API data exchange",
            "Lightweight spatial analysis"
        ],
        ExportFormat.KML: [
            "Google Earth Desktop visualization",
            "GPS device import",
            "3D visualization",
            "Field data collection"
        ],
        ExportFormat.KMZ: [
            "Google Earth Desktop (compressed)",
            "Sharing via email or web",
            "Mobile GPS applications",
            "Reduced bandwidth scenarios"
        ],
        ExportFormat.CSV: [
            "Spreadsheet analysis",
            "Database import",
            "Statistical analysis",
            "Reporting and documentation"
        ],
        ExportFormat.SHAPEFILE: [
            "Professional GIS software",
            "Spatial analysis",
            "Cartographic production",
            "Data archival"
        ],
        ExportFormat.DWG: [
            "AutoCAD projects",
            "Engineering drawings",
            "Architectural designs",
            "Infrastructure planning"
        ],
    }
    
    return use_cases.get(format, [])


def _get_software_compatibility(format: ExportFormat) -> List[str]:
    """Get software compatibility for format"""
    
    compatibility = {
        ExportFormat.GEOJSON: ["QGIS", "ArcGIS", "Leaflet", "OpenLayers", "Mapbox GL JS", "Web browsers"],
        ExportFormat.KML: ["Google Earth Desktop", "Google Earth Pro", "ArcGIS", "QGIS", "GPS devices"],
        ExportFormat.KMZ: ["Google Earth Desktop", "Google Earth Pro", "Mobile apps", "GPS devices"],
        ExportFormat.CSV: ["Excel", "Google Sheets", "R", "Python", "Database systems", "Statistical software"],
        ExportFormat.SHAPEFILE: ["QGIS", "ArcGIS", "MapInfo", "FME", "PostGIS", "Most GIS software"],
        ExportFormat.DWG: ["AutoCAD", "BricsCAD", "DraftSight", "FreeCAD", "LibreCAD"],
    }
    
    return compatibility.get(format, [])


def _get_format_features(format: ExportFormat) -> List[str]:
    """Get format-specific features"""
    
    features = {
        ExportFormat.GEOJSON: [
            "Native coordinate reference system support",
            "Preserves all attributes",
            "Hierarchical source organization",
            "Metadata inclusion"
        ],
        ExportFormat.KML: [
            "Folder organization by source",
            "Custom styling per data source",
            "Rich feature descriptions",
            "3D coordinate support"
        ],
        ExportFormat.KMZ: [
            "Compressed file size",
            "Embedded resources",
            "Folder organization",
            "Custom styling"
        ],
        ExportFormat.CSV: [
            "WKT geometry representation",
            "All attribute preservation",
            "Source attribution columns",
            "Statistics and metadata"
        ],
        ExportFormat.SHAPEFILE: [
            "Multiple files per source",
            "Projection files included",
            "Attribute tables",
            "GIS-standard format"
        ],
        ExportFormat.DWG: [
            "Layer organization",
            "CAD-compatible geometry",
            "Architectural standards",
            "Engineering workflows"
        ],
    }
    
    return features.get(format, [])


# DEPRECATED: Helper function for v1 backward compatibility
# V2 API uses proper job storage interfaces
def store_job_result(job_id: UUID, response_data):
    """Store job result for export access - DEPRECATED, use IJobStorage"""
    # For backward compatibility, store in the new job storage system
    import asyncio
    from src.core.storage.job_storage import InMemoryJobStorage
    
    async def _store():
        job_storage = InMemoryJobStorage()
        # Convert to v2 format if needed
        if hasattr(response_data, 'dict'):
            # Assume it's already RawDataResponse format
            await job_storage.store_job_result(job_id, response_data)
        else:
            # Legacy format - would need conversion logic here
            pass
    
    # Run async store operation
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(_store())
    except RuntimeError:
        # No event loop running
        pass