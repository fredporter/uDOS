#!/usr/bin/env python3
"""
uDOS Server - Enhanced with uCORE Integration
Serves the browser-based UI with startup checks and system validation
"""

import os
import sys
import json
import time
import subprocess
import threading
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit

# Add uCORE to path for imports
UDOS_ROOT = Path(__file__).parent.parent
UI_PATH = UDOS_ROOT / "uCORE" / "launcher" / "universal" / "ucode-ui"
sys.path.append(str(UDOS_ROOT / "uCORE" / "core"))

app = Flask(__name__, 
           static_folder=str(UI_PATH / "static"),
           template_folder=str(UI_PATH))

app.config['SECRET_KEY'] = 'udos-secure-key-v131'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
connected_clients = []
system_logs = []
startup_complete = False
system_status = {
    'server_running': True,
    'startup_time': time.time(),
    'checks_passed': 0,
    'total_checks': 6,
    'current_check': 'Starting...',
    'udos_mode': os.environ.get('UDOS_CURRENT_ROLE', 'wizard'),
    'access_level': os.environ.get('UDOS_ACCESS_LEVEL', '100')
}

@app.route('/')
def index():
    """Main uCODE interface with startup integration"""
    # Only run startup checks once on first load
    global startup_complete
    if not startup_complete:
        # Check if startup is already in progress
        if not hasattr(app, '_startup_in_progress'):
            app._startup_in_progress = True
            threading.Thread(target=run_startup_checks, daemon=True).start()
    
    return render_template('index.html', 
                         udos_mode=system_status['udos_mode'],
                         access_level=system_status['access_level'])

@app.route('/api/status')
def status():
    """Enhanced system status endpoint"""
    return jsonify({
        'status': 'running',
        'mode': system_status['udos_mode'],
        'access_level': system_status['access_level'],
        'clients': len(connected_clients),
        'udos_root': str(UDOS_ROOT),
        'startup_complete': startup_complete,
        'checks_passed': system_status['checks_passed'],
        'total_checks': system_status['total_checks'],
        'current_check': system_status['current_check'],
        'uptime': time.time() - system_status['startup_time'],
        'modules': get_available_modules()
    })

@app.route('/api/startup-status')
def startup_status():
    """Startup progress endpoint"""
    return jsonify(system_status)

def get_available_modules():
    """Get list of available uDOS modules"""
    modules = []
    module_dirs = ['uCORE', 'uSERVER', 'uSCRIPT', 'uMEMORY', 'uKNOWLEDGE']
    role_dirs = ['ghost', 'tomb', 'drone', 'imp', 'sorcerer', 'wizard']
    
    for module in module_dirs:
        if (UDOS_ROOT / module).exists():
            modules.append(module)
    
    for role in role_dirs:
        if (UDOS_ROOT / role).exists():
            modules.append(role)
    
    return modules

def run_startup_checks():
    """Run comprehensive startup checks"""
    global startup_complete, system_status
    
    checks = [
        ("Validating uDOS installation", check_udos_installation),
        ("Checking uCORE modules", check_ucore_modules),
        ("Validating role permissions", check_role_permissions),
        ("Loading configuration", load_configuration),
        ("Initializing subsystems", initialize_subsystems),
        ("Startup complete", finalize_startup)
    ]
    
    for i, (check_name, check_func) in enumerate(checks):
        system_status['current_check'] = check_name
        system_status['checks_passed'] = i
        
        # Broadcast progress to all clients
        socketio.emit('startup_progress', system_status)
        log_message(f"🔍 {check_name}...")
        
        try:
            result = check_func()
            if result:
                log_message(f"✅ {check_name} - OK")
            else:
                log_message(f"⚠️  {check_name} - Warning")
        except Exception as e:
            log_message(f"❌ {check_name} - Error: {str(e)}")
        
        time.sleep(0.5)  # Visual delay for user experience
    
    system_status['checks_passed'] = len(checks)
    startup_complete = True
    # Clear the startup progress flag
    if hasattr(app, '_startup_in_progress'):
        delattr(app, '_startup_in_progress')
    log_message("🚀 uDOS startup sequence complete")
    socketio.emit('startup_complete', system_status)

def check_udos_installation():
    """Check if uDOS is properly installed"""
    required_paths = [
        UDOS_ROOT / "uCORE",
        UDOS_ROOT / "uSERVER", 
        UDOS_ROOT / "uMEMORY",
        UI_PATH / "index.html"
    ]
    
    for path in required_paths:
        if not path.exists():
            log_message(f"❌ Missing: {path}")
            return False
    
    return True

