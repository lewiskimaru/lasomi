"""
Core feature aggregation and processing engine
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
import logging
from uuid import UUID, uuid4

from geojson_pydantic import FeatureCollection
from shapely.geometry import Polygon

from src.api.api_schemas import (
    DataSourceType, DataSourceConfig, ExtractFeaturesRequest, 
    ExtractFeaturesResponse, DataSourceResult, ProcessingStatus, FeatureStats, ExportFormat
)
from src.core.data_sources.base import BaseDataSource
from src.core.data_sources.google_earth_engine import GoogleEarthEngineConnector
from src.core.data_sources.openstreetmap import OpenStreetMapConnector
from src.utils.exceptions import ProcessingError, ValidationError
from src.utils.geometry import geojson_to_shapely_polygon, validate_aoi_polygon, simplify_geometry
from src.utils.format_converter import format_converter
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class FeatureAggregator:
    """Main processing engine for feature extraction and aggregation"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
    
    async def process_request(self, request: ExtractFeaturesRequest) -> ExtractFeaturesResponse:
        """
        Process a feature extraction request across multiple data sources.
        
        Args:
            request: ExtractFeaturesRequest containing AOI and configuration
            
        Returns:
            ExtractFeaturesResponse with results from all data sources
        """
        job_id = uuid4()
        start_time = time.time()
        
        self.logger.info(f"Starting processing job {job_id}")
        
        try:
            # Validate AOI
            aoi_polygon = await self._validate_and_process_aoi(request.aoi_boundary)
            
            # Get enabled data sources
            enabled_sources = self._get_enabled_sources(request.data_sources)
            
            if not enabled_sources:
                raise ValidationError("No data sources enabled")
            
            self.logger.info(f"Processing {len(enabled_sources)} data sources: {[s.value for s in enabled_sources]}")
            
            # Process all data sources concurrently
            results = await self._process_data_sources(
                enabled_sources,
                request.data_sources,
                aoi_polygon,
                request.filters
            )
            
            # Calculate processing statistics
            processing_time = time.time() - start_time
            total_features = sum(result.stats.count for result in results.values())
            successful_sources = sum(1 for result in results.values() if result.status == ProcessingStatus.COMPLETED)
            failed_sources = len(results) - successful_sources
            
            # Determine overall status
            if successful_sources == 0:
                overall_status = ProcessingStatus.FAILED
            elif failed_sources == 0:
                overall_status = ProcessingStatus.COMPLETED
            else:
                overall_status = ProcessingStatus.PARTIAL
            
            # Generate export URLs
            export_urls = self._generate_export_urls(job_id)
            
            # Create base response
            response = ExtractFeaturesResponse(
                job_id=job_id,
                status=overall_status,
                processing_time=processing_time,
                requested_sources=enabled_sources,
                results=results,
                export_urls=export_urls,
                total_features=total_features,
                successful_sources=successful_sources,
                failed_sources=failed_sources
            )
            
            # Handle inline format conversion if requested
            if request.output_format and request.raw:
                response = await self._apply_inline_format_conversion(response, request.output_format)
            
            self.logger.info(
                f"Completed job {job_id} in {processing_time:.2f}s: "
                f"{total_features} features from {successful_sources}/{len(enabled_sources)} sources"
            )
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Job {job_id} failed after {processing_time:.2f}s: {str(e)}")
            raise ProcessingError(f"Feature extraction failed: {str(e)}")
    
    async def _validate_and_process_aoi(self, aoi_boundary) -> Polygon:
        """Validate and process AOI boundary"""
        
        try:
            # Convert to Shapely polygon
            aoi_polygon = geojson_to_shapely_polygon(aoi_boundary)
            
            # Validate polygon and constraints
            is_valid, area_km2, errors = validate_aoi_polygon(
                aoi_boundary, 
                self.settings.max_aoi_area_km2
            )
            
            if not is_valid:
                raise ValidationError(f"Invalid AOI: {'; '.join(errors)}")
            
            self.logger.info(f"AOI validated: {area_km2:.2f} km²")
            return aoi_polygon
            
        except Exception as e:
            raise ValidationError(f"AOI validation failed: {str(e)}")
    
    def _get_enabled_sources(self, data_sources: Dict[DataSourceType, DataSourceConfig]) -> List[DataSourceType]:
        """Get list of enabled data sources"""
        return [
            source_type for source_type, config in data_sources.items()
            if config.enabled
        ]
    
    async def _process_data_sources(
        self,
        enabled_sources: List[DataSourceType],
        source_configs: Dict[DataSourceType, DataSourceConfig],
        aoi_polygon: Polygon,
        filters: Optional[Any]
    ) -> Dict[DataSourceType, DataSourceResult]:
        """Process all enabled data sources concurrently"""
        
        # Create connector tasks
        tasks = []
        source_map = {}
        
        for source_type in enabled_sources:
            config = source_configs[source_type]
            connector = self._create_connector(source_type, config)
            
            task = asyncio.create_task(
                self._process_single_source(connector, aoi_polygon, filters)
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
                # Task failed
                self.logger.error(f"Source {source_type.value} failed: {str(result)}")
                results[source_type] = DataSourceResult(
                    source=source_type,
                    status=ProcessingStatus.FAILED,
                    stats=FeatureStats(count=0, processing_time=0.0),
                    geojson=FeatureCollection(type="FeatureCollection", features=[]),
                    error_message=str(result)
                )
            else:
                # Task succeeded
                results[source_type] = result
        
        return results
    
    def _create_connector(self, source_type: DataSourceType, config: DataSourceConfig) -> BaseDataSource:
        """Create appropriate connector for data source type"""
        
        if source_type in [DataSourceType.MICROSOFT_BUILDINGS, DataSourceType.GOOGLE_BUILDINGS]:
            return GoogleEarthEngineConnector(source_type, config)
        elif source_type in [
            DataSourceType.OSM_BUILDINGS, DataSourceType.OSM_ROADS,
            DataSourceType.OSM_RAILWAYS, DataSourceType.OSM_LANDMARKS,
            DataSourceType.OSM_NATURAL
        ]:
            return OpenStreetMapConnector(source_type, config)
        else:
            raise ProcessingError(f"Unknown data source type: {source_type.value}")
    
    async def _process_single_source(
        self,
        connector: BaseDataSource,
        aoi_polygon: Polygon,
        filters: Optional[Any]
    ) -> DataSourceResult:
        """Process a single data source"""
        
        start_time = time.time()
        
        try:
            # Extract features - RAW DATA ONLY, no processing
            filter_dict = filters.dict() if filters else None
            features = await connector.extract_with_timeout(aoi_polygon, filter_dict)
            
            # DO NOT apply any geometry simplification - preserve raw data integrity
            # User requested raw data without coordinate dropping
            
            # Calculate statistics
            processing_time = time.time() - start_time
            stats = connector.calculate_stats(features, processing_time)

            return DataSourceResult(
                source=connector.source_type,
                status=ProcessingStatus.COMPLETED,
                stats=stats,
                geojson=features,
                error_message=None
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Failed to process {connector.source_type.value}: {str(e)}")
            
            return DataSourceResult(
                source=connector.source_type,
                status=ProcessingStatus.FAILED,
                stats=FeatureStats(count=0, processing_time=processing_time),
                geojson=FeatureCollection(type="FeatureCollection", features=[]),
                error_message=str(e)
            )
    
    def _simplify_features(self, features: FeatureCollection, tolerance: float) -> FeatureCollection:
        """Apply geometry simplification to features"""
        
        try:
            if not features.features:
                return features
            
            simplified_features = []
            from shapely.geometry import shape
            
            for feature in features.features:
                try:
                    if feature.geometry:
                        # Convert to Shapely geometry
                        geom = shape(feature.geometry)
                        
                        # Simplify geometry
                        simplified_geom = simplify_geometry(geom, tolerance)
                        
                        # Convert back to GeoJSON
                        from shapely.geometry import mapping
                        feature.geometry = mapping(simplified_geom)
                    
                    simplified_features.append(feature)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to simplify feature geometry: {e}")
                    simplified_features.append(feature)  # Keep original
            
            features.features = simplified_features
            return features
            
        except Exception as e:
            self.logger.warning(f"Geometry simplification failed: {e}")
            return features  # Return original if simplification fails
    
    def _generate_export_urls(self, job_id: UUID) -> Dict[str, str]:
        """Generate export URLs for different formats"""
        
        base_url = f"/api/v1/export/{job_id}"
        
        return {
            "geojson": f"{base_url}/geojson",
            "kml": f"{base_url}/kml",
            "kmz": f"{base_url}/kmz",
            "dwg": f"{base_url}/dwg",
            "shapefile": f"{base_url}/shapefile",
            "csv": f"{base_url}/csv"
        }
    
    async def _apply_inline_format_conversion(self, response: ExtractFeaturesResponse, target_format: ExportFormat) -> ExtractFeaturesResponse:
        """
        Apply inline format conversion to response data.
        
        Args:
            response: The original response
            target_format: Target format for conversion
            
        Returns:
            Modified response with converted data in the 'data' field
        """
        
        try:
            self.logger.info(f"Applying inline format conversion to {target_format.value}")
            
            # Convert the response data to the target format
            converted_data = await format_converter.convert_response_to_format(
                response, target_format, include_metadata=True
            )
            
            # Validate the conversion
            is_valid = format_converter.validate_conversion_result(
                response, converted_data, target_format
            )
            
            if not is_valid:
                self.logger.warning(f"Format conversion validation failed for {target_format.value}")
                # Continue with conversion but log the warning
            
            # Update response with converted data
            response.output_format = target_format
            response.data = converted_data
            
            self.logger.info(f"Successfully applied inline format conversion to {target_format.value}")
            return response
            
        except Exception as e:
            self.logger.error(f"Inline format conversion failed: {str(e)}")
            # Don't fail the entire request - just log the error and return original response
            # The user can still use the export URLs
            return response