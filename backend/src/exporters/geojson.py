"""
GeoJSON format exporter
"""

import json
import os
from typing import Dict, Any, Optional, List
import logging

from src.exporters.base import BaseExporter
from src.api.api_schemas import ExtractFeaturesResponse, DataSourceType, ExportFormat
from src.utils.exceptions import ExportError

logger = logging.getLogger(__name__)


class GeoJSONExporter(BaseExporter):
    """Exporter for GeoJSON format"""
    
    def __init__(self):
        super().__init__(ExportFormat.GEOJSON)
    
    async def export(
        self,
        response_data: ExtractFeaturesResponse,
        output_path: str,
        sources: Optional[List[DataSourceType]] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export data to GeoJSON format.
        
        Creates a structured GeoJSON with separate FeatureCollections for each data source.
        """
        
        try:
            self.ensure_output_directory(output_path)
            
            # Filter sources if specified
            filtered_results = self.filter_sources(response_data, sources)
            include_sources = list(filtered_results.keys())
            
            # Create the main GeoJSON structure
            export_data = {
                "type": "FeatureCollection",
                "features": [],
                "atlas_metadata": None
            }
            
            # Add metadata if requested
            if include_metadata:
                export_data["atlas_metadata"] = self.create_metadata(response_data, include_sources)
            
            # Combine features from all sources with source attribution
            for source_type, result in filtered_results.items():
                if result.geojson and result.geojson.features:
                    for feature in result.geojson.features:
                        # Add source attribution to feature properties
                        if not feature.properties:
                            feature.properties = {}

                        # Remove 'description' property entirely to prevent downstream tooling (e.g., AutoCAD) from creating layers per description
                        try:
                            if isinstance(feature.properties, dict) and 'description' in feature.properties:
                                feature.properties.pop('description', None)
                        except Exception:
                            pass

                        feature.properties["atlas_source"] = source_type.value
                        feature.properties["atlas_source_status"] = result.status.value

                        export_data["features"].append(feature.dict())
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(export_data['features'])} features to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"GeoJSON export failed: {str(e)}")
            raise ExportError(self.export_format.value, str(e))
    
    async def export_by_source(
        self,
        response_data: ExtractFeaturesResponse,
        output_dir: str,
        sources: Optional[List[DataSourceType]] = None,
        include_metadata: bool = True
    ) -> Dict[str, str]:
        """
        Export separate GeoJSON files for each data source.
        
        Returns:
            Dictionary mapping source names to file paths
        """
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Filter sources if specified
            filtered_results = self.filter_sources(response_data, sources)
            include_sources = list(filtered_results.keys())
            
            exported_files = {}
            
            for source_type, result in filtered_results.items():
                # Create filename
                source_display_name = self._get_source_display_name(source_type)
                filename = f"{source_display_name}.geojson"
                file_path = os.path.join(output_dir, filename)

                # Create source-specific GeoJSON
                # Clean features by removing 'description' property
                cleaned_features = []
                if result.geojson and result.geojson.features:
                    for feature in result.geojson.features:
                        try:
                            if not feature.properties:
                                feature.properties = {}
                            if isinstance(feature.properties, dict) and 'description' in feature.properties:
                                feature.properties.pop('description', None)
                        except Exception:
                            pass
                        cleaned_features.append(feature)

                source_data = {
                    "type": "FeatureCollection",
                    "features": cleaned_features if cleaned_features else (result.geojson.features if result.geojson else []),
                    "atlas_metadata": None
                }
                
                # Add metadata
                if include_metadata:
                    source_metadata = self.create_metadata(response_data, [source_type])
                    source_metadata.update({
                        "source_type": source_type.value,
                        "source_status": result.status.value,
                        "feature_count": result.stats.count,
                        "processing_time": result.stats.processing_time,
                        "error_message": result.error_message
                    })
                    source_data["atlas_metadata"] = source_metadata
                
                # Write file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(source_data, f, indent=2, ensure_ascii=False)
                
                exported_files[source_type.value] = file_path
                self.logger.info(f"Exported {len(source_data['features'])} features for {source_type.value} to {file_path}")
            
            return exported_files
            
        except Exception as e:
            self.logger.error(f"GeoJSON by-source export failed: {str(e)}")
            raise ExportError(self.export_format.value, str(e))

    def _get_source_display_name(self, source_type: DataSourceType) -> str:
        """Get display name for data source"""
        display_names = {
            DataSourceType.MICROSOFT_BUILDINGS: "Microsoft Building Footprints",
            DataSourceType.GOOGLE_BUILDINGS: "Google Open Buildings",
            DataSourceType.OSM_BUILDINGS: "OpenStreetMap Buildings",
            DataSourceType.OSM_ROADS: "OpenStreetMap Roads",
            DataSourceType.OSM_RAILWAYS: "OpenStreetMap Railways",
            DataSourceType.OSM_LANDMARKS: "Osm Landmarks",  # Match the example file name
            DataSourceType.OSM_NATURAL: "OpenStreetMap Natural Features",
        }
        return display_names.get(source_type, source_type.value.replace('_', ' ').title())