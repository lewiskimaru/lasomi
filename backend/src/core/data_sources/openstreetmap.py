"""
OpenStreetMap connector using Overpass API and OSMnx
"""

import asyncio
import time
from typing import Dict, Optional, Any, List
import logging

import aiohttp
import osmnx as ox
import geopandas as gpd
from geojson_pydantic import FeatureCollection
from shapely.geometry import Polygon
import overpy

from src.core.interfaces import IDataSourceConnector
from src.api.api_schemas import DataSourceType, DataSourceConfig
from src.utils.exceptions import DataSourceError, RateLimitError, TimeoutError
from src.utils.geometry import create_bounding_box
from src.core.config import get_settings

logger = logging.getLogger(__name__)

# Configure OSMnx using the new settings module
ox.settings.use_cache = True
ox.settings.log_console = False


class OpenStreetMapConnector(IDataSourceConnector):
    """Connector for OpenStreetMap data via Overpass API implementing proper interface"""
    
    def __init__(self, source_type: DataSourceType, config: DataSourceConfig):
        self.source_type = source_type
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{source_type.value}")
        self.settings = get_settings()
        self.overpass_api = overpy.Overpass()
        self._last_request_time = 0
        
        # Rate limiting
        self.min_request_interval = 1.0 / self.settings.overpass_rate_limit  # seconds between requests
    
    async def test_connection(self) -> bool:
        """Test Overpass API connection"""
        try:
            # Simple test query
            test_query = """
            [out:json][timeout:5];
            (
              node["amenity"="hospital"](51.5,-0.13,51.51,-0.12);
            );
            out 1;
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.settings.overpass_api_url,
                    data=test_query,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Overpass API connection test failed: {e}")
            return False
    
    async def extract_features(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]] = None) -> FeatureCollection:
        """Extract features from OpenStreetMap"""
        
        try:
            # Apply rate limiting
            await self._apply_rate_limit()
            
            # Extract features based on source type
            if self.source_type == DataSourceType.OSM_BUILDINGS:
                return await self._extract_buildings(aoi_polygon, filters)
            elif self.source_type == DataSourceType.OSM_ROADS:
                return await self._extract_roads(aoi_polygon, filters)
            elif self.source_type == DataSourceType.OSM_RAILWAYS:
                return await self._extract_railways(aoi_polygon, filters)
            elif self.source_type == DataSourceType.OSM_LANDMARKS:
                return await self._extract_landmarks(aoi_polygon, filters)
            elif self.source_type == DataSourceType.OSM_NATURAL:
                return await self._extract_natural_features(aoi_polygon, filters)
            else:
                raise DataSourceError(
                    self.source_type.value,
                    f"Unsupported OSM source type: {self.source_type.value}"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to extract {self.source_type.value}: {e}")
            raise DataSourceError(self.source_type.value, str(e))
    
    def get_source_type(self) -> DataSourceType:
        """Get the data source type identifier"""
        return self.source_type
    
    async def extract_raw_features(self, aoi: Polygon, timeout: Optional[int] = None) -> FeatureCollection:
        """Extract raw features implementing the interface"""
        # Convert timeout to filters dict format expected by existing method
        filters = {} if not timeout else {'timeout': timeout}
        return await self.extract_features(aoi, filters)
    
    async def _apply_rate_limit(self):
        """Apply rate limiting for Overpass API"""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    async def _extract_buildings(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract building features from OSM using raw Overpass API (like Overpass Turbo)"""
        
        # Always use direct Overpass API for raw, unprocessed data
        return await self._extract_buildings_overpass(aoi_polygon, filters)
    
    async def _extract_buildings_overpass(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract buildings using direct Overpass API query (exactly like Overpass Turbo)"""
        
        bbox = create_bounding_box(aoi_polygon)
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"  # south,west,north,east
        
        # Comprehensive query to get ALL building data like Overpass Turbo
        query = f"""
        [out:json][timeout:{self.settings.overpass_timeout}];
        (
          way["building"]({bbox_str});
          relation["building"]({bbox_str});
          node["building"]({bbox_str});
        );
        out geom;
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.settings.overpass_api_url,
                    data=query,
                    timeout=aiohttp.ClientTimeout(total=self.settings.overpass_timeout + 5)
                ) as response:
                    if response.status == 429:
                        raise RateLimitError("overpass_api")
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Convert to GeoJSON and apply building processing
                    geojson_collection = self._convert_overpass_to_geojson(data, "buildings")

                    # Apply building feature processing for clean properties
                    from src.utils.building_processor import building_processor
                    if hasattr(geojson_collection, 'dict'):
                        # Convert Pydantic object to dict for processing
                        collection_dict = geojson_collection.dict()
                    else:
                        collection_dict = geojson_collection

                    processed_collection = building_processor.process_feature_collection(collection_dict, self.source_type)

                    # Convert back to FeatureCollection
                    from geojson_pydantic import FeatureCollection
                    return FeatureCollection(**processed_collection)
                    
        except asyncio.TimeoutError:
            raise TimeoutError("overpass_buildings_query", self.settings.overpass_timeout)
        except Exception as e:
            raise DataSourceError("osm_buildings", f"Overpass query failed: {str(e)}")
    
    async def _extract_roads(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract road features using raw Overpass API (like Overpass Turbo)"""
        
        bbox = create_bounding_box(aoi_polygon)
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"  # south,west,north,east
        
        # Get ALL road types - user can filter client-side if needed
        query = f"""
        [out:json][timeout:{self.settings.overpass_timeout}];
        (
          way["highway"]({bbox_str});
          relation["highway"]({bbox_str});
        );
        out geom;
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.settings.overpass_api_url,
                    data=query,
                    timeout=aiohttp.ClientTimeout(total=self.settings.overpass_timeout + 5)
                ) as response:
                    if response.status == 429:
                        raise RateLimitError("overpass_api")
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    return self._convert_overpass_to_geojson(data, "roads")
                    
        except asyncio.TimeoutError:
            raise TimeoutError("overpass_roads_query", self.settings.overpass_timeout)
        except Exception as e:
            raise DataSourceError("osm_roads", f"Overpass query failed: {str(e)}")
    
    async def _extract_railways(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract railway features using raw Overpass API"""
        
        bbox = create_bounding_box(aoi_polygon)
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"  # south,west,north,east
        
        query = f"""
        [out:json][timeout:{self.settings.overpass_timeout}];
        (
          way["railway"]({bbox_str});
          relation["railway"]({bbox_str});
          node["railway"]({bbox_str});
        );
        out geom;
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.settings.overpass_api_url,
                    data=query,
                    timeout=aiohttp.ClientTimeout(total=self.settings.overpass_timeout + 5)
                ) as response:
                    if response.status == 429:
                        raise RateLimitError("overpass_api")
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    return self._convert_overpass_to_geojson(data, "railways")
                    
        except asyncio.TimeoutError:
            raise TimeoutError("overpass_railways_query", self.settings.overpass_timeout)
        except Exception as e:
            raise DataSourceError("osm_railways", f"Overpass query failed: {str(e)}")
    
    async def _extract_landmarks(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract landmark features using raw Overpass API"""
        
        bbox = create_bounding_box(aoi_polygon)
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"  # south,west,north,east
        
        # Query for all amenities, tourism, shops, and leisure features
        query = f"""
        [out:json][timeout:{self.settings.overpass_timeout}];
        (
          way["amenity"]({bbox_str});
          way["tourism"]({bbox_str});
          way["shop"]({bbox_str});
          way["leisure"]({bbox_str});
          relation["amenity"]({bbox_str});
          relation["tourism"]({bbox_str});
          relation["shop"]({bbox_str});
          relation["leisure"]({bbox_str});
          node["amenity"]({bbox_str});
          node["tourism"]({bbox_str});
          node["shop"]({bbox_str});
          node["leisure"]({bbox_str});
        );
        out geom;
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.settings.overpass_api_url,
                    data=query,
                    timeout=aiohttp.ClientTimeout(total=self.settings.overpass_timeout + 5)
                ) as response:
                    if response.status == 429:
                        raise RateLimitError("overpass_api")
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    return self._convert_overpass_to_geojson(data, "landmarks")
                    
        except asyncio.TimeoutError:
            raise TimeoutError("overpass_landmarks_query", self.settings.overpass_timeout)
        except Exception as e:
            raise DataSourceError("osm_landmarks", f"Overpass query failed: {str(e)}")
    
    async def _extract_natural_features(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]]) -> FeatureCollection:
        """Extract natural features using raw Overpass API"""
        
        bbox = create_bounding_box(aoi_polygon)
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"  # south,west,north,east
        
        # Query for natural features and land use
        query = f"""
        [out:json][timeout:{self.settings.overpass_timeout}];
        (
          way["natural"]({bbox_str});
          way["landuse"]({bbox_str});
          relation["natural"]({bbox_str});
          relation["landuse"]({bbox_str});
          node["natural"]({bbox_str});
        );
        out geom;
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.settings.overpass_api_url,
                    data=query,
                    timeout=aiohttp.ClientTimeout(total=self.settings.overpass_timeout + 5)
                ) as response:
                    if response.status == 429:
                        raise RateLimitError("overpass_api")
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    return self._convert_overpass_to_geojson(data, "natural")
                    
        except asyncio.TimeoutError:
            raise TimeoutError("overpass_natural_query", self.settings.overpass_timeout)
        except Exception as e:
            raise DataSourceError("osm_natural", f"Overpass query failed: {str(e)}")
    
    def _convert_overpass_to_geojson(self, overpass_data: Dict, feature_type: str = "features") -> FeatureCollection:
        """Convert Overpass API response to GeoJSON FeatureCollection preserving ALL coordinate data"""
        
        features = []
        
        try:
            self.logger.info(f"Converting {len(overpass_data.get('elements', []))} raw OSM elements to GeoJSON")
            
            for element in overpass_data.get('elements', []):
                feature = self._convert_osm_element_to_feature(element)
                if feature:
                    features.append(feature)
            
            self.logger.info(f"Successfully converted {len(features)} OSM {feature_type} features")
            
            return FeatureCollection(
                type="FeatureCollection",
                features=features
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert Overpass data to GeoJSON: {e}")
            return FeatureCollection(type="FeatureCollection", features=[])
    
    def _convert_osm_element_to_feature(self, element: Dict) -> Optional[Dict]:
        """Convert a single OSM element to GeoJSON feature with full coordinate preservation"""
        
        try:
            element_type = element.get('type')
            element_id = element.get('id')
            tags = element.get('tags', {})
            
            # Handle nodes (points)
            if element_type == 'node':
                if 'lat' in element and 'lon' in element:
                    feature = {
                        "type": "Feature",
                        "id": f"node/{element_id}",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [element['lon'], element['lat']]
                        },
                        "properties": {
                            "osm_type": "node",
                            "osm_id": element_id,
                            **tags
                        }
                    }
                    
                    # Apply name extraction for landmarks
                    if self.source_type == DataSourceType.OSM_LANDMARKS:
                        feature = self._apply_meaningful_naming(feature)
                    
                    return feature
            
            # Handle ways (lines/polygons)
            elif element_type == 'way' and 'geometry' in element:
                coords = [[node['lon'], node['lat']] for node in element['geometry']]
                
                if len(coords) < 2:
                    return None
                
                # Determine if it's a polygon (closed way) or linestring
                if len(coords) >= 4 and coords[0] == coords[-1]:
                    # Closed way - polygon
                    geometry = {
                        "type": "Polygon",
                        "coordinates": [coords]
                    }
                else:
                    # Open way - linestring
                    geometry = {
                        "type": "LineString",
                        "coordinates": coords
                    }
                
                feature = {
                    "type": "Feature",
                    "id": f"way/{element_id}",
                    "geometry": geometry,
                    "properties": {
                        "osm_type": "way",
                        "osm_id": element_id,
                        **tags
                    }
                }
                
                # Apply name extraction for landmarks
                if self.source_type == DataSourceType.OSM_LANDMARKS:
                    feature = self._apply_meaningful_naming(feature)
                
                return feature
            
            # Handle relations (multipolygons, etc.)
            elif element_type == 'relation':
                # For relations, we need to process the members
                # This is complex, but we'll create a basic representation
                members = element.get('members', [])
                
                # Try to extract geometry if available
                if 'geometry' in element:
                    coords = [[node['lon'], node['lat']] for node in element['geometry']]
                    if len(coords) >= 4 and coords[0] == coords[-1]:
                        geometry = {
                            "type": "Polygon",
                            "coordinates": [coords]
                        }
                    elif len(coords) >= 2:
                        geometry = {
                            "type": "LineString",
                            "coordinates": coords
                        }
                    else:
                        return None
                    
                    feature = {
                        "type": "Feature",
                        "id": f"relation/{element_id}",
                        "geometry": geometry,
                        "properties": {
                            "osm_type": "relation",
                            "osm_id": element_id,
                            **tags
                        }
                    }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to convert OSM element {element.get('id', 'unknown')}: {e}")
            return None
    
    def _apply_meaningful_naming(self, feature: Dict) -> Dict:
        """Apply meaningful naming to OSM landmark features"""

        try:
            from src.utils.osm_name_extractor import osm_name_extractor

            # Get original properties for debugging
            original_properties = feature.get('properties', {})
            original_name = original_properties.get('name', 'No name')
            osm_id = original_properties.get('osm_id', 'unknown')

            self.logger.debug(f"Processing OSM feature {osm_id} with properties: {original_properties}")

            # Apply meaningful naming
            updated_feature = osm_name_extractor.update_feature_properties(feature)

            # Verify the result
            updated_properties = updated_feature.get('properties', {})
            meaningful_name = updated_properties.get('Name', 'No Name set')

            # Log the result for debugging (reduced verbosity)
            self.logger.debug(f"OSM {osm_id}: Applied meaningful naming '{original_name}' -> '{meaningful_name}'")

            # Ensure the Name property is set and not None
            if not meaningful_name or meaningful_name == 'No Name set':
                # Fallback: try to extract name manually
                fallback_name = self._extract_fallback_name(original_properties)
                updated_properties['Name'] = fallback_name
                self.logger.warning(f"OSM {osm_id}: Used fallback name '{fallback_name}'")

            return updated_feature

        except Exception as e:
            self.logger.error(f"Failed to apply meaningful naming: {e}")
            # Ensure we at least set a basic name
            if 'properties' not in feature:
                feature['properties'] = {}

            fallback_name = self._extract_fallback_name(feature['properties'])
            feature['properties']['Name'] = fallback_name
            self.logger.warning(f"Used emergency fallback name: '{fallback_name}'")

            return feature

    def _extract_fallback_name(self, properties: Dict) -> str:
        """Extract a fallback name from OSM properties"""

        # Priority order for fallback naming
        name_fields = ['name', 'name:en', 'brand', 'operator']

        # Try explicit name fields first
        for field in name_fields:
            if field in properties and properties[field]:
                value = str(properties[field]).strip()
                if value and value.lower() not in ['yes', 'no', 'true', 'false']:
                    return value

        # Try type-based naming
        type_fields = ['amenity', 'tourism', 'leisure', 'shop', 'building']
        for field in type_fields:
            if field in properties and properties[field]:
                value = str(properties[field]).strip()
                if value and value.lower() not in ['yes', 'no', 'true', 'false']:
                    # Clean up the type name
                    cleaned = value.replace('_', ' ').title()
                    return cleaned

        # Final fallback using OSM ID
        if 'osm_type' in properties and 'osm_id' in properties:
            return f"{properties['osm_type'].title()} {properties['osm_id']}"

        return "Unnamed Landmark"