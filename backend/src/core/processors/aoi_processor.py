"""
AOI (Area of Interest) processing utilities
"""

import logging
from typing import Tuple, List, Optional
from datetime import datetime

from geojson_pydantic import Polygon as GeoJSONPolygon
from shapely.geometry import Polygon

from src.api.api_schemas import ValidationResponse, DataSourceType
from src.utils.geometry import validate_aoi_polygon, calculate_polygon_area_km2, geojson_to_shapely_polygon
from src.utils.exceptions import ValidationError
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class AOIProcessor:
    """Processor for Area of Interest validation and analysis"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def validate_aoi(self, aoi_boundary: GeoJSONPolygon) -> ValidationResponse:
        """
        Validate AOI and provide estimation metrics.
        
        Args:
            aoi_boundary: GeoJSON polygon representing the AOI
            
        Returns:
            ValidationResponse with validation results and estimates
        """
        
        try:
            # Validate the polygon
            is_valid, area_km2, errors = validate_aoi_polygon(
                aoi_boundary,
                self.settings.max_aoi_area_km2
            )
            
            warnings = []
            
            # Generate warnings for large areas
            if area_km2 > 50:
                warnings.append("Large AOI may result in longer processing times")
            
            if area_km2 > 25:
                warnings.append("Consider breaking large areas into smaller chunks for faster processing")
            
            # Estimate feature counts and processing time
            estimated_features = self._estimate_feature_counts(area_km2)
            estimated_processing_time = self._estimate_processing_time(area_km2, estimated_features)
            
            return ValidationResponse(
                valid=is_valid,
                area_km2=area_km2,
                estimated_features=estimated_features,
                estimated_processing_time=estimated_processing_time,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"AOI validation failed: {str(e)}")
            return ValidationResponse(
                valid=False,
                area_km2=0.0,
                estimated_features={},
                estimated_processing_time=0.0,
                warnings=[],
                errors=[f"Validation error: {str(e)}"]
            )
    
    def _estimate_feature_counts(self, area_km2: float) -> dict:
        """
        Estimate feature counts based on area size.
        These are rough estimates based on typical urban/suburban densities.
        """
        
        # Base estimates per km² (these are rough approximations)
        density_estimates = {
            DataSourceType.MICROSOFT_BUILDINGS: 500,    # buildings per km²
            DataSourceType.GOOGLE_BUILDINGS: 450,       # buildings per km²
            DataSourceType.OSM_BUILDINGS: 300,          # buildings per km²
            DataSourceType.OSM_ROADS: 50,               # road segments per km²
            DataSourceType.OSM_RAILWAYS: 2,             # railway segments per km²
            DataSourceType.OSM_LANDMARKS: 20,           # landmarks per km²
            DataSourceType.OSM_NATURAL: 10,             # natural features per km²
        }
        
        # Adjust estimates based on area size (larger areas tend to have lower density)
        area_factor = max(0.3, 1.0 - (area_km2 - 1.0) * 0.01)  # Reduce density for larger areas
        
        estimated_counts = {}
        for source_type, base_density in density_estimates.items():
            estimated_count = int(base_density * area_km2 * area_factor)
            estimated_counts[source_type] = max(0, estimated_count)
        
        return estimated_counts
    
    def _estimate_processing_time(self, area_km2: float, estimated_features: dict) -> float:
        """
        Estimate processing time based on area and expected feature counts.
        """
        
        # Base processing time factors (seconds)
        base_time_per_km2 = 2.0  # Base time per km²
        time_per_1000_features = 1.5  # Additional time per 1000 features
        
        # Calculate base time
        base_time = area_km2 * base_time_per_km2
        
        # Add time based on feature count
        total_features = sum(estimated_features.values())
        feature_time = (total_features / 1000.0) * time_per_1000_features
        
        # Add overhead for multiple data sources
        num_sources = len([count for count in estimated_features.values() if count > 0])
        overhead_time = num_sources * 2.0  # 2 seconds overhead per source
        
        total_time = base_time + feature_time + overhead_time
        
        # Apply constraints
        return min(max(total_time, 5.0), 300.0)  # Between 5 seconds and 5 minutes
    
    def analyze_aoi_characteristics(self, aoi_polygon: Polygon) -> dict:
        """
        Analyze AOI characteristics for optimization suggestions.
        
        Args:
            aoi_polygon: Shapely Polygon representing the AOI
            
        Returns:
            Dictionary with AOI characteristics and suggestions
        """
        
        try:
            # Calculate basic metrics
            area_km2 = calculate_polygon_area_km2(aoi_polygon)
            bounds = aoi_polygon.bounds
            width = bounds[2] - bounds[0]  # max_x - min_x
            height = bounds[3] - bounds[1]  # max_y - min_y
            
            # Calculate aspect ratio
            aspect_ratio = max(width, height) / min(width, height) if min(width, height) > 0 else 1.0
            
            # Determine shape characteristics
            perimeter = aoi_polygon.length
            compactness = (4 * 3.14159 * aoi_polygon.area) / (perimeter ** 2) if perimeter > 0 else 0
            
            # Generate optimization suggestions
            suggestions = []
            
            if area_km2 > 50:
                suggestions.append("Consider splitting large areas into smaller chunks for better performance")
            
            if aspect_ratio > 5:
                suggestions.append("Very elongated AOI may be inefficient - consider rectangular chunks")
            
            if compactness < 0.3:
                suggestions.append("Complex polygon shape detected - simple rectangles may be more efficient")
            
            return {
                "area_km2": area_km2,
                "width_degrees": width,
                "height_degrees": height,
                "aspect_ratio": aspect_ratio,
                "compactness": compactness,
                "suggestions": suggestions,
                "complexity": "high" if compactness < 0.3 or aspect_ratio > 3 else "medium" if aspect_ratio > 2 else "low"
            }
            
        except Exception as e:
            logger.error(f"AOI analysis failed: {str(e)}")
            return {
                "area_km2": 0.0,
                "suggestions": ["Analysis failed - please check AOI geometry"],
                "complexity": "unknown"
            }