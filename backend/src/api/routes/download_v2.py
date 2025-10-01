"""
Improved download endpoints with proper stateless design
"""

import asyncio
import time
from typing import Optional, List
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import Response

from src.api.schemas_v2 import ExportFormat, DataSourceType, InlineExportRequest, RawDataResponse, ProcessingStatus
from src.core.interfaces import IJobStorage, IExportService
from src.core.storage.job_storage import InMemoryJobStorage
from src.core.services.export_service import RawDataExportService
from src.utils.exceptions import ExportError
from src.core.config import get_settings
from src.utils.logging_config import log_request_separator

router = APIRouter()
_JOB_STORAGE = InMemoryJobStorage()  # Shared singleton for this process
logger = logging.getLogger(__name__)


# Dependency injection setup
def get_job_storage() -> IJobStorage:
    """Get job storage instance (shared singleton)."""
    # In production, this would return RedisJobStorage
    return _JOB_STORAGE


def get_export_service() -> IExportService:
    """Get export service instance"""
    return RawDataExportService()


@router.post("/download-inline/{format}")
async def download_inline(
    format: ExportFormat,
    request: InlineExportRequest,
    http_request: Request,
    export_service: IExportService = Depends(get_export_service)
):
    """
    Stateless export: client sends the results payload; server returns export bytes.
    Avoids dependency on server-side job storage.
    """
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        # Reconstruct a minimal RawDataResponse for the exporter
        rd = RawDataResponse(
            job_id=UUID(int=0),
            status=ProcessingStatus.COMPLETED,
            processing_time=request.processing_time or 0.0,
            results=request.results,
            total_features=sum(v.stats.count for v in request.results.values()),
            successful_sources=sum(1 for v in request.results.values() if v.status == ProcessingStatus.COMPLETED)
        )
        export_data = await export_service.export_data(rd, format.value)
        content_type, filename = _get_content_type_and_filename(format, rd.job_id)
        return Response(
            content=export_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Atlas-Export-Format": format.value
            }
        )
    except Exception as e:
        logger.exception("Inline download failed")
        raise HTTPException(status_code=500, detail="Inline download failed")


@router.get("/download/{job_id}/{format}")
async def download_data(
    job_id: UUID,
    format: ExportFormat,
    http_request: Request,
    job_storage: IJobStorage = Depends(get_job_storage),
    export_service: IExportService = Depends(get_export_service),
    sources: Optional[List[DataSourceType]] = Query(None, description="Specific sources to include")
):
    """
    Download processed data in the specified format.
    
    **Improved V2 Endpoint Features:**
    - Proper stateless design with job storage
    - Clean dependency injection
    - Raw data export without processing
    - Better error handling and recovery
    
    **Supported Formats:**
    - **geojson**: Raw GeoJSON with source attribution
    - **kml**: KML with folder organization by source
    - **kmz**: Compressed KML for Google Earth
    - **csv**: Tabular data with WKT geometry
    """
    
    start_time = time.time()
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        logger.info(f"Download request: job={job_id}, format={format.value}")
        
        # Retrieve job result from storage
        job_result = await job_storage.get_job_result(job_id)
        if not job_result:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found or has expired"
            )
        
        # Validate format support
        if format.value not in export_service.get_supported_formats():
            supported = export_service.get_supported_formats()
            raise HTTPException(
                status_code=400,
                detail=f"Format '{format.value}' not supported. Available: {supported}"
            )
        
        # Validate requested sources
        if sources:
            available_sources = list(job_result.results.keys())
            invalid_sources = [s for s in sources if s not in available_sources]
            if invalid_sources:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid sources: {[s.value for s in invalid_sources]}. Available: {[s.value for s in available_sources]}"
                )
        
        # Export data
        export_data = await export_service.export_data(
            result=job_result,
            format=format.value,
            sources=sources
        )
        
        # Determine content type and filename
        content_type, filename = _get_content_type_and_filename(format, job_id)
        
        processing_time = time.time() - start_time
        logger.info(f"Download completed in {processing_time:.2f}s: {len(export_data)} bytes")
        
        # Return data as response
        return Response(
            content=export_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Atlas-Job-ID": str(job_id),
                "X-Atlas-Export-Format": format.value,
                "X-Atlas-Processing-Time": f"{processing_time:.2f}s",
                "X-Atlas-Features": str(job_result.total_features)
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except ExportError as e:
        logger.error(f"Export error for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")
    
    except Exception as e:
        processing_time = time.time() - start_time
        logger.exception(f"Download failed for job {job_id} after {processing_time:.2f}s")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during download"
        )


@router.get("/job/{job_id}/status")
async def get_job_status(
    job_id: UUID,
    http_request: Request,
    job_storage: IJobStorage = Depends(get_job_storage),
    include_results: bool = Query(False, description="Include full job results in response")
):
    """
    Get job status and basic information.
    
    **Clean Status Endpoint:**
    - Simple job existence check
    - Basic metadata without heavy processing
    - Stateless design with proper storage
    """
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        # Check if job exists
        job_result = await job_storage.get_job_result(job_id)
        if not job_result:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found or has expired"
            )
        
        # Build response
        response_data = {
            "job_id": str(job_id),
            "status": job_result.status.value,
            "processing_time": job_result.processing_time,
            "total_features": job_result.total_features,
            "successful_sources": job_result.successful_sources,
            "available_sources": [source.value for source in job_result.results.keys()],
            "download_urls": {
                "geojson": f"/api/v2/download/{job_id}/geojson",
                "kml": f"/api/v2/download/{job_id}/kml",
                "kmz": f"/api/v2/download/{job_id}/kmz",
                "csv": f"/api/v2/download/{job_id}/csv"
            }
        }
        
        # Include full results if requested
        if include_results:
            response_data["results"] = job_result.dict()
        
        return response_data
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.exception(f"Error retrieving job status for {job_id}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve job status"
        )


@router.delete("/job/{job_id}")
async def cleanup_job(
    job_id: UUID,
    http_request: Request,
    job_storage: IJobStorage = Depends(get_job_storage)
):
    """
    Clean up job data.
    
    **Proper Cleanup:**
    - Remove from job storage
    - Clean temporary files
    - Stateless operation
    """
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        # Delete from storage
        success = await job_storage.delete_job_result(job_id)
        
        # Note: In a full implementation, you would also clean up temporary export files
        # from the file system here
        
        return {
            "job_id": str(job_id),
            "status": "cleaned" if success else "not_found",
            "message": "Job data cleaned up successfully" if success else "Job not found"
        }
        
    except Exception as e:
        logger.exception(f"Error cleaning up job {job_id}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cleanup job data"
        )


def _get_content_type_and_filename(format: ExportFormat, job_id: UUID) -> tuple:
    """Get appropriate content type and filename for download"""
    
    content_types = {
        ExportFormat.GEOJSON: ("application/geo+json", f"atlas_export_{job_id}.geojson"),
        ExportFormat.KML: ("application/vnd.google-earth.kml+xml", f"atlas_export_{job_id}.kml"),
        ExportFormat.KMZ: ("application/vnd.google-earth.kmz", f"atlas_export_{job_id}.kmz"),
        ExportFormat.CSV: ("text/csv", f"atlas_export_{job_id}.csv"),
    }
    
    return content_types.get(format, ("application/octet-stream", f"atlas_export_{job_id}.bin"))