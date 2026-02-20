"""
WSGI entry point for Vercel
"""
import sys
import os

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your Flask app
try:
    from api import app as application

    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    # Create a fallback app for debugging
    from flask import Flask, jsonify

    application = Flask(__name__)


    @application.route('/')
    def home():
        return jsonify({
            'status': 'error',
            'message': f'App import failed: {str(e)}'
        })

# Vercel expects 'app'
app = application