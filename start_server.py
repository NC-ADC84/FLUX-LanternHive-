#!/usr/bin/env python3
"""
FLUX-LanternHive Integration Startup Script
This script starts the backend server with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import flask
        import flask_socketio
        import openai
        import cryptography
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy env_template.txt to .env and configure your settings")
        print("Required variables:")
        print("  - OPENAI_API_KEY (for LanternHive cognitive features)")
        print("  - SECRET_KEY (for Flask session security)")
        return False
    
    # Load and check .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    secret_key = os.getenv('SECRET_KEY')
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("⚠️  OPENAI_API_KEY not configured in .env file")
        print("LanternHive cognitive features will be disabled")
    
    if not secret_key or secret_key == 'your_flask_secret_key_here':
        print("⚠️  SECRET_KEY not configured in .env file")
        print("Using default secret key (not recommended for production)")
    
    return True

def start_server():
    """Start the FLUX backend server"""
    print("🚀 Starting FLUX-LanternHive Backend Server...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment configuration
    check_env_file()
    
    # Import and start the server
    try:
        from flux_backend import app, socketio, initialize_lantern_hive, initialize_ptpf_generator, initialize_strategy_engine, initialize_lantern_framework
        
        # Initialize LanternHive
        print("🧠 Initializing LanternHive...")
        lantern_status = initialize_lantern_hive()
        print(f"LanternHive Status: {'✓ Enabled' if lantern_status else '⚠️  Disabled (no API key)'}")
        
        # Initialize PTPF+FLUX Generator
        print("🎯 Initializing PTPF+FLUX Generator...")
        ptpf_status = initialize_ptpf_generator()
        print(f"PTPF+FLUX Generator Status: {'✓ Enabled' if ptpf_status else '⚠️  Disabled'}")
        
        # Initialize Recursive Strategy Engine
        print("🔄 Initializing Recursive Strategy Engine...")
        strategy_status = initialize_strategy_engine()
        print(f"Recursive Strategy Engine Status: {'✓ Enabled' if strategy_status else '⚠️  Disabled'}")
        
        # Initialize Lantern Framework
        print("🏮 Initializing Lantern Framework...")
        lantern_framework_status = initialize_lantern_framework()
        print(f"Lantern Framework Status: {'✓ Enabled' if lantern_framework_status else '⚠️  Disabled'}")
        
        # Get port from environment variable (Cloud Run requirement)
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_ENV') != 'production'
        
        # Force production mode for Cloud Run
        if os.getenv('FLASK_ENV') == 'production':
            debug = False
        
        print("\n🌐 Server Configuration:")
        print(f"  Host: 0.0.0.0")
        print(f"  Port: {port}")
        print(f"  Debug: {debug}")
        print(f"  Async Mode: threading")
        
        print("\n📡 WebSocket Endpoints:")
        print("  - /socket.io/ (Socket.IO connection)")
        print("  - execute_flux (FLUX code execution)")
        print("  - lantern_query (LanternHive cognitive queries)")
        print("  - generate_ptpf_flux (PTPF+FLUX generation)")
        print("  - rehydrate_ptpf (PTPF rehydration)")
        print("  - get_ptpf_session_history (PTPF session history)")
        print("  - clear_ptpf_session (Clear PTPF session)")
        print("  - get_system_state (System state retrieval)")
        
        print("\n🔗 REST API Endpoints:")
        print("  - GET  /api/health (Health check)")
        print("  - POST /api/flux/parse (Parse FLUX code)")
        print("  - POST /api/flux/execute (Execute FLUX code)")
        print("  - POST /api/lantern/process (Process with LanternHive)")
        print("  - POST /api/ptpf/generate (Generate PTPF+FLUX)")
        print("  - POST /api/ptpf/rehydrate (Rehydrate PTPF)")
        print("  - GET  /api/ptpf/session (Get PTPF session history)")
        print("  - DELETE /api/ptpf/session (Clear PTPF session)")
        print("  - GET  /api/ptpf/status (Get PTPF status)")
        print("  - GET  /api/connections (Get active connections)")
        print("  - GET  /api/memory (Get floating memory)")
        print("  - GET  /api/fingerprints (Get fingerprints)")
        print("  - POST /api/lantern/agi15/translate (AGI15 translation)")
        print("  - POST /api/lantern/cluster/process (Cluster syntax processing)")
        print("  - POST /api/lantern/warden/synthesize (Warden reality synthesis)")
        print("  - POST /api/lantern/brack/execute (Brack code execution)")
        
        print("\n" + "=" * 50)
        print("🎯 Frontend Access:")
        print("  Open index.html in your web browser")
        print("  Or serve it with: python -m http.server 8080")
        print("=" * 50)
        
        # Start the server
        if debug:
            socketio.run(app, debug=debug, host='0.0.0.0', port=port)
        else:
            # Production mode - use allow_unsafe_werkzeug for Cloud Run
            socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_server()
