"""
Simple Vercel handler that bypasses the problematic runtime
"""

import sys
import os
import traceback

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Print debug info
print("🚀 Starting Vercel handler...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

try:
    # Import the Flask app
    from api import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    traceback.print_exc()
    # Create a fallback app
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({
            'status': 'error',
            'message': f'App import failed: {str(e)}',
            'fix': 'Check the logs'
        })

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'degraded', 'error': str(e)})

    @app.route('/api/test')
    def test():
        return jsonify({'message': 'Test endpoint working'})

# Vercel requires a variable named 'handler'
handler = app