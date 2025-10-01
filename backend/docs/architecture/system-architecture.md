# Atlas FastAPI Service - System Architecture Design

## 1. Executive Summary

Atlas is a stateless FastAPI microservice that provides real-time geospatial data extraction from multiple authoritative sources (Microsoft Building Footprints, Google Open Buildings, OpenStreetMap) for telecom fiber network planning. The service operates without authentication, user management, or persistent storage, focusing on on-demand data aggregation and multi-format export capabilities.

## 2. Business Requirements

### 2.1 Core Functionality
- **Area of Interest (AOI) Processing**: Accept polygon boundaries and extract relevant geospatial features
- **Multi-Source Data Integration**: Query Microsoft, Google, and OSM data sources independently
- **Feature Categorization**: Organize data by feature types (buildings, roads, railways, landmarks, natural features)
- **Source Independence**: Maintain separate datasets from each source without merging or comparison
- **Interactive Visualization**: Enable layer-based toggling for different data sources and feature types
- **Multi-Format Export**: Support GeoJSON, KML/KMZ, DWG, Shapefile, and CSV exports

### 2.2 Non-Functional Requirements
- **Stateless Operation**: No user authentication, sessions, or persistent storage
- **Real-time Processing**: On-demand data extraction with acceptable response times
- **Scalability**: Handle concurrent requests efficiently
- **Reliability**: Robust error handling for external API failures
- **Flexibility**: Easy addition of new data sources and export formats

## 3. System Architecture Overview

### 3.1 High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │────│   FastAPI App    │────│  Data Sources   │
│   (Frontend)    │    │   (Backend)      │    │   (External)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────┴──────┐
                       │   Export    │
                       │  Processors │
                       └─────────────┘
```

### 3.2 Component Architecture

```
Atlas FastAPI Service
├── API Layer
│   ├── REST Endpoints
│   ├── Request Validation
│   └── Response Formatting
├── Core Processing Engine
│   ├── AOI Processor
│   ├── Data Source Orchestrator
│   └── Feature Aggregator
├── Data Source Connectors
│   ├── Google Earth Engine Connector
│   ├── Microsoft Buildings Connector
│   └── OpenStreetMap Connector
├── Export Engine
│   ├── GeoJSON Exporter
│   ├── KML/KMZ Exporter
│   ├── DWG Exporter
│   ├── Shapefile Exporter
│   └── CSV Exporter
└── Utilities
    ├── Geometry Processor
    ├── Coordinate System Handler
    └── Error Handler
```

## 4. Data Sources Integration

### 4.1 Google Earth Engine (Microsoft Buildings + Google Open Buildings)

**Data Access Method**: Python `ee` library with service account authentication
**Data Format**: GeoJSON via Earth Engine API
**Coverage**: Global building footprints

```python
# Microsoft Buildings: projects/sat-io/open-datasets/MSBuildings/{country}
# Google Buildings: GOOGLE/Research/open-buildings/v3/polygons
```

**API Key Requirements**:
- Google Earth Engine Service Account JSON key
- Project with Earth Engine API enabled

### 4.2 OpenStreetMap (Overpass API)

**Data Access Method**: Direct HTTP requests to Overpass API
**Data Format**: JSON/XML converted to GeoJSON
**Coverage**: Global crowdsourced data

```python
# Overpass API endpoint: https://overpass-api.de/api/interpreter
# Query language: Overpass QL
```

**API Key Requirements**: None (public API with rate limits)

### 4.3 Data Source Independence Strategy

Each data source maintains separate processing pipelines:

```
AOI Request
    ├── Microsoft Buildings Pipeline
    │   ├── Query GEE
    │   ├── Process Features
    │   └── Store as "microsoft_buildings"
    ├── Google Buildings Pipeline
    │   ├── Query GEE
    │   ├── Process Features
    │   └── Store as "google_buildings"
    └── OSM Pipeline
        ├── Query Overpass
        ├── Process Features
        └── Store as "osm_features"
```

## 5. API Design

### 5.1 Core Endpoints

#### POST /api/v1/extract-features
Extract geospatial features for a given AOI.

**Request Schema:**
```json
{
  "aoi_boundary": {
    "type": "Polygon",
    "coordinates": [[[lng, lat], [lng, lat], ...]]
  },
  "data_sources": {
    "microsoft_buildings": true,
    "google_buildings": true,
    "osm_buildings": true,
    "osm_roads": true,
    "osm_railways": true,
    "osm_landmarks": true,
    "osm_natural": true
  },
  "filters": {
    "min_building_area": 10,
    "road_types": ["primary", "secondary", "residential"],
    "simplification_tolerance": 0.001
  }
}
```

**Response Schema:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "processing_time": 15.32,
  "features": {
    "microsoft_buildings": {
      "count": 1250,
      "geojson": {...}
    },
    "google_buildings": {
      "count": 1180,
      "geojson": {...}
    },
    "osm_buildings": {
      "count": 890,
      "geojson": {...}
    },
    "osm_roads": {
      "count": 145,
      "geojson": {...}
    },
    "osm_railways": {
      "count": 3,
      "geojson": {...}
    },
    "osm_landmarks": {
      "count": 67,
      "geojson": {...}
    },
    "osm_natural": {
      "count": 23,
      "geojson": {...}
    }
  },
  "export_urls": {
    "geojson": "/api/v1/export/{job_id}/geojson",
    "kml": "/api/v1/export/{job_id}/kml",
    "dwg": "/api/v1/export/{job_id}/dwg",
    "shapefile": "/api/v1/export/{job_id}/shapefile",
    "csv": "/api/v1/export/{job_id}/csv"
  }
}
```

