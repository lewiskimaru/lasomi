"""
Format conversion utilities for geospatial data
Handles conversion between GeoJSON, KML, and KMZ formats with data integrity preservation
"""

import os
import json
import tempfile
import zipfile
from typing import Dict, Any, Union, Optional
import logging

import simplekml
from geojson_pydantic import FeatureCollection

from src.api.api_schemas import ExtractFeaturesResponse, DataSourceType, ExportFormat
from src.utils.exceptions import ExportError

logger = logging.getLogger(__name__)


class FormatConverter:
    """Utility class for converting between geospatial data formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Color scheme for different data sources (consistent with KML exporter)
        self.source_colors = {
            DataSourceType.MICROSOFT_BUILDINGS: simplekml.Color.red,
            DataSourceType.GOOGLE_BUILDINGS: simplekml.Color.cyan,
            DataSourceType.OSM_BUILDINGS: simplekml.Color.blue,
            DataSourceType.OSM_ROADS: simplekml.Color.orange,
            DataSourceType.OSM_RAILWAYS: simplekml.Color.green,
            DataSourceType.OSM_LANDMARKS: simplekml.Color.yellow,
            DataSourceType.OSM_NATURAL: simplekml.Color.lightgreen,
        }
    
    async def convert_response_to_format(
        self,
        response_data: ExtractFeaturesResponse,
        target_format: ExportFormat,
        include_metadata: bool = True
    ) -> Union[Dict[str, Any], str]:
        """
        Convert ExtractFeaturesResponse to specified format.
        
        Args:
            response_data: The response data to convert
            target_format: Target format (GEOJSON, KML, or KMZ)
            include_metadata: Whether to include processing metadata
            
        Returns:
            Converted data - Dict for GeoJSON, string for KML/KMZ
        """
        
        try:
            if target_format == ExportFormat.GEOJSON:
                return await self._convert_to_geojson(response_data, include_metadata)
            elif target_format == ExportFormat.KML:
                return await self._convert_to_kml(response_data, include_metadata, create_kmz=False)
            elif target_format == ExportFormat.KMZ:
                return await self._convert_to_kml(response_data, include_metadata, create_kmz=True)
            else:
                raise ExportError(target_format.value, f"Conversion to {target_format.value} not supported")
                
        except Exception as e:
            self.logger.error(f"Format conversion to {target_format.value} failed: {str(e)}")
            raise ExportError(target_format.value, str(e))
    
    async def _convert_to_geojson(
        self,
        response_data: ExtractFeaturesResponse,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Convert response to GeoJSON format"""
        
        try:
            # Create the main GeoJSON structure
            geojson_data = {
                "type": "FeatureCollection",
                "features": []
            }
            
            # Add metadata if requested
            if include_metadata:
                geojson_data["atlas_metadata"] = {
                    "job_id": str(response_data.job_id),
                    "export_format": "geojson",
                    "processing_time": response_data.processing_time,
                    "total_features": response_data.total_features,
                    "successful_sources": response_data.successful_sources,
                    "failed_sources": response_data.failed_sources,
                    "requested_sources": [source.value for source in response_data.requested_sources],
                    "atlas_version": "1.0.0"
                }
            
            # Combine features from all sources with source attribution
            for source_type, result in response_data.results.items():
                if result.geojson and result.geojson.features:
                    for feature in result.geojson.features:
                        # Create a copy of feature and add source attribution
                        feature_dict = feature.dict() if hasattr(feature, 'dict') else feature
                        
                        if not feature_dict.get('properties'):
                            feature_dict['properties'] = {}
                        
                        feature_dict['properties']['atlas_source'] = source_type.value
                        feature_dict['properties']['atlas_source_status'] = result.status.value
                        
                        geojson_data['features'].append(feature_dict)
            
            return geojson_data
            
        except Exception as e:
            raise ExportError("geojson", f"GeoJSON conversion failed: {str(e)}")
    
    async def _convert_to_kml(
        self,
        response_data: ExtractFeaturesResponse,
        include_metadata: bool = True,
        create_kmz: bool = False
    ) -> str:
        """Convert response to KML/KMZ format"""
        
        try:
            # Create KML document
            kml = simplekml.Kml()
            kml.document.name = f"Atlas Geospatial Data - Job {response_data.job_id}"
            kml.document.description = (
                f"Extracted geospatial features from {response_data.successful_sources} data sources. "
                f"Processing time: {response_data.processing_time:.2f} seconds. "
                f"Total features: {response_data.total_features}."
            )
            
            # Create folders for each data source
            for source_type, result in response_data.results.items():
                if not result.geojson or not result.geojson.features:
                    continue
                
                # Create folder for this source
                source_folder = kml.newfolder(name=self._get_source_display_name(source_type))
                source_folder.description = (
                    f"Source: {source_type.value}\\n"
                    f"Status: {result.status.value}\\n"
                    f"Features: {result.stats.count}\\n"
                    f"Processing time: {result.stats.processing_time:.2f}s"
                )
                
                if result.error_message:
                    source_folder.description += f"\\nError: {result.error_message}"
                
                # Add features to folder
                await self._add_features_to_kml_folder(source_folder, result, source_type)
            
            # Add metadata if requested
            if include_metadata:
                await self._add_metadata_to_kml(kml, response_data)
            
            # Generate KML/KMZ content
            if create_kmz:
                # Create temporary file for KMZ
                with tempfile.NamedTemporaryFile(suffix='.kmz', delete=False) as temp_file:
                    kml.savekmz(temp_file.name)
                    
                    # Read the KMZ content
                    with open(temp_file.name, 'rb') as f:
                        kmz_content = f.read()
                    
                    # Clean up temp file
                    os.unlink(temp_file.name)
                    
                    # Return base64 encoded content for API response
                    import base64
                    return base64.b64encode(kmz_content).decode('utf-8')
            else:
                # Return KML as string
                return kml.kml()
                
        except Exception as e:
            format_name = "kmz" if create_kmz else "kml"
            raise ExportError(format_name, f"KML conversion failed: {str(e)}")
    
    async def _add_features_to_kml_folder(self, folder, result, source_type: DataSourceType):
        """Add features from a data source to a KML folder"""
        
        try:
            source_color = self.source_colors.get(source_type, simplekml.Color.white)
            
            for feature in result.geojson.features:
                if not feature.geometry:
                    continue
                
                # Get feature properties
                properties = feature.properties or {}
                feature_name = self._get_feature_name(properties, source_type)
                feature_description = self._create_feature_description(properties, source_type)
                
                # Add feature based on geometry type
                geometry = feature.geometry
                
                if geometry.type == "Point":
                    placemark = folder.newpoint(name=feature_name, description=feature_description)
                    coords = geometry.coordinates
                    placemark.coords = [(coords[0], coords[1])]
                    placemark.style.iconstyle.color = source_color
                    placemark.style.iconstyle.scale = 0.8
                
                elif geometry.type == "LineString":
                    placemark = folder.newlinestring(name=feature_name, description=feature_description)
                    placemark.coords = [(coord[0], coord[1]) for coord in geometry.coordinates]
                    placemark.style.linestyle.color = source_color
                    placemark.style.linestyle.width = 2
                
                elif geometry.type == "Polygon":
                    placemark = folder.newpolygon(name=feature_name, description=feature_description)
                    exterior_coords = geometry.coordinates[0]
                    placemark.outerboundaryis = [(coord[0], coord[1]) for coord in exterior_coords]
                    
                    # Handle holes if present
                    if len(geometry.coordinates) > 1:
                        for hole in geometry.coordinates[1:]:
                            placemark.innerboundaryis = [(coord[0], coord[1]) for coord in hole]
                    
                    placemark.style.polystyle.color = simplekml.Color.changealphaint(100, source_color)
                    placemark.style.linestyle.color = source_color
                    placemark.style.linestyle.width = 1
                
                elif geometry.type == "MultiPolygon":
                    # Handle MultiPolygon by creating multiple placemarks
                    for i, polygon_coords in enumerate(geometry.coordinates):
                        placemark = folder.newpolygon(
                            name=f"{feature_name} (Part {i+1})",
                            description=feature_description
                        )
                        exterior_coords = polygon_coords[0]
                        placemark.outerboundaryis = [(coord[0], coord[1]) for coord in exterior_coords]
                        
                        placemark.style.polystyle.color = simplekml.Color.changealphaint(100, source_color)
                        placemark.style.linestyle.color = source_color
                        placemark.style.linestyle.width = 1
                
        except Exception as e:
            self.logger.warning(f"Failed to add some features from {source_type.value}: {str(e)}")
    
    async def _add_metadata_to_kml(self, kml, response_data: ExtractFeaturesResponse):
        """Add metadata folder to KML"""
        
        try:
            metadata_folder = kml.newfolder(name="Atlas Metadata")
            
            # Create metadata placemark
            metadata_placemark = metadata_folder.newplacemark(name="Processing Information")
            metadata_placemark.description = (
                f"Job ID: {response_data.job_id}\\n"
                f"Processing Time: {response_data.processing_time:.2f} seconds\\n"
                f"Total Features: {response_data.total_features}\\n"
                f"Successful Sources: {response_data.successful_sources}\\n"
                f"Failed Sources: {response_data.failed_sources}\\n"
                f"Requested Sources: {', '.join([s.value for s in response_data.requested_sources])}"
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to add metadata to KML: {str(e)}")
    
    def _get_source_display_name(self, source_type: DataSourceType) -> str:
        """Get display name for data source"""
        display_names = {
            DataSourceType.MICROSOFT_BUILDINGS: "Microsoft Building Footprints",
            DataSourceType.GOOGLE_BUILDINGS: "Google Open Buildings",
            DataSourceType.OSM_BUILDINGS: "OpenStreetMap Buildings",
            DataSourceType.OSM_ROADS: "OpenStreetMap Roads",
            DataSourceType.OSM_RAILWAYS: "OpenStreetMap Railways",
            DataSourceType.OSM_LANDMARKS: "OpenStreetMap Landmarks",
            DataSourceType.OSM_NATURAL: "OpenStreetMap Natural Features",
        }
        return display_names.get(source_type, source_type.value.replace('_', ' ').title())
    
    def _get_feature_name(self, properties: dict, source_type: DataSourceType) -> str:
        """Generate a name for a feature based on its properties"""

        # For building sources, respect the clean Name property (empty string for buildings)
        from src.utils.building_processor import building_processor
        if building_processor.is_building_source(source_type):
            # Building features should have Name set to empty string for clean exports
            if 'Name' in properties:
                name_value = str(properties['Name']).strip()
                # Return the Name as-is (empty string for clean buildings)
                return name_value if name_value else "Building"
            else:
                # If no Name property, return generic building name
                return "Building"

        # Try common name fields
        name_fields = ['name', 'Name', 'NAME', 'highway', 'building', 'amenity', 'landuse']

        for field in name_fields:
            if field in properties and properties[field]:
                return str(properties[field])

        # Fallback to feature type
        type_names = {
            DataSourceType.MICROSOFT_BUILDINGS: "Building",
            DataSourceType.GOOGLE_BUILDINGS: "Building",
            DataSourceType.OSM_BUILDINGS: "Building",
            DataSourceType.OSM_ROADS: "Road",
            DataSourceType.OSM_RAILWAYS: "Railway",
            DataSourceType.OSM_LANDMARKS: "Landmark",
            DataSourceType.OSM_NATURAL: "Natural Feature",
        }

        return type_names.get(source_type, "Feature")
    
    def _create_feature_description(self, properties: dict, source_type: DataSourceType) -> str:
        """Create HTML description for feature"""
        
        if not properties:
            return f"Source: {source_type.value}"
        
        # Build description from properties
        description_parts = [f"<b>Source:</b> {source_type.value}"]
        
        # Add key properties
        key_properties = ['name', 'highway', 'building', 'amenity', 'landuse', 'area_in_meters', 'confidence']
        
        for prop in key_properties:
            if prop in properties and properties[prop] is not None:
                value = properties[prop]
                if isinstance(value, float):
                    value = f"{value:.2f}"
                description_parts.append(f"<b>{prop.replace('_', ' ').title()}:</b> {value}")
        
        return "<br/>".join(description_parts)
    
    def validate_conversion_result(self, original_data: Any, converted_data: Any, target_format: ExportFormat) -> bool:
        """
        Validate that conversion preserved essential data integrity.
        
        Args:
            original_data: Original ExtractFeaturesResponse
            converted_data: Converted data
            target_format: Target format
            
        Returns:
            True if validation passes, False otherwise
        """
        
        try:
            if target_format == ExportFormat.GEOJSON:
                return self._validate_geojson_conversion(original_data, converted_data)
            elif target_format in [ExportFormat.KML, ExportFormat.KMZ]:
                return self._validate_kml_conversion(original_data, converted_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed for {target_format.value}: {str(e)}")
            return False
    
    def _validate_geojson_conversion(self, original_data: ExtractFeaturesResponse, converted_data: Dict[str, Any]) -> bool:
        """Validate GeoJSON conversion"""
        
        # Check basic structure
        if not isinstance(converted_data, dict) or converted_data.get('type') != 'FeatureCollection':
            return False
        
        # Check feature count
        original_feature_count = sum(result.stats.count for result in original_data.results.values())
        converted_feature_count = len(converted_data.get('features', []))
        
        if original_feature_count != converted_feature_count:
            self.logger.warning(f"Feature count mismatch: {original_feature_count} vs {converted_feature_count}")
            return False
        
        return True
    
    def _validate_kml_conversion(self, original_data: ExtractFeaturesResponse, converted_data: str) -> bool:
        """Validate KML/KMZ conversion"""
        
        # Basic validation - check if it's a string and contains KML elements
        if not isinstance(converted_data, str):
            return False
        
        # Check for basic KML structure
        required_elements = ['<kml', '<Document', '</kml>']
        for element in required_elements:
            if element not in converted_data:
                return False
        
        return True


# Global converter instance
format_converter = FormatConverter()