#!/usr/bin/env python3
"""
Google Cloud Deployment Script for FLUX-LanternHive Integration
This script deploys the application to Google Cloud Run.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_gcloud_auth():
    """Check if gcloud is authenticated"""
    print("🔐 Checking Google Cloud authentication...")
    
    # Check if gcloud is installed
    if not run_command('gcloud --version', 'Checking gcloud installation', check=False):
        print("❌ gcloud CLI not found. Please install it from:")
        print("   https://cloud.google.com/sdk/docs/install")
        return False
    
    # Check authentication
    result = subprocess.run('gcloud auth list --filter=status:ACTIVE --format="value(account)"', 
                          shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("❌ No active Google Cloud authentication found")
        print("Please run: gcloud auth login")
        return False
    
    print(f"✓ Authenticated as: {result.stdout.strip()}")
    return True

def set_project(project_id):
    """Set the Google Cloud project"""
    print(f"🎯 Setting project to: {project_id}")
    return run_command(f'gcloud config set project {project_id}', 'Setting project')

def enable_apis(project_id):
    """Enable required Google Cloud APIs"""
    print("🔧 Enabling required APIs...")
    
    apis = [
        'cloudbuild.googleapis.com',
        'run.googleapis.com',
        'containerregistry.googleapis.com'
    ]
    
    for api in apis:
        if not run_command(f'gcloud services enable {api}', f'Enabling {api}'):
            return False
    
    return True

def build_and_deploy(project_id, service_name='flux-lanternhive', region='us-central1'):
    """Build and deploy the application"""
    print(f"🚀 Building and deploying to Cloud Run...")
    
    # Build the container
    image_name = f'gcr.io/{project_id}/{service_name}'
    if not run_command(f'docker build -t {image_name} .', 'Building Docker image'):
        return False
    
    # Push to Container Registry
    if not run_command(f'docker push {image_name}', 'Pushing to Container Registry'):
        return False
    
    # Deploy to Cloud Run
    deploy_cmd = f'''gcloud run deploy {service_name} \
        --image {image_name} \
        --region {region} \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10 \
        --set-env-vars FLASK_ENV=production'''
    
    if not run_command(deploy_cmd, 'Deploying to Cloud Run'):
        return False
    
    # Get the service URL
    result = subprocess.run(f'gcloud run services describe {service_name} --region {region} --format="value(status.url)"', 
                          shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        service_url = result.stdout.strip()
        print(f"🌐 Service deployed at: {service_url}")
        return service_url
    
    return True

def create_env_secrets(project_id, region='us-central1'):
    """Create environment variables as secrets"""
    print("🔐 Setting up environment variables...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found. Please create it with your configuration.")
        return True
    
    # Read .env file
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Set environment variables for Cloud Run
    for key, value in env_vars.items():
        if key in ['OPENAI_API_KEY', 'SECRET_KEY']:
            print(f"   Setting {key}...")
            # Note: In production, you'd want to use Google Secret Manager
            # For now, we'll set them as environment variables
            run_command(f'gcloud run services update flux-lanternhive --region {region} --set-env-vars {key}={value}', 
                       f'Setting {key}', check=False)
    
    return True

def main():
    """Main deployment function"""
    print("🚀 FLUX-LanternHive Google Cloud Deployment")
    print("=" * 50)
    
    # Get project ID from command line or use default
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
    else:
        project_id = 'tetris-effect-469618-t1'  # Your project ID
    
    print(f"Project ID: {project_id}")
    
    # Check authentication
    if not check_gcloud_auth():
        sys.exit(1)
    
    # Set project
    if not set_project(project_id):
        sys.exit(1)
    
    # Enable APIs
    if not enable_apis(project_id):
        sys.exit(1)
    
    # Build and deploy
    service_url = build_and_deploy(project_id)
    if not service_url:
        print("❌ Deployment failed")
        sys.exit(1)
    
    # Set up environment variables
    create_env_secrets(project_id)
    
    print("\n" + "=" * 50)
    print("🎉 Deployment Complete!")
    print("=" * 50)
    print(f"🌐 Service URL: {service_url}")
    print(f"📊 Monitor: https://console.cloud.google.com/run/detail/us-central1/flux-lanternhive/metrics?project={project_id}")
    print(f"🔧 Logs: https://console.cloud.google.com/run/detail/us-central1/flux-lanternhive/logs?project={project_id}")
    
    print("\n📋 Next Steps:")
    print("1. Update your frontend to use the new service URL")
    print("2. Test the deployment")
    print("3. Set up custom domain (optional)")
    print("4. Configure monitoring and alerts")

if __name__ == '__main__':
    main()


