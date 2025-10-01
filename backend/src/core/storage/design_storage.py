"""
Design storage system for uploaded design files
Handles storage, retrieval, and metadata management
"""

import json
import os
from typing import Optional, Dict, Any
from uuid import UUID
import logging
from pathlib import Path

from src.api.schemas.design_upload import ParsedDesign, DesignMetadata
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class DesignStorage:
    """Handles storage and retrieval of uploaded design files"""
    
    def __init__(self):
        self.settings = get_settings()
        self.storage_dir = Path(self.settings.export_temp_dir) / "designs"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def store_design(self, design: ParsedDesign) -> bool:
        """
        Store parsed design with metadata
        
        Args:
            design: Parsed design to store
            
        Returns:
            True if stored successfully
        """
        
        try:
            design_id = design.design_id
            
            # Create design directory
            design_dir = self.storage_dir / str(design_id)
            design_dir.mkdir(exist_ok=True)
            
            # Store metadata
            metadata_path = design_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(design.metadata.dict(), f, indent=2, default=str)
            
            # Store layer information
            layers_path = design_dir / "layers.json"
            layers_data = [layer.dict() for layer in design.layers]
            with open(layers_path, 'w') as f:
                json.dump(layers_data, f, indent=2, default=str)
            
            # Store combined features for quick access
            features_path = design_dir / "all_features.json"
            with open(features_path, 'w') as f:
                json.dump(design.all_features.dict(), f, indent=2)
            
            self.logger.info(f"Stored design {design_id} with {len(design.layers)} layers")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store design {design.design_id}: {str(e)}")
            return False
    
    async def get_design_metadata(self, design_id: UUID) -> Optional[DesignMetadata]:
        """
        Retrieve design metadata
        
        Args:
            design_id: Design identifier
            
        Returns:
            Design metadata or None if not found
        """
        
        try:
            metadata_path = self.storage_dir / str(design_id) / "metadata.json"
            
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, 'r') as f:
                metadata_data = json.load(f)
            
            # Convert to DesignMetadata object
            return DesignMetadata(**metadata_data)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve metadata for design {design_id}: {str(e)}")
            return None
    
    async def get_design_layers(self, design_id: UUID, layer_names: Optional[list] = None) -> Optional[list]:
        """
        Retrieve design layers
        
        Args:
            design_id: Design identifier
            layer_names: Specific layers to retrieve (None for all)
            
        Returns:
            List of layers or None if not found
        """
        
        try:
            layers_path = self.storage_dir / str(design_id) / "layers.json"
            
            if not layers_path.exists():
                return None
            
            with open(layers_path, 'r') as f:
                layers_data = json.load(f)
            
            # Filter layers if specific names requested
            if layer_names:
                filtered_layers = [
                    layer for layer in layers_data 
                    if layer.get('name') in layer_names
                ]
                return filtered_layers
            
            return layers_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve layers for design {design_id}: {str(e)}")
            return None
    
    async def get_design_features(self, design_id: UUID) -> Optional[Dict]:
        """
        Retrieve all design features for quick rendering
        
        Args:
            design_id: Design identifier
            
        Returns:
            Combined features or None if not found
        """
        
        try:
            features_path = self.storage_dir / str(design_id) / "all_features.json"
            
            if not features_path.exists():
                return None
            
            with open(features_path, 'r') as f:
                features_data = json.load(f)
            
            return features_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve features for design {design_id}: {str(e)}")
            return None
    
    async def delete_design(self, design_id: UUID) -> bool:
        """
        Delete stored design
        
        Args:
            design_id: Design identifier
            
        Returns:
            True if deleted successfully
        """
        
        try:
            design_dir = self.storage_dir / str(design_id)
            
            if design_dir.exists():
                import shutil
                shutil.rmtree(design_dir)
                self.logger.info(f"Deleted design {design_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete design {design_id}: {str(e)}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        
        try:
            total_size = 0
            design_count = 0
            
            if self.storage_dir.exists():
                for design_dir in self.storage_dir.iterdir():
                    if design_dir.is_dir():
                        design_count += 1
                        for file_path in design_dir.rglob('*'):
                            if file_path.is_file():
                                total_size += file_path.stat().st_size
            
            return {
                'total_designs': design_count,
                'total_size_bytes': total_size,
                'storage_path': str(self.storage_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {str(e)}")
            return {
                'total_designs': 0,
                'total_size_bytes': 0,
                'storage_path': str(self.storage_dir),
                'error': str(e)
            }