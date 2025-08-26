#!/usr/bin/env python3
"""
uDOS Server v1.0.4.2 - Enhanced with uSCRIPT venv Integration and uCORE Protocol Compatibility
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
UDOS_ROOT = Path(__file__).parent.parent.parent
UI_PATH = UDOS_ROOT / "uNETWORK" / "display"
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

# Import task manager API
try:
    from task_manager_api import task_api
    TASK_MANAGER_AVAILABLE = True
except ImportError:
    TASK_MANAGER_AVAILABLE = False
    print("Warning: Task Manager API not available")

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
           template_folder=str(UI_PATH / "templates"))
app.config['SECRET_KEY'] = 'udos-secure-key-v131'
socketio = SocketIO(app, cors_allowed_origins="*")

# Register Task Manager API blueprint
if TASK_MANAGER_AVAILABLE:
    app.register_blueprint(task_api)
    print("✅ Task Manager API registered")

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
    """Main uDOS interface - comprehensive browser UI"""
    try:
        global startup_complete
        if not startup_complete:
            # Check if startup is already in progress
            if not hasattr(app, '_startup_in_progress'):
                app._startup_in_progress = True
                threading.Thread(target=run_startup_checks, daemon=True).start()

        return render_template('udos-app.html',
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

@app.route('/dashboard')
def dashboard():
    """Legacy dashboard interface for compatibility"""
    try:
        return render_template('dashboard.html',
                             udos_mode=system_status['udos_mode'],
                             access_level=system_status['access_level'])
    except Exception as e:
        error_id = log_error('ROUTE_ERROR', f'Failed to load dashboard interface: {str(e)}', e)
        role_message = get_role_error_message('server_error')
        return f"""
        <html><body>
        <h1>{role_message}</h1>
        <p>Error ID: {error_id}</p>
        <p>Details: {str(e)}</p>
        <p><a href="javascript:location.reload()">Retry</a></p>
        </body></html>
        """, 500

@app.route('/terminal')
def terminal():
    """Terminal interface"""
    try:
        return render_template('terminal.html',
                             udos_mode=system_status['udos_mode'],
                             access_level=system_status['access_level'])
    except Exception as e:
        error_id = log_error('ROUTE_ERROR', f'Failed to load terminal interface: {str(e)}', e)
        return f"Terminal interface error: {error_id}", 500

@app.route('/memory')
def memory():
    """Memory browser interface"""
    try:
        return render_template('memory.html',
                             udos_mode=system_status['udos_mode'],
                             access_level=system_status['access_level'])
    except Exception as e:
        error_id = log_error('ROUTE_ERROR', f'Failed to load memory interface: {str(e)}', e)
        return f"Memory interface error: {error_id}", 500

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
        UDOS_ROOT / "uNETWORK",
        UDOS_ROOT / "uMEMORY",
        UI_PATH / "templates" / "dashboard.html"
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

# Documentation Browser Routes
@app.route('/docs')
def docs_browser():
    """uDOS Documentation Browser"""
    try:
        docs_ui_path = UDOS_ROOT / "uNETWORK" / "display" / "static" / "docs"
        return send_from_directory(docs_ui_path, 'index.html')
    except Exception as e:
        error_id = log_error('ROUTE_ERROR', f'Failed to load documentation browser: {str(e)}', e)
        return f"Documentation browser error: {error_id}", 500

@app.route('/docs/static/<path:filename>')
def docs_static(filename):
    """Serve static files for documentation browser"""
    try:
        docs_ui_path = UDOS_ROOT / "uNETWORK" / "display" / "static" / "docs"
        return send_from_directory(docs_ui_path, filename)
    except Exception as e:
        error_id = log_error('ROUTE_ERROR', f'Failed to serve static file: {filename}', e)
        return f"Static file error: {error_id}", 404

@app.route('/api/docs/tree')
def get_docs_tree():
    """Get documentation file tree"""
    try:
        import glob
        from pathlib import Path

        def build_tree(root_path, base_path=""):
            """Recursively build file tree"""
            tree = []
            root = Path(root_path)

            if not root.exists():
                return tree

            # Get directories first
            for item in sorted(root.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    relative_path = str(item.relative_to(UDOS_ROOT))
                    children = build_tree(item, base_path)
                    if children:  # Only include directories with markdown files
                        tree.append({
                            'name': item.name,
                            'type': 'folder',
                            'path': relative_path,
                            'children': children
                        })

            # Get markdown files
            for item in sorted(root.iterdir()):
                if item.is_file() and item.suffix.lower() == '.md':
                    relative_path = str(item.relative_to(UDOS_ROOT))
                    tree.append({
                        'name': item.name,
                        'type': 'file',
                        'path': relative_path,
                        'size': item.stat().st_size,
                        'modified': item.stat().st_mtime
                    })

            return tree

        # Build tree for main documentation directories
        docs_tree = []

        # Main docs directory
        docs_path = UDOS_ROOT / "docs"
        if docs_path.exists():
            docs_tree.append({
                'name': 'docs',
                'type': 'folder',
                'path': 'docs',
                'children': build_tree(docs_path)
            })

        # Development docs
        dev_docs_path = UDOS_ROOT / "dev" / "docs"
        if dev_docs_path.exists():
            docs_tree.append({
                'name': 'dev/docs',
                'type': 'folder',
                'path': 'dev/docs',
                'children': build_tree(dev_docs_path)
            })

        # README files in major directories
        for dir_name in ['uCORE', 'uMEMORY', 'uNETWORK', 'uSCRIPT', 'sandbox', 'extensions']:
            dir_path = UDOS_ROOT / dir_name
            if dir_path.exists():
                readme_files = []
                for readme in ['README.md', 'readme.md', 'Readme.md']:
                    readme_path = dir_path / readme
                    if readme_path.exists():
                        readme_files.append({
                            'name': readme,
                            'type': 'file',
                            'path': str(readme_path.relative_to(UDOS_ROOT)),
                            'size': readme_path.stat().st_size,
                            'modified': readme_path.stat().st_mtime
                        })

                if readme_files:
                    docs_tree.append({
                        'name': dir_name,
                        'type': 'folder',
                        'path': dir_name,
                        'children': readme_files
                    })

        return jsonify(docs_tree)

    except Exception as e:
        error_id = log_error('API_ERROR', f'Failed to get docs tree: {str(e)}', e)
        return jsonify({
            'error': 'Failed to load documentation tree',
            'error_id': error_id
        }), 500

@app.route('/api/docs/content')
def get_doc_content():
    """Get content of a specific document"""
    try:
        doc_path = request.args.get('path')
        if not doc_path:
            return jsonify({'error': 'Document path required'}), 400

        # Security: ensure path is within UDOS_ROOT
        full_path = UDOS_ROOT / doc_path
        try:
            full_path = full_path.resolve()
            UDOS_ROOT.resolve()
            if not str(full_path).startswith(str(UDOS_ROOT.resolve())):
                return jsonify({'error': 'Invalid document path'}), 403
        except:
            return jsonify({'error': 'Invalid document path'}), 403

        if not full_path.exists():
            return jsonify({'error': 'Document not found'}), 404

        if not full_path.suffix.lower() == '.md':
            return jsonify({'error': 'Not a markdown document'}), 400

        # Read and return content
        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Get file metadata
        stat = full_path.stat()

        return jsonify({
            'content': content,
            'path': doc_path,
            'name': full_path.name,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'encoding': 'utf-8'
        })

    except Exception as e:
        error_id = log_error('API_ERROR', f'Failed to get document content: {str(e)}', e)
        return jsonify({
            'error': 'Failed to load document',
            'error_id': error_id
        }), 500

@app.route('/api/docs/search')
def search_docs():
    """Search through documentation content"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify({'results': []})

        import re
        from pathlib import Path

        results = []
        query_lower = query.lower()

        # Search through all markdown files
        for md_file in UDOS_ROOT.rglob('*.md'):
            try:
                # Skip hidden directories and files
                if any(part.startswith('.') for part in md_file.parts):
                    continue

                relative_path = str(md_file.relative_to(UDOS_ROOT))

                # Check if filename matches
                if query_lower in md_file.name.lower():
                    results.append({
                        'path': relative_path,
                        'name': md_file.name,
                        'type': 'filename',
                        'match': md_file.name,
                        'score': 100
                    })
                    continue

                # Search file content
                try:
                    with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if query_lower in content.lower():
                        # Find context around matches
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if query_lower in line.lower():
                                # Get context (line before and after)
                                start = max(0, i - 1)
                                end = min(len(lines), i + 2)
                                context = '\n'.join(lines[start:end])

                                results.append({
                                    'path': relative_path,
                                    'name': md_file.name,
                                    'type': 'content',
                                    'match': line.strip(),
                                    'context': context,
                                    'line': i + 1,
                                    'score': 50
                                })
                                break  # Only first match per file

                except Exception:
                    continue  # Skip files that can't be read

            except Exception:
                continue  # Skip files with path issues

        # Sort by score (filename matches first)
        results.sort(key=lambda x: x['score'], reverse=True)

        # Limit results
        results = results[:20]

        return jsonify({'results': results, 'query': query})

    except Exception as e:
        error_id = log_error('API_ERROR', f'Failed to search docs: {str(e)}', e)
        return jsonify({
            'error': 'Search failed',
            'error_id': error_id
        }), 500

