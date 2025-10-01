# Cloud Deployment Guide

This guide covers deploying the Atlas GIS API to various cloud platforms with proper service account key management.

## 🚀 Platform-Specific Deployment

### **Hugging Face Spaces**

#### **1. Prepare Your Service Account Key**

```bash
# Convert your service account key to base64
cd /Users/lewis/projects/atlas
base64 -i keys/gee-service-account.json > gee-key-base64.txt

# Copy the output (it will be a long string)
cat gee-key-base64.txt
```

#### **2. Create Hugging Face Space**

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Choose **"Gradio"** or **"Streamlit"** SDK (or Docker if available)
4. Set your space to **Private** if using sensitive data

#### **3. Environment Variables**

In your Hugging Face Space settings, add these environment variables:

```bash
# Required for Google Earth Engine
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=<your-base64-encoded-key>
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# Optional settings
DEBUG=false
LOG_LEVEL=INFO
MAX_AOI_AREA_KM2=100.0
OVERPASS_RATE_LIMIT=0.5
```

#### **4. Create app.py for Hugging Face**

```python
# app.py for Hugging Face Spaces
import gradio as gr
import uvicorn
from src.main import app

# Create Gradio interface that embeds the FastAPI app
def launch_api():
    return "Atlas API is running at /docs for API documentation"

# Simple Gradio interface
iface = gr.Interface(
    fn=launch_api,
    inputs=None,
    outputs="text",
    title="Atlas Geospatial API",
    description="FastAPI service for geospatial data extraction"
)

# Launch both Gradio and FastAPI
if __name__ == "__main__":
    # Start FastAPI in the background
    import threading
    import time
    
    def start_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=7860)
    
    api_thread = threading.Thread(target=start_fastapi)
    api_thread.daemon = True
    api_thread.start()
    
    # Give FastAPI time to start
    time.sleep(2)
    
    # Launch Gradio interface
    iface.launch()
```

### **Railway**

#### **1. Prepare Environment Variables**

```bash
# Convert service account key to base64
base64 -i keys/gee-service-account.json
```

#### **2. Railway Deployment**

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Create project: `railway init`
4. Add environment variables:

```bash
railway variables:set GOOGLE_SERVICE_ACCOUNT_KEY_BASE64="<your-base64-key>"
railway variables:set GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
railway variables:set DEBUG="false"
railway variables:set LOG_LEVEL="INFO"
```

#### **3. Create railway.json**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/v1/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### **4. Create Procfile**

```bash
# Procfile
web: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### **Render**

#### **1. Environment Variables**

In Render dashboard, add:

```bash
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=<your-base64-key>
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
DEBUG=false
LOG_LEVEL=INFO
```

#### **2. render.yaml**

```yaml
services:
  - type: web
    name: atlas-gis-api
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GOOGLE_SERVICE_ACCOUNT_KEY_BASE64
        sync: false
      - key: GOOGLE_CLOUD_PROJECT
        sync: false
      - key: DEBUG
        value: false
```

### **Heroku**

#### **1. Install Heroku CLI**

```bash
# Install Heroku CLI and login
heroku login
```

#### **2. Create Heroku App**

```bash
heroku create your-atlas-api
```

#### **3. Set Environment Variables**

```bash
heroku config:set GOOGLE_SERVICE_ACCOUNT_KEY_BASE64="<your-base64-key>"
heroku config:set GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
heroku config:set DEBUG="false"
heroku config:set LOG_LEVEL="INFO"
```

#### **4. Create Procfile**

```bash
# Procfile
web: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

## 🔒 **Security Best Practices**

### **Environment Variable Security**

1. **Never commit base64 keys to git**:
   ```bash
   # Add to .gitignore
   echo "gee-key-base64.txt" >> .gitignore
   echo "*.key" >> .gitignore
   ```

2. **Use platform secret management**:
   - **Railway**: Built-in environment variables
   - **Render**: Environment variables with encryption
   - **Heroku**: Config vars (encrypted at rest)
   - **Hugging Face**: Private space environment variables

3. **Rotate keys regularly**:
   ```bash
   # Generate new service account key every 90 days
   # Update environment variables on all platforms
   ```

### **Key Conversion Script**

Create a helper script for key conversion:

```bash
#!/bin/bash
# convert-key.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path-to-service-account.json>"
    exit 1
fi

KEY_FILE="$1"

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: File $KEY_FILE not found"
    exit 1
fi

echo "Converting $KEY_FILE to base64..."
BASE64_KEY=$(base64 -i "$KEY_FILE")

echo ""
echo "Base64 encoded key (copy this to your environment variables):"
echo "GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=\"$BASE64_KEY\""
echo ""
echo "⚠️  Security reminder:"
echo "- Never commit this key to version control"
echo "- Store it securely in your deployment platform's environment variables"
echo "- Rotate the key every 90 days"
```

## 🧪 **Testing Your Deployment**

### **Health Check**

Once deployed, test your service:

```bash
# Replace with your deployed URL
curl https://your-app-url.com/api/v1/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-01-16T10:30:00Z",
  "version": "1.0.0",
  "google_earth_engine": "available"
}
```

### **API Documentation**

Visit your deployed URL + `/docs` to access the interactive API documentation.

## 💰 **Cost Considerations**

### **Platform Costs**
- **Hugging Face Spaces**: Free tier available, paid for more resources
- **Railway**: $5/month minimum, usage-based pricing
- **Render**: Free tier available, $7/month for production
- **Heroku**: $7/month for basic dyno

### **Google Earth Engine Costs**
- Monitor usage in Google Cloud Console
- Set up billing alerts
- Consider implementing usage quotas in your API

## 🚨 **Troubleshooting**

### **Common Issues**

1. **"Authentication failed"**:
   - Verify base64 encoding is correct
   - Check environment variable names
   - Ensure Earth Engine registration is approved

2. **"Module not found"**:
   - Check requirements.txt is complete
   - Verify Python version compatibility (3.11+)

3. **"Quota exceeded"**:
   - Monitor Earth Engine usage
   - Implement rate limiting
   - Consider upgrading to paid tier

### **Debug Mode**

For troubleshooting, temporarily enable debug mode:

```bash
# Set environment variable
DEBUG=true
LOG_LEVEL=DEBUG
```

This will provide detailed error messages and enable `/docs` and `/redoc` endpoints.