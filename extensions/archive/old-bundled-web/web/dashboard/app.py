"""
uDOS Advanced Dashboard Application
Integrates real-time metrics, file operations, and system management
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import os
from datetime import datetime
from services.metrics_service import SystemMetricsService
from services.file_browser_service import FileBrowserService

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize services
metrics_service = SystemMetricsService()
file_service = FileBrowserService(os.path.expanduser('~'))

@app.route('/')
def dashboard():
    """Render the main dashboard interface."""
    return render_template('index.html')

# Import routes
from routes import file_routes

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    metrics_service.start_collection()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')
    metrics_service.stop_collection()

@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle real-time metrics request from client."""
    metrics = metrics_service.get_latest_metrics()
    emit('metrics_update', metrics_service.to_json(metrics))

@socketio.on('request_metrics_history')
def handle_metrics_history_request(metric_type=None):
    """Handle request for historical metrics data."""
    history = metrics_service.get_metrics_history(metric_type)
    emit('metrics_history_update', metrics_service.to_json(history))

def start_dashboard(port=5000, debug=False):
    """Start the dashboard server."""
    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)
    finally:
        metrics_service.stop_collection()

if __name__ == '__main__':
    start_dashboard(debug=True)
