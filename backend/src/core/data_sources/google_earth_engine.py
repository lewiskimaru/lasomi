"""
Google Earth Engine connector for Microsoft Buildings and Google Open Buildings
"""

import asyncio
import json
import os
from typing import Dict, Optional, Any
import logging

import ee
from geojson_pydantic import FeatureCollection
from shapely.geometry import Polygon

from src.core.interfaces import IDataSourceConnector
from src.api.api_schemas import DataSourceType, DataSourceConfig
from src.api.schemas_v2 import DataSourceType as DataSourceTypeV2
from src.utils.exceptions import DataSourceError, AuthenticationError
from src.utils.geometry import create_bounding_box
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class GoogleEarthEngineConnector(IDataSourceConnector):
    """Connector for Google Earth Engine data sources implementing proper interface"""
    
    def __init__(self, source_type: DataSourceType, config: DataSourceConfig):
        self.source_type = source_type
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{source_type.value}")
        self._authenticated = False
        self.settings = get_settings()
        self._initialize_ee()
    
    def _initialize_ee(self):
        """Initialize Earth Engine authentication"""
        try:
            # Check if service account credentials are available
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if not credentials_path or not os.path.exists(credentials_path):
                raise AuthenticationError(
                    "google_earth_engine",
                    "Service account credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable."
                )
            
            # Read service account key
            with open(credentials_path, 'r') as f:
                key_data = json.load(f)
            
            # Initialize Earth Engine with service account
            credentials = ee.ServiceAccountCredentials(
                key_data['client_email'],
                credentials_path
            )
            
            ee.Initialize(credentials)
            self._authenticated = True
            self.logger.info("Google Earth Engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Earth Engine: {e}")
            raise AuthenticationError("google_earth_engine", str(e))
    
    async def test_connection(self) -> bool:
        """Test Google Earth Engine connection"""
        try:
            if not self._authenticated:
                return False
            
            # Test with a simple operation
            test_collection = ee.ImageCollection('COPERNICUS/S2_SR').limit(1)
            test_collection.size().getInfo()  # This will fail if not authenticated
            
            return True
            
        except Exception as e:
            self.logger.error(f"Google Earth Engine connection test failed: {e}")
            return False
    
    async def extract_features(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]] = None) -> FeatureCollection:
        """Extract features from Google Earth Engine"""
        
        if not self._authenticated:
            raise DataSourceError(self.source_type.value, "Google Earth Engine not authenticated")
        
        try:
            # Create Earth Engine geometry from AOI
            coords = list(aoi_polygon.exterior.coords)
            ee_geometry = ee.Geometry.Polygon(coords)
            
            # Get the appropriate feature collection based on source type
            if self.source_type == DataSourceType.MICROSOFT_BUILDINGS:
                features = await self._extract_microsoft_buildings(ee_geometry, filters)
            elif self.source_type == DataSourceType.GOOGLE_BUILDINGS:
                features = await self._extract_google_buildings(ee_geometry, filters)
            else:
                raise DataSourceError(
                    self.source_type.value,
                    f"Unsupported source type for Google Earth Engine: {self.source_type.value}"
                )
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract features from {self.source_type.value}: {e}")
            raise DataSourceError(self.source_type.value, str(e))
    
    def get_source_type(self) -> DataSourceType:
        """Get the data source type identifier"""
        return self.source_type
    
    async def extract_raw_features(self, aoi: Polygon, timeout: Optional[int] = None) -> FeatureCollection:
        """Extract raw features implementing the interface"""
        # Convert timeout to filters dict format expected by existing method
        filters = {} if not timeout else {'timeout': timeout}
        return await self.extract_features(aoi, filters)
    
    async def _extract_microsoft_buildings(self, ee_geometry: ee.Geometry, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract Microsoft Building Footprints using optimized Earth Engine export"""
        
        try:
            # Determine country/region (simplified - you might want to improve this)
            # For now, we'll try Kenya as an example
            collection_id = 'projects/sat-io/open-datasets/MSBuildings/Kenya'
            
            try:
                buildings_collection = ee.FeatureCollection(collection_id)
            except Exception:
                # Fallback: try to determine the correct collection based on geometry
                # This is a simplified approach - in production you'd want better region detection
                self.logger.warning(f"Could not load {collection_id}, trying to detect region...")
                buildings_collection = await self._detect_ms_buildings_collection(ee_geometry)
            
            # Filter by AOI
            filtered_buildings = buildings_collection.filterBounds(ee_geometry)
            
            # Apply additional filters if provided
            if filters:
                if filters.get('min_building_area'):
                    # Note: Microsoft buildings may not have area attribute directly
                    # You might need to calculate it or use confidence scores
                    pass
                if filters.get('min_confidence'):
                    min_confidence = filters['min_confidence']
                    filtered_buildings = filtered_buildings.filter(
                        ee.Filter.gte('confidence', min_confidence)
                    )
            
            # Use size-aware processing with configurable thresholds
            feature_count = filtered_buildings.size().getInfo()
            self.logger.info(f"Found {feature_count} Microsoft buildings in AOI")
            
            # Extract ALL features without any limits, sampling, or simplification
            # Raw data as-is from Google Earth Engine
            self.logger.info(f"Extracting ALL {feature_count} Microsoft buildings - no limits applied")
            geojson_data = filtered_buildings.getInfo()
            
            # Convert to FeatureCollection and apply building processing
            features = []
            if geojson_data and 'features' in geojson_data:
                features = geojson_data['features']

            # Apply building feature processing for clean properties
            from src.utils.building_processor import building_processor
            processed_collection = {
                "type": "FeatureCollection",
                "features": features
            }
            processed_collection = building_processor.process_feature_collection(processed_collection, self.source_type)

            self.logger.info(f"Successfully extracted and processed {len(processed_collection['features'])} Microsoft buildings with clean properties")

            return FeatureCollection(
                type="FeatureCollection",
                features=processed_collection['features']
            )
            
        except Exception as e:
            raise DataSourceError("microsoft_buildings", f"Failed to extract Microsoft buildings: {str(e)}")
    
    async def _extract_google_buildings(self, ee_geometry: ee.Geometry, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract Google Open Buildings using optimized Earth Engine export"""
        
        try:
            # Google Open Buildings collection v3 - latest version (May 2023)
            buildings_collection = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons')
            
            # Filter by AOI
            filtered_buildings = buildings_collection.filterBounds(ee_geometry)
            
            # Apply confidence filter if specified
            if filters and filters.get('min_confidence'):
                min_confidence = filters['min_confidence']
                filtered_buildings = filtered_buildings.filter(
                    ee.Filter.gte('confidence', min_confidence)
                )
            
            # Use size-aware processing with configurable thresholds
            feature_count = filtered_buildings.size().getInfo()
            self.logger.info(f"Found {feature_count} Google Open Buildings in AOI")
            
            # Extract ALL features without any limits, sampling, or simplification
            # Raw data as-is from Google Earth Engine
            self.logger.info(f"Extracting ALL {feature_count} Google Open Buildings - no limits applied")
            geojson_data = filtered_buildings.getInfo()
            
            # Convert to FeatureCollection and apply building processing
            features = []
            if geojson_data and 'features' in geojson_data:
                features = geojson_data['features']

            # Apply building feature processing for clean properties
            from src.utils.building_processor import building_processor
            processed_collection = {
                "type": "FeatureCollection",
                "features": features
            }
            processed_collection = building_processor.process_feature_collection(processed_collection, self.source_type)

            self.logger.info(f"Successfully extracted and processed {len(processed_collection['features'])} Google Open Buildings with clean properties")

            return FeatureCollection(
                type="FeatureCollection",
                features=processed_collection['features']
            )
            
        except Exception as e:
            raise DataSourceError("google_buildings", f"Failed to extract Google buildings: {str(e)}")
    
    async def _detect_ms_buildings_collection(self, ee_geometry: ee.Geometry) -> ee.FeatureCollection:
        """
        Attempt to detect the correct Microsoft Buildings collection based on geometry.
        This is a simplified implementation - you might want to improve the region detection logic.
        """
        
        # Get geometry centroid
        centroid = ee_geometry.centroid()
        coords = centroid.coordinates().getInfo()
        lon, lat = coords[0], coords[1]
        
        # Simple region detection based on coordinates
        # You could expand this with a proper country/region lookup
        region_mapping = {
            'Kenya': (-5, 5, 33, 42),  # (min_lat, max_lat, min_lon, max_lon)
            'Nigeria': (4, 14, 2, 15),
            'Tanzania': (-12, -1, 29, 41),
            # Add more regions as needed
        }
        
        detected_region = None
        for region, (min_lat, max_lat, min_lon, max_lon) in region_mapping.items():
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                detected_region = region
                break
        
        if detected_region:
            collection_id = f'projects/sat-io/open-datasets/MSBuildings/{detected_region}'
            self.logger.info(f"Detected region: {detected_region}, using collection: {collection_id}")
            return ee.FeatureCollection(collection_id)
        else:
            # Fallback to a default or raise an error
            raise DataSourceError(
                "microsoft_buildings",
                f"Could not determine Microsoft Buildings collection for coordinates: {lon}, {lat}"
            )