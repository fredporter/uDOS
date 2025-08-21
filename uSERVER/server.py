#!/usr/bin/env python3
"""
uDOS Server - Omni-device uCODE Window
Serves the browser-based UI for universal uDOS access
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit
import json

# Add uCORE to path for imports
UDOS_ROOT = Path(__file__).parent.parent
sys.path.append(str(UDOS_ROOT / "uCORE" / "core"))

app = Flask(__name__, 
           static_folder=str(UDOS_ROOT / "uCORE" / "launcher" / "universal" / "ucode-ui" / "static"),
           template_folder=str(UDOS_ROOT / "uCORE" / "launcher" / "universal" / "ucode-ui"))

app.config['SECRET_KEY'] = 'udos-dev-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
connected_clients = []
system_logs = []

@app.route('/')
def index():
    """Main uCODE interface"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """System status endpoint"""
    return jsonify({
        'status': 'running',
        'mode': 'DEV',
        'clients': len(connected_clients),
        'udos_root': str(UDOS_ROOT),
        'modules': ['uCORE', 'uSERVER', 'uSCRIPT', 'uMEMORY']
    })

@app.route('/api/logs')
def get_logs():
    """Get system logs"""
    return jsonify(system_logs[-100:])  # Last 100 logs

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.append(client_id)
    emit('status', {'message': f'Connected to uDOS (Client: {client_id})'})
    log_message(f'Client connected: {client_id}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        connected_clients.remove(client_id)
    log_message(f'Client disconnected: {client_id}')

@socketio.on('execute_command')
def handle_command(data):
    """Execute uDOS command"""
    command = data.get('command', '')
    log_message(f'Command received: {command}')
    
    # Process command (placeholder - integrate with uCORE)
    result = process_udos_command(command)
    
    emit('command_result', {
        'command': command,
        'result': result,
        'timestamp': time.time()
    })

def process_udos_command(command):
    """Process uDOS command - integrate with uCORE"""
    # Placeholder implementation
    if command.startswith('help'):
        return {
            'output': 'uDOS Commands:\n- help: Show this help\n- status: System status\n- modules: List modules',
            'success': True
        }
    elif command.startswith('status'):
        return {
            'output': f'uDOS Status: Running in DEV mode\nClients: {len(connected_clients)}',
            'success': True
        }
    elif command.startswith('modules'):
        modules = ['uCORE', 'uSERVER', 'uSCRIPT', 'uMEMORY', 'imp', 'ghost', 'sorcerer', 'tomb']
        return {
            'output': 'Available modules:\n' + '\n'.join(f'- {mod}' for mod in modules),
            'success': True
        }
    else:
        return {
            'output': f'Unknown command: {command}\nType "help" for available commands.',
            'success': False
        }

def log_message(message):
    """Add message to system logs"""
    log_entry = {
        'timestamp': time.time(),
        'message': message
    }
    system_logs.append(log_entry)
    
    # Broadcast to all connected clients
    socketio.emit('log_update', log_entry)

def open_browser(url, delay=2):
    """Open browser after server starts"""
    time.sleep(delay)
    print(f"\n🌐 Opening uDOS in browser: {url}")
    webbrowser.open(url)

def main():
    """Main entry point"""
    host = '127.0.0.1'
    port = 8080
    
    print("🚀 Starting uDOS Server - Omni-device uCODE Window")
    print(f"📁 uDOS Root: {UDOS_ROOT}")
    print(f"🌐 Server will start at: http://{host}:{port}")
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser, args=(f"http://{host}:{port}",))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    socketio.run(app, host=host, port=port, debug=True, use_reloader=False)

if __name__ == '__main__':
    main()
