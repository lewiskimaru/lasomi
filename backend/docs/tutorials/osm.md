# Python OpenStreetMap Feature Extraction Guide

## Overview

This guide shows you how to build a Python-based map feature extraction engine using OpenStreetMap data. Instead of manually digitizing features from Google Earth, you can automatically extract buildings, roads, railways, and other landmarks from OSM data.

## Why Use OSM Instead of Manual Digitization?

- **Time Savings**: Extract thousands of features in seconds instead of hours
- **Accuracy**: OSM data is often more accurate than manual tracing
- **Completeness**: Get attributes like road names, building types, etc. automatically
- **Consistency**: Standardized data format and classification
- **Free**: No licensing fees or usage restrictions

## Required Libraries

```bash
pip install osmnx geopandas folium overpy requests shapely matplotlib contextily
```

## Method 1: Using OSMnx (Recommended for Most Cases)

OSMnx is the most user-friendly library for extracting OSM features.

### Basic Setup

```python
import osmnx as ox
import geopandas as gpd
import folium
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

# Configure OSMnx
ox.config(use_cache=True, log_console=True)
```

### Extract Features by Place Name

```python
def extract_features_by_place(place_name):
    """Extract all major features from a named place"""
    
    # Get the boundary of the place
    gdf_boundary = ox.geocode_to_gdf(place_name)
    
    # Extract street network
    print("Extracting roads...")
    roads = ox.graph_to_gdfs(ox.graph_from_place(place_name, network_type='all'))
    
    # Extract buildings
    print("Extracting buildings...")
    buildings = ox.geometries_from_place(place_name, tags={'building': True})
    
    # Extract railways
    print("Extracting railways...")
    railways = ox.geometries_from_place(place_name, tags={'railway': True})
    
    # Extract landmarks (POIs)
    print("Extracting landmarks...")
    landmarks = ox.geometries_from_place(place_name, tags={
        'amenity': True,
        'tourism': True,
        'shop': True,
        'leisure': True
    })
    
    return {
        'boundary': gdf_boundary,
        'roads': roads,
        'buildings': buildings,
        'railways': railways,
        'landmarks': landmarks
    }

# Example usage
place = "Westlands, Nairobi, Kenya"
features = extract_features_by_place(place)
```

### Extract Features by Bounding Box

```python
def extract_features_by_bbox(north, south, east, west):
    """Extract features from a bounding box"""
    
    bbox = (north, south, east, west)  # (N, S, E, W)
    
    # Roads
    roads = ox.graph_to_gdfs(ox.graph_from_bbox(*bbox, network_type='all'))
    
    # Buildings
    buildings = ox.geometries_from_bbox(*bbox, tags={'building': True})
    
    # Railways
    railways = ox.geometries_from_bbox(*bbox, tags={'railway': True})
    
    # Water features
    water = ox.geometries_from_bbox(*bbox, tags={'natural': 'water'})
    
    # Green spaces
    green_spaces = ox.geometries_from_bbox(*bbox, tags={
        'leisure': ['park', 'garden', 'recreation_ground'],
        'landuse': ['forest', 'grass']
    })
    
    return {
        'roads': roads,
        'buildings': buildings,
        'railways': railways,
        'water': water,
        'green_spaces': green_spaces
    }

# Example for your Nairobi coordinates
features = extract_features_by_bbox(
    north=-1.315,
    south=-1.320, 
    east=36.898,
    west=36.894
)
```

### Extract Features by Custom Polygon

```python
def extract_features_by_polygon(polygon_coords):
    """Extract features from a custom polygon boundary"""
    
    # Create polygon from coordinates
    # Expected format: [(lon, lat), (lon, lat), ...]
    polygon = Polygon(polygon_coords)
    
    # Convert to GeoDataFrame
    gdf_polygon = gpd.GeoDataFrame([1], geometry=[polygon], crs="EPSG:4326")
    
    # Extract features within polygon
    buildings = ox.geometries_from_polygon(polygon, tags={'building': True})
    roads = ox.graph_to_gdfs(ox.graph_from_polygon(polygon, network_type='all'))
    railways = ox.geometries_from_polygon(polygon, tags={'railway': True})
    
    return {
        'boundary': gdf_polygon,
        'buildings': buildings,
        'roads': roads,
        'railways': railways
    }

# Using your polygon coordinates
your_polygon = [
    (36.89398291607937, -1.3162570972426764),
    (36.896214513979764, -1.3200755521178542),
    (36.89823153515896, -1.3188527891154982),
    (36.89605486823382, -1.3152353991157921),
    (36.89398291607937, -1.3162570972426764)
]

features = extract_features_by_polygon(your_polygon)
```

