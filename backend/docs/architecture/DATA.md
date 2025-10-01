# Data Sources Documentation
## Telecom GIS API Data Sources Integration Guide

### Overview

This document provides detailed information about accessing and integrating with the primary geospatial data sources for the Telecom GIS API. Each source has different access methods, licensing requirements, data formats, and usage limitations that must be carefully considered during implementation.

---

## 1. Google Open Buildings Dataset

### Dataset Overview
- **Provider**: Google Research - Open Buildings project based in Ghana, focusing on Africa and Global South
- **Coverage**: 1.8B building detections in Africa, Latin America, Caribbean, South Asia and Southeast Asia spanning 58M km²
- **Data Source**: High-resolution 50cm satellite imagery
- **Last Updated**: May 2023

### Data Access Methods

#### Method 1: Google Earth Engine (Recommended for API)
- **Dataset ID**: `GOOGLE/Research/open-buildings/v3/polygons`
- **Access Requirements**: 
  - Google Earth Engine account (free for non-commercial use)
  - Service account authentication for API access
  - Earth Engine Python API (`ee` library)

**Setup Steps:**
1. Create Google Earth Engine account at [earthengine.google.com](https://earthengine.google.com)
2. Create service account in Google Cloud Console
3. Download service account JSON key
4. Install Earth Engine API: `pip install earthengine-api`

**Python Integration Example:**
```python
import ee

# Authenticate with service account
ee.Authenticate()
ee.Initialize()

# Load the Open Buildings dataset
buildings = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons')

# Filter by area of interest (AOI)
aoi = ee.Geometry.Rectangle([lng_min, lat_min, lng_max, lat_max])
filtered_buildings = buildings.filterBounds(aoi)

# Export to GeoJSON
task = ee.batch.Export.table.toDrive(
    collection=filtered_buildings,
    description='buildings_export',
    fileFormat='GeoJSON'
)
```

#### Method 2: Direct Download via Community Tools
- **Tool**: opengeos/open-buildings Python package
- **Installation**: `pip install open-buildings`
- **Usage**: Command-line interface allows supplying GeoJSON boundary files to download buildings in common GIS formats

#### Method 3: Third-Party Aggregators
- **Source Cooperative**: Beta platform providing HTTP access without proprietary APIs
- **Awesome GEE Community**: Consolidated Google-Microsoft dataset in cloud-native formats (GeoParquet, FlatGeobuf, PMTiles)

### Data Structure
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[lng, lat], ...]]
  },
  "properties": {
    "area_in_meters": 245.67,
    "confidence": 0.85,
    "full_plus_code": "6FR562F2+2G"
  }
}
```

### Key Attributes
- **area_in_meters**: Area in square meters of the polygon
- **confidence**: Confidence score [0.65; 1.0] assigned by the model
- **full_plus_code**: Plus Code corresponding to the center of the building
- **longitude_latitude**: Centroid of the polygon

### Licensing & Attribution
- **License**: Open Data License (permissive)
- **Attribution**: Required - "Data © Google"
- **Commercial Use**: Permitted
- **Citation**: W. Sirko, S. Kashubin, M. Ritter, et al. Continental-scale building detection from high resolution satellite imagery. arXiv:2107.12283, 2021

### Rate Limits & Quotas
- **Earth Engine**: 
  - 5,000 requests/day (free tier)
  - 50 concurrent requests
  - 250MB memory limit per request
- **Processing Time**: Varies based on AOI size (seconds to minutes)

---

## 2. Microsoft Building Footprints

### Dataset Overview
- **Provider**: Microsoft Bing Maps
- **Coverage**: 1.4B building footprints worldwide from imagery between 2014-2024
- **Data Source**: Maxar, Airbus, and IGN France imagery processed using deep neural networks
- **Update Frequency**: Monthly updates with recent additions in February 2025

### Data Access Methods

#### Method 1: Direct Download from Azure Storage (Recommended)
- **Index File**: https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv
- **Format**: Line-delimited GeoJSON (.csv.gz files)
- **Partitioning**: Country-quadkey partitioned files using L9 quad keys

**Python Integration Example:**
```python
import pandas as pd
import requests
import gzip
import json

