"""
Clean processing service with proper separation of concerns
"""

import asyncio
import time
from typing import Dict, Any, List
from uuid import UUID, uuid4
import logging

from shapely.geometry import Polygon

from src.core.interfaces import IDataSourceFactory, IProcessingService
from src.api.schemas_v2 import (
    DataSourceType, DataSourceResult, RawDataResponse, 
    ProcessingStatus, FeatureStats
)
from src.utils.exceptions import ProcessingError, ValidationError
from src.utils.geometry import geojson_to_shapely_polygon, validate_aoi_polygon
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class RawDataProcessingService(IProcessingService):
    """
    Clean processing service focused on raw data extraction.
    Single responsibility: orchestrate data extraction from multiple sources.
    """
    
    def __init__(self, data_source_factory: IDataSourceFactory):
        self.data_source_factory = data_source_factory
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
    
    async def process_extraction_request(
        self, 
        aoi: Polygon, 
        source_selections: Dict[DataSourceType, Dict[str, Any]]
    ) -> Dict[DataSourceType, DataSourceResult]:
        """
        Process extraction request across multiple data sources.
        
        Args:
            aoi: Area of interest polygon
            source_selections: Dictionary of source types and their configurations
            
        Returns:
            Dictionary mapping source types to their results
        """
        
        self.logger.info(f"Processing extraction for {len(source_selections)} data sources")
        
        # Validate AOI
        await self._validate_aoi(aoi)
        
        # Get enabled sources
        enabled_sources = {
            source_type: config 
            for source_type, config in source_selections.items() 
            if config.get('enabled', True)
        }
        
        if not enabled_sources:
            raise ValidationError("No data sources enabled")
        
        # Process all sources concurrently
        results = await self._process_sources_concurrently(aoi, enabled_sources)
        
        self.logger.info(f"Completed processing: {len(results)} sources processed")
        return results
    
    async def _validate_aoi(self, aoi: Polygon) -> None:
        """Validate area of interest"""
        try:
            # Convert polygon to GeoJSON for validation
            from shapely.geometry import mapping
            geojson_polygon = mapping(aoi)
            
            # Use existing validation
            is_valid, area_km2, errors = validate_aoi_polygon(
                type("MockPolygon", (), {"coordinates": geojson_polygon["coordinates"]}),
                self.settings.max_aoi_area_km2
            )
            
            if not is_valid:
                raise ValidationError(f"Invalid AOI: {'; '.join(errors)}")
            
            self.logger.info(f"AOI validated: {area_km2:.2f} km²")
            
        except Exception as e:
            raise ValidationError(f"AOI validation failed: {str(e)}")
    
    async def _process_sources_concurrently(
        self, 
        aoi: Polygon, 
        source_configs: Dict[DataSourceType, Dict[str, Any]]
    ) -> Dict[DataSourceType, DataSourceResult]:
        """Process all data sources concurrently for maximum performance"""
        
        # Create tasks for each enabled source
        tasks = []
        source_map = {}
        
        for source_type, config in source_configs.items():
            task = asyncio.create_task(
                self._process_single_source(source_type, aoi, config)
            )
            tasks.append(task)
            source_map[task] = source_type
        
        # Execute all tasks concurrently
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        results = {}
        for task, result in zip(tasks, completed_tasks):
            source_type = source_map[task]
            
            if isinstance(result, Exception):
                # Task failed - create error result
                self.logger.error(f"Source {source_type.value} failed: {str(result)}")
                results[source_type] = self._create_error_result(source_type, str(result))
            else:
                # Task succeeded
                results[source_type] = result
        
        return results
    
    async def _process_single_source(
        self, 
        source_type: DataSourceType, 
        aoi: Polygon, 
        config: Dict[str, Any]
    ) -> DataSourceResult:
        """Process a single data source"""
        
        start_time = time.time()
        
        try:
            # Create connector
            connector = self.data_source_factory.create_connector(source_type, config)
            
            # Extract raw features
            timeout = config.get('timeout')
            features = await connector.extract_raw_features(aoi, timeout)
            
            # Calculate stats
            processing_time = time.time() - start_time
            stats = FeatureStats(
                count=len(features.features) if features.features else 0,
                processing_time=processing_time
            )
            
            self.logger.info(
                f"Source {source_type.value} completed: {stats.count} features in {processing_time:.2f}s"
            )
            
            return DataSourceResult(
                source=source_type,
                status=ProcessingStatus.COMPLETED,
                stats=stats,
                data=features,
                error=None
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Source {source_type.value} failed after {processing_time:.2f}s: {str(e)}")
            
            return self._create_error_result(source_type, str(e), processing_time)
    
    def _create_error_result(
        self, 
        source_type: DataSourceType, 
        error_message: str, 
        processing_time: float = 0.0
    ) -> DataSourceResult:
        """Create an error result for a failed data source"""
        
        from geojson_pydantic import FeatureCollection
        
        return DataSourceResult(
            source=source_type,
            status=ProcessingStatus.FAILED,
            stats=FeatureStats(count=0, processing_time=processing_time),
            data=FeatureCollection(type="FeatureCollection", features=[]),
            error=error_message
        )