def check_ucore_modules():
    """Check uCORE module availability"""
    core_modules = [
        "core", "code", "config", "launcher", "templates"
    ]
    
    for module in core_modules:
        module_path = UDOS_ROOT / "uCORE" / module
        if not module_path.exists():
            log_message(f"⚠️  uCORE module missing: {module}")
    
    return True

def check_role_permissions():
    """Check role-based permissions"""
    current_role = system_status['udos_mode']
    role_path = UDOS_ROOT / current_role
    
    if not role_path.exists():
        log_message(f"⚠️  Role directory missing: {current_role}")
        return False
    
    # Check permissions file if it exists
    permissions_file = role_path / "permissions.json"
    if permissions_file.exists():
        try:
            with open(permissions_file, 'r') as f:
                permissions = json.load(f)
                log_message(f"📋 Role permissions loaded for {current_role}")
        except Exception as e:
            log_message(f"⚠️  Failed to load permissions: {e}")
    
    return True

def load_configuration():
    """Load uDOS configuration"""
    config_paths = [
        UI_PATH / "config" / "startup.json",
        UDOS_ROOT / "uCORE" / "config" / "system.json"
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    log_message(f"📄 Loaded config: {config_path.name}")
            except Exception as e:
                log_message(f"⚠️  Config error in {config_path.name}: {e}")
    
    return True

def initialize_subsystems():
    """Initialize uDOS subsystems"""
    # Check for setup script
    setup_script = UDOS_ROOT / "uSERVER" / "setup-check.py"
    if setup_script.exists():
        try:
            result = subprocess.run([sys.executable, str(setup_script)], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                log_message("🔧 System setup validation passed")
            else:
                log_message(f"⚠️  Setup validation warnings: {result.stderr}")
        except Exception as e:
            log_message(f"⚠️  Setup check failed: {e}")
    
    return True

def finalize_startup():
    """Finalize startup process"""
    log_message(f"🎭 Role: {system_status['udos_mode']} (Level {system_status['access_level']})")
    log_message(f"📁 Root: {UDOS_ROOT}")
    log_message(f"🌐 UI: {UI_PATH}")
    return True

@app.route('/api/logs')
def get_logs():
    """Get system logs"""
    return jsonify(system_logs[-100:])  # Last 100 logs

@socketio.on('connect')
def handle_connect():
    """Handle client connection with startup state"""
    client_id = request.sid
    connected_clients.append(client_id)
    
    # Send current system state to new client
    emit('status', {
        'message': f'Connected to uDOS {system_status["udos_mode"]} (Level {system_status["access_level"]})',
        'startup_complete': startup_complete,
        'system_status': system_status
    })
    
    # Send startup progress if still in progress
    if not startup_complete:
        emit('startup_progress', system_status)
    else:
        emit('startup_complete', system_status)
    
    log_message(f'🔗 Client connected: {client_id}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        connected_clients.remove(client_id)
    log_message(f'🔌 Client disconnected: {client_id}')

@socketio.on('request_startup_status')
def handle_startup_status_request():
    """Send current startup status to client"""
    if startup_complete:
        emit('startup_complete', system_status)
    else:
        emit('startup_progress', system_status)

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
    """Main entry point - integrated with uDOS launcher"""
    host = os.environ.get('UDOS_SERVER_HOST', '127.0.0.1')
    port = int(os.environ.get('UDOS_SERVER_PORT', '8080'))
    debug_mode = os.environ.get('UDOS_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 uDOS Server v1.3.1 - {system_status['udos_mode'].title()} Mode")
    print(f"📁 uDOS Root: {UDOS_ROOT}")
    print(f"� Role: {system_status['udos_mode']} (Level {system_status['access_level']})")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🖥️  UI Integration: {UI_PATH}")
    
    # Don't auto-open browser - let launcher handle it
    log_message("🔧 uSERVER starting...")
    log_message(f"🎭 Role: {system_status['udos_mode']}")
    log_message(f"🔐 Access Level: {system_status['access_level']}")
    
    try:
        # Start the server
        socketio.run(app, host=host, port=port, debug=debug_mode, use_reloader=False)
    except KeyboardInterrupt:
        log_message("🛑 Server stopped by user")
    except Exception as e:
        log_message(f"❌ Server error: {e}")
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