# Download the dataset index
index_url = "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv"
index_df = pd.read_csv(index_url)

# Filter by country/region
country_files = index_df[index_df['Location'] == 'Kenya']

# Download specific files
for _, row in country_files.iterrows():
    response = requests.get(row['Url'])
    with gzip.open(io.BytesIO(response.content), 'rt') as f:
        for line in f:
            building = json.loads(line)
            # Process building footprint
```

#### Method 2: Microsoft Planetary Computer API
- **Endpoint**: Planetary Computer STAC API
- **Access**: Free, no authentication required
- **Format**: Cloud-optimized formats

#### Method 3: GitHub Repository Access
- **Global Repository**: microsoft/GlobalMLBuildingFootprints
- **Regional Repositories**: 
  - US: microsoft/USBuildingFootprints (129M buildings)
  - Canada: microsoft/CanadianBuildingFootprints (11M buildings)
  - Australia: microsoft/AustraliaBuildingFootprints (11M buildings)

### Data Structure
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[lng, lat], ...]]
  },
  "properties": {
    "height": 15.2,
    "confidence": 0.92,
    "capture_dates_range": "2020/2023",
    "release_version": "v3.1"
  }
}
```

### Key Attributes
- **height**: Height estimates in meters (average height within building polygon, -1 for no estimate)
- **confidence**: Detection confidence scores between 0-1, with higher values indicating higher detection confidence
- **capture_dates_range**: Imagery capture date range
- **release_version**: Dataset version for tracking updates

### Quality Metrics
Microsoft provides detailed quality metrics by region:

| Region | Precision | Recall | False Positive Rate |
|--------|-----------|--------|-------------------|
| Africa | 94.4% | 70.9% | 1.1% |
| Europe | 94.3% | 85.9% | 1.4% |
| North America | - | - | 1.0% |
| South Asia | 94.8% | 76.7% | 1.4% |

### Licensing & Attribution
- **License**: Open Data Commons Open Database License (ODbL)
- **Attribution**: Required - "© Microsoft"
- **Commercial Use**: Permitted with attribution
- **OSM Integration**: Data is available in HOT Tasking Manager and Facebook Rapid editor

### Rate Limits & Quotas
- **Direct Download**: No rate limits (HTTP-based)
- **File Sizes**: Very large files requiring parallel processing or memory-efficient streaming
- **Bandwidth**: Limited by your internet connection

### Processing Considerations
Microsoft provides a script for handling large files:
- Use parallel processing tools (Spark, Dask)
- Implement streaming readers for memory efficiency
- Convert .csv.gz extensions using provided utilities

---

## 3. OpenStreetMap (OSM) via Overpass API

### Dataset Overview
- **Provider**: OpenStreetMap community (crowdsourced)
- **Coverage**: Global coverage with varying data density
- **Data Types**: Buildings, roads, landmarks, amenities, infrastructure, OpenRailwayMap
- **Update Frequency**: Real-time updates from global contributors

### Data Access Methods

#### Method 1: Overpass API (Recommended)
- **Primary Endpoint**: `https://overpass-api.de/api/interpreter`
- **Mirror Endpoints**: Multiple mirrors available for load distribution
- **Query Language**: Overpass QL (Query Language) and Overpass XML

**Python Integration Example:**
```python
import requests

def query_overpass(query):
    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={'data': query})
    return response.json()

# Query for buildings in bounding box
buildings_query = """
[out:json][timeout:25];
(
  way["building"](bbox);
  relation["building"](bbox);
);
out geom;
"""

# Query for roads
roads_query = """
[out:json][timeout:25];
(
  way["highway"](bbox);
);
out geom;
"""

# Query for landmarks/amenities
landmarks_query = """
[out:json][timeout:25];
(
  node["amenity"](bbox);
  way["amenity"](bbox);
  node["tourism"](bbox);
  way["tourism"](bbox);
);
out geom;
"""
```

#### Method 2: Overpass Turbo (Development & Testing)
- **URL**: https://overpass-turbo.eu/
- **Purpose**: Web-based tool for testing queries and visualizing results on interactive map
- **Features**: Query wizard for beginners, direct query execution

#### Method 3: Third-Party APIs
- **Geoapify**: Places API with OSM data integration
- **Nominatim**: Geocoding service with OSM data
- **Hot OSM**: Specialized humanitarian data access

### Query Examples by Data Type

#### Buildings
```sql
[out:json][timeout:25];
(
  way["building"]({{bbox}});
  relation["building"]["type"="multipolygon"]({{bbox}});
);
out geom;
```

#### Roads by Classification
```sql
[out:json][timeout:25];
(
  way["highway"~"^(primary|secondary|tertiary|residential)$"]({{bbox}});
);
out geom;
```

#### Landmarks and Amenities
```sql
[out:json][timeout:25];
(
  node["amenity"~"^(hospital|school|bank|restaurant)$"]({{bbox}});
  way["amenity"~"^(hospital|school|bank|restaurant)$"]({{bbox}});
  node["tourism"~"^(attraction|hotel|museum)$"]({{bbox}});
  way["tourism"~"^(attraction|hotel|museum)$"]({{bbox}});
);
out geom;
```

### Data Structure
```json
{
  "version": 0.6,
  "generator": "Overpass API",
  "elements": [
    {
      "type": "way",
      "id": 123456,
      "nodes": [1, 2, 3, 4, 1],
      "tags": {
        "building": "residential",
        "addr:street": "Main Street",
        "height": "10"
      },
      "geometry": [
        {"lat": -1.2921, "lon": 36.8219},
        {"lat": -1.2922, "lon": 36.8220}
      ]
    }
  ]
}
```

### Key Tag Categories

#### Building Tags
- `building=*`: residential, commercial, industrial, yes
- `building:levels=*`: Number of floors
- `height=*`: Building height in meters
- `addr:*`: Address information

#### Highway/Road Tags
- `highway=*`: primary, secondary, tertiary, residential, footway
- `surface=*`: paved, unpaved, asphalt, concrete
- `lanes=*`: Number of lanes
- `maxspeed=*`: Speed limits

#### Amenity Tags
- `amenity=*`: hospital, school, bank, restaurant, fuel
- `tourism=*`: hotel, museum, attraction
- `shop=*`: Various retail categories

### Rate Limits & Usage Policy
- **Query Limit**: 10,000 queries per day per IP address
- **Timeout**: Maximum 180 seconds per query (recommended: 25s)
- **Concurrent Requests**: Maximum 2 simultaneous requests
- **Data Volume**: No explicit limits, but queries should be reasonable
- **Fair Use**: Intended for legitimate use cases, not data scraping

### Licensing & Attribution
- **License**: Open Database License (ODbL)
- **Attribution**: Required - "© OpenStreetMap contributors"
- **Share-Alike**: Derivative works must use compatible license
- **Commercial Use**: Permitted with proper attribution

---

## 4. Integration Architecture Recommendations

### Multi-Source Data Strategy

#### Priority Hierarchy
1. **Primary Source Selection**:
   - Microsoft Building Footprints (most comprehensive, recent)
   - Google Open Buildings (good for Global South)
   - OSM (real-time updates, local knowledge)

2. **Fallback Strategy**:
   - Query Microsoft first for building footprints
   - Fall back to Google for uncovered regions
   - Use OSM for roads and landmarks universally

3. **Data Deduplication**:
   - Implement spatial overlap detection (buffer tolerance: 1-2 meters)
   - Prioritize by confidence scores
   - Maintain source attribution