def update_server_status():
    """Update and display current server status"""
    uptime = time.time() - system_status['startup_time']
    uptime_str = f"{int(uptime//3600):02d}:{int((uptime%3600)//60):02d}:{int(uptime%60):02d}"

    print(f"\033[2K\033[1A\033[2K\033[1A\033[2K\033[1A\033[2K", end="")  # Clear last 3 lines
    print(f"\033[1;32m✅ Server Running\033[0m | \033[1;36m👥 {len(connected_clients)} clients\033[0m | \033[1;33m⏱️  {uptime_str}\033[0m | \033[1;35m❤️  {system_status['health_status']}\033[0m")
    print(f"\033[1;37m🌐 Dashboard: http://localhost:8080 | 💻 Terminal: /terminal | 💾 Memory: /memory\033[0m")
    print(f"\033[1;37m💡 Press Ctrl+C to stop the server\033[0m")

@socketio.on('connect')
def handle_connect():
    """Handle client connection with enhanced error handling"""
    try:
        client_id = request.sid
        connected_clients.append(client_id)

        # Update live status display
        update_server_status()

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

        # Update live status display
        update_server_status()

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

# New WebSocket handlers for enhanced UI

@socketio.on('terminal_command')
def handle_terminal_command(data):
    """Handle terminal command execution"""
    try:
        command = data.get('command', '').strip()
        session_id = data.get('session_id', 'default')

        log_message(f'Terminal command: {command}')

        # Process command through existing system
        result = process_udos_command(command)

        # Emit response back to specific session
        emit('terminal_response', {
            'session_id': session_id,
            'command': command,
            'output': result.get('output', ''),
            'success': result.get('success', True),
            'timestamp': time.time()
        })

    except Exception as e:
        emit('terminal_response', {
            'session_id': data.get('session_id', 'default'),
            'command': data.get('command', ''),
            'output': f'Error: {str(e)}',
            'success': False,
            'timestamp': time.time()
        })

@socketio.on('grid_request')
def handle_grid_request(data):
    """Handle grid data requests"""
    try:
        grid_type = data.get('type', 'simple')
        size = data.get('size', 16)

        # Use the same logic as the REST API
        if grid_type == 'memory':
            grid_data = []
            for i in range(size):
                row = []
                for j in range(size):
                    cell_value = (i * size + j) % 256
                    row.append({
                        'id': f'{i}-{j}',
                        'value': cell_value,
                        'type': 'memory',
                        'address': f'0x{(i * size + j):04X}'
                    })
                grid_data.append(row)
        elif grid_type == 'map':
            grid_data = []
            for i in range(size):
                row = []
                for j in range(size):
                    tile_id = f'tile_{i}_{j}'
                    row.append({
                        'id': tile_id,
                        'value': f'{i},{j}',
                        'type': 'map',
                        'coordinates': {'lat': 40.7128 + (i * 0.01), 'lng': -74.0060 + (j * 0.01)}
                    })
                grid_data.append(row)
        else:
            grid_data = []
            for i in range(size):
                row = []
                for j in range(size):
                    pattern_value = (i + j) % 4
                    row.append({
                        'id': f'{i}-{j}',
                        'value': pattern_value,
                        'type': 'pattern'
                    })
                grid_data.append(row)

        emit('grid_data', {
            'data': grid_data,
            'type': grid_type,
            'size': size,
            'timestamp': time.time()
        })

    except Exception as e:
        emit('grid_error', {
            'error': str(e),
            'timestamp': time.time()
        })

