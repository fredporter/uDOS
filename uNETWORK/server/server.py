#!/usr/bin/env python3
"""
uDOS Server v1.3.3 - Enhanced with uSCRIPT venv Integration and uCORE Protocol Compatibility
Serves the browser-based UI with comprehensive error management, role-based permissions,
and full integration with uCORE logging, error handling, and backup protocols
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import traceback
import logging
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit

# Add uCORE to path for imports
UDOS_ROOT = Path(__file__).parent.parent
UI_PATH = UDOS_ROOT / "uCORE" / "launcher" / "universal" / "ucode-ui"
ERROR_LOG_PATH = UDOS_ROOT / "wizard" / "logs" / "errors"
DEBUG_LOG_PATH = UDOS_ROOT / "wizard" / "logs" / "debug"
CRASH_LOG_PATH = UDOS_ROOT / "wizard" / "logs" / "crashes"

sys.path.append(str(UDOS_ROOT / "uCORE" / "core"))

# Import uCORE integration
try:
    sys.path.append(str(Path(__file__).parent / "integration"))
    from ucore_protocols import create_ucore_integration
    UCORE_INTEGRATION_AVAILABLE = True
except ImportError:
    UCORE_INTEGRATION_AVAILABLE = False
    print("Warning: uCORE integration not available")

# Ensure log directories exist
ERROR_LOG_PATH.mkdir(parents=True, exist_ok=True)
DEBUG_LOG_PATH.mkdir(parents=True, exist_ok=True)
CRASH_LOG_PATH.mkdir(parents=True, exist_ok=True)

# Initialize uCORE integration
ucore_protocols = None
if UCORE_INTEGRATION_AVAILABLE:
    try:
        ucore_protocols = create_ucore_integration(str(UDOS_ROOT))
        print(f"✅ uCORE integration initialized for role: {ucore_protocols.current_role}")
    except Exception as e:
        print(f"Warning: uCORE integration failed: {e}")
        UCORE_INTEGRATION_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DEBUG_LOG_PATH / f"server-{time.strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('uDOS-Server')

# Error handling configuration
ERROR_COUNT = 0
MAX_ERRORS = 10
RESTART_COUNT = 0
MAX_RESTARTS = 3

app = Flask(__name__,
           static_folder=str(UI_PATH / "static"),
           template_folder=str(UI_PATH))

app.config['SECRET_KEY'] = 'udos-secure-key-v131'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
connected_clients = []
system_logs = []
startup_complete = False
error_logs = []
system_status = {
    'server_running': True,
    'startup_time': time.time(),
    'checks_passed': 0,
    'total_checks': 6,
    'current_check': 'Starting...',
    'udos_mode': os.environ.get('UDOS_CURRENT_ROLE', 'wizard'),
    'access_level': os.environ.get('UDOS_ACCESS_LEVEL', '100'),
    'error_count': 0,
    'restart_count': 0,
    'health_status': 'healthy'
}

def generate_error_id():
    """Generate unique error ID"""
    import random
    return f"E{time.strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999):04x}"

def get_role_error_message(error_type, role=None):
    """Get role-specific error messages"""
    if role is None:
        role = system_status.get('udos_mode', 'wizard')

    messages = {
        'ghost': {
            'server_error': "👻 The spectral server encountered turbulence...",
            'restart': "👻 Restarting ethereal processes...",
            'crash': "👻 The phantom server has vanished into the void...",
            'loop': "👻 Caught in a ghostly recursion..."
        },
        'tomb': {
            'server_error': "⚰️ Ancient server systems have crumbled...",
            'restart': "⚰️ Excavating server from the digital ruins...",
            'crash': "⚰️ The server has been entombed...",
            'loop': "⚰️ Trapped in an eternal digital cycle..."
        },
        'crypt': {
            'server_error': "🪦 Crypt systems sealed. Attempting resurrection...",
            'restart': "🪦 Crypt server awakening...",
            'crash': "🪦 The crypt server is dormant...",
            'loop': "🪦 Crypt recursion detected. Breaking the seal..."
        },
        'drone': {
            'server_error': "🤖 Drone systems experiencing malfunction...",
            'restart': "🤖 Initiating automated recovery protocols...",
            'crash': "🤖 Primary systems offline, switching to backup...",
            'loop': "🤖 Infinite loop detected in automation sequence..."
        },
        'imp': {
            'server_error': "👹 Mischievous code has caused server chaos!",
            'restart': "👹 The imp is fixing its pranks...",
            'crash': "👹 The server fell victim to imp trickery...",
            'loop': "👹 Caught in the imp's endless joke loop..."
        },
        'knight': {
            'server_error': "🛡️ The Knight stands guard. System breach repelled...",
            'restart': "🛡️ Knightly restart in progress...",
            'crash': "🛡️ The Knight has fallen, recovery underway...",
            'loop': "🛡️ Knight detected a recursive battle. Breaking the siege..."
        },
        'sorcerer': {
            'server_error': "🔮 The magical server spell has backfired...",
            'restart': "🔮 Recasting server enchantments...",
            'crash': "🔮 The server's magic has been dispelled...",
            'loop': "🔮 Trapped in a recursive magical incantation..."
        },
        'wizard': {
            'server_error': "🧙‍♂️ Advanced server diagnostics required...",
            'restart': "🧙‍♂️ Applying master-level recovery techniques...",
            'crash': "🧙‍♂️ Critical system failure detected...",
            'loop': "🧙‍♂️ Infinite recursion detected, breaking spell..."
        }
    }

    default_messages = {
        'server_error': "⚠️ Server error detected...",
        'restart': "🔄 Restarting server...",
        'crash': "💥 Server has crashed...",
        'loop': "🔄 Loop detected..."
    }

    return messages.get(role, default_messages).get(error_type, default_messages['server_error'])

def log_error(error_type, message, exception=None):
    """Enhanced error logging with uCORE protocol integration"""
    global ERROR_COUNT
    ERROR_COUNT += 1
    system_status['error_count'] = ERROR_COUNT

    error_id = generate_error_id()

    # Use uCORE integration if available
    if ucore_protocols:
        try:
            error_id = ucore_protocols.log_error(error_type, message, exception)
            return error_id
        except Exception as e:
            print(f"uCORE error logging failed, using fallback: {e}")

    # Fallback error logging
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    role = system_status.get('udos_mode', 'wizard')

    # Create error entry
    error_entry = {
        'id': error_id,
        'timestamp': timestamp,
        'type': error_type,
        'message': message,
        'role': role,
        'exception': str(exception) if exception else None,
        'stack_trace': traceback.format_exc() if exception else None
    }

    error_logs.append(error_entry)

    # Log to file
    error_log_file = ERROR_LOG_PATH / f"error-{time.strftime('%Y%m%d')}.log"
    with open(error_log_file, 'a') as f:
        f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write(f"ERROR: {error_id}\n")
        f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Type: {error_type}\n")
        f.write(f"Source: uNETWORK\n")
        f.write(f"Role: {role}\n")
        f.write(f"Message: {message}\n")
        if exception:
            f.write(f"Exception: {exception}\n")
            f.write(f"Stack Trace:\n{traceback.format_exc()}\n")
        f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

    # Broadcast to clients
    role_message = get_role_error_message(error_type, role)
    socketio.emit('error_notification', {
        'id': error_id,
        'message': role_message,
        'details': message,
        'timestamp': timestamp,
        'role': role
    })

    logger.error(f"[{error_id}] {error_type}: {message}")

    # Check error threshold
    if ERROR_COUNT >= MAX_ERRORS:
        system_status['health_status'] = 'critical'
        emergency_shutdown(f"Error threshold exceeded: {ERROR_COUNT}/{MAX_ERRORS}")

    return error_id

def detect_restart_loop():
    """Detect if server is restarting too frequently"""
    global RESTART_COUNT
    RESTART_COUNT += 1
    system_status['restart_count'] = RESTART_COUNT

    if RESTART_COUNT >= MAX_RESTARTS:
        error_id = log_error('RESTART_LOOP', f'Server restart loop detected: {RESTART_COUNT} restarts')
        emergency_shutdown(f"Restart loop detected: {RESTART_COUNT}/{MAX_RESTARTS}")
        return True

    return False

def emergency_shutdown(reason):
    """Emergency shutdown with comprehensive logging"""
    try:
        error_id = generate_error_id()
        role_message = get_role_error_message('crash')

        # Create emergency log
        emergency_log = CRASH_LOG_PATH / f"emergency-{time.strftime('%Y%m%d%H%M%S')}.log"
        with open(emergency_log, 'w') as f:
            f.write(f"EMERGENCY SHUTDOWN: {error_id}\n")
            f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Role: {system_status.get('udos_mode', 'unknown')}\n")
            f.write(f"Error Count: {ERROR_COUNT}\n")
            f.write(f"Restart Count: {RESTART_COUNT}\n")
            f.write(f"Uptime: {time.time() - system_status['startup_time']:.1f}s\n")
            f.write(f"Connected Clients: {len(connected_clients)}\n")
            f.write(f"System Status: {json.dumps(system_status, indent=2)}\n")
            f.write(f"Recent Errors:\n")
            for error in error_logs[-5:]:
                f.write(f"  - {error['timestamp']} [{error['type']}] {error['message']}\n")
            f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # Notify clients
        socketio.emit('emergency_shutdown', {
            'message': role_message,
            'reason': reason,
            'error_id': error_id
        })

        logger.critical(f"Emergency shutdown: {reason}")

        # Clean shutdown
        time.sleep(2)  # Give clients time to receive notification
        os._exit(1)

    except Exception as e:
        # Last resort
        logger.critical(f"Emergency shutdown failed: {e}")
        os._exit(1)

@app.route('/')
def index():
    """Main uCODE interface with enhanced error handling"""
    try:
        global startup_complete
        if not startup_complete:
            # Check if startup is already in progress
            if not hasattr(app, '_startup_in_progress'):
                app._startup_in_progress = True
                threading.Thread(target=run_startup_checks, daemon=True).start()

        return render_template('index.html',
                             udos_mode=system_status['udos_mode'],
                             access_level=system_status['access_level'])
    except Exception as e:
        error_id = log_error('ROUTE_ERROR', f'Failed to load main interface: {str(e)}', e)
        role_message = get_role_error_message('server_error')
        return f"""
        <html><body>
        <h1>{role_message}</h1>
        <p>Error ID: {error_id}</p>
        <p>Details: {str(e)}</p>
        <p><a href="javascript:location.reload()">Retry</a></p>
        </body></html>
        """, 500

@app.route('/api/status')
def status():
    """Enhanced system status endpoint with error reporting and role permissions"""
    try:
        # Check permissions if uCORE integration is available
        if ucore_protocols and not ucore_protocols.check_permission('network_status'):
            return jsonify({
                'status': 'forbidden',
                'message': f'Role {ucore_protocols.current_role} cannot access status endpoint'
            }), 403

        status_data = {
            'status': 'running' if system_status['health_status'] != 'critical' else 'degraded',
            'health': system_status['health_status'],
            'mode': system_status['udos_mode'],
            'access_level': system_status['access_level'],
            'clients': len(connected_clients),
            'udos_root': str(UDOS_ROOT),
            'startup_complete': startup_complete,
            'checks_passed': system_status['checks_passed'],
            'total_checks': system_status['total_checks'],
            'current_check': system_status['current_check'],
            'uptime': time.time() - system_status['startup_time'],
            'modules': get_available_modules(),
            'error_count': system_status['error_count'],
            'restart_count': system_status['restart_count'],
            'recent_errors': error_logs[-5:] if error_logs else []
        }

        # Add uCORE integration status if available
        if ucore_protocols:
            status_data['ucore_integration'] = ucore_protocols.get_system_status()

        return jsonify(status_data)
    except Exception as e:
        error_id = log_error('API_ERROR', f'Status API error: {str(e)}', e)
        return jsonify({
            'status': 'error',
            'error_id': error_id,
            'message': get_role_error_message('server_error')
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        health_data = {
            'status': system_status['health_status'],
            'timestamp': time.time(),
            'uptime': time.time() - system_status['startup_time'],
            'error_count': system_status['error_count'],
            'restart_count': system_status['restart_count'],
            'memory_usage': get_memory_usage(),
            'active_connections': len(connected_clients)
        }

        # Determine overall health
        if system_status['error_count'] > 5:
            health_data['status'] = 'degraded'
        if system_status['error_count'] > 10:
            health_data['status'] = 'critical'

        return jsonify(health_data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_memory_usage():
    """Get current memory usage"""
    try:
        import psutil
        process = psutil.Process()
        return {
            'rss': process.memory_info().rss,
            'vms': process.memory_info().vms,
            'percent': process.memory_percent()
        }
    except:
        return {'error': 'Memory info unavailable'}

@app.route('/api/startup-status')
def startup_status():
    """Startup progress endpoint"""
    return jsonify(system_status)

def get_available_modules():
    """Get list of available uDOS modules"""
    modules = []
    module_dirs = ['uCORE', 'uSERVER', 'uSCRIPT', 'uMEMORY', 'uKNOWLEDGE']
    role_dirs = ['ghost', 'tomb', 'crypt', 'drone', 'imp', 'knight', 'sorcerer', 'wizard']
#
# uDOS Ethos: Clean, flat, minimal data. Respect host system. Backup and cleanup always.
#

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
    """Handle client connection with enhanced error handling"""
    try:
        client_id = request.sid
        connected_clients.append(client_id)

        # Send current system state to new client
        emit('status', {
            'message': f'Connected to uDOS {system_status["udos_mode"]} (Level {system_status["access_level"]})',
            'startup_complete': startup_complete,
            'system_status': system_status,
            'health_status': system_status['health_status']
        })

        # Send startup progress if still in progress
        if not startup_complete:
            emit('startup_progress', system_status)
        else:
            emit('startup_complete', system_status)

        # Send recent errors if any
        if error_logs:
            emit('error_history', error_logs[-10:])

        log_message(f'🔗 Client connected: {client_id}')

    except Exception as e:
        error_id = log_error('WEBSOCKET_ERROR', f'Client connection error: {str(e)}', e)
        emit('error', {'message': get_role_error_message('server_error'), 'error_id': error_id})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection with cleanup"""
    try:
        client_id = request.sid
        if client_id in connected_clients:
            connected_clients.remove(client_id)
        log_message(f'🔌 Client disconnected: {client_id}')
    except Exception as e:
        log_error('WEBSOCKET_ERROR', f'Client disconnect error: {str(e)}', e)

