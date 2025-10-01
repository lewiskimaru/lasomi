# Dockerfile for Atlas GIS API on HuggingFace Spaces
# Includes GDAL installation for geospatial libraries

FROM python:3.11-slim

# Install system dependencies including GDAL and geospatial libraries
RUN apt-get update && apt-get install -y \
    # GDAL and geospatial dependencies
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    # Build tools for compilation
    build-essential \
    # Utilities
    curl \
    wget \
    git \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

# Set up a new user named "user" with user ID 1000 (HuggingFace requirement)
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Set environment variables for the application
ENV PYTHONPATH=$HOME/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy the requirements file and install Python dependencies
COPY --chown=user ./requirements.txt requirements.txt

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies with specific handling for geospatial packages
# Note: GDAL Python bindings will be automatically matched to system GDAL version
# by the requirements.txt installation process
RUN pip install --no-cache-dir --user \
    # Install other dependencies first
    -r requirements.txt

# Copy the application source code
COPY --chown=user ./src src

# Create app.py entry point for HuggingFace Spaces
COPY --chown=user ./app.py app.py

# Create necessary directories
RUN mkdir -p \
    $HOME/app/temp_exports \
    $HOME/app/logs \
    $HOME/.cache

# Expose port 7860 (HuggingFace Spaces requirement)
EXPOSE 7860

# Health check for container monitoring
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/api/v1/health || exit 1

# Start the FastAPI application on port 7860
# HuggingFace Spaces requires this specific port and host configuration
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]