#### GET /api/v1/export/{job_id}/{format}
Export processed results in specified format.

**Supported Formats:**
- `geojson`: Raw GeoJSON for web applications
- `kml`: KML/KMZ for Google Earth Desktop
- `dwg`: AutoCAD DWG format
- `shapefile`: ESRI Shapefile for QGIS
- `csv`: Tabular data with geometry as WKT

### 5.2 Supporting Endpoints

#### GET /api/v1/health
Service health check

#### GET /api/v1/data-sources
List available data sources and their capabilities

#### POST /api/v1/validate-aoi
Validate AOI geometry and size constraints

## 6. Technology Stack

### 6.1 Core Framework
- **FastAPI**: Async web framework with automatic OpenAPI documentation
- **Python 3.11+**: Modern Python with type hints
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

### 6.2 Geospatial Libraries
- **geopandas**: Geospatial data manipulation
- **shapely**: Geometric operations
- **fiona**: Geospatial file I/O
- **pyproj**: Coordinate system transformations
- **folium**: Interactive map visualization

### 6.3 Data Source Libraries
- **earthengine-api**: Google Earth Engine Python client
- **osmnx**: OpenStreetMap data extraction
- **overpy**: Overpass API client
- **requests**: HTTP client for API calls

### 6.4 Export Libraries
- **simplekml**: KML/KMZ generation
- **ezdxf**: DWG file creation
- **openpyxl**: Excel export capabilities

### 6.5 Infrastructure
- **Docker**: Containerization
- **Redis** (optional): Temporary result caching
- **Nginx**: Reverse proxy and load balancing

## 7. Data Processing Pipeline

### 7.1 Request Processing Flow

```
1. Request Validation
   ├── AOI geometry validation
   ├── Size constraints check
   └── Parameter validation

2. Parallel Data Source Queries
   ├── Microsoft Buildings (via GEE)
   ├── Google Buildings (via GEE)
   └── OSM Features (via Overpass)

3. Feature Processing
   ├── Geometry validation
   ├── Coordinate system normalization
   ├── Feature classification
   └── Quality filtering

4. Response Assembly
   ├── Organize by source and type
   ├── Generate statistics
   └── Create export URLs

5. Export Generation (on-demand)
   ├── Format-specific conversion
   ├── File packaging
   └── Download link creation
```

### 7.2 Feature Classification Schema

#### Buildings
```python
BUILDING_SOURCES = {
    "microsoft_buildings": {
        "source": "Microsoft Building Footprints",
        "attributes": ["confidence", "height"],
        "color": "#FF6B6B"  # Red
    },
    "google_buildings": {
        "source": "Google Open Buildings",
        "attributes": ["confidence"],
        "color": "#4ECDC4"  # Teal
    },
    "osm_buildings": {
        "source": "OpenStreetMap",
        "attributes": ["building_type", "levels", "material"],
        "color": "#45B7D1"  # Blue
    }
}
```

#### Infrastructure
```python
INFRASTRUCTURE_FEATURES = {
    "roads": {
        "hierarchy": ["motorway", "trunk", "primary", "secondary", "tertiary", "residential"],
        "color": "#FFA07A"  # Light Salmon
    },
    "railways": {
        "types": ["rail", "light_rail", "subway", "tram"],
        "color": "#98D8C8"  # Mint
    },
    "landmarks": {
        "categories": ["amenity", "tourism", "shop", "leisure"],
        "color": "#F7DC6F"  # Light Yellow
    },
    "natural": {
        "types": ["water", "forest", "park", "river"],
        "color": "#82E0AA"  # Light Green
    }
}
```

## 8. Export Format Specifications

### 8.1 GeoJSON Export
- **Use Case**: Web applications, JavaScript mapping libraries
- **Structure**: Separate FeatureCollection for each data source
- **Features**: Full attribute preservation

### 8.2 KML/KMZ Export
- **Use Case**: Google Earth Desktop
- **Structure**: Folder hierarchy by source and feature type
- **Features**: Custom styling, description popups, ground overlays

### 8.3 DWG Export
- **Use Case**: AutoCAD, architectural applications
- **Structure**: Layers by source and feature type
- **Features**: Polylines, polygons, text labels

### 8.4 Shapefile Export
- **Use Case**: QGIS, ArcGIS, professional GIS
- **Structure**: Separate shapefiles for each feature type
- **Features**: DBF attribute tables, PRJ projection files

