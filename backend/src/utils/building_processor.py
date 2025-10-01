"""
Building Feature Processor

Utility for processing building features to ensure clean, minimal properties
that don't clutter user designs with generic names and unnecessary metadata.
"""

import logging
from typing import Dict, Any, Optional, List
from src.api.schemas_v2 import DataSourceType

logger = logging.getLogger(__name__)


class BuildingFeatureProcessor:
    """Processor for cleaning and standardizing building feature properties"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define which data sources are building sources
        self.building_sources = {
            DataSourceType.GOOGLE_BUILDINGS,
            DataSourceType.MICROSOFT_BUILDINGS,
            DataSourceType.OSM_BUILDINGS
        }
        
        # Essential properties to preserve for buildings
        self.essential_building_properties = {
            'confidence',
            'full_plus_code', 
            'longitude_latitude',
            'area_in_meters',
            'height',
            'levels',
            'building_type'
        }
    
    def is_building_source(self, source_type: DataSourceType) -> bool:
        """Check if the source type is a building data source"""
        return source_type in self.building_sources
    
    def process_building_feature(self, feature_dict: Dict[str, Any], source_type: DataSourceType) -> Dict[str, Any]:
        """
        Process a building feature to ensure clean, minimal properties.
        
        Args:
            feature_dict: GeoJSON feature dictionary
            source_type: The data source type
            
        Returns:
            Processed feature with clean properties
        """
        
        if not self.is_building_source(source_type):
            # Not a building source, return as-is
            return feature_dict
        
        try:
            # Ensure properties exist
            if 'properties' not in feature_dict:
                feature_dict['properties'] = {}
            
            properties = feature_dict['properties']
            
            # Create clean properties dictionary
            clean_properties = self._create_clean_building_properties(properties, source_type)
            
            # Replace the properties with clean ones
            feature_dict['properties'] = clean_properties
            
            self.logger.debug(f"Processed {source_type.value} building feature with clean properties")
            
            return feature_dict
            
        except Exception as e:
            self.logger.error(f"Failed to process building feature from {source_type.value}: {e}")
            # Return original feature if processing fails
            return feature_dict
    
    def _create_clean_building_properties(self, original_properties: Dict[str, Any], source_type: DataSourceType) -> Dict[str, Any]:
        """
        Create clean building properties with only essential data.
        
        Args:
            original_properties: Original feature properties
            source_type: The data source type
            
        Returns:
            Clean properties dictionary
        """
        
        clean_properties = {
            # Always set Name to empty string for buildings
            "Name": ""
        }
        
        # Extract and preserve essential properties
        for prop_name in self.essential_building_properties:
            if prop_name in original_properties and original_properties[prop_name] is not None:
                value = original_properties[prop_name]
                
                # Clean up the value if needed
                clean_value = self._clean_property_value(prop_name, value)
                if clean_value is not None:
                    clean_properties[prop_name] = clean_value
        
        # Handle special cases for different building sources
        if source_type == DataSourceType.GOOGLE_BUILDINGS:
            clean_properties = self._process_google_buildings_properties(original_properties, clean_properties)
        elif source_type == DataSourceType.MICROSOFT_BUILDINGS:
            clean_properties = self._process_microsoft_buildings_properties(original_properties, clean_properties)
        elif source_type == DataSourceType.OSM_BUILDINGS:
            clean_properties = self._process_osm_buildings_properties(original_properties, clean_properties)
        
        return clean_properties
    
    def _clean_property_value(self, prop_name: str, value: Any) -> Any:
        """
        Clean a property value to ensure it's in the correct format.
        
        Args:
            prop_name: Property name
            value: Property value
            
        Returns:
            Cleaned property value or None if invalid
        """
        
        try:
            if prop_name == 'confidence':
                # Ensure confidence is a float between 0 and 1
                if isinstance(value, (int, float)):
                    conf_val = float(value)
                    if 0 <= conf_val <= 1:
                        return round(conf_val, 4)  # Round to 4 decimal places
                return None
            
            elif prop_name == 'area_in_meters':
                # Ensure area is a positive number
                if isinstance(value, (int, float)):
                    area_val = float(value)
                    if area_val > 0:
                        return round(area_val, 2)  # Round to 2 decimal places
                return None
            
            elif prop_name in ['height', 'levels']:
                # Ensure height/levels are positive numbers
                if isinstance(value, (int, float)):
                    num_val = float(value)
                    if num_val > 0:
                        return num_val
                return None
            
            elif prop_name in ['full_plus_code', 'longitude_latitude', 'building_type']:
                # String properties - clean and validate
                if isinstance(value, str):
                    cleaned = value.strip()
                    return cleaned if cleaned else None
                elif value is not None:
                    # Convert to string if not None
                    return str(value).strip()
                return None
            
            else:
                # For other properties, return as-is if not None
                return value if value is not None else None
                
        except Exception as e:
            self.logger.warning(f"Failed to clean property {prop_name} with value {value}: {e}")
            return None
    
    def _process_google_buildings_properties(self, original: Dict[str, Any], clean: Dict[str, Any]) -> Dict[str, Any]:
        """Process Google Buildings specific properties"""
        
        # Google Buildings often have longitude_latitude as a complex object
        if 'longitude_latitude' in original:
            lon_lat = original['longitude_latitude']
            if isinstance(lon_lat, dict) and 'coordinates' in lon_lat:
                # Extract coordinates from the Point geometry
                coords = lon_lat['coordinates']
                if isinstance(coords, list) and len(coords) >= 2:
                    clean['longitude_latitude'] = f"{coords[1]},{coords[0]}"  # lat,lon format
            elif isinstance(lon_lat, str):
                clean['longitude_latitude'] = lon_lat
        
        return clean
    
    def _process_microsoft_buildings_properties(self, original: Dict[str, Any], clean: Dict[str, Any]) -> Dict[str, Any]:
        """Process Microsoft Buildings specific properties"""
        
        # Microsoft Buildings may have different property names
        # Add any Microsoft-specific processing here
        
        return clean
    
    def _process_osm_buildings_properties(self, original: Dict[str, Any], clean: Dict[str, Any]) -> Dict[str, Any]:
        """Process OSM Buildings specific properties"""
        
        # For OSM buildings, we might want to preserve building type
        if 'building' in original and original['building'] not in ['yes', 'true', '1']:
            clean['building_type'] = str(original['building'])
        
        return clean
    
    def process_feature_collection(self, feature_collection: Dict[str, Any], source_type: DataSourceType) -> Dict[str, Any]:
        """
        Process all features in a feature collection.
        
        Args:
            feature_collection: GeoJSON FeatureCollection
            source_type: The data source type
            
        Returns:
            Processed FeatureCollection
        """
        
        if not self.is_building_source(source_type):
            return feature_collection
        
        try:
            if 'features' in feature_collection and isinstance(feature_collection['features'], list):
                processed_features = []
                
                for feature in feature_collection['features']:
                    if isinstance(feature, dict):
                        processed_feature = self.process_building_feature(feature, source_type)
                        processed_features.append(processed_feature)
                    else:
                        processed_features.append(feature)
                
                feature_collection['features'] = processed_features
                
                self.logger.debug(f"Processed {len(processed_features)} {source_type.value} building features")
            
            return feature_collection
            
        except Exception as e:
            self.logger.error(f"Failed to process feature collection from {source_type.value}: {e}")
            return feature_collection


# Global instance
building_processor = BuildingFeatureProcessor()
