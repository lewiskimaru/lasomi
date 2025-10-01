---
title: Atlasomi GIS API
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Atlasomi GIS API - HuggingFace Spaces

A FastAPI-based microservice that automates the collection and processing of geospatial data for fiber network planning and design. The API eliminates manual tracing of building footprints, road networks, and landmarks by programmatically fetching data from multiple authoritative sources and delivering it in formats optimized for CAD/GIS workflows.

## Problem Statement

Planning and design engineers at telecom companies spend significant time manually tracing building footprints, road networks, and landmarks when designing fiber deployment routes. This manual process is:
- Time-consuming (hours per route design)
- Error-prone 
- Reduces productivity in network rollout projects
- Repetitive for similar areas

## Solution

An intelligent API service that:
- Accepts area-of-interest (AOI) boundary coordinates
- Automatically aggregates relevant geospatial data from multiple authoritative sources
- Returns standardized outputs in formats compatible with Google Earth and other design tools
- Provides 80%+ time savings in route planning workflows

## Key Features

### Multi-Source Data Integration
- **Microsoft Building Footprints**: 1.4B building footprints worldwide with height estimates
- **Google Open Buildings**: 1.8B building detections in Global South regions
- **OpenStreetMap**: Real-time roads, landmarks, and infrastructure data

### Multiple Output Formats
- **GeoJSON**: For web applications and analysis
- **KML/KMZ**: Optimized for Google Earth with custom styling
- **CSV**: For spreadsheet analysis and reporting

### High Performance
- Asynchronous processing for large areas
- Intelligent caching to reduce API calls
- Parallel data fetching from multiple sources
- Memory-efficient streaming for large datasets

### Enterprise-Ready
- Comprehensive error handling and retry logic
- Rate limiting and authentication
- Detailed logging and monitoring
- Data quality validation and reporting

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL with PostGIS extension
- Redis (for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lewiskimaru/atlasomi.git
   cd atlasomi
   ```

2. **Set up environment**
   ```bash
   # Copy environment template
   cp .env.template .env
   
   # Edit .env file with your API keys and configurations
   nano .env
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the production server**
   ```bash
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

### First API Call

**Traditional Workflow (Backward Compatible):**
```bash
curl -X POST "http://localhost:8000/api/v1/extract-features" \
     -H "Content-Type: application/json" \
     -d '{
       "aoi_boundary": {
         "type": "Polygon",
         "coordinates": [[[36.8219, -1.2921], [36.8250, -1.2921], [36.8250, -1.2950], [36.8219, -1.2950], [36.8219, -1.2921]]]
       },
       "data_sources": {
         "microsoft_buildings": {"enabled": true},
         "osm_roads": {"enabled": true}
       }
     }'
# Then download: curl "/api/v1/export/{job_id}/kmz" -o buildings.kmz
```

**New Single-Request Workflow:**
```bash
curl -X POST "http://localhost:8000/api/v1/extract-features" \
     -H "Content-Type: application/json" \
     -d '{
       "aoi_boundary": {
         "type": "Polygon",
         "coordinates": [[[36.8219, -1.2921], [36.8250, -1.2921], [36.8250, -1.2950], [36.8219, -1.2950], [36.8219, -1.2921]]]
       },
       "data_sources": {
         "google_buildings": {"enabled": true}
       },
       "output_format": "kmz",
       "raw": true
     }'
# Data available immediately in response.data field (base64 for KMZ)
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Core Endpoints

#### `POST /extract-features`
Extract geospatial features for a given area of interest.

**Request Body:**
```json
{
  "aoi_boundary": {
    "type": "Polygon", 
    "coordinates": [[[lng, lat], [lng, lat], ...]]
  },
  "data_sources": {
    "microsoft_buildings": {"enabled": true, "priority": 1, "timeout": 30},
    "google_buildings": {"enabled": true, "priority": 2, "timeout": 30},
    "osm_roads": {"enabled": true, "priority": 3, "timeout": 25}
  },
  "output_format": "kmz",
  "raw": true,
  "filters": {
    "min_building_area": 10,
    "road_types": ["primary", "secondary", "residential"],
    "simplification_tolerance": 0.001
  }
}
```

**New Single-Request Export Parameters:**
- `output_format`: Optional. Specify `geojson`, `kml`, or `kmz` for immediate format conversion
- `raw`: Optional boolean. When `true` with `output_format`, returns data directly in response

**Traditional Response (without output_format):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_features": 1395,
  "export_urls": {
    "geojson": "/export/550e8400.../geojson",
    "kml": "/export/550e8400.../kml",
    "kmz": "/export/550e8400.../kmz"
  },
  "results": {...}
}
```

**New Single-Request Response (with output_format + raw=true):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed", 
  "total_features": 1395,
  "output_format": "kmz",
  "data": "UEsDBBQACAAI...",
  "export_urls": {...},
  "results": {...}
}
```

#### `GET /job-status/{job_id}`
Check processing status for async operations.

#### `GET /download/{job_id}/{format}`
Download processed results.

