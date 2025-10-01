"""
OSM Name Extraction Utility

Extracts meaningful names from OSM landmark features based on their properties
with intelligent fallback hierarchy.
"""

import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OSMNameExtractor:
    """Extracts meaningful names from OSM features with intelligent fallbacks"""
    
    def __init__(self):
        # Priority order for name extraction
        self.name_priority = [
            'name',
            'name:en', 
            'brand',
            'operator',
            'amenity',
            'tourism',
            'leisure',
            'shop',
            'building',
            'highway',
            'natural',
            'landuse'
        ]
        
        # Amenity type mappings for better display names
        self.amenity_display_names = {
            'school': 'School',
            'restaurant': 'Restaurant', 
            'guest_house': 'Guest House',
            'studio': 'Studio',
            'kindergarten': 'Kindergarten',
            'hospital': 'Hospital',
            'pharmacy': 'Pharmacy',
            'bank': 'Bank',
            'atm': 'ATM',
            'fuel': 'Gas Station',
            'parking': 'Parking',
            'place_of_worship': 'Place of Worship',
            'library': 'Library',
            'post_office': 'Post Office',
            'police': 'Police Station',
            'fire_station': 'Fire Station',
            'cafe': 'Cafe',
            'bar': 'Bar',
            'pub': 'Pub',
            'fast_food': 'Fast Food',
            'cinema': 'Cinema',
            'theatre': 'Theatre',
            'museum': 'Museum',
            'university': 'University',
            'college': 'College'
        }
        
        # Tourism type mappings
        self.tourism_display_names = {
            'hotel': 'Hotel',
            'guest_house': 'Guest House',
            'hostel': 'Hostel',
            'motel': 'Motel',
            'attraction': 'Tourist Attraction',
            'viewpoint': 'Viewpoint',
            'museum': 'Museum',
            'gallery': 'Gallery',
            'information': 'Information Center'
        }
        
        # Leisure type mappings
        self.leisure_display_names = {
            'park': 'Park',
            'playground': 'Playground',
            'sports_centre': 'Sports Centre',
            'swimming_pool': 'Swimming Pool',
            'fitness_centre': 'Fitness Centre',
            'golf_course': 'Golf Course',
            'stadium': 'Stadium',
            'pitch': 'Sports Pitch',
            'garden': 'Garden',
            'nature_reserve': 'Nature Reserve'
        }
        
        # Shop type mappings
        self.shop_display_names = {
            'supermarket': 'Supermarket',
            'convenience': 'Convenience Store',
            'clothes': 'Clothing Store',
            'electronics': 'Electronics Store',
            'bakery': 'Bakery',
            'butcher': 'Butcher',
            'pharmacy': 'Pharmacy',
            'bookshop': 'Bookstore',
            'hairdresser': 'Hair Salon',
            'beauty': 'Beauty Salon',
            'car_repair': 'Car Repair Shop',
            'bicycle': 'Bicycle Shop'
        }
    
    def extract_name_from_properties(self, properties: Dict[str, Any]) -> str:
        """
        Extract meaningful name from OSM feature properties.

        Args:
            properties: Feature properties dictionary

        Returns:
            Meaningful name string (never None or empty)
        """

        try:
            if not properties or not isinstance(properties, dict):
                return "Unnamed Feature"

            # First, try to extract from description field if it exists (for export-time processing)
            if 'description' in properties and isinstance(properties['description'], str):
                extracted_name = self._extract_from_description(properties['description'])
                if extracted_name and isinstance(extracted_name, str) and extracted_name.strip():
                    return extracted_name.strip()

            # Then try direct property access (for extraction-time processing)
            for field in self.name_priority:
                if field in properties and properties[field]:
                    try:
                        value = str(properties[field]).strip()
                        if value and value.lower() not in ['yes', 'no', 'true', 'false']:
                            # For type fields (amenity, tourism, etc.), try to get a better display name
                            if field in ['amenity', 'tourism', 'leisure', 'shop']:
                                display_name = self._get_type_display_name(field, value)
                                if display_name and isinstance(display_name, str) and display_name.strip():
                                    return display_name.strip()

                            cleaned_name = self._clean_name(value)
                            if cleaned_name and isinstance(cleaned_name, str) and cleaned_name.strip():
                                return cleaned_name.strip()
                    except Exception as e:
                        logger.warning(f"Error processing field '{field}': {e}")
                        continue

            # Fallback to OSM type + ID if available
            if 'osm_type' in properties and 'osm_id' in properties:
                try:
                    osm_type = str(properties['osm_type']).strip().title()
                    osm_id = str(properties['osm_id']).strip()
                    if osm_type and osm_id:
                        fallback_name = f"{osm_type} {osm_id}"
                        return fallback_name
                except Exception as e:
                    logger.warning(f"Error creating OSM fallback name: {e}")

            # Final fallback
            return "Unnamed Feature"

        except Exception as e:
            logger.error(f"Critical error in extract_name_from_properties: {e}")
            return "Unnamed Feature"
    
    def _extract_from_description(self, description: str) -> Optional[str]:
        """
        Extract name from OSM description string.
        
        The description contains OSM metadata in format:
        "osm_type: node\nosm_id: 5327988317\namenity: school\nname: Imani Montessori School"
        """
        
        try:
            # Parse the description to extract key-value pairs
            properties = {}
            lines = description.split('\n')
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    properties[key.strip()] = value.strip()
            
            # Try to extract name using priority order
            for field in self.name_priority:
                if field in properties and properties[field]:
                    value = properties[field].strip()
                    if value and value.lower() not in ['yes', 'no', 'true', 'false']:
                        # If it's a type field, try to get a better display name
                        if field in ['amenity', 'tourism', 'leisure', 'shop']:
                            display_name = self._get_type_display_name(field, value)
                            if display_name:
                                return display_name
                        return self._clean_name(value)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract name from description: {e}")
            return None
    
    def _get_type_display_name(self, type_field: str, type_value: str) -> Optional[str]:
        """Get display name for amenity/tourism/leisure/shop types"""
        
        type_value = type_value.lower()
        
        if type_field == 'amenity':
            return self.amenity_display_names.get(type_value)
        elif type_field == 'tourism':
            return self.tourism_display_names.get(type_value)
        elif type_field == 'leisure':
            return self.leisure_display_names.get(type_value)
        elif type_field == 'shop':
            return self.shop_display_names.get(type_value)
        
        # Fallback: clean up the type value
        return self._clean_name(type_value)
    
    def _clean_name(self, name: str) -> str:
        """Clean and standardize a name string"""

        try:
            if not name or not isinstance(name, str):
                return ""

            # Remove underscores and replace with spaces
            name = name.replace('_', ' ')

            # Title case
            name = name.title()

            # Fix common abbreviations
            replacements = {
                'Atm': 'ATM',
                'Gps': 'GPS',
                'Wifi': 'WiFi',
                'Tv': 'TV',
                'Usa': 'USA',
                'Uk': 'UK',
                'Usd': 'USD',
                'Id': 'ID'
            }

            for old, new in replacements.items():
                try:
                    name = re.sub(r'\b' + old + r'\b', new, name)
                except Exception:
                    continue

            return name.strip()

        except Exception as e:
            logger.warning(f"Error cleaning name '{name}': {e}")
            return str(name) if name else ""
    
    def update_feature_properties(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update feature properties with meaningful name.

        Args:
            feature_dict: GeoJSON feature dictionary

        Returns:
            Updated feature dictionary with meaningful Name property
        """

        if 'properties' not in feature_dict:
            feature_dict['properties'] = {}

        properties = feature_dict['properties']

        # Extract meaningful name
        meaningful_name = self.extract_name_from_properties(properties)

        # Ensure we have a valid name
        if not meaningful_name or not isinstance(meaningful_name, str) or meaningful_name.strip() == '':
            logger.warning(f"Empty meaningful name extracted, using fallback")
            meaningful_name = "Unnamed Feature"

        # Update the Name property
        properties['Name'] = meaningful_name.strip()

        return feature_dict


# Global instance for easy access
osm_name_extractor = OSMNameExtractor()