@socketio.on('request_startup_status')
def handle_startup_status_request():
    """Send current startup status to client with error handling"""
    try:
        if startup_complete:
            emit('startup_complete', system_status)
        else:
            emit('startup_progress', system_status)
    except Exception as e:
        error_id = log_error('WEBSOCKET_ERROR', f'Startup status request error: {str(e)}', e)
        emit('error', {'message': get_role_error_message('server_error'), 'error_id': error_id})

@socketio.on('execute_command')
def handle_command(data):
    """Execute uDOS command with comprehensive error handling"""
    try:
        command = data.get('command', '')
        log_message(f'Command received: {command}')

        # Process command
        result = process_udos_command(command)

        emit('command_result', {
            'command': command,
            'result': result,
            'timestamp': time.time()
        })

    except Exception as e:
        error_id = log_error('COMMAND_ERROR', f'Command execution error: {str(e)}', e)
        emit('command_result', {
            'command': data.get('command', 'unknown'),
            'result': {
                'output': get_role_error_message('server_error'),
                'success': False,
                'error_id': error_id
            },
            'timestamp': time.time()
        })

@socketio.on('server_restart')
def handle_server_restart():
    """Handle server restart requests with loop detection"""
    try:
        if detect_restart_loop():
            return  # Emergency shutdown will be triggered

        log_message('🔄 Server restart requested')
        role_message = get_role_error_message('restart')

        # Send restart notification to all clients
        socketio.emit('server_restarting', {
            'message': role_message,
            'timestamp': time.time()
        })

        # Schedule restart after brief delay
        threading.Timer(2.0, restart_server).start()

    except Exception as e:
        error_id = log_error('RESTART_ERROR', f'Server restart error: {str(e)}', e)
        emit('error', {'message': get_role_error_message('server_error'), 'error_id': error_id})

def restart_server():
    """Restart the server process"""
    try:
        log_message('🔄 Initiating server restart...')

        # Get the current process info
        import psutil
        current_process = psutil.Process()

        # Kill the current process and let the launcher restart it
        os.kill(current_process.pid, signal.SIGTERM)

    except Exception as e:
        log_message(f'❌ Restart failed: {e}')

@socketio.on('server_stop')
def handle_server_stop():
    """Handle server stop requests"""
    log_message('🛑 Server stop requested')

    # Send stop notification to all clients
    socketio.emit('server_stopping', {
        'message': 'Server is shutting down...',
        'timestamp': time.time()
    })

    # Schedule shutdown after brief delay
    threading.Timer(1.0, stop_server).start()

def stop_server():
    """Stop the server gracefully"""
    try:
        log_message('🛑 Initiating server shutdown...')
        os._exit(0)
    except Exception as e:
        log_message(f'❌ Shutdown failed: {e}')

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
    """Process uDOS command with enhanced functionality and role permissions"""

    # Check permissions for command execution
    if ucore_protocols and not ucore_protocols.check_permission('network_execute'):
        return {
            'output': f'Permission denied: Role {ucore_protocols.current_role} cannot execute commands',
            'success': False,
            'role': ucore_protocols.current_role
        }

    # Handle uSCRIPT integration commands
    if command.startswith('uscript '):
        uscript_cmd = command[8:].strip()
        if ucore_protocols:
            result = ucore_protocols.execute_uscript('system-info' if uscript_cmd == 'status' else uscript_cmd)
            return {
                'output': result.get('output', result.get('error', 'Unknown error')),
                'success': result.get('success', False),
                'uscript_result': result
            }
        else:
            return {
                'output': '❌ uSCRIPT integration not available',
                'success': False
            }

    # Placeholder implementation for other commands
    if command.startswith('help'):
        return {
            'output': '''uDOS Commands v1.3.3 (with uCORE Integration):
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
- server restart: Restart the server
- server stop: Stop the server
- uscript <command>: Execute uSCRIPT commands
- role info: Show current role information
- permissions: Show current permissions
- backup create: Create system backup (if permitted)
- clear: Clear terminal output''',
            'success': True
        }
    elif command.startswith('role info'):
        if ucore_protocols:
            return {
                'output': f'''Current Role Information:
Role: {ucore_protocols.current_role}
Level: {ucore_protocols.role_permissions.get(ucore_protocols.current_role, {}).get("level", "Unknown")}
Network Access: {"✅" if ucore_protocols.check_permission("network") else "❌"}
uScript Access: {"✅" if ucore_protocols.check_permission("uscript_execute") else "❌"}
Admin Access: {"✅" if ucore_protocols.check_permission("admin") else "❌"}
Backup Access: {"✅" if ucore_protocols.check_permission("backup_create") else "❌"}''',
                'success': True
            }
        else:
            return {
                'output': f'Role: {system_status["udos_mode"]} (uCORE integration unavailable)',
                'success': True
            }
    elif command.startswith('permissions'):
        if ucore_protocols:
            perms = []
            test_permissions = ['network', 'uscript_execute', 'admin', 'backup_create', 'umemory_read', 'sandbox']
            for perm in test_permissions:
                status = "✅" if ucore_protocols.check_permission(perm) else "❌"
                perms.append(f"{status} {perm}")
            return {
                'output': f'Permissions for role {ucore_protocols.current_role}:\n' + '\n'.join(perms),
                'success': True
            }
        else:
            return {
                'output': 'Permission checking requires uCORE integration',
                'success': False
            }
    elif command.startswith('backup create'):
        if ucore_protocols:
            if ucore_protocols.check_permission('backup_create'):
                # Trigger backup through uCORE protocols
                try:
                    backup_file = ucore_protocols.create_error_backup('MANUAL', 'User-requested backup')
                    return {
                        'output': f'✅ Backup created successfully',
                        'success': True
                    }
                except Exception as e:
                    return {
                        'output': f'❌ Backup failed: {str(e)}',
                        'success': False
                    }
            else:
                return {
                    'output': f'❌ Permission denied: Role {ucore_protocols.current_role} cannot create backups',
                    'success': False
                }
        else:
            return {
                'output': '❌ Backup requires uCORE integration',
                'success': False
            }
    elif command.startswith('status'):
        status_info = f'''uDOS System Status v1.3.3:
Mode: {system_status["udos_mode"]}
Clients: {len(connected_clients)}
Modules: uCORE, uNETWORK, uSCRIPT, uMEMORY
Uptime: {time.time() - system_status["startup_time"]:.1f}s
Memory: Available
Version: 1.3.3'''

        if ucore_protocols:
            integration_status = ucore_protocols.get_system_status()
            status_info += f'''
uCORE Integration: ✅ Active
Role: {ucore_protocols.current_role}
Permissions: ✅ Loaded
uSCRIPT: {"✅" if integration_status.get("uscript_integration", {}).get("available") else "❌"}
Sandbox: {"✅" if integration_status.get("sandbox_integration", {}).get("available") else "❌"}'''
        else:
            status_info += '\nuCORE Integration: ❌ Not available'

        return {
            'output': status_info,
            'success': True
        }
    elif command.startswith('server restart'):
        # Emit server restart event
        socketio.emit('server_restarting', {
            'message': 'Server restart initiated...',
            'timestamp': time.time()
        })
        threading.Timer(2.0, restart_server).start()
        return {
            'output': '🔄 Server restart initiated. Please wait...',
            'success': True
        }
    elif command.startswith('server stop'):
        # Emit server stop event
        socketio.emit('server_stopping', {
            'message': 'Server shutdown initiated...',
            'timestamp': time.time()
        })
        threading.Timer(1.0, stop_server).start()
        return {
            'output': '🛑 Server shutdown initiated...',
            'success': True
        }
    elif command.startswith('modules'):
        modules = ['uCORE', 'uSERVER', 'uSCRIPT', 'uMEMORY', 'imp', 'ghost', 'sorcerer', 'tomb', 'wizard', 'drone']
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
