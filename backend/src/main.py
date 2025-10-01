"""
Atlas FastAPI Service - Main Application Entry Point

A stateless microservice for extracting geospatial data from multiple sources
including Microsoft Building Footprints, Google Open Buildings, and OpenStreetMap.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import extract, export, health
from src.api.routes import extract_v2, download_v2, design_upload  # Import improved v2 routes
from src.api.swagger_config import custom_openapi_schema
from src.web.routes import router as web_router
from src.core.config import get_settings
from src.utils.exceptions import AtlasException
from src.utils.logging_config import setup_logging
from src.utils.gee_auth import initialize_earth_engine

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with professional startup logging"""
    from src.utils.startup_logger import get_startup_logger, mark_startup_completed
    
    startup_logger = get_startup_logger()
    if startup_logger:  # Only proceed if startup logger exists
        startup_logger.start()
        
        # Static files mounting step
        static_step = startup_logger.add_step("static", "Static files mounting")
        
        # Handle different working directory scenarios (local vs HuggingFace Spaces)
        static_dir = Path("src/web/static")
        if not static_dir.exists():
            # Try alternative paths for different deployment scenarios
            static_dir = Path(__file__).parent / "web" / "static"
            if not static_dir.exists():
                static_dir = Path("/home/user/app/src/web/static")  # HF Spaces path
                if not static_dir.exists():
                    static_step.error("static directory not found")
                    static_dir = Path("src/web/static")  # Fallback to original
                else:
                    static_step.success("mounted (/web/static)")
            else:
                static_step.success("mounted (/web/static)")
        else:
            static_step.success("mounted (/web/static)")
        
        # Initialize Google Earth Engine
        gee_status = initialize_earth_engine()
        if gee_status:
            # Test the connection
            from src.utils.gee_auth import test_earth_engine_connection
            test_result = test_earth_engine_connection()
            if not test_result:
                logger.warning("Google Earth Engine connection test failed - check service account permissions")
        else:
            logger.warning("Google Earth Engine initialization failed - some features may be unavailable")
        
        # Add data sources information
        data_sources_step = startup_logger.add_step("sources", "Data sources")
        available_sources = []
        
        # Check what data sources are available
        if gee_status:
            available_sources.extend(["microsoft", "google"])
        available_sources.extend(["osm-buildings", "osm-roads", "osm-railways", "osm-landmarks", "osm-natural"])
        
        data_sources_step.success(f"ready ({len(available_sources)}: {', '.join(available_sources)})")
        
        # Complete startup sequence
        startup_logger.finish()
        mark_startup_completed()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Atlas FastAPI Service")


# Create FastAPI application
app = FastAPI(
    title="Atlas Geospatial API",
    description="""
    # 🌍 Atlas Geospatial API
    
    A high-performance FastAPI microservice for automated geospatial data extraction designed for **telecom fiber network planning** and infrastructure design.
    
    ## 🚀 Features
    
    * **🔗 Multi-Source Integration**: Microsoft Buildings, Google Open Buildings, OpenStreetMap
    * **⚡ Real-time Processing**: On-demand AOI-based data extraction
    * **📁 Multiple Export Formats**: GeoJSON, KML/KMZ, DWG, Shapefile, CSV
    * **🎛️ Source Independence**: Separate toggleable layers for each data source
    * **🔒 Stateless Operation**: No authentication or persistent storage required
    * **📊 Built-in Validation**: AOI geometry validation with processing estimates
    
    ## 📡 Data Sources
    
    | Source | Coverage | Features |
    |--------|----------|----------|
    | **Microsoft Building Footprints** | 1.4B+ buildings worldwide | High accuracy, height estimates |
    | **Google Open Buildings** | 1.8B+ buildings (Global South) | AI-detected buildings with confidence scores |
    | **OpenStreetMap** | Global crowdsourced data | Buildings, roads, railways, landmarks, natural features |
    
    ## 🎯 Use Cases
    
    * **Telecom Network Planning**: Automated building and infrastructure mapping
    * **Fiber Deployment**: Route planning with obstacle identification
    * **Urban Analysis**: Comprehensive geospatial feature extraction
    * **Infrastructure Design**: Multi-format data export for various CAD/GIS tools
    
    ## 📋 Workflow
    
    1. **Define AOI**: Submit polygon boundary for your area of interest
    2. **Select Sources**: Choose from Microsoft, Google, and/or OSM data
    3. **Process Data**: Service extracts features from all selected sources
    4. **Export Results**: Download in your preferred format (GeoJSON, KML, CSV, etc.)
    5. **Use in Tools**: Import into Google Earth, AutoCAD, QGIS, or web applications
    
    ## 🔧 API Limits
    
    * **Max AOI Area**: 100 km²
    * **Request Timeout**: 5 minutes
    
    ---
    
    **💡 Tip**: Start with the `/validate-aoi` endpoint to check your area and get processing estimates before extraction.
    """,
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
    contact={
        "name": "Atlas API Support",
        "url": "https://github.com/lewiskimaru/atlas",
        "email": "lewis@atomio.tech"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.yourdomain.com",
            "description": "Production server"
        }
    ],
    openapi_tags=[
        {
            "name": "extract",
            "description": "🎯 **Feature Extraction** - Extract geospatial features from multiple data sources",
            "externalDocs": {
                "description": "Feature Extraction Guide",
                "url": "https://github.com/lewiskimaru/atlas/blob/main/docs/tutorials/"
            }
        },
        {
            "name": "export", 
            "description": "📁 **Data Export** - Download processed data in multiple formats (GeoJSON, KML, CSV, etc.)",
            "externalDocs": {
                "description": "Export Formats Guide",
                "url": "https://github.com/lewiskimaru/atlas/blob/main/docs/architecture/system-architecture.md#export-format-specifications"
            }
        },
        {
            "name": "health",
            "description": "🏥 **Health & Monitoring** - Service health checks and system status monitoring"
        }
    ]
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global exception handler
@app.exception_handler(AtlasException)
async def atlas_exception_handler(request: Request, exc: AtlasException):
    """Handle custom Atlas exceptions"""
    logger.error(f"Atlas exception: {exc.message}", extra={"error_code": exc.error_code})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception("Unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if settings.debug else None
        }
    )


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(extract.router, prefix="/api/v1", tags=["extract"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])

# Include improved v2 routes (with better architecture)
app.include_router(extract_v2.router, prefix="/api/v2", tags=["extract-v2"])
app.include_router(download_v2.router, prefix="/api/v2", tags=["download-v2"])
app.include_router(design_upload.router, prefix="/api/v2/designs", tags=["design-upload"])

app.include_router(web_router)  # Web interface routes

# Mount static files for web interface
static_dir = Path("src/web/static")
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Set custom OpenAPI schema
app.openapi = lambda: custom_openapi_schema(app)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to web interface"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/web/")
    return {
        "service": settings.service_name,
        "version": settings.version,
        "status": "operational",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "health_check": "/api/v1/health",
        "api_specification": "/openapi.json",
        "features": [
            "🔗 Multi-source geospatial data integration",
            "⚡ Real-time AOI-based processing", 
            "📁 Multiple export formats (GeoJSON, KML, CSV)",
            "🎛️ Independent data source layers",
            "🔒 Stateless operation (no auth required)"
        ]
    }


@app.get("/swagger", include_in_schema=False)
async def custom_swagger_ui():
    """Enhanced Swagger UI with custom styling"""
    from fastapi.responses import HTMLResponse
    from src.api.swagger_config import get_swagger_ui_html
    
    return HTMLResponse(content=get_swagger_ui_html())


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )