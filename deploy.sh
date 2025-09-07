#!/bin/bash

# FLUX-LanternHive Google Cloud Deployment Script
# Usage: ./deploy.sh [project-id]

set -e

PROJECT_ID=${1:-"tetris-effect-469618-t1"}
SERVICE_NAME="flux-lanternhive"
REGION="us-central1"

echo "🚀 FLUX-LanternHive Google Cloud Deployment"
echo "=============================================="
echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it from:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check authentication
echo "🔐 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ No active Google Cloud authentication found"
    echo "Please run: gcloud auth login"
    exit 1
fi

echo "✓ Authenticated as: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"

# Set project
echo "🎯 Setting project..."
gcloud config set project $PROJECT_ID

# Enable APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push image
echo "🏗️  Building Docker image..."
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
docker build -t $IMAGE_NAME .

echo "📤 Pushing to Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars FLASK_ENV=production

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Monitor: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"
echo "🔧 Logs: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/logs?project=$PROJECT_ID"

echo ""
echo "📋 Next Steps:"
echo "1. Test the deployment: curl $SERVICE_URL/api/health"
echo "2. Update your frontend configuration"
echo "3. Set up environment variables for production"


