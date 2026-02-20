from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Test handler works!"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

handler = app