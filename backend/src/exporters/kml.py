"""
KML/KMZ format exporter for Google Earth
"""

import os
import zipfile
from typing import Dict, Any, Optional, List
import logging

import simplekml

from src.exporters.base import BaseExporter
from src.api.api_schemas import ExtractFeaturesResponse, DataSourceType, ExportFormat
from src.utils.exceptions import ExportError

logger = logging.getLogger(__name__)


class KMLExporter(BaseExporter):
    """Exporter for KML/KMZ format compatible with Google Earth"""
    
    def __init__(self, create_kmz: bool = False):
        super().__init__(ExportFormat.KMZ if create_kmz else ExportFormat.KML)
        self.create_kmz = create_kmz
        
        # Color scheme for different data sources
        self.source_colors = {
            DataSourceType.MICROSOFT_BUILDINGS: simplekml.Color.red,
            DataSourceType.GOOGLE_BUILDINGS: simplekml.Color.cyan,
            DataSourceType.OSM_BUILDINGS: simplekml.Color.blue,
            DataSourceType.OSM_ROADS: simplekml.Color.orange,
            DataSourceType.OSM_RAILWAYS: simplekml.Color.green,
            DataSourceType.OSM_LANDMARKS: simplekml.Color.yellow,
            DataSourceType.OSM_NATURAL: simplekml.Color.lightgreen,
        }
    
    async def export(
        self,
        response_data: ExtractFeaturesResponse,
        output_path: str,
        sources: Optional[List[DataSourceType]] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export data to KML/KMZ format with folder organization by data source.
        """
        
        try:
            self.ensure_output_directory(output_path)
            
            # Create KML document
            kml = simplekml.Kml()
            kml.document.name = f"Atlas Geospatial Data - Job {response_data.job_id}"
            kml.document.description = (
                f"Extracted geospatial features from {response_data.successful_sources} data sources. "
                f"Processing time: {response_data.processing_time:.2f} seconds. "
                f"Total features: {response_data.total_features}."
            )
            
            # Filter sources if specified
            filtered_results = self.filter_sources(response_data, sources)
            
            # Create folders for each data source
            for source_type, result in filtered_results.items():
                if not result.geojson or not result.geojson.features:
                    continue
                
                # Create folder for this source
                source_folder = kml.newfolder(name=self._get_source_display_name(source_type))
                source_folder.description = (
                    f"Source: {source_type.value}\n"
                    f"Status: {result.status.value}\n"
                    f"Features: {result.stats.count}\n"
                    f"Processing time: {result.stats.processing_time:.2f}s"
                )
                
                if result.error_message:
                    source_folder.description += f"\nError: {result.error_message}"
                
                # Add features to folder
                await self._add_features_to_folder(source_folder, result, source_type)
            
            # Add metadata if requested
            if include_metadata:
                await self._add_metadata_folder(kml, response_data, list(filtered_results.keys()))
            
            # Save KML
            if self.create_kmz:
                # Save as KMZ (compressed)
                kml.savekmz(output_path)
            else:
                # Save as KML
                kml.save(output_path)
            
            self.logger.info(f"Exported to {self.export_format.value.upper()}: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"KML export failed: {str(e)}")
            raise ExportError(self.export_format.value, str(e))
    
    async def _add_features_to_folder(self, folder, result, source_type: DataSourceType):
        """Add features from a data source to a KML folder"""
        
        try:
            source_color = self.source_colors.get(source_type, simplekml.Color.white)
            
            for feature in result.geojson.features:
                if not feature.geometry:
                    continue
                
                # Get feature properties
                properties = feature.properties or {}
                feature_name = self._get_feature_name(properties, source_type)
                # Force empty descriptions for placemarks to prevent layer proliferation in CAD tools
                feature_description = ""
                
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
                            description=""
                        )
                        exterior_coords = polygon_coords[0]
                        placemark.outerboundaryis = [(coord[0], coord[1]) for coord in exterior_coords]
                        
                        placemark.style.polystyle.color = simplekml.Color.changealphaint(100, source_color)
                        placemark.style.linestyle.color = source_color
                        placemark.style.linestyle.width = 1
                
        except Exception as e:
            self.logger.warning(f"Failed to add some features from {source_type.value}: {str(e)}")
    
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

        # For OSM landmarks, use the OSM name extractor for consistent naming
        if source_type == DataSourceType.OSM_LANDMARKS:
            try:
                from src.utils.osm_name_extractor import osm_name_extractor
                meaningful_name = osm_name_extractor.extract_name_from_properties(properties)

                # Don't use generic fallbacks from the name extractor
                if meaningful_name and not meaningful_name.startswith('Node ') and not meaningful_name.startswith('Way ') and meaningful_name != "Unnamed Feature":
                    return meaningful_name

            except Exception as e:
                self.logger.warning(f"Failed to use OSM name extractor: {e}")

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
        """Create HTML description for a feature"""

        description_parts = [f"<b>Source:</b> {self._get_source_display_name(source_type)}<br/>"]

        # For building sources, only show essential properties
        from src.utils.building_processor import building_processor
        if building_processor.is_building_source(source_type):
            # Only show essential building properties
            building_fields = ['confidence', 'full_plus_code', 'area_in_meters', 'longitude_latitude', 'height', 'levels', 'building_type']

            for field in building_fields:
                if field in properties and properties[field] is not None:
                    value = properties[field]
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    description_parts.append(f"<b>{field.replace('_', ' ').title()}:</b> {value}<br/>")
        else:
            # For non-building sources, add relevant properties
            important_fields = [
                'name', 'highway', 'building', 'amenity', 'landuse', 'natural',
                'surface', 'lanes', 'maxspeed', 'levels', 'height', 'confidence'
            ]

            for field in important_fields:
                if field in properties and properties[field] is not None:
                    value = properties[field]
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    description_parts.append(f"<b>{field.title()}:</b> {value}<br/>")

        # Add feature ID if available (for non-buildings)
        if not building_processor.is_building_source(source_type) and 'id' in properties:
            description_parts.append(f"<b>ID:</b> {properties['id']}<br/>")

        return ''.join(description_parts)
    
    async def _add_metadata_folder(self, kml, response_data: ExtractFeaturesResponse, include_sources: List[DataSourceType]):
        """Add metadata folder to KML"""
        
        try:
            metadata_folder = kml.newfolder(name="Processing Metadata")
            
            # Create metadata placemark
            metadata_point = metadata_folder.newpoint(name="Job Information")
            
            # Use center of AOI if available, otherwise use a default location
            metadata_point.coords = [(0, 0)]  # You could calculate AOI centroid here
            
            metadata_description = f"""
            <b>Job ID:</b> {response_data.job_id}<br/>
            <b>Processing Time:</b> {response_data.processing_time:.2f} seconds<br/>
            <b>Total Features:</b> {response_data.total_features}<br/>
            <b>Successful Sources:</b> {response_data.successful_sources}<br/>
            <b>Failed Sources:</b> {response_data.failed_sources}<br/>
            <b>Status:</b> {response_data.status.value}<br/>
            <b>Sources Included:</b> {', '.join(source.value for source in include_sources)}<br/>
            <b>Atlas Version:</b> 1.0.0<br/>
            """
            
            metadata_point.description = metadata_description
            metadata_point.style.iconstyle.color = simplekml.Color.white
            metadata_point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/info-i.png'
            
        except Exception as e:
            self.logger.warning(f"Failed to add metadata folder: {str(e)}")