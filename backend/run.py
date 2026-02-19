#!/usr/bin/env python
"""
LAUTECH Chatbot - Development Server Runner
Run this file to start the Flask development server
"""

import os
import sys
from api import app

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 LAUTECH Chatbot API Server")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Environment: Development")
    print(f"Host: http://localhost:5000")
    print(f"API endpoint: http://localhost:5000/api/chat")
    print("=" * 60)
    print("Press CTRL+C to stop the server")
    print("=" * 60)

    # Run the Flask app
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,
        debug=True,  # Enable debug mode for development
        threaded=True  # Handle multiple requests
    )