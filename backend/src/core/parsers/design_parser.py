"""
Robust parsers for design files (KMZ, KML, GeoJSON)
Handles complex folder structures, styling, and various coordinate systems
"""

import json
import zipfile
import tempfile
import os
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from xml.etree import ElementTree as ET

from geojson_pydantic import FeatureCollection, Feature
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj

from src.api.schemas.design_upload import (
    DesignFileFormat, DesignLayer, DesignMetadata, ParsedDesign
)
from src.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DesignFileParser:
    """Main parser that handles all supported design file formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # KML namespace handling
        self.kml_namespaces = {
            'kml': 'http://www.opengis.net/kml/2.2',
            'gx': 'http://www.google.com/kml/ext/2.2'
        }
    
    async def parse_design_file(self, file_content: bytes, filename: str) -> ParsedDesign:
        """
        Parse design file and extract all layers, features, and metadata
        
        Args:
            file_content: Raw file bytes
            filename: Original filename for format detection
            
        Returns:
            ParsedDesign with all extracted information
        """
        
        start_time = time.time()
        
        try:
            # Detect file format
            file_format = self._detect_format(filename, file_content)
            self.logger.info(f"Processing {file_format.value} file: {filename}")
            
            # Parse based on format
            if file_format == DesignFileFormat.GEOJSON:
                layers, metadata = await self._parse_geojson(file_content, filename)
            elif file_format == DesignFileFormat.KML:
                layers, metadata = await self._parse_kml(file_content, filename)
            elif file_format == DesignFileFormat.KMZ:
                layers, metadata = await self._parse_kmz(file_content, filename)
            else:
                raise ValidationError(f"Unsupported file format: {file_format}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create combined features for quick rendering
            all_features = self._combine_all_features(layers)
            
            # Calculate suggested zoom level
            suggested_zoom = self._calculate_suggested_zoom(metadata.bbox)
            
            parsed_design = ParsedDesign(
                metadata=metadata,
                layers=layers,
                all_features=all_features,
                suggested_zoom=suggested_zoom
            )
            
            self.logger.info(
                f"Successfully parsed {filename}: {len(layers)} layers, "
                f"{metadata.total_features} features in {processing_time:.2f}s"
            )
            
            return parsed_design
            
        except Exception as e:
            self.logger.error(f"Failed to parse {filename}: {str(e)}")
            raise ValidationError(f"Failed to parse design file: {str(e)}")
    
    def _detect_format(self, filename: str, content: bytes) -> DesignFileFormat:
        """Detect file format from filename and content"""
        
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.kmz'):
            return DesignFileFormat.KMZ
        elif filename_lower.endswith('.kml'):
            return DesignFileFormat.KML
        elif filename_lower.endswith(('.geojson', '.json')):
            return DesignFileFormat.GEOJSON
        
        # Try to detect from content
        try:
            # Check if it's a ZIP file (KMZ)
            if content[:2] == b'PK':
                return DesignFileFormat.KMZ
            
            # Try to parse as JSON (GeoJSON)
            content_str = content.decode('utf-8')
            json.loads(content_str)
            return DesignFileFormat.GEOJSON
            
        except:
            pass
        
        # Check if it looks like XML/KML
        try:
            content_str = content.decode('utf-8')
            if '<kml' in content_str.lower() or '<?xml' in content_str.lower():
                return DesignFileFormat.KML
        except:
            pass
        
        raise ValidationError(f"Could not determine file format for: {filename}")
    
    async def _parse_geojson(self, content: bytes, filename: str) -> Tuple[List[DesignLayer], DesignMetadata]:
        """Parse GeoJSON file with enhanced feature detection"""
        
        try:
            content_str = content.decode('utf-8')
            data = json.loads(content_str)
            
            # Handle different GeoJSON structures
            if data.get('type') == 'FeatureCollection':
                features = data.get('features', [])
                # Single layer from FeatureCollection
                layer = DesignLayer(
                    name="Main Layer",
                    description=f"Features from {filename}",
                    features=FeatureCollection(type="FeatureCollection", features=features),
                    feature_count=len(features)
                )
                layers = [layer]
                
            elif data.get('type') == 'Feature':
                # Single feature
                features = [data]
                layer = DesignLayer(
                    name="Single Feature",
                    description=f"Feature from {filename}",
                    features=FeatureCollection(type="FeatureCollection", features=features),
                    feature_count=1
                )
                layers = [layer]
                
            else:
                # Try to find layers in custom structure
                layers = self._extract_geojson_layers(data, filename)
            
            # Calculate metadata
            all_features = []
            for layer in layers:
                all_features.extend(layer.features.features)
            
            bbox, center = self._calculate_bounds(all_features)
            
            metadata = DesignMetadata(
                filename=filename,
                format=DesignFileFormat.GEOJSON,
                file_size=len(content),
                total_features=len(all_features),
                layer_count=len(layers),
                bbox=bbox,
                center=center,
                has_folders=len(layers) > 1,
                has_styling=self._detect_geojson_styling(all_features),
                coordinate_system="WGS84",
                processing_time=0.0  # Will be updated later
            )
            
            return layers, metadata
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in GeoJSON file: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Failed to parse GeoJSON: {str(e)}")
    
    async def _parse_kml(self, content: bytes, filename: str) -> Tuple[List[DesignLayer], DesignMetadata]:
        """Parse KML file with folder structure and styling preservation"""
        
        try:
            # Parse XML
            root = ET.fromstring(content.decode('utf-8'))
            
            # Find Document or kml root
            document = root.find('.//kml:Document', self.kml_namespaces)
            if document is None:
                document = root.find('.//kml:kml', self.kml_namespaces)
            if document is None:
                document = root
            
            # Extract layers from folders and placemarks
            layers = self._extract_kml_layers(document)
            
            # Calculate metadata
            all_features = []
            for layer in layers:
                all_features.extend(layer.features.features)
            
            bbox, center = self._calculate_bounds(all_features)
            
            metadata = DesignMetadata(
                filename=filename,
                format=DesignFileFormat.KML,
                file_size=len(content),
                total_features=len(all_features),
                layer_count=len(layers),
                bbox=bbox,
                center=center,
                has_folders=self._has_kml_folders(document),
                has_styling=self._has_kml_styling(document),
                coordinate_system="WGS84",
                processing_time=0.0  # Will be updated later
            )
            
            return layers, metadata
            
        except ET.ParseError as e:
            raise ValidationError(f"Invalid XML in KML file: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Failed to parse KML: {str(e)}")
    
    async def _parse_kmz(self, content: bytes, filename: str) -> Tuple[List[DesignLayer], DesignMetadata]:
        """Parse KMZ file (ZIP archive with KML)"""
        
        try:
            # Use BytesIO instead of temporary file to avoid permission issues
            import io
            with io.BytesIO(content) as kmz_buffer:
                # Extract KMZ
                with zipfile.ZipFile(kmz_buffer, 'r') as kmz:
                    # Find main KML file
                    kml_files = [f for f in kmz.namelist() if f.lower().endswith('.kml')]
                    
                    if not kml_files:
                        raise ValidationError("No KML files found in KMZ archive")
                    
                    # Use the main KML file (usually doc.kml or first one)
                    main_kml = 'doc.kml' if 'doc.kml' in kml_files else kml_files[0]
                    
                    # Read KML content
                    kml_content = kmz.read(main_kml)
                    
                    # Parse as KML
                    layers, metadata = await self._parse_kml(kml_content, filename)
                    
                    # Update format in metadata
                    metadata.format = DesignFileFormat.KMZ
                    metadata.file_size = len(content)  # Original KMZ size
                    
                    return layers, metadata
                    
        except zipfile.BadZipFile:
            raise ValidationError("Invalid KMZ file (not a valid ZIP archive)")
        except Exception as e:
            raise ValidationError(f"Failed to parse KMZ: {str(e)}")
    
    def _extract_geojson_layers(self, data: dict, filename: str) -> List[DesignLayer]:
        """Extract layers from custom GeoJSON structure"""
        
        layers = []
        
        # Look for common layer patterns
        if 'layers' in data:
            for i, layer_data in enumerate(data['layers']):
                layer_name = layer_data.get('name', f"Layer {i+1}")
                features = layer_data.get('features', [])
                
                layer = DesignLayer(
                    name=layer_name,
                    description=layer_data.get('description'),
                    features=FeatureCollection(type="FeatureCollection", features=features),
                    feature_count=len(features)
                )
                layers.append(layer)
        else:
            # Fallback: single layer
            features = data.get('features', [])
            layer = DesignLayer(
                name="Main Layer",
                description=f"Features from {filename}",
                features=FeatureCollection(type="FeatureCollection", features=features),
                feature_count=len(features)
            )
            layers.append(layer)
        
        return layers
    
    def _extract_kml_layers(self, document: ET.Element) -> List[DesignLayer]:
        """Extract layers from KML document structure"""
        
        layers = []
        
        # Find all folders
        folders = document.findall('.//kml:Folder', self.kml_namespaces)
        
        if folders:
            # Process each folder as a layer
            for folder in folders:
                layer = self._process_kml_folder(folder)
                if layer.feature_count > 0:
                    layers.append(layer)
        else:
            # No folders, process all placemarks as single layer
            placemarks = document.findall('.//kml:Placemark', self.kml_namespaces)
            if placemarks:
                features = []
                for placemark in placemarks:
                    feature = self._convert_kml_placemark_to_geojson(placemark)
                    if feature:
                        features.append(feature)
                
                layer = DesignLayer(
                    name="Main Layer",
                    description="All placemarks",
                    features=FeatureCollection(type="FeatureCollection", features=features),
                    feature_count=len(features)
                )
                layers.append(layer)
        
        return layers if layers else [DesignLayer(
            name="Empty Layer",
            description="No features found",
            features=FeatureCollection(type="FeatureCollection", features=[]),
            feature_count=0
        )]
    
    def _process_kml_folder(self, folder: ET.Element) -> DesignLayer:
        """Process a KML folder into a design layer"""
        
        # Extract folder name and description
        name_elem = folder.find('kml:name', self.kml_namespaces)
        name = name_elem.text if name_elem is not None and name_elem.text is not None else "Unnamed Folder"
        
        desc_elem = folder.find('kml:description', self.kml_namespaces)
        description = desc_elem.text if desc_elem is not None else None
        
        # Extract placemarks
        placemarks = folder.findall('.//kml:Placemark', self.kml_namespaces)
        features = []
        
        for placemark in placemarks:
            feature = self._convert_kml_placemark_to_geojson(placemark)
            if feature:
                features.append(feature)
        
        # Extract styling information
        style_info = self._extract_kml_folder_style(folder)
        
        return DesignLayer(
            name=name,
            description=description,
            features=FeatureCollection(type="FeatureCollection", features=features),
            style=style_info,
            feature_count=len(features)
        )
    
    def _convert_kml_placemark_to_geojson(self, placemark: ET.Element) -> Optional[dict]:
        """Convert KML Placemark to GeoJSON feature"""
        
        try:
            # Extract name and description
            name_elem = placemark.find('kml:name', self.kml_namespaces)
            name = name_elem.text if name_elem is not None else None
            
            desc_elem = placemark.find('kml:description', self.kml_namespaces)
            description = desc_elem.text if desc_elem is not None else None
            
            # Extract geometry
            geometry = self._extract_kml_geometry(placemark)
            if not geometry:
                return None
            
            # Build properties
            properties = {}
            if name:
                properties['name'] = name
            if description:
                properties['description'] = description
            
            # Extract extended data
            extended_data = placemark.find('kml:ExtendedData', self.kml_namespaces)
            if extended_data is not None:
                for data in extended_data.findall('kml:Data', self.kml_namespaces):
                    name_attr = data.get('name')
                    value_elem = data.find('kml:value', self.kml_namespaces)
                    if name_attr and value_elem is not None:
                        properties[name_attr] = value_elem.text
            
            return {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to convert KML placemark: {str(e)}")
            return None
    
    def _extract_kml_geometry(self, placemark: ET.Element) -> Optional[dict]:
        """Extract geometry from KML placemark"""
        
        # Point
        point = placemark.find('.//kml:Point/kml:coordinates', self.kml_namespaces)
        if point is not None and point.text is not None:
            coords = self._parse_kml_coordinates(point.text)
            if coords and len(coords) > 0:
                return {
                    "type": "Point",
                    "coordinates": coords[0]
                }
        
        # LineString
        linestring = placemark.find('.//kml:LineString/kml:coordinates', self.kml_namespaces)
        if linestring is not None and linestring.text is not None:
            coords = self._parse_kml_coordinates(linestring.text)
            if coords:
                return {
                    "type": "LineString",
                    "coordinates": coords
                }
        
        # Polygon
        polygon = placemark.find('.//kml:Polygon', self.kml_namespaces)
        if polygon is not None:
            # Outer boundary
            outer = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', self.kml_namespaces)
            if outer is not None and outer.text is not None:
                outer_coords = self._parse_kml_coordinates(outer.text)
                
                coordinates = [outer_coords]
                
                # Inner boundaries (holes)
                inners = polygon.findall('.//kml:innerBoundaryIs/kml:LinearRing/kml:coordinates', self.kml_namespaces)
                for inner in inners:
                    if inner.text is not None:
                        inner_coords = self._parse_kml_coordinates(inner.text)
                        coordinates.append(inner_coords)
                
                return {
                    "type": "Polygon",
                    "coordinates": coordinates
                }
        
        return None
    
    def _parse_kml_coordinates(self, coord_string: str) -> List[List[float]]:
        """Parse KML coordinate string into list of [lon, lat, alt] coordinates"""
        
        if not coord_string:
            return []
        
        coordinates = []
        
        # Split by whitespace or commas
        coord_pairs = coord_string.strip().split()
        
        for pair in coord_pairs:
            if not pair.strip():
                continue
                
            parts = pair.split(',')
            if len(parts) >= 2:
                try:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    alt = float(parts[2]) if len(parts) > 2 else 0.0
                    coordinates.append([lon, lat, alt])
                except ValueError:
                    continue
        
        return coordinates
    
    def _calculate_bounds(self, features: List[dict]) -> Tuple[List[float], List[float]]:
        """Calculate bounding box and center from features"""
        
        if not features:
            return [0, 0, 0, 0], [0, 0]
        
        min_lon = min_lat = float('inf')
        max_lon = max_lat = float('-inf')
        
        for feature in features:
            # Handle both dictionary features and potential geojson_pydantic.Feature objects
            if isinstance(feature, dict):
                # This is a dictionary feature
                geometry = feature.get('geometry')
            else:
                # This might be a geojson_pydantic.Feature object
                geometry = getattr(feature, 'geometry', None)
            
            if not geometry:
                continue
            
            try:
                geom = shape(geometry)
                bounds = geom.bounds
                min_lon = min(min_lon, bounds[0])
                min_lat = min(min_lat, bounds[1])
                max_lon = max(max_lon, bounds[2])
                max_lat = max(max_lat, bounds[3])
            except:
                continue
        
        if min_lon == float('inf'):
            return [0, 0, 0, 0], [0, 0]
        
        bbox = [min_lon, min_lat, max_lon, max_lat]
        center = [(min_lon + max_lon) / 2, (min_lat + max_lat) / 2]
        
        return bbox, center
    
    def _calculate_suggested_zoom(self, bbox: List[float]) -> int:
        """Calculate suggested zoom level based on bounding box"""
        
        if not bbox or len(bbox) != 4:
            return 10
        
        width = abs(bbox[2] - bbox[0])
        height = abs(bbox[3] - bbox[1])
        max_dimension = max(width, height)
        
        # Rough zoom level calculation
        if max_dimension > 10:
            return 3
        elif max_dimension > 5:
            return 5
        elif max_dimension > 1:
            return 8
        elif max_dimension > 0.1:
            return 12
        elif max_dimension > 0.01:
            return 15
        else:
            return 18
    
    def _combine_all_features(self, layers: List[DesignLayer]) -> FeatureCollection:
        """Combine all features from all layers for quick rendering"""
        
        all_features = []
        for layer in layers:
            for feature in layer.features.features:
                # Handle both dictionary features and potential geojson_pydantic.Feature objects
                if isinstance(feature, dict):
                    # This is a dictionary feature
                    if 'properties' not in feature or not feature['properties']:
                        feature['properties'] = {}
                    feature['properties']['atlas_layer'] = layer.name
                    all_features.append(feature)
                else:
                    # This might be a geojson_pydantic.Feature object
                    if not getattr(feature, 'properties', None):
                        feature.properties = {}
                    feature.properties['atlas_layer'] = layer.name
                    all_features.append(feature)
        
        return FeatureCollection(type="FeatureCollection", features=all_features)
    
    def _detect_geojson_styling(self, features: List[dict]) -> bool:
        """Detect if GeoJSON contains styling information"""
        
        for feature in features:
            # Handle both dictionary features and potential geojson_pydantic.Feature objects
            if isinstance(feature, dict):
                # This is a dictionary feature
                properties = feature.get('properties', {})
            else:
                # This might be a geojson_pydantic.Feature object
                properties = getattr(feature, 'properties', {})
                
            if any(key.startswith(('stroke', 'fill', 'marker', 'style')) for key in properties.keys()):
                return True
        return False
    
    def _has_kml_folders(self, document: ET.Element) -> bool:
        """Check if KML document has folder structure"""
        folders = document.findall('.//kml:Folder', self.kml_namespaces)
        return len(folders) > 0
    
    def _has_kml_styling(self, document: ET.Element) -> bool:
        """Check if KML document has styling information"""
        styles = document.findall('.//kml:Style', self.kml_namespaces)
        return len(styles) > 0
    
    def _extract_kml_folder_style(self, folder: ET.Element) -> Optional[dict]:
        """Extract styling information from KML folder"""
        
        style_info = {}
        
        # Look for styleUrl
        style_url = folder.find('kml:styleUrl', self.kml_namespaces)
        if style_url is not None:
            style_info['styleUrl'] = style_url.text
        
        # Look for inline Style
        style = folder.find('kml:Style', self.kml_namespaces)
        if style is not None:
            # Extract line style
            line_style = style.find('kml:LineStyle', self.kml_namespaces)
            if line_style is not None:
                color = line_style.find('kml:color', self.kml_namespaces)
                width = line_style.find('kml:width', self.kml_namespaces)
                if color is not None:
                    style_info['lineColor'] = color.text
                if width is not None:
                    style_info['lineWidth'] = width.text
            
            # Extract poly style
            poly_style = style.find('kml:PolyStyle', self.kml_namespaces)
            if poly_style is not None:
                color = poly_style.find('kml:color', self.kml_namespaces)
                if color is not None:
                    style_info['fillColor'] = color.text
        
        return style_info if style_info else None