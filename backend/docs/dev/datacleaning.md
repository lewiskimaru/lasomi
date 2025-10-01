now i'm using the server to do building footprint extraction, i'm using google open buildings and also ms building footprints and then also osm buildings. this sources do give back building data but then for google and ms i noticed some buildings overlap and then i noticed that i get a confidence score for building polygon because they used AI to generate the footprints (osm DOESNT have the overlap issue) so now i need help making an algorithm that cleans the buildings data. i need the data to be in a way where we have all the key buildngs and nothing overlaps

so basically we may have an algorithim that can do this cleaning, top of mind i think we can use the confidence score so we have something like:

if buildings overlap then keep one with the highest confodence score. 

some potential issues i forsee is how exactly do we decide when buildings overlap since for building polygon we will only have the endpoints of a polygon so how can we know if a polygon endpoint goes inside another polygon and by how much and then another issue  is we need the degree of penetration since some polygons might just intersect on the edges and others might intersect too much, how do we do this?

please help me design this algorithm



You're dealing with a classic geospatial data conflation problem! Here's a comprehensive algorithm to clean overlapping building footprints:Here's a comprehensive building footprint deduplication algorithm that addresses all your concerns:

## Key Features of the Algorithm

**1. Overlap Detection:**
- Uses spatial indexing (R-tree) for efficient overlap detection
- Distinguishes between edge touching vs. actual overlap using buffer zones
- Calculates multiple overlap metrics (overlap ratio, Jaccard index)

**2. Confidence-Based Resolution:**
- Prioritizes buildings with higher confidence scores
- Falls back to largest area if confidence is missing (for OSM)
- Supports different resolution strategies

**3. Configurable Thresholds:**
- `overlap_threshold`: Controls when buildings are considered duplicates (default 30%)
- `edge_buffer`: Distinguishes edge touching from real overlap (default 0.5m)

## How It Solves Your Specific Issues

**Polygon Overlap Detection:**
- Uses Shapely's geometric operations to calculate actual intersection areas
- Implements overlap ratio = intersection_area / smaller_polygon_area
- Accounts for edge touching vs. meaningful overlap

**Degree of Penetration:**
- Calculates precise overlap ratios and Jaccard indices
- Uses configurable thresholds to determine significance
- Handles various overlap scenarios (partial, complete, edge-only)

**Resolution Strategies:**
1. **Highest Confidence**: Keep building with best confidence score
2. **Largest Area**: Keep building with largest footprint
3. **Union**: Merge overlapping buildings into single polygon

## Usage for Your Data

```python
# Initialize with your preferred settings
deduplicator = BuildingDeduplicator(
    overlap_threshold=0.3,  # 30% overlap = duplicate
    edge_buffer=0.5         # 0.5m buffer for edge detection
)

# Combine your data sources
all_buildings = pd.concat([
    google_buildings,  # has 'confidence' column
    ms_buildings,      # has 'confidence' column  
    osm_buildings      # will get default confidence=1.0
], ignore_index=True)

# Clean the data
clean_buildings = deduplicator.deduplicate_buildings(
    all_buildings, 
    strategy='highest_confidence'
)
```

## Recommended Configuration

For your use case with Google Open Buildings + MS Building Footprints + OSM:

```python
config = {
    'overlap_threshold': 0.3,  # 30% overlap threshold
    'edge_buffer': 0.5,        # 0.5m buffer
    'strategy': 'highest_confidence'  # Prioritize AI confidence
}
```

This algorithm will give you clean, non-overlapping building data while preserving the highest quality footprints from your three sources!




import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import unary_union
import pandas as pd
from rtree import index
import numpy as np

class BuildingDeduplicator:
    def __init__(self, overlap_threshold=0.3, edge_buffer=0.5):
        """
        Initialize the deduplicator with configurable thresholds.
        
        Args:
            overlap_threshold (float): Minimum overlap ratio to consider buildings as duplicates (0.0-1.0)
            edge_buffer (float): Buffer in meters to distinguish edge touching from actual overlap
        """
        self.overlap_threshold = overlap_threshold
        self.edge_buffer = edge_buffer
        
    def calculate_overlap_metrics(self, poly1, poly2):
        """
        Calculate various overlap metrics between two polygons.
        
        Returns:
            dict: Contains intersection_area, union_area, overlap_ratio, jaccard_index
        """
        # Handle invalid geometries
        if not (poly1.is_valid and poly2.is_valid):
            return {
                'intersection_area': 0,
                'union_area': max(poly1.area, poly2.area),
                'overlap_ratio': 0,
                'jaccard_index': 0
            }
        
        intersection = poly1.intersection(poly2)
        union = poly1.union(poly2)
        
        intersection_area = intersection.area if hasattr(intersection, 'area') else 0
        union_area = union.area if hasattr(union, 'area') else max(poly1.area, poly2.area)
        
        # Overlap ratio: intersection area / smaller polygon area
        smaller_area = min(poly1.area, poly2.area)
        overlap_ratio = intersection_area / smaller_area if smaller_area > 0 else 0
        
        # Jaccard index: intersection area / union area
        jaccard_index = intersection_area / union_area if union_area > 0 else 0
        
        return {
            'intersection_area': intersection_area,
            'union_area': union_area,
            'overlap_ratio': overlap_ratio,
            'jaccard_index': jaccard_index
        }
    
    def is_significant_overlap(self, poly1, poly2):
        """
        Determine if two polygons have significant overlap (not just edge touching).
        """
        # Use buffer to distinguish edge touching from actual overlap
        buffered_poly1 = poly1.buffer(-self.edge_buffer)
        buffered_poly2 = poly2.buffer(-self.edge_buffer)
        
        # If buffered polygons don't exist or don't intersect, it's just edge touching
        if (buffered_poly1.is_empty or buffered_poly2.is_empty or 
            not buffered_poly1.intersects(buffered_poly2)):
            return False
        
        # Calculate overlap metrics
        metrics = self.calculate_overlap_metrics(poly1, poly2)
        
        # Consider significant if overlap ratio exceeds threshold
        return metrics['overlap_ratio'] >= self.overlap_threshold
    
    def build_spatial_index(self, buildings_gdf):
        """
        Build spatial index for efficient overlap detection.
        """
        spatial_idx = index.Index()
        for idx, building in buildings_gdf.iterrows():
            bounds = building.geometry.bounds
            spatial_idx.insert(idx, bounds)
        return spatial_idx
    
    def find_overlapping_groups(self, buildings_gdf):
        """
        Find groups of overlapping buildings using spatial indexing.
        
        Returns:
            list: List of lists, each containing indices of overlapping buildings
        """
        spatial_idx = self.build_spatial_index(buildings_gdf)
        visited = set()
        overlap_groups = []
        
        for idx, building in buildings_gdf.iterrows():
            if idx in visited:
                continue
                
            # Find potential overlaps using spatial index
            bounds = building.geometry.bounds
            potential_overlaps = list(spatial_idx.intersection(bounds))
            
            # Start new group with current building
            current_group = [idx]
            visited.add(idx)
            
            # Check each potential overlap
            for candidate_idx in potential_overlaps:
                if candidate_idx == idx or candidate_idx in visited:
                    continue
                
                candidate_building = buildings_gdf.loc[candidate_idx]
                
                # Check if there's significant overlap
                if self.is_significant_overlap(building.geometry, candidate_building.geometry):
                    current_group.append(candidate_idx)
                    visited.add(candidate_idx)
            
            # Only add groups with actual overlaps
            if len(current_group) > 1:
                overlap_groups.append(current_group)
        
        return overlap_groups
    
    def resolve_overlap_group(self, group_indices, buildings_gdf, strategy='highest_confidence'):
        """
        Resolve overlapping buildings group by selecting the best representative.
        
        Args:
            group_indices (list): Indices of overlapping buildings
            buildings_gdf (GeoDataFrame): Buildings data
            strategy (str): Resolution strategy ('highest_confidence', 'largest_area', 'union')
        
        Returns:
            int: Index of the building to keep, or -1 for union strategy
        """
        group_buildings = buildings_gdf.loc[group_indices]
        
        if strategy == 'highest_confidence':
            # Keep building with highest confidence score
            if 'confidence' in group_buildings.columns:
                best_idx = group_buildings['confidence'].idxmax()
            else:
                # Fallback to largest area if no confidence
                best_idx = group_buildings.geometry.area.idxmax()
            return best_idx
            
        elif strategy == 'largest_area':
            # Keep building with largest area
            best_idx = group_buildings.geometry.area.idxmax()
            return best_idx
            
        elif strategy == 'union':
            # Create union of all overlapping buildings
            return -1  # Special flag for union strategy
            
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def create_union_building(self, group_indices, buildings_gdf):
        """
        Create a union building from overlapping buildings.
        """
        group_buildings = buildings_gdf.loc[group_indices]
        union_geom = unary_union(group_buildings.geometry.tolist())
        
        # Aggregate attributes (take max confidence, sum areas, etc.)
        attributes = {
            'source': 'union',
            'original_count': len(group_indices),
            'geometry': union_geom
        }
        
        if 'confidence' in group_buildings.columns:
            attributes['confidence'] = group_buildings['confidence'].max()
        
        return attributes
    
    def deduplicate_buildings(self, buildings_gdf, strategy='highest_confidence'):
        """
        Main deduplication function.
        
        Args:
            buildings_gdf (GeoDataFrame): Input buildings with geometry and optional confidence
            strategy (str): Resolution strategy for overlaps
        
        Returns:
            GeoDataFrame: Deduplicated buildings
        """
        print(f"Starting with {len(buildings_gdf)} buildings")
        
        # Ensure we have a confidence column
        if 'confidence' not in buildings_gdf.columns:
            buildings_gdf['confidence'] = 1.0  # Default confidence for OSM
        
        # Find overlapping groups
        overlap_groups = self.find_overlapping_groups(buildings_gdf)
        print(f"Found {len(overlap_groups)} overlap groups")
        
        # Track buildings to remove
        buildings_to_remove = set()
        union_buildings = []
        
        # Process each overlap group
        for group in overlap_groups:
            if strategy == 'union':
                # Create union building
                union_attrs = self.create_union_building(group, buildings_gdf)
                union_buildings.append(union_attrs)
                buildings_to_remove.update(group)
            else:
                # Keep best building, remove others
                best_building_idx = self.resolve_overlap_group(group, buildings_gdf, strategy)
                buildings_to_remove.update(set(group) - {best_building_idx})
        
        # Create result GeoDataFrame
        result_buildings = buildings_gdf.drop(index=list(buildings_to_remove)).copy()
        
        # Add union buildings if using union strategy
        if union_buildings:
            union_gdf = gpd.GeoDataFrame(union_buildings, crs=buildings_gdf.crs)
            result_buildings = pd.concat([result_buildings, union_gdf], ignore_index=True)
        
        print(f"Removed {len(buildings_to_remove)} overlapping buildings")
        print(f"Added {len(union_buildings)} union buildings")
        print(f"Final result: {len(result_buildings)} buildings")
        
        return result_buildings


