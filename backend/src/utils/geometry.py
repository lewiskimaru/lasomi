"""
Geometry processing utilities
"""

import logging
from typing import List, Tuple, Optional
from math import radians, sin, cos, sqrt, atan2

import geopandas as gpd
from shapely.geometry import Polygon, Point
from shapely.ops import transform
import pyproj
from geojson_pydantic import Polygon as GeoJSONPolygon

from src.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)


def calculate_polygon_area_km2(polygon: Polygon) -> float:
    """
    Calculate the area of a polygon in square kilometers using accurate projection.
    
    Args:
        polygon: Shapely Polygon in WGS84 coordinates
        
    Returns:
        Area in square kilometers
    """
    try:
        # Get the centroid to determine appropriate UTM zone
        centroid = polygon.centroid
        utm_crs = _get_utm_crs_from_point(centroid.x, centroid.y)
        
        # Create transformer to UTM
        transformer = pyproj.Transformer.from_crs(
            pyproj.CRS.from_epsg(4326),  # WGS84
            pyproj.CRS.from_epsg(utm_crs),
            always_xy=True
        )
        
        # Transform polygon to UTM
        utm_polygon = transform(transformer.transform, polygon)
        
        # Calculate area in square meters, convert to km²
        area_m2 = utm_polygon.area
        area_km2 = area_m2 / 1_000_000
        
        return area_km2
        
    except Exception as e:
        logger.warning(f"Failed to calculate precise area, using approximation: {e}")
        return _approximate_polygon_area_km2(polygon)


def _get_utm_crs_from_point(lon: float, lat: float) -> int:
    """Get appropriate UTM CRS code for a given point"""
    # Calculate UTM zone
    zone = int((lon + 180) / 6) + 1
    
    # Determine hemisphere
    if lat >= 0:
        # Northern hemisphere
        epsg_code = 32600 + zone
    else:
        # Southern hemisphere  
        epsg_code = 32700 + zone
    
    return epsg_code


def _approximate_polygon_area_km2(polygon: Polygon) -> float:
    """Approximate polygon area using Haversine formula"""
    try:
        coords = list(polygon.exterior.coords)
        if len(coords) < 4:
            return 0.0
        
        # Simple bounding box approximation
        lons = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]
        
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        # Calculate width and height in km
        width_km = _haversine_distance(min_lat, min_lon, min_lat, max_lon)
        height_km = _haversine_distance(min_lat, min_lon, max_lat, min_lon)
        
        # Rough approximation (will overestimate for non-rectangular shapes)
        return width_km * height_km * 0.7  # Factor to account for irregular shapes
        
    except Exception:
        logger.warning("Failed to calculate approximate area")
        return 0.0


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def validate_aoi_polygon(aoi: GeoJSONPolygon, max_area_km2: float) -> Tuple[bool, float, List[str]]:
    """
    Validate AOI polygon geometry and size constraints.
    
    Args:
        aoi: GeoJSON Polygon
        max_area_km2: Maximum allowed area in square kilometers
        
    Returns:
        Tuple of (is_valid, area_km2, validation_errors)
    """
    errors = []
    
    try:
        # Convert to Shapely polygon
        coords = aoi.coordinates[0]  # Exterior ring
        polygon = Polygon(coords)
        
        # Check if polygon is valid
        if not polygon.is_valid:
            errors.append(f"Invalid polygon geometry: {polygon.is_valid}")
            return False, 0.0, errors
        
        # Check if polygon is closed
        if coords[0] != coords[-1]:
            errors.append("Polygon must be closed (first and last coordinates must be the same)")
            return False, 0.0, errors
        
        # Check minimum number of coordinates
        if len(coords) < 4:
            errors.append("Polygon must have at least 4 coordinate pairs")
            return False, 0.0, errors
        
        # Calculate area
        area_km2 = calculate_polygon_area_km2(polygon)
        
        # Check area constraints
        if area_km2 <= 0:
            errors.append("Polygon area must be greater than 0")
            return False, area_km2, errors
        
        if area_km2 > max_area_km2:
            errors.append(f"Polygon area ({area_km2:.2f} km²) exceeds maximum allowed ({max_area_km2} km²)")
            return False, area_km2, errors
        
        # Check coordinate bounds (must be valid lat/lon)
        for coord in coords:
            lon, lat = coord[0], coord[1]
            if not (-180 <= lon <= 180):
                errors.append(f"Invalid longitude: {lon} (must be between -180 and 180)")
            if not (-90 <= lat <= 90):
                errors.append(f"Invalid latitude: {lat} (must be between -90 and 90)")
        
        if errors:
            return False, area_km2, errors
        
        return True, area_km2, []
        
    except Exception as e:
        errors.append(f"Error validating polygon: {str(e)}")
        return False, 0.0, errors


def simplify_geometry(geometry, tolerance: float = 0.001):
    """Simplify geometry using Douglas-Peucker algorithm"""
    try:
        if hasattr(geometry, 'simplify'):
            return geometry.simplify(tolerance, preserve_topology=True)
        return geometry
    except Exception as e:
        logger.warning(f"Failed to simplify geometry: {e}")
        return geometry


def geojson_to_shapely_polygon(geojson_polygon: GeoJSONPolygon) -> Polygon:
    """Convert GeoJSON Polygon to Shapely Polygon"""
    try:
        coordinates = geojson_polygon.coordinates
        if not coordinates or len(coordinates) == 0:
            raise ValidationError("Empty polygon coordinates")
        
        exterior = coordinates[0]
        holes = coordinates[1:] if len(coordinates) > 1 else None
        
        return Polygon(exterior, holes)
        
    except Exception as e:
        raise ValidationError(f"Failed to convert GeoJSON polygon: {str(e)}")


def create_bounding_box(polygon: Polygon, buffer_km: float = 0.1) -> Tuple[float, float, float, float]:
    """
    Create bounding box coordinates for a polygon with optional buffer.
    
    Args:
        polygon: Shapely Polygon
        buffer_km: Buffer distance in kilometers
        
    Returns:
        Tuple of (west, south, east, north) coordinates
    """
    bounds = polygon.bounds
    west, south, east, north = bounds
    
    if buffer_km > 0:
        # Convert buffer from km to degrees (rough approximation)
        buffer_deg = buffer_km / 111.0  # 1 degree ≈ 111 km
        
        west -= buffer_deg
        south -= buffer_deg
        east += buffer_deg
        north += buffer_deg
    
    return west, south, east, north