@socketio.on('system_info_request')
def handle_system_info_request():
    """Handle system information requests"""
    try:
        import platform
        import psutil

        info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine()
            },
            'udos': {
                'root': str(UDOS_ROOT),
                'mode': system_status.get('udos_mode', 'unknown'),
                'level': system_status.get('access_level', 0),
                'clients': len(connected_clients),
                'uptime': time.time() - server_start_time if 'server_start_time' in globals() else 0
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free
            }
        }

        emit('system_info', info)

    except Exception as e:
        emit('system_error', {'error': str(e)})

@socketio.on('theme_change')
def handle_theme_change(data):
    """Handle theme changes"""
    try:
        theme = data.get('theme', 'polaroid')
        log_message(f'Theme changed to: {theme}')

        # Broadcast theme change to all clients
        socketio.emit('theme_update', {
            'theme': theme,
            'timestamp': time.time()
        })

    except Exception as e:
        emit('theme_error', {'error': str(e)})

@socketio.on('memory_browse')
def handle_memory_browse(data):
    """Handle memory browsing requests"""
    try:
        path = data.get('path', '')
        memory_path = UDOS_ROOT / 'uMEMORY'

        if path:
            target_path = memory_path / path
        else:
            target_path = memory_path

        result = {
            'path': path,
            'items': [],
            'timestamp': time.time()
        }

        if target_path.exists() and target_path.is_dir():
            for item in target_path.iterdir():
                item_info = {
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'path': str(item.relative_to(memory_path))
                }

                if item.is_file():
                    try:
                        item_info['size'] = item.stat().st_size
                        item_info['modified'] = item.stat().st_mtime
                    except:
                        item_info['size'] = 0
                        item_info['modified'] = 0

                result['items'].append(item_info)

        emit('memory_data', result)

    except Exception as e:
        emit('memory_error', {'error': str(e), 'path': data.get('path', '')})

@socketio.on('variable_request')
def handle_variable_request():
    """Handle system variable requests"""
    try:
        variables = {}

        # System variables
        variables['UDOS-ROOT'] = str(UDOS_ROOT)
        variables['UDOS-MODE'] = system_status.get('udos_mode', 'unknown')
        variables['ACCESS-LEVEL'] = str(system_status.get('access_level', 0))
        variables['SERVER-STATUS'] = system_status.get('health_status', 'unknown')
        variables['CLIENTS-CONNECTED'] = str(len(connected_clients))
        variables['SERVER-UPTIME'] = str(int(time.time() - server_start_time)) if 'server_start_time' in globals() else '0'

        emit('variable_data', {
            'variables': variables,
            'timestamp': time.time()
        })

    except Exception as e:
        emit('variable_error', {'error': str(e)})

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
            'output': '''uDOS Commands v1.0.4 (with uCORE Integration):
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
        status_info = f'''uDOS System Status v1.0.4:
Mode: {system_status["udos_mode"]}
Clients: {len(connected_clients)}
Modules: uCORE, uNETWORK, uSCRIPT, uMEMORY
Uptime: {time.time() - system_status["startup_time"]:.1f}s
Memory: Available
Version: 1.0.4'''

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

# New API Endpoints for Enhanced UI

@app.route('/api/grid/data', methods=['GET'])
def get_grid_data():
    """Get grid visualization data"""
    try:
        grid_type = request.args.get('type', 'simple')
        size = int(request.args.get('size', 16))

        if grid_type == 'memory':
            # Generate memory visualization grid
            grid_data = []
            for i in range(size):
                row = []
                for j in range(size):
                    cell_value = (i * size + j) % 256
                    row.append({
                        'id': f'{i}-{j}',
                        'value': cell_value,
                        'type': 'memory',
                        'address': f'0x{(i * size + j):04X}'
                    })
                grid_data.append(row)
        elif grid_type == 'map':
            # Generate map tile grid
            grid_data = []
            for i in range(size):
                row = []
                for j in range(size):
                    tile_id = f'tile_{i}_{j}'
                    row.append({
                        'id': tile_id,
                        'value': f'{i},{j}',
                        'type': 'map',
                        'coordinates': {'lat': 40.7128 + (i * 0.01), 'lng': -74.0060 + (j * 0.01)}
                    })
                grid_data.append(row)
        else:
            # Simple pattern grid
            grid_data = []
            for i in range(size):
                row = []
                for j in range(size):
                    pattern_value = (i + j) % 4
                    row.append({
                        'id': f'{i}-{j}',
                        'value': pattern_value,
                        'type': 'pattern'
                    })
                grid_data.append(row)

        return jsonify({
            'success': True,
            'data': grid_data,
            'type': grid_type,
            'size': size
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/structure', methods=['GET'])
def get_memory_structure():
    """Get uMEMORY directory structure"""
    try:
        memory_path = UDOS_ROOT / 'uMEMORY'
        structure = {}

        if memory_path.exists():
            for item in memory_path.iterdir():
                if item.is_dir():
                    structure[item.name] = {
                        'type': 'directory',
                        'path': str(item.relative_to(UDOS_ROOT)),
                        'files': []
                    }
                    # Get files in directory
                    try:
                        for file_item in item.iterdir():
                            if file_item.is_file():
                                structure[item.name]['files'].append({
                                    'name': file_item.name,
                                    'size': file_item.stat().st_size,
                                    'modified': file_item.stat().st_mtime
                                })
                    except PermissionError:
                        structure[item.name]['files'] = ['Permission denied']

        return jsonify({
            'success': True,
            'structure': structure
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/variables', methods=['GET'])
def get_system_variables():
    """Get system variables from uMEMORY"""
    try:
        variables = {}

        # Read common system variables
        variables['UDOS-ROOT'] = str(UDOS_ROOT)
        variables['UDOS-MODE'] = system_status.get('udos_mode', 'unknown')
        variables['ACCESS-LEVEL'] = str(system_status.get('access_level', 0))
        variables['SERVER-STATUS'] = system_status.get('health_status', 'unknown')
        variables['CLIENTS-CONNECTED'] = str(len(connected_clients))

        # Try to read from system data files
        system_data_path = UDOS_ROOT / 'uMEMORY' / 'system'
        if system_data_path.exists():
            # Look for uDATA files
            for data_file in system_data_path.glob('*.json'):
                try:
                    with open(data_file, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for key, value in data.items():
                                variables[f'{data_file.stem.upper()}-{key.upper()}'] = str(value)
                except Exception:
                    continue

        return jsonify({
            'success': True,
            'variables': variables
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics for dashboard"""
    try:
        import platform
        import psutil

        stats = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine()
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free
            },
            'udos': {
                'root': str(UDOS_ROOT),
                'mode': system_status.get('udos_mode', 'unknown'),
                'level': system_status.get('access_level', 0),
                'clients': len(connected_clients),
                'uptime': time.time() - server_start_time if 'server_start_time' in globals() else 0
            }
        }

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates/list', methods=['GET'])
def get_templates():
    """Get available templates"""
    try:
        templates = []

        # Check uMEMORY templates
        memory_templates = UDOS_ROOT / 'uMEMORY' / 'templates'
        if memory_templates.exists():
            for template_file in memory_templates.glob('*.json'):
                templates.append({
                    'name': template_file.stem,
                    'path': str(template_file.relative_to(UDOS_ROOT)),
                    'type': 'memory',
                    'size': template_file.stat().st_size
                })

        # Check sandbox templates
        sandbox_templates = UDOS_ROOT / 'sandbox' / 'templates'
        if sandbox_templates.exists():
            for template_file in sandbox_templates.glob('*.json'):
                templates.append({
                    'name': template_file.stem,
                    'path': str(template_file.relative_to(UDOS_ROOT)),
                    'type': 'sandbox',
                    'size': template_file.stat().st_size
                })

        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/command/execute', methods=['POST'])
def execute_command():
    """Execute uCODE commands"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()

        if not command:
            return jsonify({'success': False, 'error': 'No command provided'}), 400

        # Basic command processing
        result = {
            'success': True,
            'command': command,
            'output': '',
            'timestamp': time.time()
        }

        # Simple command routing
        if command.upper().startswith('[STATUS]'):
            result['output'] = f"uDOS Status: {system_status['udos_mode']} mode, Level {system_status['access_level']}"
        elif command.upper().startswith('[HELP]'):
            result['output'] = "uDOS Help: Available commands include [STATUS], [GRID], [MEMORY], [CLEAR]"
        elif command.upper().startswith('[GRID]'):
            result['output'] = "Grid system activated. Use grid interface for visualization."
        elif command.upper().startswith('[MEMORY]'):
            result['output'] = "Memory browser activated. Check memory tab for details."
        elif command.upper().startswith('[CLEAR]'):
            result['output'] = "Terminal cleared."
        elif command.upper().startswith('[SHOW]'):
            # Handle markdown file viewing
            parts = command.split(' ', 1)
            if len(parts) > 1:
                filename = parts[1].strip()
                result['output'] = f"Opening markdown viewer for: {filename}"
                result['action'] = 'show_markdown'
                result['filename'] = filename
            else:
                result['output'] = "Usage: [SHOW] <filename.md>"
        elif command.upper().startswith('[EDIT]'):
            # Handle file editing
            parts = command.split(' ', 1)
            if len(parts) > 1:
                filename = parts[1].strip()
                result['output'] = f"Opening editor for: {filename}"
                result['action'] = 'edit_file'
                result['filename'] = filename
            else:
                result['output'] = "Usage: [EDIT] <filename>"
        else:
            result['output'] = f"Command processed: {command}"

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/markdown/content', methods=['GET'])
def get_markdown_content():
    """Get markdown file content for browser viewing"""
    try:
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({'success': False, 'error': 'No file path provided'}), 400

        # Resolve file path
        possible_paths = [
            Path(file_path),
            UDOS_ROOT / "sandbox" / "documents" / file_path,
            UDOS_ROOT / "uMEMORY" / "user" / file_path,
            UDOS_ROOT / "docs" / file_path
        ]

        content_file = None
        for path in possible_paths:
            if path.exists() and path.is_file():
                content_file = path
                break

        if not content_file:
            return jsonify({'success': False, 'error': f'File not found: {file_path}'}), 404

        # Read file content
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(content_file, 'r', encoding='latin-1') as f:
                content = f.read()

        # Get file info
        file_stats = content_file.stat()

        result = {
            'success': True,
            'content': content,
            'filename': content_file.name,
            'path': str(content_file),
            'size': file_stats.st_size,
            'modified': file_stats.st_mtime,
            'is_markdown': content_file.suffix.lower() in ['.md', '.markdown']
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/markdown/list', methods=['GET'])
def list_markdown_files():
    """List available markdown files"""
    try:
        markdown_files = []

        # Search common locations
        search_paths = [
            (UDOS_ROOT / "sandbox" / "documents", "Documents"),
            (UDOS_ROOT / "uMEMORY" / "user", "User Memory"),
            (UDOS_ROOT / "docs", "Documentation")
        ]

        for path, category in search_paths:
            if path.exists():
                for md_file in path.rglob("*.md"):
                    if md_file.is_file():
                        try:
                            stats = md_file.stat()
                            markdown_files.append({
                                'name': md_file.name,
                                'path': str(md_file),
                                'relative_path': str(md_file.relative_to(UDOS_ROOT)),
                                'category': category,
                                'size': stats.st_size,
                                'modified': stats.st_mtime
                            })
                        except Exception:
                            continue

        # Sort by modified time (newest first)
        markdown_files.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({
            'success': True,
            'files': markdown_files[:50],  # Limit to 50 files
            'total': len(markdown_files)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Set server start time
server_start_time = time.time()

def show_rainbow_banner():
    """Display the uDOS rainbow ASCII banner"""
    print("")
    print("\033[0;31m██╗   ██╗\033[0;33m██████╗ \033[0;32m ██████╗ \033[0;36m███████╗\033[0m")
    print("\033[0;31m██║   ██║\033[0;33m██╔══██╗\033[0;32m██╔═══██╗\033[0;36m██╔════╝\033[0m")
    print("\033[0;31m██║   ██║\033[0;33m██║  ██║\033[0;32m██║   ██║\033[0;36m███████╗\033[0m")
    print("\033[0;31m██║   ██║\033[0;33m██║  ██║\033[0;32m██║   ██║\033[0;36m╚════██║\033[0m")
    print("\033[0;31m╚██████╔╝\033[0;33m██████╔╝\033[0;32m╚██████╔╝\033[0;36m███████║\033[0m")
    print("\033[0;31m ╚═════╝ \033[0;33m╚═════╝ \033[0;32m ╚═════╝ \033[0;36m╚══════╝\033[0m")
    print("")
    print("\033[0;35m▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄\033[0m")
    print("\033[0;35m█\033[1;31m███\033[1;33m███\033[1;32m███\033[1;36m███\033[1;34m███\033[1;35m███\033[0;31m███\033[0;33m███\033[0;32m███\033[0;36m███\033[0;34m███\033[0;35m███\033[1;31m███\033[1;33m███\033[1;32m███\033[1;36m███\033[1;34m███\033[1;35m███\033[0;31m███\033[0;35m█\033[0m")
    print("\033[0;35m█\033[0;37m Universal Device Operating System v1.0.4.2             \033[0;35m█\033[0m")
    print("\033[0;35m█\033[0;37m Simple • Lean • Fast • Foundational Architecture     \033[0;35m█\033[0m")
    print("\033[0;35m█\033[1;31m███\033[1;33m███\033[1;32m███\033[1;36m███\033[1;34m███\033[1;35m███\033[0;31m███\033[0;33m███\033[0;32m███\033[0;36m███\033[0;34m███\033[0;35m███\033[1;31m███\033[1;33m███\033[1;32m███\033[1;36m███\033[1;34m███\033[1;35m███\033[0;31m███\033[0;35m█\033[0m")
    print("\033[0;35m▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀\033[0m")
    print("")

def show_server_status():
    """Display detailed server status with colors"""
    print("\033[1;36m╔══════════════════════════════════════════════════════════════════╗\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;32m🚀 uDOS Server v1.0 - {system_status['udos_mode'].title()} Mode\033[0m" + " " * (40 - len(system_status['udos_mode'])) + "\033[1;36m║\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;33m📁 Root:\033[0m {str(UDOS_ROOT):<50}\033[1;36m║\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;35m🎭 Role:\033[0m {system_status['udos_mode']} (Level {system_status['access_level']})" + " " * (40 - len(f"{system_status['udos_mode']} (Level {system_status['access_level']})")) + "\033[1;36m║\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;34m🌐 Server:\033[0m http://127.0.0.1:8080" + " " * 39 + "\033[1;36m║\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;31m🖥️  UI Integration:\033[0m {str(UI_PATH):<42}\033[1;36m║\033[0m")
    print("\033[1;36m╠══════════════════════════════════════════════════════════════════╣\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;37m⚡ Status:\033[0m \033[1;32mStarting up...\033[0m" + " " * 42 + "\033[1;36m║\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;37m🔄 Health:\033[0m \033[1;32m{system_status['health_status'].title()}\033[0m" + " " * (50 - len(system_status['health_status'])) + "\033[1;36m║\033[0m")
    print(f"\033[1;36m║\033[0m \033[1;37m📊 Clients:\033[0m {len(connected_clients)} connected" + " " * (45 - len(f"{len(connected_clients)} connected")) + "\033[1;36m║\033[0m")
    print("\033[1;36m╚══════════════════════════════════════════════════════════════════╝\033[0m")
    print("")

def main():
    """Main entry point - integrated with uDOS launcher"""
    host = os.environ.get('UDOS_SERVER_HOST', '127.0.0.1')
    port = int(os.environ.get('UDOS_SERVER_PORT', '8080'))
    debug_mode = os.environ.get('UDOS_DEBUG', 'false').lower() == 'true'

    # Show rainbow banner
    show_rainbow_banner()

    # Show detailed status
    show_server_status()

    print(f"\033[1;36m� uSERVER starting...\033[0m")
    print(f"\033[1;35m🎭 Role: {system_status['udos_mode']}\033[0m")
    print(f"\033[1;33m🔐 Access Level: {system_status['access_level']}\033[0m")
    print("")

    # Don't auto-open browser - let launcher handle it
    log_message("🔧 uSERVER starting...")
    log_message(f"🎭 Role: {system_status['udos_mode']}")
    log_message(f"🔐 Access Level: {system_status['access_level']}")

    try:
        print("\033[1;32m✅ Starting Flask-SocketIO server...\033[0m")
        print("\033[1;37m💡 Press Ctrl+C to stop the server\033[0m")
        print("")
        # Start the server
        socketio.run(app, host=host, port=port, debug=debug_mode, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\033[1;33m🛑 Server stopped by user\033[0m")
        log_message("🛑 Server stopped by user")
    except Exception as e:
        print(f"\n\033[1;31m❌ Server failed to start: {e}\033[0m")
        log_message(f"❌ Server error: {e}")
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
