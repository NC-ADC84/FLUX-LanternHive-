@echo off
REM FLUX-LanternHive Google Cloud Deployment Script for Windows
REM Usage: deploy_windows.bat [project-id]

setlocal enabledelayedexpansion

set PROJECT_ID=%1
if "%PROJECT_ID%"=="" set PROJECT_ID=tetris-effect-469618-t1

echo 🚀 FLUX-LanternHive Google Cloud Deployment
echo ==============================================
echo Project ID: %PROJECT_ID%
echo.

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ❌ gcloud CLI not found. Please install it first.
    echo Run: install_gcloud_windows.ps1
    pause
    exit /b 1
)

echo ✅ gcloud CLI found

REM Check authentication
echo 🔐 Checking authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" > temp_auth.txt 2>&1
set /p AUTH_ACCOUNT=<temp_auth.txt
del temp_auth.txt

if "%AUTH_ACCOUNT%"=="" (
    echo ❌ No active Google Cloud authentication found
    echo Please run: gcloud auth login
    pause
    exit /b 1
)

echo ✅ Authenticated as: %AUTH_ACCOUNT%

REM Set project
echo 🎯 Setting project...
gcloud config set project %PROJECT_ID%

REM Enable APIs
echo 🔧 Enabling required APIs...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

REM Build and push image
echo 🏗️  Building Docker image...
set IMAGE_NAME=gcr.io/%PROJECT_ID%/flux-lanternhive
docker build -t %IMAGE_NAME% .

if errorlevel 1 (
    echo ❌ Docker build failed. Make sure Docker is running.
    pause
    exit /b 1
)

echo 📤 Pushing to Container Registry...
docker push %IMAGE_NAME%

if errorlevel 1 (
    echo ❌ Docker push failed. Check your authentication.
    pause
    exit /b 1
)

REM Deploy to Cloud Run
echo 🚀 Deploying to Cloud Run...
gcloud run deploy flux-lanternhive ^
    --image %IMAGE_NAME% ^
    --region us-central1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --port 8080 ^
    --memory 1Gi ^
    --cpu 1 ^
    --max-instances 10 ^
    --set-env-vars FLASK_ENV=production

if errorlevel 1 (
    echo ❌ Deployment failed.
    pause
    exit /b 1
)

REM Get service URL
echo 📡 Getting service URL...
for /f "tokens=*" %%i in ('gcloud run services describe flux-lanternhive --region us-central1 --format="value(status.url)"') do set SERVICE_URL=%%i

echo.
echo 🎉 Deployment Complete!
echo ======================
echo 🌐 Service URL: %SERVICE_URL%
echo 📊 Monitor: https://console.cloud.google.com/run/detail/us-central1/flux-lanternhive/metrics?project=%PROJECT_ID%
echo 🔧 Logs: https://console.cloud.google.com/run/detail/us-central1/flux-lanternhive/logs?project=%PROJECT_ID%

echo.
echo 📋 Next Steps:
echo 1. Test the deployment: curl %SERVICE_URL%/api/health
echo 2. Set environment variables for production
echo 3. Update your frontend configuration

echo.
echo Press any key to continue...
pause >nul


