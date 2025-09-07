#!/usr/bin/env python3
"""
Simple static file server for FLUX-LanternHive frontend
This can be used to serve the frontend files from your Google Cloud server.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class FLUXRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler for FLUX-LanternHive frontend"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

def main():
    """Start the frontend server"""
    port = int(os.getenv('FRONTEND_PORT', 8080))
    
    print(f"🌐 Starting FLUX-LanternHive Frontend Server...")
    print(f"Port: {port}")
    print(f"Directory: {os.getcwd()}")
    print(f"URL: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        with HTTPServer(('0.0.0.0', port), FLUXRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")

if __name__ == '__main__':
    main()


