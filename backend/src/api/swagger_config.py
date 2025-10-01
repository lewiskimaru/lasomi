"""
Custom Swagger UI configuration for Atlas API
"""

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def custom_openapi_schema(app: FastAPI):
    """Generate custom OpenAPI schema with enhanced documentation"""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="🌍 Atlas Geospatial API",
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=app.servers
    )
    
    # Add custom extensions
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/lewiskimaru/atlas/main/docs/assets/atlas-logo.png",
        "altText": "Atlas Geospatial API"
    }
    
    # Add example workflows
    openapi_schema["info"]["x-code-samples"] = [
        {
            "lang": "Python",
            "label": "Python Example",
            "source": """
import requests
import json

# 1. Validate AOI
aoi = {
    "type": "Polygon",
    "coordinates": [[[36.8219, -1.2921], [36.8250, -1.2921], 
                     [36.8250, -1.2950], [36.8219, -1.2950], 
                     [36.8219, -1.2921]]]
}

validation = requests.post("http://localhost:8000/api/v1/validate-aoi", 
                          json={"aoi_boundary": aoi})
print(f"AOI Area: {validation.json()['area_km2']:.4f} km²")

# 2. Extract features (Traditional workflow)
extraction_request = {
    "aoi_boundary": aoi,
    "data_sources": {
        "microsoft_buildings": {"enabled": True},
        "osm_roads": {"enabled": True}
    }
}

response = requests.post("http://localhost:8000/api/v1/extract-features",
                        json=extraction_request)
result = response.json()
job_id = result["job_id"]

# 3. Download results
geojson_url = f"http://localhost:8000/api/v1/export/{job_id}/geojson"
with open("extracted_features.geojson", "wb") as f:
    f.write(requests.get(geojson_url).content)

print(f"✅ Extracted {result['total_features']} features in {result['processing_time']:.1f}s")

# NEW: Single-request workflow with immediate KMZ
single_request = {
    "aoi_boundary": aoi,
    "data_sources": {
        "google_buildings": {"enabled": True}
    },
    "output_format": "kmz",
    "raw": True
}

response = requests.post("http://localhost:8000/api/v1/extract-features",
                        json=single_request)
result = response.json()

# KMZ data available immediately in result["data"] as base64
import base64
with open("buildings.kmz", "wb") as f:
    f.write(base64.b64decode(result["data"]))

print(f"✅ Generated KMZ with {result['total_features']} features immediately!")
            """
        },
        {
            "lang": "JavaScript",
            "label": "JavaScript/Node.js Example",
            "source": """
const axios = require('axios');
const fs = require('fs');

async function extractFeatures() {
    const baseUrl = 'http://localhost:8000/api/v1';
    
    // Define AOI (Area of Interest)
    const aoi = {
        type: "Polygon",
        coordinates: [[[36.8219, -1.2921], [36.8250, -1.2921], 
                       [36.8250, -1.2950], [36.8219, -1.2950], 
                       [36.8219, -1.2921]]]
    };
    
    try {
        // 1. Validate AOI
        const validation = await axios.post(`${baseUrl}/validate-aoi`, {
            aoi_boundary: aoi
        });
        console.log(`AOI Area: ${validation.data.area_km2.toFixed(4)} km²`);
        
        // 2. Extract features (Traditional)
        const extractionRequest = {
            aoi_boundary: aoi,
            data_sources: {
                microsoft_buildings: { enabled: true },
                osm_roads: { enabled: true }
            }
        };
        
        const response = await axios.post(`${baseUrl}/extract-features`, extractionRequest);
        const { job_id, total_features, processing_time } = response.data;
        
        // 3. Download GeoJSON
        const exportResponse = await axios.get(`${baseUrl}/export/${job_id}/geojson`, {
            responseType: 'stream'
        });
        
        exportResponse.data.pipe(fs.createWriteStream('extracted_features.geojson'));
        console.log(`✅ Traditional: ${total_features} features in ${processing_time}s`);
        
        // NEW: Single-request KMZ export
        const singleRequest = {
            aoi_boundary: aoi,
            data_sources: {
                google_buildings: { enabled: true }
            },
            output_format: 'kmz',
            raw: true
        };
        
        const kmzResponse = await axios.post(`${baseUrl}/extract-features`, singleRequest);
        const kmzData = Buffer.from(kmzResponse.data.data, 'base64');
        fs.writeFileSync('buildings.kmz', kmzData);
        console.log(`✅ Single-request: ${kmzResponse.data.total_features} features as KMZ!`);
        
        console.log(`✅ Extracted ${total_features} features in ${processing_time.toFixed(1)}s`);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

extractFeatures();
            """
        },
        {
            "lang": "cURL",
            "label": "cURL Example",
            "source": """
# 1. Health Check
curl http://localhost:8000/api/v1/health

# 2. Validate AOI
curl -X POST "http://localhost:8000/api/v1/validate-aoi" \\
  -H "Content-Type: application/json" \\
  -d '{
    "aoi_boundary": {
      "type": "Polygon",
      "coordinates": [[[36.8219, -1.2921], [36.8250, -1.2921], [36.8250, -1.2950], [36.8219, -1.2950], [36.8219, -1.2921]]]
    }
  }'

# 3. Extract Features
curl -X POST "http://localhost:8000/api/v1/extract-features" \\
  -H "Content-Type: application/json" \\
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

# 4. Download Results (replace JOB_ID with actual job ID)
curl "http://localhost:8000/api/v1/export/JOB_ID/geojson" --output extracted_features.geojson
curl "http://localhost:8000/api/v1/export/JOB_ID/kml" --output extracted_features.kml
            """
        }
    ]
    
    # Enhanced server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "🔧 Development server - Local development and testing"
        },
        {
            "url": "https://api.yourdomain.com",
            "description": "🚀 Production server - Live API endpoint"
        }
    ]
    
    # Add security definitions (even though we don't use auth, for future extension)
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key authentication (not currently required)"
        }
    }
    
    # Add response examples to common endpoints
    if "paths" in openapi_schema:
        # Add comprehensive examples to extract-features endpoint
        extract_path = "/api/v1/extract-features"
        if extract_path in openapi_schema["paths"]:
            openapi_schema["paths"][extract_path]["post"]["responses"]["200"]["content"]["application/json"]["examples"] = {
                "successful_extraction": {
                    "summary": "Successful Feature Extraction",
                    "description": "Example of a successful extraction with multiple data sources",
                    "value": {
                        "job_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "completed",
                        "processing_time": 15.32,
                        "requested_sources": ["microsoft_buildings", "osm_buildings", "osm_roads"],
                        "results": {
                            "microsoft_buildings": {
                                "source": "microsoft_buildings",
                                "status": "completed",
                                "stats": {"count": 1250, "processing_time": 8.5},
                                "geojson": {"type": "FeatureCollection", "features": []}
                            }
                        },
                        "export_urls": {
                            "geojson": "/api/v1/export/550e8400-e29b-41d4-a716-446655440000/geojson",
                            "kml": "/api/v1/export/550e8400-e29b-41d4-a716-446655440000/kml"
                        },
                        "total_features": 1395,
                        "successful_sources": 3,
                        "failed_sources": 0
                    }
                },
                "partial_success": {
                    "summary": "Partial Success (Some Sources Failed)",
                    "description": "Example when some data sources fail but others succeed",
                    "value": {
                        "job_id": "550e8400-e29b-41d4-a716-446655440001",
                        "status": "partial",
                        "processing_time": 22.45,
                        "total_features": 890,
                        "successful_sources": 2,
                        "failed_sources": 1
                    }
                }
            }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def get_swagger_ui_html():
    """Custom Swagger UI HTML with enhanced styling"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌍 Atlas Geospatial API - Interactive Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
        <link rel="icon" type="image/png" href="https://fastapi.tiangolo.com/img/favicon.png" />
        <style>
            .swagger-ui .topbar { background-color: #1f2937; }
            .swagger-ui .topbar .download-url-wrapper .select-label { color: #ffffff; }
            .swagger-ui .info .title { color: #059669; font-size: 2.5rem; }
            .swagger-ui .info .description { font-size: 1rem; line-height: 1.6; }
            .swagger-ui .scheme-container { background: #f3f4f6; border-radius: 8px; padding: 16px; margin: 16px 0; }
            .swagger-ui .opblock.opblock-post { border-color: #059669; }
            .swagger-ui .opblock.opblock-post .opblock-summary { border-color: #059669; background: rgba(5, 150, 105, 0.1); }
            .swagger-ui .opblock.opblock-get { border-color: #3b82f6; }
            .swagger-ui .opblock.opblock-get .opblock-summary { border-color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
            .atlas-badge { background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.875rem; font-weight: 500; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                layout: "BaseLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                tryItOutEnabled: true,
                requestInterceptor: function(req) {
                    req.headers['Content-Type'] = 'application/json';
                    return req;
                },
                responseInterceptor: function(res) {
                    console.log('Atlas API Response:', res);
                    return res;
                }
            });
            
            // Add custom header
            setTimeout(() => {
                const title = document.querySelector('.swagger-ui .info .title');
                if (title) {
                    title.innerHTML = '🌍 Atlas Geospatial API <span class="atlas-badge">v1.0.0</span>';
                }
            }, 1000);
        </script>
    </body>
    </html>
    """