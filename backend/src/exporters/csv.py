"""
CSV format exporter for spreadsheet analysis
"""

import csv
import os
from typing import Dict, Any, Optional, List
import logging

from shapely.geometry import shape
from shapely import wkt

from src.exporters.base import BaseExporter
from src.api.api_schemas import ExtractFeaturesResponse, DataSourceType, ExportFormat
from src.utils.exceptions import ExportError

logger = logging.getLogger(__name__)


class CSVExporter(BaseExporter):
    """Exporter for CSV format with WKT geometry"""
    
    def __init__(self):
        super().__init__(ExportFormat.CSV)
    
    async def export(
        self,
        response_data: ExtractFeaturesResponse,
        output_path: str,
        sources: Optional[List[DataSourceType]] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export data to CSV format with WKT geometry representation.
        """
        
        try:
            self.ensure_output_directory(output_path)
            
            # Filter sources if specified
            filtered_results = self.filter_sources(response_data, sources)
            
            # Collect all features with source attribution
            all_features = []
            
            for source_type, result in filtered_results.items():
                if not result.geojson or not result.geojson.features:
                    continue
                
                for feature in result.geojson.features:
                    feature_data = {
                        'atlas_source': source_type.value,
                        'atlas_source_status': result.status.value,
                        'feature_id': feature.id if hasattr(feature, 'id') else None,
                        'geometry_type': feature.geometry.type if feature.geometry else None,
                        'geometry_wkt': self._geometry_to_wkt(feature.geometry) if feature.geometry else None
                    }
                    
                    # Add all properties except verbose 'description'
                    if feature.properties:
                        for key, value in feature.properties.items():
                            if str(key).lower() == 'description':
                                continue
                            # Clean key name for CSV column
                            clean_key = str(key).replace(' ', '_').replace('-', '_')
                            feature_data[clean_key] = value
                    
                    all_features.append(feature_data)
            
            if not all_features:
                # Create empty CSV with headers
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['atlas_source', 'atlas_source_status', 'message'])
                    writer.writerow(['N/A', 'N/A', 'No features found'])
                return output_path
            
            # Get all unique column names
            all_columns = set()
            for feature in all_features:
                all_columns.update(feature.keys())
            
            # Sort columns with atlas columns first
            atlas_columns = [col for col in all_columns if col.startswith('atlas_')]
            other_columns = sorted([col for col in all_columns if not col.startswith('atlas_')])
            column_order = atlas_columns + other_columns
            
            # Write CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=column_order)
                writer.writeheader()
                
                for feature in all_features:
                    # Ensure all columns are present
                    row_data = {col: feature.get(col, '') for col in column_order}
                    writer.writerow(row_data)
            
            self.logger.info(f"Exported {len(all_features)} features to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"CSV export failed: {str(e)}")
            raise ExportError(self.export_format.value, str(e))
    
    def _geometry_to_wkt(self, geometry) -> str:
        """Convert GeoJSON geometry to WKT format"""
        try:
            if not geometry:
                return ""
            
            # Convert GeoJSON geometry to Shapely geometry
            geom = shape(geometry)
            
            # Convert to WKT
            return geom.wkt
            
        except Exception as e:
            self.logger.warning(f"Failed to convert geometry to WKT: {str(e)}")
            return f"INVALID_GEOMETRY: {str(e)}"
    
    async def export_summary(
        self,
        response_data: ExtractFeaturesResponse,
        output_path: str,
        sources: Optional[List[DataSourceType]] = None
    ) -> str:
        """
        Export summary statistics to CSV format.
        """
        
        try:
            self.ensure_output_directory(output_path)
            
            # Filter sources if specified
            filtered_results = self.filter_sources(response_data, sources)
            
            summary_data = []
            
            # Add overall summary
            summary_data.append({
                'source': 'OVERALL',
                'status': response_data.status.value,
                'feature_count': response_data.total_features,
                'processing_time_seconds': response_data.processing_time,
                'successful_sources': response_data.successful_sources,
                'failed_sources': response_data.failed_sources,
                'error_message': ''
            })
            
            # Add per-source summary
            for source_type, result in filtered_results.items():
                summary_data.append({
                    'source': source_type.value,
                    'status': result.status.value,
                    'feature_count': result.stats.count,
                    'processing_time_seconds': result.stats.processing_time,
                    'total_area': result.stats.total_area or '',
                    'total_length': result.stats.total_length or '',
                    'error_message': result.error_message or ''
                })
            
            # Write summary CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'source', 'status', 'feature_count', 'processing_time_seconds',
                    'total_area', 'total_length', 'successful_sources', 'failed_sources', 'error_message'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in summary_data:
                    # Ensure all fields are present
                    complete_row = {field: row.get(field, '') for field in fieldnames}
                    writer.writerow(complete_row)
            
            self.logger.info(f"Exported summary to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"CSV summary export failed: {str(e)}")
            raise ExportError(self.export_format.value, str(e))