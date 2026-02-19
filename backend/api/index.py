from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Enable CORS
    CORS(app, origins=["*"])

    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False

    # Import and register blueprints
    try:
        from api.chat import chat_bp
        from api.admin import admin_bp
        from api.unknown import unknown_bp

        app.register_blueprint(chat_bp, url_prefix='/api')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(unknown_bp, url_prefix='/api')
        print("✅ Blueprints registered successfully")
    except Exception as e:
        print(f"❌ Error registering blueprints: {e}")
        raise

    @app.route('/')
    def home():
        return {
            'status': 'online',
            'message': 'LAUTECH Chatbot API is running',
            'version': '1.0.0',
            'environment': os.environ.get('VERCEL_ENV', 'development')
        }

    @app.route('/api/health')
    def health():
        return {'status': 'healthy', 'timestamp': __import__('datetime').datetime.now().isoformat()}

    return app


# Create app instance
app = create_app()


# Vercel serverless handler - SIMPLIFIED
def handler(request):
    """Simple handler for Vercel"""
    return app(request)