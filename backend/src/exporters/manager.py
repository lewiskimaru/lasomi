"""
Export manager for coordinating multiple format exports
"""

import os
import asyncio
from typing import Dict, Optional, List
import logging
from uuid import UUID

from src.api.api_schemas import ExtractFeaturesResponse, DataSourceType, ExportFormat
from src.exporters.base import BaseExporter
from src.exporters.geojson import GeoJSONExporter
from src.exporters.kml import KMLExporter
from src.exporters.csv import CSVExporter
from src.utils.exceptions import ExportError
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class ExportManager:
    """Manager for coordinating exports across multiple formats"""
    
    def __init__(self):
        self.settings = get_settings()
        self.exporters = self._initialize_exporters()
    
    def _initialize_exporters(self) -> Dict[ExportFormat, BaseExporter]:
        """Initialize all available exporters"""
        return {
            ExportFormat.GEOJSON: GeoJSONExporter(),
            ExportFormat.KML: KMLExporter(create_kmz=False),
            ExportFormat.KMZ: KMLExporter(create_kmz=True),
            ExportFormat.CSV: CSVExporter(),
            # Note: Shapefile and DWG exporters would be added here
            # ExportFormat.SHAPEFILE: ShapefileExporter(),
            # ExportFormat.DWG: DWGExporter(),
        }
    
    async def export_single_format(
        self,
        job_id: UUID,
        export_format: ExportFormat,
        response_data: ExtractFeaturesResponse,
        sources: Optional[List[DataSourceType]] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export data in a single format.
        
        Args:
            job_id: Job identifier for file naming
            export_format: Target export format
            response_data: Data to export
            sources: Optional list of sources to include
            include_metadata: Whether to include processing metadata
            
        Returns:
            Path to the exported file
        """
        
        try:
            # Check if exporter is available
            if export_format not in self.exporters:
                raise ExportError(
                    export_format.value,
                    f"Exporter for {export_format.value} format is not available"
                )
            
            # Get exporter
            exporter = self.exporters[export_format]
            
            # Generate output path
            output_path = self._generate_output_path(job_id, export_format)
            
            # Perform export
            result_path = await exporter.export(
                response_data=response_data,
                output_path=output_path,
                sources=sources,
                include_metadata=include_metadata
            )
            
            self.logger.info(f"Successfully exported {export_format.value} to {result_path}")
            return result_path
            
        except Exception as e:
            self.logger.error(f"Export failed for {export_format.value}: {str(e)}")
            raise ExportError(export_format.value, str(e))
    
    async def export_multiple_formats(
        self,
        job_id: UUID,
        export_formats: List[ExportFormat],
        response_data: ExtractFeaturesResponse,
        sources: Optional[List[DataSourceType]] = None,
        include_metadata: bool = True
    ) -> Dict[ExportFormat, str]:
        """
        Export data in multiple formats concurrently.
        
        Args:
            job_id: Job identifier for file naming
            export_formats: List of target export formats
            response_data: Data to export
            sources: Optional list of sources to include
            include_metadata: Whether to include processing metadata
            
        Returns:
            Dictionary mapping formats to file paths
        """
        
        try:
            # Create export tasks
            tasks = []
            format_map = {}
            
            for export_format in export_formats:
                if export_format in self.exporters:
                    task = asyncio.create_task(
                        self.export_single_format(
                            job_id, export_format, response_data, sources, include_metadata
                        )
                    )
                    tasks.append(task)
                    format_map[task] = export_format
                else:
                    self.logger.warning(f"Skipping unsupported format: {export_format.value}")
            
            # Execute all exports concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            export_results = {}
            for task, result in zip(tasks, results):
                export_format = format_map[task]
                
                if isinstance(result, Exception):
                    self.logger.error(f"Export failed for {export_format.value}: {str(result)}")
                    # Could optionally include failed exports in result
                else:
                    export_results[export_format] = result
            
            return export_results
            
        except Exception as e:
            self.logger.error(f"Multiple format export failed: {str(e)}")
            raise ExportError("multiple_formats", str(e))
    
    def _generate_output_path(self, job_id: UUID, export_format: ExportFormat) -> str:
        """Generate output file path for export"""
        
        # Create export directory
        export_dir = os.path.join(self.settings.export_temp_dir, str(job_id))
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename with appropriate extension
        file_extensions = {
            ExportFormat.GEOJSON: ".geojson",
            ExportFormat.KML: ".kml",
            ExportFormat.KMZ: ".kmz",
            ExportFormat.CSV: ".csv",
            ExportFormat.SHAPEFILE: ".zip",  # Shapefile as ZIP archive
            ExportFormat.DWG: ".dwg",
        }
        
        extension = file_extensions.get(export_format, f".{export_format.value}")
        filename = f"atlas_export_{job_id}{extension}"
        
        return os.path.join(export_dir, filename)
    
    def cleanup_exports(self, job_id: UUID) -> bool:
        """
        Clean up export files for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cleanup successful, False otherwise
        """
        
        try:
            export_dir = os.path.join(self.settings.export_temp_dir, str(job_id))
            
            if os.path.exists(export_dir):
                import shutil
                shutil.rmtree(export_dir)
                self.logger.info(f"Cleaned up export directory for job {job_id}")
                return True
            
            return True  # Directory doesn't exist, consider it cleaned
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup exports for job {job_id}: {str(e)}")
            return False
    
    def get_available_formats(self) -> List[ExportFormat]:
        """Get list of available export formats"""
        return list(self.exporters.keys())
    
    def is_format_supported(self, export_format: ExportFormat) -> bool:
        """Check if an export format is supported"""
        return export_format in self.exporters