#### `GET /data-sources`
List available data sources and their capabilities.

#### `GET /api/v2/job/{job_id}/status`
Check processing status for async operations.

#### `GET /api/v2/download/{job_id}/{format}`
Download processed results.

#### `GET /api/v2/data-sources`
List available data sources and their capabilities.

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
atlasomi/
├── src/                        # Source code
│   ├── api/                    # FastAPI routes and schemas  
│   ├── core/                   # Business logic
│   │   ├── data_sources/       # Data source connectors
│   │   ├── processors/         # Data processing pipeline
│   │   └── exporters/          # Format exporters
│   ├── utils/                  # Utilities
│   └── web/                    # Web interface
├── docs/                       # Detailed documentation
└── requirements.txt            # Production dependencies
```

## 🔧 Configuration

### Environment Variables

Required environment variables in `.env`:

```bash
# API Keys
GOOGLE_EARTH_ENGINE_SERVICE_ACCOUNT_KEY=/path/to/service-account.json
OVERPASS_API_URL=https://overpass-api.de/api/interpreter

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/telecom_gis
REDIS_URL=redis://localhost:6379

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
CACHE_TTL=3600

# Data Sources
MICROSOFT_BUILDINGS_BASE_URL=https://minedbuildings.z5.web.core.windows.net/global-buildings/
ENABLE_CACHING=true
MAX_AOI_AREA_KM2=100
```

### Data Source Configuration

Each data source can be configured in `config/data_sources.yaml`:

```yaml
microsoft_buildings:
  enabled: true
  priority: 1
  cache_ttl: 86400
  retry_attempts: 3
  rate_limit: 100  # requests per minute

google_buildings:
  enabled: true
  priority: 2
  service_account_key: ${GOOGLE_EARTH_ENGINE_SERVICE_ACCOUNT_KEY}
  cache_ttl: 86400

osm_overpass:
  enabled: true
  priority: 3
  base_url: ${OVERPASS_API_URL}
  rate_limit: 2  # requests per second
  timeout: 25
```



## Performance Benchmarks

| AOI Size | Processing Time | Memory Usage | Output Size |
|----------|----------------|--------------|-------------|
| <1 km²   | <30 seconds    | <500 MB      | <5 MB       |
| 1-10 km² | 1-2 minutes    | <1 GB        | 5-50 MB     |
| >10 km²  | 2-10 minutes   | <2 GB        | 50-500 MB   |

*Benchmarks based on typical urban areas with standard building density*

## Production Setup

### Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# Start the server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Adding New Data Sources

1. Create connector in `src/core/data_sources/`
2. Implement the `BaseDataSource` interface
3. Add configuration in `config/data_sources.yaml`
4. Write comprehensive tests
5. Update documentation

Example connector structure:
```python
from src.core.data_sources.base import BaseDataSource

class NewDataSource(BaseDataSource):
    def __init__(self, config):
        super().__init__(config)
    
    async def fetch_buildings(self, aoi_bounds):
        # Implementation
        pass
    
    async def fetch_roads(self, aoi_bounds):
        # Implementation  
        pass
```

## Documentation

### Available Documentation
- **[System Design](docs/system-design.md)** - Architecture and design decisions
- **[Data Sources](docs/data-sources.md)** - Detailed data source documentation  
- **[API Specification](docs/api-spec.md)** - Complete API reference
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### Research Documentation
- **[Data Source Analysis](research/data-source-analysis.md)** - Comparative analysis of data sources
- **[Performance Benchmarks](research/benchmarks/)** - Performance test results
- **[Algorithm Research](research/algorithms/)** - Spatial processing algorithms

## Deployment

### Production Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.template .env
# Edit .env with your production settings

# Start the production server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Process Management
For production deployment, consider using a process manager like:
- **Gunicorn**: `gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker`
- **Systemd**: Create a service file for automatic startup
- **Supervisor**: Process monitoring and automatic restart

## Monitoring & Observability

### Health Checks
- **API Health**: `GET /health`
- **Database Health**: `GET /health/database`
- **Data Sources Health**: `GET /health/data-sources`

### Metrics & Logging
- **Prometheus metrics** exposed at `/metrics`
- **Structured logging** with correlation IDs
- **Request tracing** with OpenTelemetry
- **Error tracking** with Sentry integration

### Monitoring Dashboard
Access Grafana dashboard at: `http://localhost:3000`
- API performance metrics
- Data source availability
- Processing queue status
- Error rates and response times

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure your code follows the project standards
5. Update documentation for any API changes
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Write comprehensive docstrings for new features
- Update documentation for any API changes
- Use conventional commits for commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Acknowledgments

- **Microsoft** for providing open building footprints dataset
- **Google Research** for Open Buildings dataset  
- **OpenStreetMap** community for crowdsourced geographic data
- **FastAPI** team for the excellent web framework
- **PostGIS** team for spatial database capabilities

## Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/lewiskimaru/atlasomi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lewiskimaru/atlasomi/discussions)
- **Email**: lewis@atomio.tech
