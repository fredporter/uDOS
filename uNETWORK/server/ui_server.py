#!/usr/bin/env python3
"""
uDOS UI Server (Crypt+ roles)
Runs Flask/FastAPI web UI and advanced Python features.
"""
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "uDOS UI Server (Crypt+) is running."

@app.route('/run_ucode', methods=['POST'])
def run_ucode():
    script = request.json.get('script')
    args = request.json.get('args', [])
    if not script or not os.path.isfile(script):
        return jsonify({'error': 'Script not found'}), 404
    # Run script and return output
    import subprocess
    try:
        result = subprocess.run([script] + args, capture_output=True, text=True, check=True)
        return jsonify({'output': result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
