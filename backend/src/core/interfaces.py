"""
Clean interfaces and abstractions for better architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID

from shapely.geometry import Polygon
from geojson_pydantic import FeatureCollection

from src.api.schemas_v2 import DataSourceType, DataSourceResult, RawDataResponse


class IDataSourceConnector(ABC):
    """Interface for data source connectors"""
    
    @abstractmethod
    async def extract_raw_features(self, aoi: Polygon, timeout: Optional[int] = None) -> FeatureCollection:
        """
        Extract raw features from this data source.
        
        Args:
            aoi: Area of interest polygon
            timeout: Optional timeout override
            
        Returns:
            Raw feature collection without any processing
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the data source is accessible"""
        pass
    
    @abstractmethod
    def get_source_type(self) -> DataSourceType:
        """Get the data source type identifier"""
        pass


class IDataSourceFactory(ABC):
    """Factory interface for creating data source connectors"""
    
    @abstractmethod
    def create_connector(self, source_type: DataSourceType, config: Dict[str, Any]) -> IDataSourceConnector:
        """Create a connector for the specified data source type"""
        pass


class IJobStorage(ABC):
    """Interface for job data storage (for stateless operation)"""
    
    @abstractmethod
    async def store_job_result(self, job_id: UUID, result: RawDataResponse, ttl_seconds: int = 3600) -> bool:
        """Store job result with time-to-live"""
        pass
    
    @abstractmethod
    async def get_job_result(self, job_id: UUID) -> Optional[RawDataResponse]:
        """Retrieve job result by ID"""
        pass
    
    @abstractmethod
    async def delete_job_result(self, job_id: UUID) -> bool:
        """Delete job result"""
        pass


class IExportService(ABC):
    """Interface for export services"""
    
    @abstractmethod
    async def export_data(self, result: RawDataResponse, format: str, sources: Optional[list] = None) -> bytes:
        """Export data in specified format as bytes"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list:
        """Get list of supported export formats as strings"""
        pass


class IProcessingService(ABC):
    """Interface for data processing orchestration"""
    
    @abstractmethod
    async def process_extraction_request(
        self, 
        aoi: Polygon, 
        source_selections: Dict[DataSourceType, Dict[str, Any]]
    ) -> Dict[DataSourceType, DataSourceResult]:
        """Process extraction request across multiple data sources"""
        pass