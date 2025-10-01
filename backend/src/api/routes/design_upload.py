"""
Design upload and rendering API endpoints
"""

import asyncio
import time
import logging
from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from src.api.schemas.design_upload import (
    DesignUploadResponse, DesignRenderRequest, DesignRenderResponse,
    DesignFileFormat, DesignMetadata
)
from src.core.parsers.design_parser import DesignFileParser
from src.core.storage.design_storage import DesignStorage
from src.utils.logging_config import log_request_separator
from src.core.config import get_settings
from src.api.schemas_v2 import ExportFormat

router = APIRouter()
logger = logging.getLogger(__name__)


# Dependency injection
def get_design_parser() -> DesignFileParser:
    """Get design parser instance"""
    return DesignFileParser()


def get_design_storage() -> DesignStorage:
    """Get design storage instance"""
    return DesignStorage()


@router.post("/upload", response_model=DesignUploadResponse)
async def upload_design_file(
    file: UploadFile = File(..., description="Design file (GeoJSON, KML, or KMZ)"),
    http_request: Request = None,
    parser: DesignFileParser = Depends(get_design_parser),
    storage: DesignStorage = Depends(get_design_storage)
):
    """
    Upload and parse design file for map rendering and AOI tracing.
    
    **Supported Formats:**
    - **GeoJSON**: Standard GeoJSON files with features and properties
    - **KML**: Keyhole Markup Language files with folders and styling
    - **KMZ**: Compressed KML files (ZIP archives containing KML)
    
    **User Experience Benefits:**
    - Upload your existing design to guide AOI tracing
    - Automatic map navigation to your design area
    - Layer/folder structure preservation
    - Visual reference while drawing AOI
    
    **Processing Features:**
    - Robust parsing of complex file structures
    - Automatic coordinate system detection
    - Bounding box calculation for map navigation
    - Layer information extraction for UI display
    """
    
    start_time = time.time()
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        logger.info(f"Processing design upload: {file.filename} ({file.content_type})")
        
        # Validate file size
        settings = get_settings()
        if file.size and file.size > settings.max_export_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_export_size_mb}MB"
            )
        
        # Read file content
        content = await file.read()
        logger.info(f"Read {len(content)} bytes from {file.filename}")
        
        # Parse design file
        parsed_design = await parser.parse_design_file(content, file.filename)
        
        # Store design for future access
        await storage.store_design(parsed_design)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create user-friendly response
        response = DesignUploadResponse(
            design_id=parsed_design.design_id,
            status="processed",
            metadata=parsed_design.metadata,
            map_center=parsed_design.metadata.center,
            map_zoom=parsed_design.suggested_zoom,
            map_bounds=parsed_design.metadata.bbox,
            layer_summary=[
                {
                    "name": layer.name,
                    "feature_count": layer.feature_count,
                    "visible": layer.visible
                }
                for layer in parsed_design.layers
            ],
            message=f"Successfully processed {file.filename}. You can now trace your AOI on the map.",
            next_action="Navigate to the map view and draw your AOI"
        )
        
        logger.info(
            f"Design upload completed: {parsed_design.design_id} "
            f"in {processing_time:.2f}s, {parsed_design.metadata.total_features} features"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Design upload failed after {processing_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process design file: {str(e)}"
        )


@router.post("/render", response_model=DesignRenderResponse)
async def render_design_on_map(
    request: DesignRenderRequest,
    http_request: Request = None,
    storage: DesignStorage = Depends(get_design_storage)
):
    """
    Render uploaded design on map for AOI tracing.
    
    **Rendering Options:**
    - Select specific layers to display
    - Simplified geometries for better performance
    - Feature count limits for large designs
    
    **Response Structure:**
    - Layer-based organization for UI controls
    - Bounds information for map positioning
    - Performance indicators for user feedback
    """
    
    start_time = time.time()
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        logger.info(f"Rendering design {request.design_id}")
        
        # Retrieve design metadata
        metadata = await storage.get_design_metadata(request.design_id)
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Design {request.design_id} not found"
            )
        
        # Retrieve requested layers
        layer_data = await storage.get_design_layers(
            request.design_id, 
            request.layers
        )
        
        if not layer_data:
            raise HTTPException(
                status_code=404,
                detail=f"No layers found for design {request.design_id}"
            )
        
        # Convert to DesignLayer objects
        from src.api.schemas.design_upload import DesignLayer, FeatureCollection
        layers = []
        for layer_dict in layer_data:
            # Convert features to FeatureCollection
            features_data = layer_dict.get('features', {})
            features_collection = FeatureCollection(**features_data)
            
            layer = DesignLayer(
                name=layer_dict.get('name', 'Unknown'),
                description=layer_dict.get('description'),
                features=features_collection,
                style=layer_dict.get('style'),
                visible=layer_dict.get('visible', True),
                feature_count=layer_dict.get('feature_count', 0)
            )
            layers.append(layer)
        
        # Calculate total features
        total_features = sum(layer.feature_count for layer in layers)
        
        # Get bounds from metadata
        bounds = metadata.bbox
        
        # Create response
        response = DesignRenderResponse(
            design_id=request.design_id,
            layers=layers,
            total_features=total_features,
            bounds=bounds,
            simplified=request.simplified
        )
        
        processing_time = time.time() - start_time
        logger.info(
            f"Design rendering completed: {request.design_id} "
            f"in {processing_time:.2f}s, {total_features} features"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Design rendering failed after {processing_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render design: {str(e)}"
        )


@router.get("/metadata/{design_id}", response_model=DesignMetadata)
async def get_design_metadata(
    design_id: UUID,
    http_request: Request = None,
    storage: DesignStorage = Depends(get_design_storage)
):
    """
    Get metadata for uploaded design.
    
    **Useful for:**
    - UI initialization and layer controls
    - Map navigation setup
    - Performance optimization decisions
    - User guidance and feedback
    """
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        metadata = await storage.get_design_metadata(design_id)
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Design {design_id} not found"
            )
        
        return metadata
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Failed to retrieve metadata for design {design_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve design metadata: {str(e)}"
        )


