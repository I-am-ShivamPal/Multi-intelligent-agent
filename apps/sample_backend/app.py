#!/usr/bin/env python3
"""Sample Backend Application"""
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello from backend", "data": [1, 2, 3, 4, 5]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)