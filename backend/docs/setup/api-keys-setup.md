# API Keys and Credentials Setup Guide

This guide walks you through obtaining all necessary API keys and credentials for the Atlas GIS API.

## 🔑 Required Credentials

### Google Earth Engine (Required)
- **Purpose**: Access Google Open Buildings dataset and Earth Engine processing
- **Cost**: Free tier available, usage-based pricing for heavy use
- **Setup Time**: 15-30 minutes

### Other Data Sources (No Keys Required)
- **Microsoft Building Footprints**: Public dataset, no authentication needed
- **OpenStreetMap**: Public Overpass API, no authentication needed

## 📋 Step-by-Step Setup

### 1. Google Earth Engine Setup

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" or select existing project
3. Note your **Project ID** (format: `my-project-12345`)

#### Step 2: Enable APIs
1. Navigate to **APIs & Services > Library**
2. Search and enable:
   - **Google Earth Engine API**
   - **Google Cloud Storage API** (optional, for large exports)

#### Step 3: Register for Earth Engine
1. Visit [Google Earth Engine](https://earthengine.google.com/)
2. Click **"Get Started"**
3. Choose use case:
   - **Non-commercial**: Research, education, non-profit
   - **Commercial**: Business, commercial applications
4. Complete registration with your Google Cloud Project ID
5. **Wait for approval** (can take 1-3 business days)

#### Step 4: Create Service Account
1. Go to **IAM & Admin > Service Accounts**
2. Click **"Create Service Account"**
3. Configure:
   ```
   Name: atlas-gee-service-account
   ID: atlas-gee-service-account
   Description: Service account for Atlas GIS API Earth Engine access
   ```

#### Step 5: Assign Permissions
Add these roles to your service account:
- **Earth Engine Resource Admin**
- **Earth Engine Resource Viewer**
- **Service Account User**

#### Step 6: Generate Key
1. Click on your service account name
2. Go to **"Keys"** tab
3. Click **"Add Key" > "Create new key"**
4. Choose **JSON** format
5. Download the JSON file

#### Step 7: Install Key
```bash
# Create keys directory
mkdir -p keys

# Move downloaded key (replace with your actual filename)
mv ~/Downloads/your-project-id-abc123.json keys/gee-service-account.json

# Secure the key file
chmod 600 keys/gee-service-account.json
```

### 2. Update Environment Configuration

Edit your `.env` file:

```bash
# Update these values with your actual information
GOOGLE_APPLICATION_CREDENTIALS=./keys/gee-service-account.json
GOOGLE_CLOUD_PROJECT=your-actual-project-id
```

### 3. Verify Setup

Test your Earth Engine authentication:

```python
import ee

# Initialize Earth Engine
ee.Initialize()

# Test authentication
print("Earth Engine initialized successfully!")
```

## 🌍 Data Source Details

### Microsoft Building Footprints
- **URL**: `https://minedbuildings.z5.web.core.windows.net/global-buildings/`
- **Coverage**: 1.4 billion buildings worldwide
- **Format**: GeoJSON tiles
- **Authentication**: None required
- **Rate Limits**: Reasonable usage expected

### OpenStreetMap (Overpass API)
- **URL**: `https://overpass-api.de/api/interpreter`
- **Coverage**: Global roads, landmarks, infrastructure
- **Format**: XML/JSON responses
- **Authentication**: None required
- **Rate Limits**: 0.5 requests/second (be respectful)

### Google Open Buildings (via Earth Engine)
- **Access**: Through Google Earth Engine
- **Coverage**: 1.8 billion buildings (Global South focus)
- **Format**: Earth Engine ImageCollection
- **Authentication**: Uses GEE service account
- **Rate Limits**: Earth Engine quotas apply

## 🔒 Security Best Practices

### Protecting Your Credentials

1. **Never commit keys to version control**:
   ```bash
   # Add to .gitignore
   echo "keys/*.json" >> .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

3. **Rotate keys regularly**:
   - Generate new service account keys every 90 days
   - Delete old keys after rotation

4. **Limit service account permissions**:
   - Only grant minimum required permissions
   - Use separate service accounts for different environments

### Production Deployment

For production environments:

```bash
# Set environment variables instead of using .env file
export GOOGLE_APPLICATION_CREDENTIALS="/secure/path/gee-service-account.json"
export GOOGLE_CLOUD_PROJECT="production-project-id"

# Or use cloud provider's secret management
# AWS: AWS Secrets Manager
# GCP: Secret Manager
# Azure: Key Vault
```

## 🚨 Troubleshooting

### Common Issues

#### Earth Engine Authentication Failed
```python
# Error: Authentication failed
ee.EEException: Authentication failed
```

**Solutions**:
1. Verify service account JSON file path
2. Check if Earth Engine registration is approved
3. Ensure correct project ID in environment variables

#### Quota Exceeded
```python
# Error: Quota exceeded
ee.EEException: Quota exceeded
```

**Solutions**:
1. Check your Earth Engine usage in Google Cloud Console
2. Implement request throttling
3. Consider upgrading to paid tier

#### Permission Denied
```python
# Error: Permission denied
ee.EEException: Permission denied
```

**Solutions**:
1. Verify service account has correct roles
2. Check if Earth Engine API is enabled
3. Ensure project has Earth Engine access

### Getting Help

- **Earth Engine Forum**: [https://groups.google.com/forum/#!forum/google-earth-engine-developers](https://groups.google.com/forum/#!forum/google-earth-engine-developers)
- **Google Cloud Support**: [https://cloud.google.com/support](https://cloud.google.com/support)
- **Project Issues**: [GitHub Issues](https://github.com/lewiskimaru/atlas/issues)

## ✅ Verification Checklist

Before proceeding with the API:

- [ ] Google Cloud Project created
- [ ] Earth Engine API enabled
- [ ] Earth Engine registration approved
- [ ] Service account created with correct permissions
- [ ] Service account key downloaded and secured
- [ ] Environment variables configured
- [ ] Key file path is correct in `.env`
- [ ] Authentication test passes

## 💰 Cost Considerations

### Google Earth Engine Pricing
- **Free Tier**: 
  - 250,000 requests per month
  - Limited compute time
  - Personal/research use

- **Paid Tier**:
  - Usage-based pricing
  - Higher quotas
  - Commercial use allowed

### Estimating Costs
For typical Atlas API usage:
- Small AOI (<1 km²): ~$0.01-0.05 per request
- Medium AOI (1-10 km²): ~$0.05-0.25 per request
- Large AOI (>10 km²): ~$0.25-1.00 per request

Monitor usage in Google Cloud Console to avoid unexpected charges.