@router.get("/download/{design_id}/{format}")
async def download_design(
    design_id: UUID,
    format: ExportFormat,
    http_request: Request = None,
    storage: DesignStorage = Depends(get_design_storage)
):
    """
    Download uploaded design data as-is in the requested format (geojson, kml, kmz).
    Preserves geometry and properties to maintain data integrity.
    """
    import json
    import tempfile
    import zipfile
    try:
        log_request_separator(logger, http_request.method if http_request else "GET", f"/api/v2/designs/download/{design_id}/{format.value}")
        
        layers = await storage.get_design_layers(design_id)
        features_fc = await storage.get_design_features(design_id)
        if layers is None or features_fc is None:
            raise HTTPException(status_code=404, detail=f"Design {design_id} not found")
        
        if format == ExportFormat.GEOJSON:
            content = json.dumps(features_fc, separators=(',', ':')).encode('utf-8')
            return Response(content=content, media_type="application/geo+json", headers={
                "Content-Disposition": f"attachment; filename=design_{design_id}.geojson"
            })
        
        import simplekml
        from shapely.geometry import shape
        kml = simplekml.Kml()
        kml.document.name = f"Design {design_id}"
        
        for layer in layers:
            folder = kml.newfolder(name=layer.get('name', 'Layer'))
            fc = layer.get('features', {"type": "FeatureCollection", "features": []})
            for idx, feat in enumerate(fc.get('features', [])):
                geom = feat.get('geometry')
                if not geom:
                    continue
                props = feat.get('properties') or {}
                placemark = folder.newplacemark()
                placemark.name = props.get('name') or f"{layer.get('name','Layer')}_{idx}"
                if props:
                    placemark.description = "\n".join([f"{k}: {v}" for k, v in props.items()])
                try:
                    shp = shape(geom)
                    if shp.geom_type == 'Point':
                        placemark.point = simplekml.Point(shp.coords[0])
                    elif shp.geom_type == 'LineString':
                        placemark.linestring = simplekml.LineString(coords=list(shp.coords))
                    elif shp.geom_type == 'Polygon':
                        if hasattr(shp, 'exterior') and shp.exterior:
                            placemark.polygon = simplekml.Polygon(outerboundaryis=list(shp.exterior.coords))
                except Exception:
                    continue
        kml_content = kml.kml().encode('utf-8')
        
        if format == ExportFormat.KML:
            return Response(content=kml_content, media_type="application/vnd.google-earth.kml+xml", headers={
                "Content-Disposition": f"attachment; filename=design_{design_id}.kml"
            })
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.kmz') as temp_file:
            with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as kmz:
                kmz.writestr('doc.kml', kml_content)
            temp_file.seek(0)
            with open(temp_file.name, 'rb') as f:
                kmz_bytes = f.read()
        try:
            import os
            os.unlink(temp_file.name)
        except Exception:
            pass
        return Response(content=kmz_bytes, media_type="application/vnd.google-earth.kmz", headers={
            "Content-Disposition": f"attachment; filename=design_{design_id}.kmz"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Design download failed for {design_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download design")

@router.delete("/designs/{design_id}")
async def delete_design(
    design_id: UUID,
    http_request: Request = None,
    storage: DesignStorage = Depends(get_design_storage)
):
    """
    Delete uploaded design and associated data.
    
    **Cleanup Features:**
    - Remove stored design files
    - Free storage space
    - Maintain system performance
    """
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        success = await storage.delete_design(design_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete design {design_id}"
            )
        
        return {
            "design_id": str(design_id),
            "status": "deleted",
            "message": "Design deleted successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Failed to delete design {design_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete design: {str(e)}"
        )


@router.get("/storage/stats")
async def get_storage_stats(
    http_request: Request = None,
    storage: DesignStorage = Depends(get_design_storage)
):
    """
    Get design storage statistics.
    
    **Monitoring Information:**
    - Total designs stored
    - Storage space usage
    - System performance metrics
    """
    
    try:
        log_request_separator(logger, http_request.method, str(http_request.url.path))
        
        stats = storage.get_storage_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to retrieve storage stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve storage statistics: {str(e)}"
        )