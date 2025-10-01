"""
Abstract base class for format exporters
"""

import os
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from src.api.api_schemas import ExtractFeaturesResponse, DataSourceType, ExportFormat
from src.utils.exceptions import ExportError

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Abstract base class for all format exporters"""
    
    def __init__(self, export_format: ExportFormat):
        self.export_format = export_format
        self.logger = logging.getLogger(f"{__name__}.{export_format.value}")
    
    @abstractmethod
    async def export(
        self,
        response_data: ExtractFeaturesResponse,
        output_path: str,
        sources: Optional[list] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export data to the specified format.
        
        Args:
            response_data: ExtractFeaturesResponse containing the data to export
            output_path: Path where the exported file should be saved
            sources: Optional list of specific sources to include
            include_metadata: Whether to include processing metadata
            
        Returns:
            Path to the exported file
        """
        pass
    
    def create_temp_file(self, suffix: str) -> str:
        """Create a temporary file for export operations"""
        try:
            temp_dir = os.getenv('TEMP_EXPORT_DIR', tempfile.gettempdir())
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_file = tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
                dir=temp_dir
            )
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            raise ExportError(self.export_format.value, f"Failed to create temporary file: {str(e)}")
    
    def filter_sources(
        self,
        response_data: ExtractFeaturesResponse,
        sources: Optional[list] = None
    ) -> Dict[DataSourceType, Any]:
        """Filter response data to include only specified sources"""
        
        if sources is None:
            return response_data.results
        
        filtered_results = {}
        for source_type in sources:
            if source_type in response_data.results:
                filtered_results[source_type] = response_data.results[source_type]
            else:
                self.logger.warning(f"Requested source {source_type.value} not found in results")
        
        return filtered_results
    
    def create_metadata(
        self,
        response_data: ExtractFeaturesResponse,
        include_sources: list
    ) -> Dict[str, Any]:
        """Create metadata for export"""
        
        metadata = {
            "job_id": str(response_data.job_id),
            "export_format": self.export_format.value,
            "processing_time": response_data.processing_time,
            "total_features": response_data.total_features,
            "successful_sources": response_data.successful_sources,
            "failed_sources": response_data.failed_sources,
            "export_timestamp": "utc_timestamp_here",
            "sources_included": [source.value for source in include_sources],
            "atlas_version": "1.0.0"
        }
        
        return metadata
    
    def ensure_output_directory(self, output_path: str) -> str:
        """Ensure output directory exists"""
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            return output_path
        except Exception as e:
            raise ExportError(self.export_format.value, f"Failed to create output directory: {str(e)}")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.export_format.value})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(export_format={self.export_format.value})"