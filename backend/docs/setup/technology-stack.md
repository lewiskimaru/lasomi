# Technology Stack and Dependencies Specification

## Overview

This document outlines the complete technology stack for the Atlas FastAPI service, including core dependencies, development tools, and infrastructure requirements. The stack is optimized for geospatial data processing, multi-format export capabilities, and production deployment.

## Core Technology Stack

### 1. Web Framework
- **FastAPI 0.104.1**: Modern, fast async web framework
  - Automatic OpenAPI/Swagger documentation
  - Built-in data validation with Pydantic
  - Async/await support for concurrent operations
  - Type hints throughout

- **Uvicorn 0.24.0**: ASGI server
  - High-performance async server
  - Hot reloading for development
  - Production-ready with proper process management

### 2. Geospatial Processing Core

#### Primary Geospatial Libraries
```python
geopandas==0.14.1      # High-level geospatial data manipulation
shapely==2.0.2         # Geometric operations and spatial analysis
fiona==1.9.5          # Geospatial file I/O operations
pyproj==3.6.1         # Coordinate system transformations
rasterio==1.3.9       # Raster data processing (if needed)
```

#### Why These Libraries?
- **GeoPandas**: Built on pandas, provides intuitive DataFrame-like interface for geospatial data
- **Shapely**: Industry standard for geometric operations (intersection, union, buffer, etc.)
- **Fiona**: Pythonic interface to OGR (GDAL) for reading/writing spatial data formats
- **PyProj**: Handles complex coordinate reference system transformations

### 3. Data Source Integration

#### Google Earth Engine
```python
earthengine-api==0.1.383  # Official Google Earth Engine Python client
```
- Access to Microsoft Building Footprints
- Access to Google Open Buildings dataset
- Handles authentication and quota management

#### OpenStreetMap Integration
```python
osmnx==1.7.1             # Simplified OSM data retrieval
overpy==0.7              # Direct Overpass API client
requests==2.31.0         # HTTP client for custom API calls
```
- **OSMnx**: High-level interface for OSM data with built-in processing
- **OverPy**: Low-level Overpass API client for custom queries
- **Requests**: Direct HTTP access for maximum control

### 4. Export Format Support

#### Multi-Format Export Libraries
```python
simplekml==1.3.6         # KML/KMZ generation for Google Earth
ezdxf==1.1.4            # DWG file creation for AutoCAD
openpyxl==3.1.2         # Excel format support
```

#### Built-in Format Support
- **GeoJSON**: Native support via GeoPandas
- **Shapefile**: Native support via Fiona/GeoPandas
- **CSV**: Native support via Pandas

### 5. Async Processing and Performance

#### Concurrency Libraries
```python
aiohttp==3.9.1           # Async HTTP client for external APIs
aiofiles==23.2.1         # Async file operations
asyncio-throttle==1.0.2  # Rate limiting for external APIs
```

#### Data Processing
```python
pandas==2.1.4           # Data manipulation and analysis
numpy==1.25.2           # Numerical computing foundation
```

### 6. Optional Performance Enhancements

#### Caching Layer
```python
redis==5.0.1            # In-memory caching for frequent requests
hiredis==2.2.3          # High-performance Redis client
```

#### Visualization
```python
matplotlib==3.8.2       # Plotting and visualization
folium==0.15.1          # Interactive web maps
```

## Development Environment

### Code Quality and Testing
```python
pytest==7.4.3           # Testing framework
pytest-asyncio==0.21.1  # Async testing support
pytest-cov==4.1.0       # Coverage reporting
black==23.11.0          # Code formatting
isort==5.12.0           # Import sorting
flake8==6.1.0           # Linting
mypy==1.7.1             # Type checking
```

### Development Tools
```python
pre-commit==3.6.0       # Git hooks for code quality
ipython==8.17.2         # Enhanced Python shell
jupyter==1.0.0          # Notebook environment
```

## Infrastructure Requirements

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    build-essential \
    libgdal-dev \
    gdal-bin \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    libffi-dev \
    libssl-dev \
    redis-server
```

#### CentOS/RHEL
```bash
sudo yum update
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    python311 \
    python311-devel \
    gdal-devel \
    proj-devel \
    geos-devel \
    spatialindex-devel \
    libffi-devel \
    openssl-devel \
    redis
```

#### Windows (via conda)
```bash
conda install -c conda-forge \
    python=3.11 \
    gdal \
    proj \
    geos \
    fiona \
    shapely \
    geopandas
```

### Docker Environment

#### Base Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgdal-dev \
    gdal-bin \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY keys/ ./keys/

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance Considerations

### Memory Requirements
- **Minimum**: 2GB RAM for small AOIs (<1 km²)
- **Recommended**: 8GB RAM for production use
- **Large AOI Processing**: 16GB+ RAM for areas >10 km²

### CPU Requirements
- **Minimum**: 2 cores for development
- **Recommended**: 4+ cores for production
- **Async Processing**: Benefits from higher core count

### Storage Requirements
- **Application**: ~500MB with all dependencies
- **Temporary Files**: Variable based on export size
- **Logs**: Configure log rotation to manage size

## Version Compatibility Matrix

### Python Version Support
- **Python 3.11**: Recommended (tested and optimized)
- **Python 3.10**: Supported
- **Python 3.9**: Supported (some performance limitations)

### Key Library Compatibility
```
FastAPI 0.104+ requires:
├── Pydantic >= 2.0
├── Python >= 3.8
└── Starlette >= 0.27

GeoPandas 0.14+ requires:
├── Pandas >= 1.4
├── Shapely >= 1.8
├── Fiona >= 1.8
└── Python >= 3.9

Earth Engine API requires:
├── Python >= 3.7
├── Google Cloud credentials
└── Registered Earth Engine project
```

## Security Dependencies

### Production Security
```python
python-jose[cryptography]==3.3.0  # JWT handling (if auth added later)
cryptography>=41.0.0               # Encryption utilities
```

### Environment Management
```python
python-dotenv==1.0.0              # Environment variable management
pydantic-settings==2.1.0          # Settings management
```

## Monitoring and Observability

### Application Monitoring
```python
structlog==23.2.0                 # Structured logging
prometheus-client==0.19.0         # Metrics collection
```

### Health Checks
- Built-in FastAPI health endpoints
- External dependency monitoring
- Resource usage tracking

## Installation Instructions

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd atlas

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Configure environment
cp .env.template .env
# Edit .env with your configuration

# Start development server
uvicorn src.main:app --reload
```

### Production Setup
```bash
# Install production dependencies only
pip install -r requirements.txt

# Configure production environment
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export OVERPASS_API_URL=https://overpass-api.de/api/interpreter

# Start production server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting Common Issues

### GDAL Installation Issues
```bash
# If GDAL installation fails
export GDAL_CONFIG=/usr/bin/gdal-config
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"
```

### Shapely/Geos Issues
```bash
# Reinstall with proper GEOS linking
pip uninstall shapely
pip install shapely --no-binary shapely
```

### Earth Engine Authentication
```bash
# Verify service account setup
python -c "import ee; ee.Initialize(); print('EE initialized successfully')"
```

## Performance Optimization

### Production Optimizations
- Use Redis for caching frequent requests
- Configure appropriate worker count based on CPU cores
- Enable gzip compression for large responses
- Implement request rate limiting

### Memory Optimization
- Process large datasets in chunks
- Use streaming responses for large exports
- Implement garbage collection for temporary objects
- Configure appropriate ulimits

This technology stack provides a robust foundation for building a high-performance geospatial data extraction service with comprehensive export capabilities.