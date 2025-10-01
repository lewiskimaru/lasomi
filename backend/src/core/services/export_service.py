"""
Export service with clean separation of concerns
"""

import asyncio
import os
import tempfile
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
from pathlib import Path

from src.core.interfaces import IExportService
from src.api.schemas_v2 import RawDataResponse, ExportFormat, DataSourceType
from src.utils.exceptions import ExportError
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class RawDataExportService(IExportService):
    """
    Clean export service focused on raw data formats.
    Single responsibility: convert raw data to various export formats.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self._temp_dir = Path(self.settings.export_temp_dir)
        self._temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def export_data(
        self, 
        result: RawDataResponse, 
        format: str, 
        sources: Optional[List[DataSourceType]] = None
    ) -> bytes:
        """
        Export raw data in the specified format.
        
        Args:
            result: Raw data response to export
            format: Target export format (geojson, kml, kmz, csv)
            sources: Optional list of sources to include
            
        Returns:
            Exported data as bytes
        """
        
        try:
            format_enum = ExportFormat(format.lower())
            
            if format_enum == ExportFormat.GEOJSON:
                return await self._export_geojson(result, sources)
            elif format_enum == ExportFormat.KML:
                return await self._export_kml(result, sources, compressed=False)
            elif format_enum == ExportFormat.KMZ:
                return await self._export_kml(result, sources, compressed=True)
            elif format_enum == ExportFormat.CSV:
                return await self._export_csv(result, sources)
            else:
                raise ExportError("export", f"Unsupported export format: {format}")
                
        except ValueError:
            raise ExportError("export", f"Invalid export format: {format}")
        except Exception as e:
            self.logger.error(f"Export failed for format {format}: {str(e)}")
            raise ExportError("export", f"Export failed: {str(e)}")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return ["geojson", "kml", "kmz", "csv"]
    
    async def _export_geojson(
        self, 
        result: RawDataResponse, 
        sources: Optional[List[DataSourceType]] = None
    ) -> bytes:
        """Export as GeoJSON format"""
        
        try:
            # Create combined GeoJSON structure
            combined_features = []
            
            # Filter sources if specified
            target_sources = sources if sources else list(result.results.keys())
            
            for source_type in target_sources:
                if source_type in result.results:
                    source_result = result.results[source_type]
                    if source_result.data and source_result.data.features:
                        for feature in source_result.data.features:
                            # Convert Pydantic Feature object to dictionary
                            if hasattr(feature, 'dict'):
                                # This is a Pydantic model, convert to dict
                                feature_dict = feature.dict()
                            else:
                                # This is already a dictionary
                                feature_dict = feature

                            # Add source attribution
                            if not feature_dict.get('properties'):
                                feature_dict['properties'] = {}
                            # Strip any 'description' property to prevent downstream CAD layer proliferation
                            try:
                                if 'description' in feature_dict['properties']:
                                    feature_dict['properties'].pop('description', None)
                            except Exception:
                                pass
                            feature_dict['properties']["atlas_source"] = source_type.value
                            feature_dict['properties']["atlas_status"] = source_result.status.value
                            combined_features.append(feature_dict)
            
            # Create final GeoJSON structure
            geojson_data = {
                "type": "FeatureCollection",
                "features": combined_features,
                "metadata": {
                    "job_id": str(result.job_id),
                    "processing_time": result.processing_time,
                    "total_features": result.total_features,
                    "successful_sources": result.successful_sources,
                    "sources_included": [s.value for s in target_sources],
                    "export_format": "geojson"
                }
            }
            
            # Convert to JSON bytes
            import json
            return json.dumps(geojson_data, separators=(',', ':')).encode('utf-8')
            
        except Exception as e:
            raise ExportError("geojson", f"GeoJSON export failed: {str(e)}")
    
    async def _export_kml(
        self, 
        result: RawDataResponse, 
        sources: Optional[List[DataSourceType]] = None,
        compressed: bool = False
    ) -> bytes:
        """Export as KML/KMZ format"""
        
        try:
            import simplekml
            import zipfile
            from shapely.geometry import shape
            
            # Create KML document
            kml = simplekml.Kml()
            kml.document.name = f"Atlas Export - Job {result.job_id}"
            kml.document.description = f"Raw geospatial data extracted in {result.processing_time:.2f}s"
            
            # Define colors for different sources
            source_colors = {
                DataSourceType.MICROSOFT_BUILDINGS: simplekml.Color.red,
                DataSourceType.GOOGLE_BUILDINGS: simplekml.Color.cyan,
                DataSourceType.OSM_BUILDINGS: simplekml.Color.blue,
                DataSourceType.OSM_ROADS: simplekml.Color.orange,
                DataSourceType.OSM_RAILWAYS: simplekml.Color.green,
                DataSourceType.OSM_LANDMARKS: simplekml.Color.yellow,
                DataSourceType.OSM_NATURAL: simplekml.Color.lightgreen,
            }
            
            # Filter sources if specified
            target_sources = sources if sources else list(result.results.keys())
            
            for source_type in target_sources:
                if source_type in result.results:
                    source_result = result.results[source_type]
                    
                    # Create folder for this source
                    folder = kml.newfolder(name=source_type.value.replace('_', ' ').title())
                    folder.description = f"Status: {source_result.status.value}, Features: {source_result.stats.count}"
                    
                    # Add features
                    if source_result.data and source_result.data.features:
                        for i, feature in enumerate(source_result.data.features):
                            if feature.geometry:
                                # Get meaningful name from properties
                                feature_name = self._get_meaningful_name(feature.properties, source_type, i)
                                
                                # Do not set per-feature descriptions to avoid CAD tools creating layers
                                desc = ""

                                # Set geometry via correct simplekml factories
                                geom = shape(feature.geometry)
                                color = source_colors.get(source_type, simplekml.Color.white)
                                if geom.geom_type == 'Point':
                                    pm = folder.newpoint(name=feature_name, coords=[geom.coords[0]])
                                    if desc:
                                        pm.description = desc

                                    pm.style.iconstyle.color = color
                                elif geom.geom_type == 'LineString':
                                    ls = folder.newlinestring(name=feature_name, coords=list(geom.coords))
                                    if desc:
                                        ls.description = desc

                                    ls.style.linestyle.color = color
                                    ls.style.linestyle.width = 2
                                elif geom.geom_type == 'Polygon':
                                    if hasattr(geom, 'exterior') and geom.exterior:
                                        poly = folder.newpolygon(name=feature_name, outerboundaryis=list(geom.exterior.coords))
                                        if desc:
                                            poly.description = desc

                                        poly.style.linestyle.color = color
                                        poly.style.polystyle.color = color
                                        poly.style.polystyle.fill = 1
                                        poly.style.polystyle.outline = 1
            
            # Generate KML string
            kml_content = kml.kml()
            
            if compressed:
                # Create KMZ (zipped KML)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.kmz') as temp_file:
                    with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as kmz:
                        kmz.writestr('doc.kml', kml_content)
                    
                    temp_file.seek(0)
                    with open(temp_file.name, 'rb') as f:
                        kmz_data = f.read()
                    
                    # Clean up temp file
                    os.unlink(temp_file.name)
                    return kmz_data
            else:
                # Return KML as bytes
                return kml_content.encode('utf-8')
                
        except Exception as e:
            raise ExportError("kml", f"KML/KMZ export failed: {str(e)}")
    
    async def _export_csv(
        self, 
        result: RawDataResponse, 
        sources: Optional[List[DataSourceType]] = None
    ) -> bytes:
        """Export as CSV format with WKT geometry"""
        
        try:
            import csv
            import io
            from shapely.geometry import shape
            
            # Create CSV in memory
            output = io.StringIO()
            
            # Filter sources if specified
            target_sources = sources if sources else list(result.results.keys())
            
            # Collect all features
            all_features = []
            for source_type in target_sources:
                if source_type in result.results:
                    source_result = result.results[source_type]
                    if source_result.data and source_result.data.features:
                        for feature in source_result.data.features:
                            feature_data = {
                                'atlas_source': source_type.value,
                                'atlas_status': source_result.status.value,
                                'geometry_type': feature.geometry.type if feature.geometry else None,
                                'geometry_wkt': self._geometry_to_wkt(feature.geometry) if feature.geometry else None
                            }
                            
                            # Add all properties except 'description'
                            if feature.properties:
                                for key, value in feature.properties.items():
                                    if str(key).lower() == 'description':
                                        continue
                                    clean_key = str(key).replace(' ', '_').replace('-', '_')
                                    feature_data[clean_key] = value
                            
                            all_features.append(feature_data)
            
            if not all_features:
                # Empty CSV
                writer = csv.writer(output)
                writer.writerow(['atlas_source', 'atlas_status', 'message'])
                writer.writerow(['N/A', 'N/A', 'No features found'])
            else:
                # Get all column names and sort them
                all_columns = set()
                for feature in all_features:
                    all_columns.update(feature.keys())
                
                atlas_columns = [col for col in all_columns if col.startswith('atlas_')]
                other_columns = sorted([col for col in all_columns if not col.startswith('atlas_')])
                column_order = atlas_columns + other_columns
                
                # Write CSV
                writer = csv.DictWriter(output, fieldnames=column_order)
                writer.writeheader()
                
                for feature in all_features:
                    row_data = {col: feature.get(col, '') for col in column_order}
                    writer.writerow(row_data)
            
            # Return CSV as bytes
            csv_content = output.getvalue()
            output.close()
            return csv_content.encode('utf-8')
            
        except Exception as e:
            raise ExportError("csv", f"CSV export failed: {str(e)}")
    
    def _get_meaningful_name(self, properties: dict, source_type: DataSourceType, index: int) -> str:
        """Extract meaningful name from feature properties"""

        if not properties:
            return f"{source_type.value}_{index}"

        # For building sources, respect the clean Name property (empty string for buildings)
        from src.utils.building_processor import building_processor
        if building_processor.is_building_source(source_type):
            # Building features should have Name set to empty string for clean exports
            if 'Name' in properties:
                name_value = str(properties['Name']).strip()
                # Return the Name as-is (empty string for clean buildings)
                return name_value
            else:
                # If no Name property, return empty string for buildings
                return ""

        # Check if we have a meaningful name in properties (set during extraction)
        if 'Name' in properties and properties['Name']:
            name_value = str(properties['Name']).strip()
            # Don't use generic names that might have been set as fallbacks
            if name_value and not name_value.startswith(f'{source_type.value}_'):
                return name_value

        # For other sources, try common name fields
        name_fields = ['name', 'Name', 'highway', 'building', 'amenity']
        for field in name_fields:
            if field in properties and properties[field]:
                return str(properties[field])

        # Fallback to generic name
        return f"{source_type.value}_{index}"
    
    def _geometry_to_wkt(self, geometry) -> str:
        """Convert GeoJSON geometry to WKT format"""
        try:
            if not geometry:
                return ""
            
            from shapely.geometry import shape
            geom = shape(geometry)
            return geom.wkt
            
        except Exception as e:
            self.logger.warning(f"Failed to convert geometry to WKT: {str(e)}")
            return f"INVALID_GEOMETRY: {str(e)}"