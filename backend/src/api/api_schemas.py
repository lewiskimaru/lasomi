"""
Pydantic models for API request and response schemas
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator
from geojson_pydantic import Polygon, FeatureCollection


class DataSourceType(str, Enum):
    """Available data source types"""
    MICROSOFT_BUILDINGS = "microsoft_buildings"
    GOOGLE_BUILDINGS = "google_buildings"
    OSM_BUILDINGS = "osm_buildings"
    OSM_ROADS = "osm_roads"
    OSM_RAILWAYS = "osm_railways"
    OSM_LANDMARKS = "osm_landmarks"
    OSM_NATURAL = "osm_natural"


class ExportFormat(str, Enum):
    """Supported export formats"""
    GEOJSON = "geojson"
    KML = "kml"
    KMZ = "kmz"
    DWG = "dwg"
    SHAPEFILE = "shapefile"
    CSV = "csv"


class ProcessingStatus(str, Enum):
    """Processing job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class DataSourceConfig(BaseModel):
    """Configuration for individual data sources"""
    enabled: bool = Field(default=True, description="Enable this data source")
    priority: int = Field(default=1, description="Processing priority (1=highest)")
    timeout: int = Field(default=30, description="Timeout in seconds")


class FilterConfig(BaseModel):
    """Filtering configuration for extracted features"""
    min_building_area: Optional[float] = Field(
        default=None, 
        description="Minimum building area in square meters",
        ge=0
    )
    max_building_area: Optional[float] = Field(
        default=None,
        description="Maximum building area in square meters", 
        ge=0
    )
    road_types: Optional[List[str]] = Field(
        default=None,
        description="Allowed road types (motorway, trunk, primary, etc.)"
    )
    landmark_types: Optional[List[str]] = Field(
        default=None,
        description="Allowed landmark types (amenity, tourism, etc.)"
    )
    simplification_tolerance: Optional[float] = Field(
        default=0.001,
        description="Geometry simplification tolerance",
        ge=0,
        le=1.0
    )


class ExtractFeaturesRequest(BaseModel):
    """Request schema for feature extraction"""
    aoi_boundary: Polygon = Field(
        description="Area of Interest polygon in GeoJSON format (WGS84 coordinates)",
        example={
            "type": "Polygon",
            "coordinates": [[
                [36.8219, -1.2921],
                [36.8250, -1.2921], 
                [36.8250, -1.2950],
                [36.8219, -1.2950],
                [36.8219, -1.2921]
            ]]
        }
    )
    data_sources: Dict[DataSourceType, DataSourceConfig] = Field(
        default_factory=lambda: {
            DataSourceType.MICROSOFT_BUILDINGS: DataSourceConfig(),
            DataSourceType.GOOGLE_BUILDINGS: DataSourceConfig(),
            DataSourceType.OSM_BUILDINGS: DataSourceConfig(),
            DataSourceType.OSM_ROADS: DataSourceConfig(),
            DataSourceType.OSM_RAILWAYS: DataSourceConfig(),
            DataSourceType.OSM_LANDMARKS: DataSourceConfig(),
            DataSourceType.OSM_NATURAL: DataSourceConfig(),
        },
        description="Data source configurations - enable/disable specific sources",
        example={
            "microsoft_buildings": {"enabled": True, "priority": 1, "timeout": 30},
            "google_buildings": {"enabled": True, "priority": 2, "timeout": 30},
            "osm_buildings": {"enabled": True, "priority": 3, "timeout": 25},
            "osm_roads": {"enabled": True, "priority": 3, "timeout": 25},
            "osm_railways": {"enabled": False, "priority": 3, "timeout": 25},
            "osm_landmarks": {"enabled": True, "priority": 3, "timeout": 25},
            "osm_natural": {"enabled": False, "priority": 3, "timeout": 25}
        }
    )
    filters: Optional[FilterConfig] = Field(
        default_factory=FilterConfig,
        description="Feature filtering options to reduce result size",
        example={
            "min_building_area": 10,
            "road_types": ["primary", "secondary", "residential"],
            "simplification_tolerance": 0.001
        }
    )
    # Optional geometry cleaning (per-source) for AI-derived buildings (Google/MS). OSM untouched.
    clean: Optional[bool] = Field(
        default=False,
        description="If true, clean building shapes independently per source for Google/MS; OSM is left untouched."
    )
    cleaning_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional cleaning configuration: overlap_threshold (float), edge_buffer_m (float), strategy (highest_confidence|largest_area|union), min_area_m2 (float), simplify_tolerance_m (float), make_valid (bool)."
    )
    output_format: Optional[ExportFormat] = Field(
        default=None,
        description="Desired output format for immediate response (optional). If not specified, returns GeoJSON data with export URLs.",
        example="kmz"
    )
    raw: bool = Field(
        default=False,
        description="Return raw data directly in response instead of storing for separate download. Only used when output_format is specified.",
        example=True
    )
    
    @validator('aoi_boundary')
    def validate_aoi_boundary(cls, v):
        """Validate AOI boundary is a valid polygon"""
        if not v.coordinates or len(v.coordinates) == 0:
            raise ValueError("AOI boundary must have coordinates")
        
        # Check if it's a closed polygon
        first_ring = v.coordinates[0]
        if len(first_ring) < 4:
            raise ValueError("Polygon must have at least 4 coordinate pairs")
        
        if first_ring[0] != first_ring[-1]:
            raise ValueError("Polygon must be closed (first and last coordinates must be the same)")
        
        return v
    
    @validator('output_format')
    def validate_output_format(cls, v):
        """Validate output format is supported for inline export"""
        if v is not None:
            # Currently support GeoJSON, KML, and KMZ for inline export
            supported_inline_formats = [ExportFormat.GEOJSON, ExportFormat.KML, ExportFormat.KMZ]
            if v not in supported_inline_formats:
                raise ValueError(f"Output format '{v.value}' not supported for inline export. Supported formats: {[f.value for f in supported_inline_formats]}")
        return v
    
    @validator('raw')
    def validate_raw_parameter(cls, v, values):
        """Validate raw parameter usage"""
        if v and not values.get('output_format'):
            raise ValueError("'raw' parameter can only be used when 'output_format' is specified")
        return v


class FeatureStats(BaseModel):
    """Statistics for extracted features"""
    count: int = Field(description="Number of features extracted")
    total_area: Optional[float] = Field(default=None, description="Total area covered (for polygons)")
    total_length: Optional[float] = Field(default=None, description="Total length (for lines)")
    processing_time: float = Field(description="Processing time in seconds")


class DataSourceResult(BaseModel):
    """Result from a single data source"""
    source: DataSourceType = Field(description="Data source identifier")
    status: ProcessingStatus = Field(description="Processing status")
    stats: FeatureStats = Field(description="Feature statistics")
    geojson: FeatureCollection = Field(description="Extracted features in GeoJSON")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class ExtractFeaturesResponse(BaseModel):
    """Response schema for feature extraction"""
    job_id: UUID = Field(
        default_factory=uuid4, 
        description="Unique job identifier for accessing exports",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    status: ProcessingStatus = Field(
        description="Overall processing status",
        example="completed"
    )
    processing_time: float = Field(
        description="Total processing time in seconds",
        example=15.32
    )
    requested_sources: List[DataSourceType] = Field(
        description="Requested data sources",
        example=["microsoft_buildings", "osm_buildings", "osm_roads"]
    )
    
    # Results organized by data source
    results: Dict[DataSourceType, DataSourceResult] = Field(
        description="Results from each data source with independent datasets",
        example={
            "microsoft_buildings": {
                "source": "microsoft_buildings",
                "status": "completed",
                "stats": {"count": 1250, "processing_time": 8.5},
                "geojson": {"type": "FeatureCollection", "features": []}
            },
            "osm_roads": {
                "source": "osm_roads",
                "status": "completed", 
                "stats": {"count": 145, "processing_time": 4.2},
                "geojson": {"type": "FeatureCollection", "features": []}
            }
        }
    )
    
    # Export URLs
    export_urls: Dict[ExportFormat, str] = Field(
        description="URLs for downloading in different formats",
        example={
            "geojson": "/api/v1/export/550e8400-e29b-41d4-a716-446655440000/geojson",
            "kml": "/api/v1/export/550e8400-e29b-41d4-a716-446655440000/kml",
            "csv": "/api/v1/export/550e8400-e29b-41d4-a716-446655440000/csv"
        }
    )
    
    # Summary statistics
    total_features: int = Field(
        description="Total features across all sources",
        example=1395
    )
    successful_sources: int = Field(
        description="Number of successful data sources",
        example=2
    )
    failed_sources: int = Field(
        description="Number of failed data sources",
        example=0
    )
    
    # New fields for inline format export
    output_format: Optional[ExportFormat] = Field(
        default=None,
        description="Format of the data field when inline export was requested"
    )
    data: Optional[Any] = Field(
        default=None,
        description="Formatted data for immediate use when output_format and raw=true are specified. Format depends on output_format parameter."
    )


class ExportRequest(BaseModel):
    """Request schema for data export"""
    job_id: UUID = Field(description="Job ID from extraction request")
    format: ExportFormat = Field(description="Desired export format")
    sources: Optional[List[DataSourceType]] = Field(
        default=None,
        description="Specific sources to include (all if not specified)"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include processing metadata in export"
    )


class ValidationRequest(BaseModel):
    """Request schema for AOI validation"""
    aoi_boundary: Polygon = Field(
        description="AOI polygon to validate (must be a closed polygon in WGS84)",
        example={
            "type": "Polygon",
            "coordinates": [[
                [36.8219, -1.2921],
                [36.8250, -1.2921], 
                [36.8250, -1.2950],
                [36.8219, -1.2950],
                [36.8219, -1.2921]
            ]]
        }
    )


class ValidationResponse(BaseModel):
    """Response schema for AOI validation"""
    valid: bool = Field(description="Whether AOI is valid")
    area_km2: float = Field(description="AOI area in square kilometers")
    estimated_features: Dict[DataSourceType, int] = Field(
        description="Estimated feature counts per source"
    )
    estimated_processing_time: float = Field(
        description="Estimated processing time in seconds"
    )
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    errors: List[str] = Field(default_factory=list, description="Validation errors")


class HealthStatus(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    version: str = Field(description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime: float = Field(description="Service uptime in seconds")


class DataSourceHealth(BaseModel):
    """Health status for external data sources"""
    google_earth_engine: bool = Field(description="Google Earth Engine availability")
    overpass_api: bool = Field(description="Overpass API availability")
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = Field(default=True, description="Error flag")
    error_code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[Any] = Field(default=None, description="Additional error details")
    partial_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Partial results if available"
    )
    retry_suggestion: Optional[str] = Field(
        default=None,
        description="Suggestion for retry"
    )