### 8.5 CSV Export
- **Use Case**: Spreadsheet analysis, reporting
- **Structure**: Tabular data with WKT geometry
- **Features**: Feature counts, basic statistics

## 9. Error Handling Strategy

### 9.1 External API Failures
```python
ERROR_HANDLING_STRATEGY = {
    "google_earth_engine": {
        "timeout": 30,
        "retries": 3,
        "fallback": "partial_results"
    },
    "overpass_api": {
        "timeout": 25,
        "retries": 2,
        "fallback": "cached_results"
    },
    "rate_limits": {
        "strategy": "exponential_backoff",
        "max_wait": 60
    }
}
```

### 9.2 Error Response Format
```json
{
  "error": true,
  "error_code": "DATA_SOURCE_TIMEOUT",
  "message": "Google Earth Engine request timed out",
  "partial_results": {
    "available_sources": ["osm_buildings", "osm_roads"],
    "failed_sources": ["microsoft_buildings", "google_buildings"]
  },
  "retry_suggestion": "Reduce AOI size or try again later"
}
```

## 10. Performance Considerations

### 10.1 Optimization Strategies
- **Async Processing**: Parallel data source queries
- **Geometry Simplification**: Configurable tolerance levels
- **Result Streaming**: Large dataset handling
- **Memory Management**: Efficient data structures

### 10.2 Size Limitations
```python
CONSTRAINTS = {
    "max_aoi_area": "100 km²",
    "max_features_per_source": 50000,
    "max_response_size": "500 MB",
    "request_timeout": "5 minutes"
}
```

## 11. Deployment Architecture

### 11.1 Containerized Deployment
```dockerfile
# FastAPI application container
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Service Dependencies
```yaml
version: '3.8'
services:
  atlas-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/keys/gee-service-account.json
      - OVERPASS_API_URL=https://overpass-api.de/api/interpreter
    volumes:
      - ./keys:/keys
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## 12. Security Considerations

### 12.1 API Security
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Sanitize all inputs
- **CORS Configuration**: Control cross-origin requests
- **API Key Protection**: Secure credential storage

### 12.2 Data Privacy
- **No Data Persistence**: Stateless operation
- **Temporary Storage**: Short-lived export files
- **Access Logs**: Minimal logging without sensitive data

## 13. Monitoring and Observability

### 13.1 Health Checks
```python
HEALTH_ENDPOINTS = {
    "/health": "Service health",
    "/health/data-sources": "External API availability",
    "/health/ready": "Readiness probe",
    "/health/live": "Liveness probe"
}
```

### 13.2 Metrics Collection
- Request/response times
- Data source success rates
- Feature extraction counts
- Export format usage
- Error rates by type

## 14. Development Guidelines

### 14.1 Code Organization
```
src/
├── main.py                 # FastAPI application entry point
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── extract.py      # Feature extraction endpoints
│   │   ├── export.py       # Export endpoints
│   │   └── health.py       # Health check endpoints
│   └── schemas/
│       ├── request.py      # Pydantic request models
│       └── response.py     # Pydantic response models
├── core/
│   ├── __init__.py
│   ├── processors/
│   │   ├── aoi_processor.py
│   │   ├── feature_aggregator.py
│   │   └── geometry_processor.py
│   └── data_sources/
│       ├── base.py         # Abstract base connector
│       ├── google_earth_engine.py
│       ├── microsoft_buildings.py
│       └── openstreetmap.py
├── exporters/
│   ├── __init__.py
│   ├── base.py            # Abstract base exporter
│   ├── geojson.py
│   ├── kml.py
│   ├── dwg.py
│   ├── shapefile.py
│   └── csv.py
├── models/
│   ├── __init__.py
│   ├── features.py        # Feature data models
│   └── geometry.py        # Geometry models
└── utils/
    ├── __init__.py
    ├── coordinate_systems.py
    ├── validators.py
    └── exceptions.py
```

### 14.2 Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: Data source connectivity
- **Performance Tests**: Load testing with various AOI sizes
- **End-to-End Tests**: Complete workflow validation

## 15. API Key Acquisition Guide

### 15.1 Google Earth Engine Setup
1. Create Google Cloud Project
2. Enable Earth Engine API
3. Create Service Account
4. Download JSON key file
5. Configure environment variable

### 15.2 OpenStreetMap Access
- No API key required
- Respect rate limits (2 requests/second)
- Use public Overpass API instances

## 16. Future Enhancements

### 16.1 Planned Features
- **Additional Data Sources**: Local government datasets
- **Advanced Filtering**: Machine learning-based quality assessment
- **Batch Processing**: Multiple AOI processing
- **WebSocket Support**: Real-time progress updates

### 16.2 Scalability Improvements
- **Horizontal Scaling**: Load balancer configuration
- **Caching Layer**: Redis for frequently requested areas
- **CDN Integration**: Static export file delivery
- **Database Integration**: Optional result persistence

---

This architecture provides a solid foundation for building a robust, scalable geospatial data extraction service that meets all specified requirements while maintaining flexibility for future enhancements.