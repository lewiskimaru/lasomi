"""
Schemas for design file upload and rendering
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field
from geojson_pydantic import FeatureCollection


class DesignFileFormat(str, Enum):
    """Supported design file formats"""
    GEOJSON = "geojson"
    KML = "kml"
    KMZ = "kmz"


class DesignLayer(BaseModel):
    """Represents a layer/folder in the design with its features"""
    name: str = Field(description="Layer or folder name")
    description: Optional[str] = Field(default=None, description="Layer description")
    features: FeatureCollection = Field(description="Features in this layer")
    style: Optional[Dict[str, Any]] = Field(default=None, description="Layer styling information")
    visible: bool = Field(default=True, description="Whether layer should be visible by default")
    feature_count: int = Field(description="Number of features in this layer")


class DesignMetadata(BaseModel):
    """Metadata extracted from uploaded design file"""
    filename: str = Field(description="Original filename")
    format: DesignFileFormat = Field(description="File format")
    file_size: int = Field(description="File size in bytes")
    total_features: int = Field(description="Total features across all layers")
    layer_count: int = Field(description="Number of layers/folders")
    
    # Geographic bounds for map navigation
    bbox: List[float] = Field(description="Bounding box [west, south, east, north]")
    center: List[float] = Field(description="Geographic center [longitude, latitude]")
    
    # Processing metadata
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float = Field(description="Time taken to process file (seconds)")
    
    # File structure info
    has_folders: bool = Field(description="Whether file contains folder/layer structure")
    has_styling: bool = Field(description="Whether file contains styling information")
    coordinate_system: Optional[str] = Field(default=None, description="Detected coordinate system")


class ParsedDesign(BaseModel):
    """Complete parsed design with all layers and metadata"""
    design_id: UUID = Field(default_factory=uuid4, description="Unique design identifier")
    metadata: DesignMetadata = Field(description="Design metadata")
    layers: List[DesignLayer] = Field(description="All layers in the design")
    
    # Quick access for map rendering
    all_features: FeatureCollection = Field(description="All features combined for quick rendering")
    suggested_zoom: int = Field(description="Suggested map zoom level based on extent")


class DesignUploadResponse(BaseModel):
    """Response from design upload endpoint"""
    design_id: UUID = Field(description="Unique design identifier for future reference")
    status: str = Field(description="Processing status")
    metadata: DesignMetadata = Field(description="Extracted design metadata")
    
    # Map navigation assistance
    map_center: List[float] = Field(description="Suggested map center [longitude, latitude]")
    map_zoom: int = Field(description="Suggested map zoom level")
    map_bounds: List[float] = Field(description="Map bounds [west, south, east, north]")
    
    # Layer information for UI
    layer_summary: List[Dict[str, Any]] = Field(description="Summary of layers for UI display")
    
    # Next steps guidance
    message: str = Field(description="User guidance message")
    next_action: str = Field(description="Suggested next action for user")


class DesignRenderRequest(BaseModel):
    """Request for rendering design on map"""
    design_id: UUID = Field(description="Design identifier")
    layers: Optional[List[str]] = Field(default=None, description="Specific layers to render (all if None)")
    simplified: bool = Field(default=False, description="Whether to return simplified geometries for performance")
    max_features_per_layer: Optional[int] = Field(default=None, description="Limit features per layer for performance")


class DesignRenderResponse(BaseModel):
    """Response for design rendering"""
    design_id: UUID = Field(description="Design identifier")
    layers: List[DesignLayer] = Field(description="Requested layers with features")
    total_features: int = Field(description="Total features being rendered")
    bounds: List[float] = Field(description="Bounds of rendered features [west, south, east, north]")
    simplified: bool = Field(description="Whether geometries were simplified")