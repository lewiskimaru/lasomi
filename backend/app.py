#!/usr/bin/env python3
"""
HuggingFace Spaces entry point for Atlas GIS API
Handles environment variable setup and FastAPI initialization
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set default environment variables for HF Spaces
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("PORT", "7860")

# Import and run the FastAPI app
from src.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (HF Spaces uses 7860)
    port = int(os.environ.get("PORT", 7860))
    
    print(f"Atlas GIS API starting on port {port}")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )