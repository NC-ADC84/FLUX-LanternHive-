#!/usr/bin/env python3
"""
FLUX-LanternHive Integration Setup Script
This script sets up the development environment and installs dependencies.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("Please install Python 3.8 or higher")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    venv_path = Path('venv')
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    return run_command('python -m venv venv', 'Creating virtual environment')

def activate_venv_command():
    """Get the command to activate virtual environment based on OS"""
    if platform.system() == 'Windows':
        return 'venv\\Scripts\\activate'
    else:
        return 'source venv/bin/activate'

def install_dependencies():
    """Install Python dependencies"""
    activate_cmd = activate_venv_command()
    
    if platform.system() == 'Windows':
        pip_cmd = 'venv\\Scripts\\pip'
    else:
        pip_cmd = 'venv/bin/pip'
    
    # Upgrade pip first
    if not run_command(f'{pip_cmd} install --upgrade pip', 'Upgrading pip'):
        return False
    
    # Install requirements
    return run_command(f'{pip_cmd} install -r requirements.txt', 'Installing dependencies')

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path('.env')
    template_file = Path('env_template.txt')
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if not template_file.exists():
        print("⚠️  env_template.txt not found, creating basic .env file")
        with open(env_file, 'w') as f:
            f.write("# FLUX-LanternHive Integration Environment Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("SECRET_KEY=your_flask_secret_key_here\n")
    else:
        # Copy template to .env
        with open(template_file, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
    
    print("✓ Created .env file from template")
    print("⚠️  Please edit .env file and add your actual API keys")
    return True

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    activate_cmd = activate_venv_command()
    python_cmd = 'venv\\Scripts\\python' if platform.system() == 'Windows' else 'venv/bin/python'
    
    # Test import
    test_script = '''
try:
    import flux_backend
    print("✓ Backend imports successfully")
    import enhanced_lanternhive
    print("✓ LanternHive imports successfully")
    print("✓ Installation test passed")
except Exception as e:
    print(f"❌ Import test failed: {e}")
    exit(1)
'''
    
    return run_command(f'{python_cmd} -c "{test_script}"', 'Testing imports')

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "=" * 60)
    print("🎉 FLUX-LanternHive Integration Setup Complete!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your OpenAI API key:")
    print("   OPENAI_API_KEY=your_actual_api_key_here")
    print("   SECRET_KEY=your_secure_secret_key_here")
    
    print("\n2. Start the backend server:")
    if platform.system() == 'Windows':
        print("   venv\\Scripts\\activate")
        print("   python start_server.py")
    else:
        print("   source venv/bin/activate")
        print("   python start_server.py")
    
    print("\n3. Open the frontend:")
    print("   Open index.html in your web browser")
    print("   Or serve it with: python -m http.server 8080")
    
    print("\n4. Access the application:")
    print("   Backend: http://localhost:5000")
    print("   Frontend: http://localhost:8080 (if using http.server)")
    
    print("\n📚 Documentation:")
    print("   - README.md: Complete setup and usage guide")
    print("   - FLUX-language-spec.md: FLUX language specification")
    print("   - Hive_mind_thought.md: LanternHive cognitive framework")
    
    print("\n🔧 Development:")
    print("   - Run tests: pytest")
    print("   - Format code: black .")
    print("   - Lint code: flake8 .")
    
    print("\n" + "=" * 60)

def main():
    """Main setup function"""
    print("🚀 FLUX-LanternHive Integration Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to set up virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == '__main__':
    main()


