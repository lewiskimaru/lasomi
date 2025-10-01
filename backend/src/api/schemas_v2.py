"""
Improved API schemas focused on essential parameters only
Raw data extraction with minimal, purposeful configuration
"""

from enum import Enum
from typing import Dict, List, Optional, Any
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
    CSV = "csv"


class ProcessingStatus(str, Enum):
    """Processing job status"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class DataSourceSelection(BaseModel):
    """Simple data source selection - only essential parameters"""
    enabled: bool = Field(default=True, description="Enable this data source")
    timeout: Optional[int] = Field(default=None, description="Override default timeout (seconds)")


class RawDataRequest(BaseModel):
    """
    Simplified request schema for raw data extraction.
    Only includes absolutely essential parameters for querying data sources.
    """
    
    # Core required parameter
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
    
    # Simple data source selection
    sources: Dict[DataSourceType, DataSourceSelection] = Field(
        default_factory=lambda: {
            DataSourceType.MICROSOFT_BUILDINGS: DataSourceSelection(),
            DataSourceType.GOOGLE_BUILDINGS: DataSourceSelection(),
            DataSourceType.OSM_BUILDINGS: DataSourceSelection(),
            DataSourceType.OSM_ROADS: DataSourceSelection(),
            DataSourceType.OSM_RAILWAYS: DataSourceSelection(enabled=False),
            DataSourceType.OSM_LANDMARKS: DataSourceSelection(enabled=False),
            DataSourceType.OSM_NATURAL: DataSourceSelection(enabled=False),
        },
        description="Data source selection - enable/disable specific sources"
    )
    
    # Optional geometry cleaning (per-source) for AI-derived buildings (Google/MS)
    clean: Optional[bool] = Field(
        default=False,
        description="If true, clean building shapes independently per source for Google/MS; OSM is left untouched."
    )
    # Optional roads clipping (OSM roads only for now)
    clean_roads: Optional[bool] = Field(
        default=False,
        description="If true, clip OSM roads to the AOI (drop outside segments)."
    )
    cleaning_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional cleaning configuration: overlap_threshold (float), edge_buffer_m (float), strategy (highest_confidence|largest_area|union), min_area_m2 (float), simplify_tolerance_m (float), make_valid (bool)."
    )
    
    # Optional immediate export
    export_format: Optional[ExportFormat] = Field(
        default=None,
        description="Optional: Return data in specified format immediately"
    )
    
    @validator('aoi_boundary')
    def validate_aoi_boundary(cls, v):
        """Validate AOI boundary is a valid closed polygon"""
        if not v.coordinates or len(v.coordinates) == 0:
            raise ValueError("AOI boundary must have coordinates")
        
        first_ring = v.coordinates[0]
        if len(first_ring) < 4:
            raise ValueError("Polygon must have at least 4 coordinate pairs")
        
        if first_ring[0] != first_ring[-1]:
            raise ValueError("Polygon must be closed (first and last coordinates must be the same)")
        
        return v


class FeatureStats(BaseModel):
    """Statistics for extracted features"""
    count: int = Field(description="Number of features extracted")
    processing_time: float = Field(description="Processing time in seconds")
    # Removed area/length calculations - keep it simple for raw data


class DataSourceResult(BaseModel):
    """Raw result from a single data source"""
    source: DataSourceType = Field(description="Data source identifier")
    status: ProcessingStatus = Field(description="Processing status")
    stats: FeatureStats = Field(description="Feature statistics")
    data: FeatureCollection = Field(description="Raw geospatial features")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class RawDataResponse(BaseModel):
    """
    Response schema for raw data extraction.
    Clean, focused structure for delivering raw geospatial data.
    """
    
    # Job identification
    job_id: UUID = Field(default_factory=uuid4, description="Unique job identifier")
    
    # Processing status
    status: ProcessingStatus = Field(description="Overall processing status")
    processing_time: float = Field(description="Total processing time in seconds")
    
    # Core results - raw data organized by source
    results: Dict[DataSourceType, DataSourceResult] = Field(
        description="Raw geospatial data organized by source"
    )
    
    # Simple summary
    total_features: int = Field(description="Total features across all sources")
    successful_sources: int = Field(description="Number of successful data sources")
    
    # Export data if requested
    export_data: Optional[Any] = Field(
        default=None,
        description="Exported data in requested format (if export_format specified)"
    )
    
    # Download URLs for different formats
    download_urls: Optional[Dict[ExportFormat, str]] = Field(
        default=None,
        description="URLs for downloading data in different formats"
    )


class ValidationRequest(BaseModel):
    """Request schema for AOI validation"""
    aoi_boundary: Polygon = Field(description="Area of Interest polygon to validate")


class ValidationResponse(BaseModel):
    """Response schema for AOI validation"""
    valid: bool = Field(description="Whether the AOI is valid")
    area_km2: float = Field(description="Area in square kilometers")
    errors: List[str] = Field(default_factory=list, description="Validation errors if any")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    estimated_features: Optional[Dict[DataSourceType, int]] = Field(
        default=None,
        description="Estimated feature counts per source"
    )
    estimated_processing_time: Optional[float] = Field(
        default=None,
        description="Estimated processing time in seconds"
    )


# Export schemas for download endpoints
class ExportRequest(BaseModel):
    """Request schema for data export"""
    job_id: UUID = Field(description="Job ID from extraction request")
    format: ExportFormat = Field(description="Desired export format")
    sources: Optional[List[DataSourceType]] = Field(
        default=None,
        description="Specific sources to include (all if not specified)"
    )


class DataSourceInfo(BaseModel):
    """Information about a data source"""
    name: str = Field(description="Human-readable name")
    description: str = Field(description="Description of the data source")
    provider: str = Field(description="Data provider organization")
    coverage: str = Field(description="Geographic coverage")
    feature_types: List[str] = Field(description="Types of features provided")
    update_frequency: str = Field(description="How often data is updated")
    license: str = Field(description="Data license information")


class DataSourcesResponse(BaseModel):
    """Response schema for data sources listing"""
    available_sources: List[DataSourceType] = Field(description="Available data source types")
    source_details: Dict[DataSourceType, DataSourceInfo] = Field(description="Detailed information per source")
    processing_info: Dict[str, Any] = Field(description="Processing configuration information")


# Inline export request for stateless downloads
class InlineExportRequest(BaseModel):
    """Minimal payload to export results inline without stored job."""
    results: Dict[DataSourceType, DataSourceResult] = Field(description="Results map to export")
    processing_time: Optional[float] = Field(default=0.0, description="Optional processing time metadata")