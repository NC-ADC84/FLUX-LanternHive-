# FLUX-LanternHive Google Cloud Deployment Guide

## 🚀 Complete Production Deployment

This guide will help you deploy your FLUX-LanternHive application to Google Cloud Run.

### Prerequisites

1. **Google Cloud Project**: `tetris-effect-469618-t1`
2. **Google Cloud CLI**: Install from [here](https://cloud.google.com/sdk/docs/install)
3. **Docker**: For building container images
4. **OpenAI API Key**: For LanternHive cognitive features

## Step 1: Install Google Cloud CLI

### Windows (PowerShell)
```powershell
# Download and install gcloud CLI
# Visit: https://cloud.google.com/sdk/docs/install-sdk#windows
# Or use winget:
winget install Google.CloudSDK
```

### Alternative: Use Cloud Shell
If you prefer not to install locally, you can use [Google Cloud Shell](https://shell.cloud.google.com/) which has gcloud pre-installed.

## Step 2: Authenticate and Configure

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project
gcloud config set project tetris-effect-469618-t1

# Verify configuration
gcloud config list
```

## Step 3: Enable Required APIs

```bash
# Enable necessary Google Cloud APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Step 4: Create Environment Configuration

Create a `.env` file with your production settings:

```bash
# Copy the template
cp env_template.txt .env

# Edit .env file with your actual values
OPENAI_API_KEY=your_actual_openai_api_key_here
SECRET_KEY=your_secure_secret_key_here
FLASK_ENV=production
```

## Step 5: Deploy to Google Cloud Run

### Option A: Using the Deployment Script (Recommended)

```bash
# Make script executable (Linux/Mac)
chmod +x deploy.sh

# Deploy
./deploy.sh tetris-effect-469618-t1
```

### Option B: Manual Deployment

```bash
# Build the Docker image
docker build -t gcr.io/tetris-effect-469618-t1/flux-lanternhive .

# Push to Google Container Registry
docker push gcr.io/tetris-effect-469618-t1/flux-lanternhive

# Deploy to Cloud Run
gcloud run deploy flux-lanternhive \
    --image gcr.io/tetris-effect-469618-t1/flux-lanternhive \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars FLASK_ENV=production
```

## Step 6: Configure Environment Variables

After deployment, set your environment variables:

```bash
# Set OpenAI API Key
gcloud run services update flux-lanternhive \
    --region us-central1 \
    --set-env-vars OPENAI_API_KEY=your_actual_api_key

# Set Secret Key
gcloud run services update flux-lanternhive \
    --region us-central1 \
    --set-env-vars SECRET_KEY=your_secure_secret_key
```

## Step 7: Test the Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe flux-lanternhive --region us-central1 --format="value(status.url)")

# Test health endpoint
curl $SERVICE_URL/api/health

# Test FLUX parsing
curl -X POST $SERVICE_URL/api/flux/parse \
    -H "Content-Type: application/json" \
    -d '{"code": "connection test { floating<string> msg = \"Hello World\" }"}'
```

## Step 8: Frontend Integration

Your frontend is already configured to work with your Google Cloud server. The `app.js` file will automatically:

- Connect to `https://server-e8a4-231986304766.us-central1.run.app` in production
- Connect to `http://localhost:5000` in development

### Serve Frontend Locally (for testing)
```bash
# Option 1: Python HTTP server
python -m http.server 8080

# Option 2: Use the custom server
python serve_frontend.py
```

### Deploy Frontend to Google Cloud (Optional)
You can also deploy the frontend as a separate Cloud Run service or use Google Cloud Storage for static hosting.

## Step 9: Monitor and Maintain

### View Logs
```bash
gcloud run services logs read flux-lanternhive --region us-central1
```

### Monitor Performance
Visit: https://console.cloud.google.com/run/detail/us-central1/flux-lanternhive/metrics?project=tetris-effect-469618-t1

### Update Deployment
```bash
# Rebuild and redeploy
./deploy.sh tetris-effect-469618-t1
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Denied**
   ```bash
   # Ensure you have the necessary IAM roles
   gcloud projects add-iam-policy-binding tetris-effect-469618-t1 \
       --member="user:$(gcloud config get-value account)" \
       --role="roles/run.admin"
   ```

3. **Docker Build Fails**
   ```bash
   # Ensure Docker is running
   docker --version
   docker ps
   ```

4. **API Not Enabled**
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com
   ```

### Health Check

Test your deployment:
```bash
# Health check
curl https://server-e8a4-231986304766.us-central1.run.app/api/health

# Expected response:
{
  "status": "healthy",
  "lantern_hive_enabled": true,
  "active_connections": 0,
  "floating_memory_blocks": 0,
  "fingerprints": 0
}
```

## Production Checklist

- [ ] Google Cloud CLI installed and authenticated
- [ ] Required APIs enabled
- [ ] Environment variables configured
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Health endpoint responding
- [ ] Frontend connecting to backend
- [ ] LanternHive cognitive features working
- [ ] Monitoring and logging configured

## Cost Optimization

- **Memory**: 1Gi (adjust based on usage)
- **CPU**: 1 (adjust based on load)
- **Max Instances**: 10 (prevents runaway costs)
- **Min Instances**: 0 (scales to zero when not in use)

## Security Considerations

- Environment variables are encrypted at rest
- HTTPS is enabled by default
- CORS is configured for your frontend
- No authentication required (adjust as needed)

## Next Steps After Deployment

1. **Custom Domain**: Set up a custom domain if needed
2. **SSL Certificate**: Configure custom SSL (optional)
3. **Monitoring**: Set up alerts and monitoring
4. **Backup**: Configure backup strategies
5. **Scaling**: Monitor and adjust scaling parameters

---

**Your FLUX-LanternHive application will be available at:**
`https://server-e8a4-231986304766.us-central1.run.app`

**Frontend can be accessed at:**
`http://localhost:8080` (when served locally)


