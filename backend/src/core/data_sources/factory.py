"""
Data source factory for clean dependency injection
"""

from typing import Dict, Any
import logging

from src.core.interfaces import IDataSourceFactory, IDataSourceConnector
from src.api.schemas_v2 import DataSourceType
from src.core.data_sources.google_earth_engine import GoogleEarthEngineConnector
from src.core.data_sources.openstreetmap import OpenStreetMapConnector
from src.api.api_schemas import DataSourceConfig
from src.utils.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class DataSourceFactory(IDataSourceFactory):
    """Factory for creating data source connectors with proper dependency injection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._connector_registry = self._build_connector_registry()
    
    def _build_connector_registry(self) -> Dict[DataSourceType, type]:
        """Build registry of available connector types"""
        return {
            # Google Earth Engine sources
            DataSourceType.MICROSOFT_BUILDINGS: GoogleEarthEngineConnector,
            DataSourceType.GOOGLE_BUILDINGS: GoogleEarthEngineConnector,
            
            # OpenStreetMap sources
            DataSourceType.OSM_BUILDINGS: OpenStreetMapConnector,
            DataSourceType.OSM_ROADS: OpenStreetMapConnector,
            DataSourceType.OSM_RAILWAYS: OpenStreetMapConnector,
            DataSourceType.OSM_LANDMARKS: OpenStreetMapConnector,
            DataSourceType.OSM_NATURAL: OpenStreetMapConnector,
        }
    
    def create_connector(self, source_type: DataSourceType, config: Dict[str, Any]) -> IDataSourceConnector:
        """
        Create a connector for the specified data source type.
        
        Args:
            source_type: Type of data source
            config: Configuration parameters
            
        Returns:
            Configured data source connector
            
        Raises:
            ProcessingError: If connector type is not supported
        """
        
        try:
            if source_type not in self._connector_registry:
                raise ProcessingError(f"Unsupported data source type: {source_type.value}")
            
            connector_class = self._connector_registry[source_type]
            
            # Convert config to DataSourceConfig if needed
            if isinstance(config, dict):
                data_source_config = DataSourceConfig(
                    enabled=config.get('enabled', True),
                    timeout=config.get('timeout', 30),
                    priority=config.get('priority', 1)
                )
            else:
                data_source_config = config
            
            # Create connector instance
            connector = connector_class(source_type, data_source_config)
            
            self.logger.debug(f"Created connector for {source_type.value}")
            return connector
            
        except Exception as e:
            self.logger.error(f"Failed to create connector for {source_type.value}: {str(e)}")
            raise ProcessingError(f"Failed to create connector for {source_type.value}: {str(e)}")
    
    def get_supported_sources(self) -> list:
        """Get list of supported data source types"""
        return list(self._connector_registry.keys())
    
    def is_source_supported(self, source_type: DataSourceType) -> bool:
        """Check if a data source type is supported"""
        return source_type in self._connector_registry