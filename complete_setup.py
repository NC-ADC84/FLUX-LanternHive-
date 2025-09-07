#!/usr/bin/env python3
"""
Complete FLUX-LanternHive Setup and Deployment Script
This script handles everything from local setup to Google Cloud deployment.
"""

import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path

def run_command(command, description, check=True, shell=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=shell, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        if result.stderr and result.returncode != 0:
            print(f"   Warning: {result.stderr.strip()}")
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check Docker
    if not run_command('docker --version', 'Checking Docker', check=False):
        print("❌ Docker not found. Please install Docker Desktop")
        return False
    
    # Check gcloud
    if not run_command('gcloud --version', 'Checking gcloud CLI', check=False):
        print("⚠️  gcloud CLI not found")
        return False
    
    return True

def setup_local_environment():
    """Set up local development environment"""
    print("\n🏠 Setting up local environment...")
    
    # Create virtual environment if it doesn't exist
    venv_path = Path('venv')
    if not venv_path.exists():
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            return False
    
    # Install dependencies
    if platform.system() == 'Windows':
        pip_cmd = 'venv\\Scripts\\pip'
    else:
        pip_cmd = 'venv/bin/pip'
    
    if not run_command(f'{pip_cmd} install -r requirements.txt', 'Installing dependencies'):
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        template_file = Path('env_template.txt')
        if template_file.exists():
            with open(template_file, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✓ Created .env file from template")
        else:
            with open(env_file, 'w') as f:
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                f.write("SECRET_KEY=your_flask_secret_key_here\n")
            print("✓ Created basic .env file")
    
    return True

def test_local_setup():
    """Test the local setup"""
    print("\n🧪 Testing local setup...")
    
    if platform.system() == 'Windows':
        python_cmd = 'venv\\Scripts\\python'
    else:
        python_cmd = 'venv/bin/python'
    
    test_script = '''
try:
    import flux_backend
    print("✓ Backend imports successfully")
    import enhanced_lanternhive
    print("✓ LanternHive imports successfully")
    print("✓ Local setup test passed")
except Exception as e:
    print(f"❌ Import test failed: {e}")
    exit(1)
'''
    
    return run_command(f'{python_cmd} -c "{test_script}"', 'Testing imports')

def setup_google_cloud():
    """Set up Google Cloud deployment"""
    print("\n☁️  Setting up Google Cloud...")
    
    project_id = 'tetris-effect-469618-t1'
    
    # Check authentication
    result = subprocess.run('gcloud auth list --filter=status:ACTIVE --format="value(account)"', 
                          shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("❌ No active Google Cloud authentication found")
        print("Please run: gcloud auth login")
        return False
    
    print(f"✓ Authenticated as: {result.stdout.strip()}")
    
    # Set project
    if not run_command(f'gcloud config set project {project_id}', 'Setting project'):
        return False
    
    # Enable APIs
    apis = [
        'cloudbuild.googleapis.com',
        'run.googleapis.com',
        'containerregistry.googleapis.com'
    ]
    
    for api in apis:
        if not run_command(f'gcloud services enable {api}', f'Enabling {api}'):
            return False
    
    return True

def deploy_to_cloud():
    """Deploy to Google Cloud Run"""
    print("\n🚀 Deploying to Google Cloud Run...")
    
    project_id = 'tetris-effect-469618-t1'
    image_name = f'gcr.io/{project_id}/flux-lanternhive'
    
    # Build Docker image
    if not run_command(f'docker build -t {image_name} .', 'Building Docker image'):
        return False
    
    # Push to Container Registry
    if not run_command(f'docker push {image_name}', 'Pushing to Container Registry'):
        return False
    
    # Deploy to Cloud Run
    deploy_cmd = f'''gcloud run deploy flux-lanternhive \
        --image {image_name} \
        --region us-central1 \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10 \
        --set-env-vars FLASK_ENV=production'''
    
    if not run_command(deploy_cmd, 'Deploying to Cloud Run'):
        return False
    
    # Get service URL
    result = subprocess.run('gcloud run services describe flux-lanternhive --region us-central1 --format="value(status.url)"', 
                          shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        service_url = result.stdout.strip()
        print(f"🌐 Service deployed at: {service_url}")
        return service_url
    
    return True

def test_deployment(service_url):
    """Test the deployed service"""
    print(f"\n🧪 Testing deployment at {service_url}...")
    
    # Test health endpoint
    if not run_command(f'curl -s {service_url}/api/health', 'Testing health endpoint', check=False):
        print("⚠️  Health check failed (curl might not be available)")
    
    return True

def open_services():
    """Open relevant services in browser"""
    print("\n🌐 Opening services...")
    
    try:
        # Open Google Cloud Console
        webbrowser.open('https://console.cloud.google.com/run?project=tetris-effect-469618-t1')
        
        # Open the deployed service
        webbrowser.open('https://server-e8a4-231986304766.us-central1.run.app')
        
        print("✓ Opened Google Cloud Console and deployed service")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")

def main():
    """Main setup and deployment function"""
    print("🚀 FLUX-LanternHive Complete Setup & Deployment")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install missing components.")
        return False
    
    # Set up local environment
    if not setup_local_environment():
        print("\n❌ Local setup failed.")
        return False
    
    # Test local setup
    if not test_local_setup():
        print("\n❌ Local setup test failed.")
        return False
    
    # Set up Google Cloud
    if not setup_google_cloud():
        print("\n❌ Google Cloud setup failed.")
        return False
    
    # Deploy to cloud
    service_url = deploy_to_cloud()
    if not service_url:
        print("\n❌ Deployment failed.")
        return False
    
    # Test deployment
    test_deployment(service_url)
    
    # Open services
    open_services()
    
    print("\n" + "=" * 60)
    print("🎉 FLUX-LanternHive Setup & Deployment Complete!")
    print("=" * 60)
    print(f"🌐 Service URL: {service_url}")
    print(f"📊 Monitor: https://console.cloud.google.com/run/detail/us-central1/flux-lanternhive/metrics?project=tetris-effect-469618-t1")
    print(f"🔧 Logs: https://console.cloud.google.com/run/detail/us-central1/flux-lanternhive/logs?project=tetris-effect-469618-t1")
    
    print("\n📋 Next Steps:")
    print("1. Set environment variables in Cloud Run console")
    print("2. Test the deployed application")
    print("3. Serve frontend locally: python serve_frontend.py")
    print("4. Access your application at the service URL")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


