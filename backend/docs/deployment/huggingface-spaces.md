# HuggingFace Spaces Deployment Guide

This guide walks you through deploying the Atlas GIS API to HuggingFace Spaces using Docker.

## 🚀 Quick Deployment Steps

### **Step 1: Create HuggingFace Space**

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Configure your space:
   - **Space name**: `atlas-gis-api` (or your preferred name)
   - **License**: `MIT`
   - **SDK**: `Docker`
   - **Visibility**: `Private` (recommended for API keys)

### **Step 2: Upload Files**

Upload these files to your space:

#### **Required Files:**
- `Dockerfile` - Container configuration with GDAL
- `requirements.txt` - Python dependencies
- `src/` - Complete source code directory
- `app.py` - HuggingFace Spaces entry point
- `README_SPACES.md` - Rename to `README.md` in your space

#### **Files NOT Needed:**
- `.env` or `.env.template` - HF Spaces uses environment variables from Space settings
- `keys/` - Never upload JSON files to public spaces

### **Step 3: Set Environment Variables**

**✨ Important:** HuggingFace Spaces automatically injects environment variables set in Space settings into the container. No `.env` file is needed!

In your HuggingFace Space settings, add these environment variables:

#### **Required (Google Earth Engine):**
```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
Your
Private
Key
Here
-----END PRIVATE KEY-----"
```

#### **Optional (Application Settings):**
```bash
DEBUG=false
LOG_LEVEL=INFO
MAX_AOI_AREA_KM2=100.0
REQUEST_TIMEOUT=300
OVERPASS_API_URL=https://overpass-api.de/api/interpreter
OVERPASS_RATE_LIMIT=0.5
```

### **Step 4: Get Environment Variables**

Use the `extract_env_vars.py` script locally to get the correct values:

```bash
# Run locally to extract your service account variables
python3 extract_env_vars.py
```

Copy the output and paste into your HuggingFace Space environment variables.

## 🚀 **Direct HuggingFace Deployment**

Since local Docker testing isn't available, deploy directly to HuggingFace Spaces:

### **GDAL Installation**
```dockerfile
# Install GDAL and geospatial libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev
```

### **Why GDAL is Required**
- **Fiona**: Requires GDAL for reading/writing geospatial data formats
- **Geopandas**: Depends on Fiona for spatial operations and data I/O
- **Rasterio**: Requires GDAL for raster data handling and projections
- **PyProj**: Needs PROJ library for coordinate transformations
- **Shapely**: Needs GEOS for geometric operations

### **GDAL Installation in Our Dockerfile**
Our Dockerfile automatically handles the complex GDAL installation:

```dockerfile
# Install GDAL and all geospatial dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    build-essential

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

# Install Python GDAL bindings with correct version
RUN pip install GDAL==$(gdal-config --version)
```

### **Port Configuration**
```dockerfile
EXPOSE 7860
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

HuggingFace Spaces **requires** port 7860 for FastAPI applications.

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. GDAL Installation Fails**
```
Error: GDAL not found
```
**Solution**: The Dockerfile handles this automatically. If issues persist, try rebuilding the space.

#### **2. Authentication Errors**
```
Error: Google Earth Engine not authenticated
```
**Solution**: 
- Verify all environment variables are set correctly
- Check that private key includes proper line breaks
- Ensure your Google Cloud Project is registered with Earth Engine

#### **3. Port Issues**
```
Error: Application not accessible
```
**Solution**: 
- HuggingFace Spaces **must** use port 7860
- Our configuration automatically handles this

#### **4. Memory Issues**
```
Error: Container killed (OOM)
```
**Solution**:
- Reduce `MAX_AOI_AREA_KM2` to smaller values (e.g., 10.0)
- Use smaller test areas initially

#### **5. Missing Dependencies**
```
ModuleNotFoundError: No module named 'geojson_pydantic'
```
**Solution**: 
- This should be resolved in the latest version
- If you encounter other missing modules, check that `requirements.txt` is complete
- Rebuild the space after updating requirements

#### **6. Configuration Parsing Errors**
```
SettingsError: error parsing value for field "allowed_origins"
json.decoder.JSONDecodeError: Expecting value
```
**Solution**:
- ✅ **Fixed in latest version** - Updated to use Pydantic v2 configuration
- The config now properly handles environment variables as strings
- Supports both comma-separated strings and JSON arrays
- Example: `ALLOWED_ORIGINS="http://localhost:3000,https://myapp.com"`

### **Debugging Steps:**

1. **Check Build Logs**: View the Docker build process in HF Spaces
2. **Check Environment Variables**: Ensure all required variables are set
3. **Test Health Endpoint**: Visit `/api/v1/health` once deployed
4. **View Application Logs**: Check the space logs for error messages

## 📊 **Space Resource Limits**

### **HuggingFace Spaces Constraints:**
- **Memory**: Limited (varies by tier)
- **CPU**: Shared resources
- **Storage**: Temporary filesystem
- **Network**: Rate limited

### **Optimization Tips:**
- Keep AOI areas small (<10 km² recommended)
- Use efficient data source combinations
- Implement request timeouts
- Monitor space usage

## 🌐 **Accessing Your Deployed API**

Once deployed, your API will be available at:
```
https://your-username-atlas-gis-api.hf.space
```

### **Key Endpoints:**
- **API Docs**: `/docs`
- **Health Check**: `/api/v1/health`
- **Data Sources**: `/api/v1/data-sources`
- **Extract Features**: `/api/v1/extract-features`

## 🔒 **Security Considerations**

### **For Production Use:**
1. **Keep Space Private**: Don't expose API keys publicly
2. **Monitor Usage**: Track API calls and costs
3. **Rotate Keys**: Regularly update service account keys
4. **Rate Limiting**: Implement usage quotas if needed

### **For Development/Demo:**
1. Use test areas only
2. Set conservative limits
3. Monitor Google Earth Engine quotas
4. Consider using sample data

## 🎯 **Next Steps**

After successful deployment:

1. **Test the API**: Use the `/docs` interface to test endpoints
2. **Monitor Performance**: Check response times and resource usage
3. **Optimize Settings**: Adjust limits based on actual usage
4. **Scale if Needed**: Consider dedicated infrastructure for heavy use

Your Atlas GIS API is now ready for global access through HuggingFace Spaces! 🎉