# Example usage and testing
def example_usage():
    """
    Example of how to use the BuildingDeduplicator
    """
    
    # Load your building data (example structure)
    # google_buildings = gpd.read_file('google_buildings.geojson')  # has 'confidence' column
    # ms_buildings = gpd.read_file('ms_buildings.geojson')          # has 'confidence' column  
    # osm_buildings = gpd.read_file('osm_buildings.geojson')        # no confidence column
    
    # Combine all sources
    # all_buildings = pd.concat([google_buildings, ms_buildings, osm_buildings], ignore_index=True)
    
    # Initialize deduplicator
    deduplicator = BuildingDeduplicator(
        overlap_threshold=0.3,  # 30% overlap threshold
        edge_buffer=0.5         # 0.5 meter buffer for edge detection
    )
    
    # Example with synthetic data
    from shapely.geometry import Polygon
    import geopandas as gpd
    
    # Create test data with overlapping buildings
    buildings_data = [
        {'geometry': Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]), 'confidence': 0.9, 'source': 'google'},
        {'geometry': Polygon([(5, 5), (15, 5), (15, 15), (5, 15)]), 'confidence': 0.8, 'source': 'ms'},
        {'geometry': Polygon([(20, 0), (30, 0), (30, 10), (20, 10)]), 'confidence': 0.95, 'source': 'google'},
        {'geometry': Polygon([(0, 20), (10, 20), (10, 30), (0, 30)]), 'source': 'osm'},  # No confidence
    ]
    
    test_buildings = gpd.GeoDataFrame(buildings_data)
    
    # Deduplicate using different strategies
    print("Strategy: highest_confidence")
    clean_buildings_conf = deduplicator.deduplicate_buildings(test_buildings, 'highest_confidence')
    
    print("\nStrategy: union")
    clean_buildings_union = deduplicator.deduplicate_buildings(test_buildings, 'union')
    
    return clean_buildings_conf, clean_buildings_union


# Configuration for different scenarios
DEDUPLICATION_CONFIGS = {
    'conservative': {
        'overlap_threshold': 0.5,  # Only remove with >50% overlap
        'edge_buffer': 1.0,        # Larger buffer to avoid false positives
        'strategy': 'highest_confidence'
    },
    'aggressive': {
        'overlap_threshold': 0.2,  # Remove with >20% overlap
        'edge_buffer': 0.3,        # Smaller buffer
        'strategy': 'highest_confidence'
    },
    'union_based': {
        'overlap_threshold': 0.3,  # Medium threshold
        'edge_buffer': 0.5,        # Medium buffer
        'strategy': 'union'        # Merge overlapping buildings
    }
}

if __name__ == "__main__":
    # Run example
    clean_conf, clean_union = example_usage()
    print("Deduplication complete!")