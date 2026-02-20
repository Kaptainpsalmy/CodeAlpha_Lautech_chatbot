"""
Main Vercel handler for LAUTECH Chatbot
"""

import sys
import os
import traceback

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import the Flask app from api
    from api import app

    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    traceback.print_exc()
    # Create a fallback app for debugging
    from flask import Flask, jsonify

    app = Flask(__name__)


    @app.route('/')
    def home():
        return jsonify({
            'status': 'error',
            'message': f'App import failed: {str(e)}',
            'fix': 'Check the logs above'
        })


    @app.route('/api/health')
    def health():
        return jsonify({'status': 'degraded', 'error': str(e)})

# This is CRITICAL - Vercel looks for 'handler'
handler = app