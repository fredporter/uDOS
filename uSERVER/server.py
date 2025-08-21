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
import subprocess
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

@socketio.on('font_change')
def handle_font_change(data):
    """Handle font change requests"""
    font_name = data.get('font', 'default')
    log_message(f'Font changed to: {font_name}')
    
    # Broadcast font change to all clients
    socketio.emit('font_update', {
        'font': font_name,
        'timestamp': time.time()
    })

@socketio.on('display_change')
def handle_display_change(data):
    """Handle display mode changes"""
    display_mode = data.get('mode', 'normal')
    log_message(f'Display mode changed to: {display_mode}')
    
    # Broadcast display change to all clients
    socketio.emit('display_update', {
        'mode': display_mode,
        'timestamp': time.time()
    })

@socketio.on('palette_change')
def handle_palette_change(data):
    """Handle color palette changes"""
    palette_name = data.get('palette', 'teletext')
    log_message(f'Palette changed to: {palette_name}')
    
    # Broadcast palette change to all clients
    socketio.emit('palette_update', {
        'palette': palette_name,
        'timestamp': time.time()
    })

def process_udos_command(command):
    """Process uDOS command - integrate with uCORE"""
    # Placeholder implementation
    if command.startswith('help'):
        return {
            'output': '''uDOS Commands:
- help: Show this help
- status: System status
- modules: List modules
- fonts: List available fonts
- palettes: List available color palettes
- viewports: Show viewport commands
- font <name>: Change font (e.g., font c64, font mallard)
- palette <name>: Change color palette (e.g., palette teletext, palette retro)
- viewport <cmd>: Manage viewports (e.g., viewport launch wizard)
- display <mode>: Change display mode
- clear: Clear terminal output''',
            'success': True
        }
    elif command.startswith('status'):
        return {
            'output': f'uDOS Status: Running in DEV mode\nClients: {len(connected_clients)}\nModules: uCORE, uSERVER, uSCRIPT, uMEMORY',
            'success': True
        }
    elif command.startswith('modules'):
        modules = ['uCORE', 'uSERVER', 'uSCRIPT', 'uMEMORY', 'imp', 'ghost', 'sorcerer', 'tomb']
        return {
            'output': 'Available modules:\n' + '\n'.join(f'- {mod}' for mod in modules),
            'success': True
        }
    elif command.startswith('fonts'):
        fonts = [
            'c64', 'amiga', 'amstrad', 'atari', 'ibm', 'zx', 'apple2',
            'teletext', 'mode7', 'petscii', 'ascii', 'terminal',
            'mallard', 'mallard-neueue', 'mallard-blocky', 'blocky',
            'topaz', 'microknight', 'pot-noodle', 'terminus',
            'pragmata', 'perfect-dos', 'glass-tty', 'retro-computer'
        ]
        return {
            'output': 'Available fonts:\n' + '\n'.join(f'- {font}' for font in fonts),
            'success': True
        }
    elif command.startswith('palettes'):
        palettes = ['teletext', 'retro', 'light', 'dark', 'rainbow']
        return {
            'output': 'Available color palettes:\n' + '\n'.join(f'- {palette}' for palette in palettes),
            'success': True
        }
    elif command.startswith('viewports'):
        return {
            'output': '''Viewport Commands:
- viewport create <mode> [type]: Create new viewport
- viewport list [mode]: List active viewports  
- viewport close <id>: Close specific viewport
- viewport close-mode <mode>: Close all viewports for mode
- viewport launch <preset>: Launch preset configuration
- viewport cleanup: Clean up dead viewports

Available modes: wizard, dev, tomb, imp, sorcerer, drone, ghost, admin
Available types: development, monitoring, terminal, documentation, logs, dashboard, debug, administration
Available presets: wizard, sorcerer, imp, tomb, drone, ghost, dev-suite''',
            'success': True
        }
    elif command.startswith('font '):
        font_name = command[5:].strip()
        # Emit font change event
        socketio.emit('font_update', {'font': font_name})
        return {
            'output': f'Font changed to: {font_name}',
            'success': True
        }
    elif command.startswith('palette '):
        palette_name = command[8:].strip()
        # Emit palette change event
        socketio.emit('palette_update', {'palette': palette_name})
        return {
            'output': f'Color palette changed to: {palette_name}',
            'success': True
        }
    elif command.startswith('viewport '):
        # Handle viewport commands
        viewport_cmd = command[9:].strip()
        return handle_viewport_command(viewport_cmd)
    elif command.startswith('display '):
        display_mode = command[8:].strip()
        # Emit display change event
        socketio.emit('display_update', {'mode': display_mode})
        return {
            'output': f'Display mode changed to: {display_mode}',
            'success': True
        }
    elif command.strip() == 'clear':
        socketio.emit('clear_terminal')
        return {
            'output': 'Terminal cleared',
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

def handle_viewport_command(viewport_cmd):
    """Handle viewport management commands"""
    viewport_script = UDOS_ROOT / "extensions" / "viewport" / "viewport.sh"
    
    if not viewport_script.exists():
        return {
            'output': '❌ Viewport manager not available',
            'success': False
        }
    
    try:
        # Parse viewport command
        parts = viewport_cmd.split()
        if not parts:
            return {
                'output': '❌ Viewport command required. Type "viewports" for help.',
                'success': False
            }
        
        action = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Build command
        cmd = [str(viewport_script), action] + args
        
        # Execute viewport command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout if result.stdout else f'✅ Viewport {action} completed'
            return {
                'output': output,
                'success': True
            }
        else:
            error_output = result.stderr if result.stderr else f'❌ Viewport {action} failed'
            return {
                'output': error_output,
                'success': False
            }
            
    except subprocess.TimeoutExpired:
        return {
            'output': '❌ Viewport command timed out',
            'success': False
        }
    except Exception as e:
        return {
            'output': f'❌ Viewport error: {str(e)}',
            'success': False
        }

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
    
    # Browser opening disabled - use viewport manager instead
    # browser_thread = threading.Thread(target=open_browser, args=(f"http://{host}:{port}",))
    # browser_thread.daemon = True
    # browser_thread.start()
    
    # Start the server
    socketio.run(app, host=host, port=port, debug=True, use_reloader=False)

if __name__ == '__main__':
    main()