## Method 2: Using Overpass API with OverPy

For more control over queries and accessing the full range of OSM tags.

```python
import overpy
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon as ShapelyPolygon

def query_overpass(query):
    """Execute Overpass API query"""
    api = overpy.Overpass()
    return api.query(query)

def extract_with_overpass(bbox):
    """Extract features using Overpass API"""
    
    # Format: south, west, north, east
    bbox_str = f"{bbox[1]},{bbox[3]},{bbox[0]},{bbox[2]}"
    
    # Roads query
    roads_query = f"""
    [out:json][timeout:25];
    (
      way["highway"]({bbox_str});
    );
    out geom;
    """
    
    # Buildings query  
    buildings_query = f"""
    [out:json][timeout:25];
    (
      way["building"]({bbox_str});
      relation["building"]({bbox_str});
    );
    out geom;
    """
    
    # Execute queries
    roads_result = query_overpass(roads_query)
    buildings_result = query_overpass(buildings_query)
    
    # Convert to GeoDataFrames
    roads_gdf = overpass_to_gdf(roads_result.ways, 'road')
    buildings_gdf = overpass_to_gdf(buildings_result.ways, 'building')
    
    return roads_gdf, buildings_gdf

def overpass_to_gdf(ways, feature_type):
    """Convert Overpass ways to GeoDataFrame"""
    
    features = []
    for way in ways:
        # Extract coordinates
        coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
        
        # Create geometry
        if len(coords) > 2 and coords[0] == coords[-1]:  # Closed way (polygon)
            geom = ShapelyPolygon(coords)
        else:  # Open way (linestring)
            geom = LineString(coords)
        
        # Extract tags
        tags = dict(way.tags)
        tags['osm_id'] = way.id
        tags['feature_type'] = feature_type
        tags['geometry'] = geom
        
        features.append(tags)
    
    return gpd.GeoDataFrame(features, crs='EPSG:4326')
```

## Feature Classification and Filtering

```python
def classify_roads(roads_gdf):
    """Classify roads by type"""
    
    road_hierarchy = {
        'motorway': 1,
        'trunk': 2, 
        'primary': 3,
        'secondary': 4,
        'tertiary': 5,
        'residential': 6,
        'service': 7,
        'track': 8,
        'path': 9,
        'footway': 10
    }
    
    if 'highway' in roads_gdf.columns:
        roads_gdf['road_rank'] = roads_gdf['highway'].map(road_hierarchy).fillna(99)
        roads_gdf = roads_gdf.sort_values('road_rank')
    
    return roads_gdf

def classify_buildings(buildings_gdf):
    """Classify buildings by type"""
    
    building_types = {
        'residential': 'Residential',
        'commercial': 'Commercial', 
        'industrial': 'Industrial',
        'retail': 'Retail',
        'office': 'Office',
        'school': 'Education',
        'hospital': 'Healthcare',
        'religious': 'Religious',
        'yes': 'Generic Building'
    }
    
    if 'building' in buildings_gdf.columns:
        buildings_gdf['building_category'] = buildings_gdf['building'].map(building_types).fillna('Other')
    
    return buildings_gdf

def filter_features_by_size(gdf, min_area=None, max_area=None):
    """Filter features by area (for polygons)"""
    
    if min_area or max_area:
        # Calculate area in square meters (approximate)
        gdf_utm = gdf.to_crs(gdf.estimate_utm_crs())
        areas = gdf_utm.geometry.area
        
        if min_area:
            gdf = gdf[areas >= min_area]
        if max_area:
            gdf = gdf[areas <= max_area]
    
    return gdf
```

## Visualization

```python
def visualize_features(features_dict, save_path=None):
    """Create an interactive map with all features"""
    
    # Get the center of the area
    if 'boundary' in features_dict:
        bounds = features_dict['boundary'].total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
    else:
        # Use first available feature for centering
        first_gdf = next(iter(features_dict.values()))
        bounds = first_gdf.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
    
    # Create folium map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles='OpenStreetMap'
    )
    
    # Define colors for different feature types
    colors = {
        'buildings': 'red',
        'roads': 'blue', 
        'railways': 'green',
        'water': 'cyan',
        'green_spaces': 'darkgreen',
        'landmarks': 'orange'
    }
    
    # Add each feature type to map
    for feature_name, gdf in features_dict.items():
        if feature_name == 'boundary':
            continue
            
        color = colors.get(feature_name, 'gray')
        
        # Add to map
        folium.GeoJson(
            gdf.to_json(),
            style_function=lambda x, color=color: {
                'color': color,
                'weight': 2,
                'fillOpacity': 0.3
            },
            popup=folium.GeoJsonPopup(fields=['osm_id'], labels=False)
        ).add_to(m)
    
    if save_path:
        m.save(save_path)
    
    return m

# Example usage
features = extract_features_by_place("Westlands, Nairobi, Kenya")
map_viz = visualize_features(features, "nairobi_features.html")
```

