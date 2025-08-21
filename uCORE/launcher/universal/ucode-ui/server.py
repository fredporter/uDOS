#!/usr/bin/env python3
"""
uDOS Universal Code Interface Server
Simple Flask-SocketIO server for the enhanced uDOS interface
"""

from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit
import os
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uDOS-dev-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
connected_clients = 0
system_status = {
    'mode': 'DEV',
    'clients': 0,
    'modules': 'All systems operational',
    'display_mode': 'BBC',
    'current_font': 'MODE7GX3'
}

@app.route('/')
def index():
    """Serve the main interface"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: index.html not found", 404

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, fonts)"""
    return send_from_directory('static', filename)

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return system_status

@app.route('/api/display', methods=['POST'])
def api_display():
    """API endpoint for display configuration"""
    # This would handle display mode changes from the lean browser
    return {'status': 'ok'}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    global connected_clients
    connected_clients += 1
    system_status['clients'] = connected_clients
    
    emit('status_update', system_status)
    emit('message', {
        'type': 'info',
        'content': f'🌐 Client connected. Total clients: {connected_clients}'
    })
    
    print(f"Client connected. Total: {connected_clients}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    global connected_clients
    connected_clients = max(0, connected_clients - 1)
    system_status['clients'] = connected_clients
    
    print(f"Client disconnected. Total: {connected_clients}")

@socketio.on('command')
def handle_command(data):
    """Handle commands from the interface"""
    command = data.get('command', '').strip()
    
    if command:
        print(f"Command received: {command}")
        
        # Echo the command back
        emit('command_response', {
            'command': command,
            'response': f'✅ Command executed: {command}',
            'type': 'success'
        })
        
        # Update system status if needed
        if command.startswith('font '):
            font_name = command.split(' ', 1)[1]
            system_status['current_font'] = font_name
            emit('status_update', system_status)
        elif command.startswith('display '):
            display_mode = command.split(' ', 1)[1].upper()
            system_status['display_mode'] = display_mode
            emit('status_update', system_status)

@socketio.on('font_change')
def handle_font_change(data):
    """Handle font changes"""
    font_name = data.get('font', 'MODE7GX3')
    system_status['current_font'] = font_name
    
    emit('status_update', system_status, broadcast=True)
    print(f"Font changed to: {font_name}")

@socketio.on('display_change')
def handle_display_change(data):
    """Handle display mode changes"""
    display_mode = data.get('mode', 'BBC').upper()
    system_status['display_mode'] = display_mode
    
    emit('status_update', system_status, broadcast=True)
    print(f"Display mode changed to: {display_mode}")

def status_updater():
    """Background thread to send periodic status updates"""
    while True:
        time.sleep(30)  # Update every 30 seconds
        socketio.emit('status_update', system_status, broadcast=True)

def main():
    """Main server function"""
    print("🚀 Starting uDOS Universal Code Interface Server...")
    print("📺 Enhanced UI with clean data input")
    print("🌈 MODE7GX teletext fonts loaded")
    print("🖥️  Amiga, C64, and experimental fonts available")
    print("🔧 Display management system ready")
    print("")
    print("Server starting on http://localhost:8080")
    print("Press Ctrl+C to stop")
    
    # Start background status updater
    status_thread = threading.Thread(target=status_updater, daemon=True)
    status_thread.start()
    
    # Start the server
    try:
        socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()