### Caching Strategy

#### Geographic Partitioning
```python
# Implement quadkey-based caching
def get_quadkey(lat, lng, level=15):
    # Convert lat/lng to quadkey for spatial indexing
    pass

# Cache structure
cache_key = f"buildings_{quadkey}_{source}_{timestamp}"
```

#### Cache Invalidation
- Microsoft: Monthly refresh cycle
- Google: Check for dataset updates quarterly
- OSM: Daily refresh for high-change areas

### Error Handling & Resilience

#### Source-Specific Error Handling
```python
class DataSourceError(Exception):
    def __init__(self, source, error_type, message):
        self.source = source
        self.error_type = error_type
        self.message = message

# Implement circuit breaker pattern
class SourceManager:
    def __init__(self):
        self.failure_counts = {}
        self.circuit_open = {}
    
    def is_available(self, source):
        return not self.circuit_open.get(source, False)
```

#### Retry Logic
- Exponential backoff for transient failures
- Different retry strategies per source:
  - Microsoft: Retry network errors, skip missing tiles
  - Google Earth Engine: Retry quota errors with delay
  - OSM Overpass: Retry timeout errors, respect rate limits

### Performance Optimization

#### Parallel Processing
```python
import asyncio
import aiohttp

async def fetch_all_sources(aoi_bounds):
    tasks = [
        fetch_microsoft_buildings(aoi_bounds),
        fetch_google_buildings(aoi_bounds),
        fetch_osm_roads(aoi_bounds),
        fetch_osm_landmarks(aoi_bounds)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return process_results(results)
```

#### Memory Management
- Stream large datasets instead of loading entirely in memory
- Implement spatial indexing for efficient filtering
- Use memory-mapped files for large cached datasets

---

## 5. Implementation Checklist

### Pre-Development Setup
- [ ] Create Google Earth Engine account and service account
- [ ] Set up authentication for Google services
- [ ] Test Microsoft dataset access and download speeds
- [ ] Verify OSM Overpass API access and rate limits
- [ ] Design database schema for caching layer

### Development Phase
- [ ] Implement individual data source connectors
- [ ] Create unified data transformation pipeline
- [ ] Develop spatial deduplication algorithms
- [ ] Build error handling and retry mechanisms
- [ ] Implement caching and invalidation strategies

### Testing Phase
- [ ] Test with various AOI sizes (small: <1km², large: >10km²)
- [ ] Validate data quality across different regions
- [ ] Performance testing under concurrent load
- [ ] Verify license compliance and attribution
- [ ] Test failover scenarios

### Production Deployment
- [ ] Monitor API quotas and usage patterns
- [ ] Set up alerting for data source failures
- [ ] Implement usage analytics and optimization
- [ ] Document API endpoints and data schemas
- [ ] Prepare user documentation and examples

---

## 6. Cost Analysis

### Operational Costs (Monthly)

#### Google Earth Engine
- **Free Tier**: 5,000 requests/day
- **Paid Tier**: $0.10 per 1,000 requests (after free tier)
- **Estimated**: $50-200/month for moderate usage

#### Microsoft Building Footprints
- **Data Access**: Free (bandwidth costs only)
- **Storage**: $10-50/month for local caching
- **Processing**: Variable based on compute resources

#### OpenStreetMap
- **API Access**: Free
- **Infrastructure**: Consider OSM donation for heavy usage
- **Estimated**: $0-25/month

#### Infrastructure
- **Database (PostGIS)**: $100-300/month
- **Application Hosting**: $200-500/month
- **Caching (Redis)**: $50-150/month
- **Bandwidth**: $50-200/month

### Total Estimated Monthly Cost: $460-1,425

This documentation provides the foundation for implementing a robust, multi-source geospatial data aggregation system. Each source has been thoroughly researched to ensure successful integration while respecting licensing terms and technical limitations.