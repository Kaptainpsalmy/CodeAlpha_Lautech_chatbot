"""
Ultra-simple test handler for Vercel
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Simple handler is working!',
        'endpoints': ['/api/health', '/api/test']
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/test')
def test():
    return jsonify({'message': 'Test endpoint working'})

# CRITICAL: Vercel looks for 'handler'
handler = app