## Export Features

```python
def export_features(features_dict, output_dir="osm_exports"):
    """Export features to various formats"""
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for feature_name, gdf in features_dict.items():
        if len(gdf) > 0:
            base_path = os.path.join(output_dir, feature_name)
            
            # Export to different formats
            gdf.to_file(f"{base_path}.geojson", driver='GeoJSON')
            gdf.to_file(f"{base_path}.shp", driver='ESRI Shapefile')
            gdf.to_csv(f"{base_path}.csv")
            
            print(f"Exported {feature_name}: {len(gdf)} features")

# Example usage
features = extract_features_by_place("Westlands, Nairobi, Kenya")
export_features(features)
```

## Complete Workflow Example

```python
def automated_map_extraction(location, output_dir="map_data"):
    """Complete automated map feature extraction workflow"""
    
    print(f"Starting extraction for: {location}")
    
    # Extract features
    try:
        features = extract_features_by_place(location)
        print("✓ Feature extraction completed")
    except Exception as e:
        print(f"✗ Feature extraction failed: {e}")
        return None
    
    # Classify and filter
    if 'roads' in features and len(features['roads'][1]) > 0:  # roads returns (nodes, edges)
        features['roads'] = classify_roads(features['roads'][1])
    
    if 'buildings' in features and len(features['buildings']) > 0:
        features['buildings'] = classify_buildings(features['buildings'])
        features['buildings'] = filter_features_by_size(features['buildings'], min_area=10)
    
    print("✓ Classification and filtering completed")
    
    # Visualize
    try:
        map_viz = visualize_features(features, f"{output_dir}/map.html")
        print("✓ Visualization created")
    except Exception as e:
        print(f"⚠ Visualization failed: {e}")
    
    # Export
    try:
        export_features(features, output_dir)
        print("✓ Data exported")
    except Exception as e:
        print(f"⚠ Export failed: {e}")
    
    # Print summary
    print("\n=== EXTRACTION SUMMARY ===")
    for feature_name, gdf in features.items():
        if hasattr(gdf, '__len__'):
            print(f"{feature_name.capitalize()}: {len(gdf)} features")
    
    return features

# Run the complete workflow
features = automated_map_extraction("Westlands, Nairobi, Kenya", "nairobi_westlands_data")
```

## Error Handling and Optimization

```python
def robust_feature_extraction(location, max_retries=3):
    """Robust feature extraction with error handling"""
    
    import time
    
    for attempt in range(max_retries):
        try:
            # Add delay between attempts
            if attempt > 0:
                time.sleep(5)
            
            features = extract_features_by_place(location)
            return features
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("All attempts failed")
                return None
    
def batch_extraction(locations_list):
    """Extract features for multiple locations"""
    
    results = {}
    
    for location in locations_list:
        print(f"\nProcessing: {location}")
        features = robust_feature_extraction(location)
        
        if features:
            results[location] = features
            print(f"✓ Completed: {location}")
        else:
            print(f"✗ Failed: {location}")
    
    return results

# Example batch processing
locations = [
    "Westlands, Nairobi, Kenya",
    "Karen, Nairobi, Kenya", 
    "Kilimani, Nairobi, Kenya"
]

batch_results = batch_extraction(locations)
```

## Advanced Tips

### 1. Performance Optimization
- Use `ox.config(use_cache=True)` to cache results
- Process smaller areas for better performance
- Use multiprocessing for batch operations

### 2. Data Quality
- Always check for empty results before processing
- Validate geometries before export
- Handle CRS transformations carefully

### 3. Custom Tags
```python
# Extract specific POI types
hospitals = ox.geometries_from_place(place, tags={'amenity': 'hospital'})
schools = ox.geometries_from_place(place, tags={'amenity': 'school'})
restaurants = ox.geometries_from_place(place, tags={'amenity': 'restaurant'})
```
```sql
[out:json][timeout:25];
(
  way["highway"]({{bbox}});
  way["railway"]({{bbox}});
  way["building"]({{bbox}});
  relation["building"]({{bbox}});
);
out geom;
```
### 4. Integration with GIS
- Export to Shapefile for QGIS/ArcGIS
- Use GeoJSON for web mapping
- Convert to PostGIS for database storage

This automated approach will save you countless hours compared to manual digitization and provide more accurate, attributed data for your mapping projects.