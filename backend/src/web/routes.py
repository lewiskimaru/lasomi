"""
Web interface routes for Atlasomi API
"""

import logging
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from src.utils.logging_config import log_request_separator

# Setup logging
logger = logging.getLogger(__name__)

# Setup templates
template_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))

# Add url_for function to templates for static file URLs
def url_for_static(path: str) -> str:
    """Generate URL for static files"""
    return f"/static{path}"

# Add custom functions to Jinja2 environment
templates.env.globals["url_for"] = lambda endpoint, **values: url_for_static(values.get("path", ""))

router = APIRouter(prefix="/web", tags=["Web Interface"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main web interface"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Atlasomi - Geospatial Data Extraction API",
            "api_base_url": "/api/v1"
        }
    )


@router.get("/developer", response_class=HTMLResponse)
async def web_developer(request: Request):
    """Developer documentation page"""
    return templates.TemplateResponse(
        "developer.html",
        {
            "request": request,
            "title": "Atlasomi API - Developer Docs",
            "api_base_url": "/api/v1"
        }
    )


@router.get("/docs", response_class=HTMLResponse)
async def web_docs(request: Request):
    """Web interface documentation"""
    return templates.TemplateResponse(
        "docs.html",
        {
            "request": request,
            "title": "Atlasomi API - Documentation",
            "api_base_url": "/api/v1"
        }
    )


@router.get("/debug/static-files")
async def debug_static_files(request: Request):
    """Debug endpoint to check static file availability"""
    import os
    from pathlib import Path

    # Log request separator for debugging
    log_request_separator(logger, request.method, str(request.url.path))

    static_dir = Path(__file__).parent / "static"
    css_dir = static_dir / "css"
    js_dir = static_dir / "js"

    debug_info = {
        "static_directory": {
            "path": str(static_dir),
            "exists": static_dir.exists(),
            "is_directory": static_dir.is_dir() if static_dir.exists() else False
        },
        "css_directory": {
            "path": str(css_dir),
            "exists": css_dir.exists(),
            "files": list(css_dir.glob("*.css")) if css_dir.exists() else []
        },
        "js_directory": {
            "path": str(js_dir),
            "exists": js_dir.exists(),
            "files": list(js_dir.glob("*.js")) if js_dir.exists() else []
        },
        "working_directory": os.getcwd(),
        "environment": {
            "SPACE_ID": os.environ.get("SPACE_ID"),
            "SPACE_AUTHOR_NAME": os.environ.get("SPACE_AUTHOR_NAME")
        }
    }

    # Convert Path objects to strings for JSON serialization
    if debug_info["css_directory"]["files"]:
        debug_info["css_directory"]["files"] = [str(f) for f in debug_info["css_directory"]["files"]]
    if debug_info["js_directory"]["files"]:
        debug_info["js_directory"]["files"] = [str(f) for f in debug_info["js_directory"]["files"]]

    return debug_info