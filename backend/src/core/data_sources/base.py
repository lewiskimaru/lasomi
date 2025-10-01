"""
Abstract base class for data source connectors
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

from geojson_pydantic import FeatureCollection
from shapely.geometry import Polygon

from src.api.api_schemas import DataSourceType, DataSourceConfig, FeatureStats
from src.utils.exceptions import DataSourceError, TimeoutError

logger = logging.getLogger(__name__)


class BaseDataSource(ABC):
    """Abstract base class for all data source connectors"""
    
    def __init__(self, source_type: DataSourceType, config: DataSourceConfig):
        self.source_type = source_type
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{source_type.value}")
    
    @abstractmethod
    async def extract_features(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]] = None) -> FeatureCollection:
        """
        Extract features from this data source for the given AOI.
        
        Args:
            aoi_polygon: Area of Interest as Shapely Polygon
            filters: Optional filtering parameters
            
        Returns:
            FeatureCollection with extracted features
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test if the data source is accessible.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    async def extract_with_timeout(self, aoi_polygon: Polygon, filters: Optional[Dict[str, Any]] = None) -> FeatureCollection:
        """
        Extract features with timeout handling.
        
        Args:
            aoi_polygon: Area of Interest as Shapely Polygon
            filters: Optional filtering parameters
            
        Returns:
            FeatureCollection with extracted features
            
        Raises:
            TimeoutError: If operation times out
            DataSourceError: If extraction fails
        """
        try:
            self.logger.info(f"Starting feature extraction from {self.source_type.value}")
            start_time = time.time()
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.extract_features(aoi_polygon, filters),
                timeout=self.config.timeout
            )
            
            processing_time = time.time() - start_time
            feature_count = len(result.features) if result and result.features else 0
            
            self.logger.info(
                f"Extracted {feature_count} features from {self.source_type.value} "
                f"in {processing_time:.2f} seconds"
            )
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Extraction from {self.source_type.value} timed out after {self.config.timeout} seconds")
            raise TimeoutError(f"extract_features_{self.source_type.value}", self.config.timeout)
        
        except Exception as e:
            self.logger.error(f"Extraction from {self.source_type.value} failed: {str(e)}")
            raise DataSourceError(self.source_type.value, str(e))
    
    def calculate_stats(self, features: FeatureCollection, processing_time: float) -> FeatureStats:
        """
        Calculate statistics for extracted features.
        
        Args:
            features: Extracted features
            processing_time: Time taken for processing
            
        Returns:
            FeatureStats object
        """
        if not features or not features.features:
            return FeatureStats(
                count=0,
                total_area=0.0,
                total_length=0.0,
                processing_time=processing_time
            )
        
        count = len(features.features)
        total_area = 0.0
        total_length = 0.0
        
        try:
            from shapely.geometry import shape
            
            for feature in features.features:
                if feature.geometry:
                    geom = shape(feature.geometry)
                    
                    if hasattr(geom, 'area'):
                        total_area += geom.area
                    
                    if hasattr(geom, 'length'):
                        total_length += geom.length
                        
        except Exception as e:
            self.logger.warning(f"Failed to calculate geometry statistics: {e}")
        
        return FeatureStats(
            count=count,
            total_area=total_area if total_area > 0 else None,
            total_length=total_length if total_length > 0 else None,
            processing_time=processing_time
        )
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.source_type.value})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source_type={self.source_type.value}, enabled={self.config.enabled})"