from flask import Flask
from flask_cors import CORS
import os
import sys

# Add parent directory to path so we can import database modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_app():
    """Create and configure the Flask application"""

    app = Flask(__name__)

    # Enable CORS for all routes (allows frontend to connect)
    CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500", "*"])

    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False  # Preserve JSON order

    # Register blueprints (routes)
    from .chat import chat_bp
    from .admin import admin_bp
    from .unknown import unknown_bp

    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(unknown_bp, url_prefix='/api')

    # Root endpoint for testing
    @app.route('/')
    def home():
        return {
            'status': 'online',
            'message': 'LAUTECH Chatbot API is running',
            'version': '1.0.0'
        }

    # Health check endpoint
    @app.route('/api/test')
    def test():
        from datetime import datetime
        return jsonify({
            'status': 'ok',
            'message': 'API is working',
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('VERCEL_ENV', 'development')
        })


# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)