#!/usr/bin/env python3
"""
uDOS v1.0.19 - Teletext API Server
Comprehensive REST API for all uDOS commands via Teletext GUI
Provides 60+ endpoints for command execution, status, and data retrieval
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
from datetime import datetime
from typing import Dict, List, Optional
import threading
import time
import logging
from logging.handlers import RotatingFileHandler

# Add parent directory to path for uDOS imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from core.uDOS_parser import Parser
    from core.uDOS_commands import CommandHandler
    from core.uDOS_grid import Grid
    from core.uDOS_logger import Logger
    from core.utils.files import WorkspaceManager
    from core.services.history import CommandHistory
    from core.services.user_manager import UserManager
    UDOS_AVAILABLE = True
except ImportError:
    UDOS_AVAILABLE = False
    print("⚠️  uDOS core modules not available - running in standalone mode")

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'udos-teletext-api-v1.0.19'
CORS(app)  # Enable CORS for web interface
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging to sandbox/logs
LOG_DIR = Path(__file__).parent.parent.parent / 'sandbox' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'api_server.log'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler with rotation
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
))

# Add handlers to Flask app logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

# Create API logger
api_logger = logging.getLogger('uDOS.API')
api_logger.addHandler(file_handler)
api_logger.setLevel(logging.DEBUG)

api_logger.info('='*70)
api_logger.info('uDOS API Server Starting')
api_logger.info(f'Log file: {LOG_FILE}')
api_logger.info('='*70)

# Global uDOS instances (initialized on first request)
parser = None
command_handler = None
grid = None
logger = None
workspace_manager = None
command_history = None
user_manager = None

# Real-time update tracking
update_subscribers = set()
last_system_state = {}
update_thread = None
update_thread_running = False


# ============================================================================
# REQUEST/RESPONSE LOGGING MIDDLEWARE
# ============================================================================

@app.before_request
def log_request():
    """Log all incoming requests with details"""
    api_logger.debug(f'Request: {request.method} {request.path}')
    api_logger.debug(f'Client: {request.remote_addr}')
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            data = request.get_json()
            if data:
                api_logger.debug(f'Request data: {json.dumps(data, indent=2)}')
        except:
            pass

@app.after_request
def log_response(response):
    """Log all responses with status"""
    api_logger.debug(f'Response: {request.path} - Status {response.status_code}')
    return response

@app.errorhandler(Exception)
def handle_error(error):
    """Log all errors"""
    api_logger.error(f'Error on {request.path}: {error}', exc_info=True)
    return jsonify({
        'status': 'error',
        'message': str(error),
        'path': request.path
    }), 500


# ============================================================================
# UDOS SYSTEM INITIALIZATION
# ============================================================================

def init_udos_systems():
    """Initialize uDOS systems on first API call."""
    global parser, command_handler, grid, logger, workspace_manager, command_history, user_manager

    if not UDOS_AVAILABLE:
        api_logger.warning('uDOS core modules not available - running in standalone mode')
        return False

    if parser is None:
        try:
            api_logger.info('Initializing uDOS systems...')
            parser = Parser()
            grid = Grid()
            logger = Logger()
            workspace_manager = WorkspaceManager()
            command_history = CommandHistory()
            user_manager = UserManager()
            command_handler = CommandHandler(
                grid=grid,
                workspace_manager=workspace_manager,
                user_manager=user_manager,
                logger=logger
            )
            api_logger.info('uDOS systems initialized successfully')
            return True
        except Exception as e:
            api_logger.error(f'Failed to initialize uDOS: {e}', exc_info=True)
            print(f"❌ Failed to initialize uDOS: {e}")
            return False

    return True


def execute_command(command_str: str) -> Dict:
    """
    Execute a uDOS command and return structured result.

    Args:
        command_str: Command string (e.g., "HELP", "FILE LIST")

    Returns:
        Dict with status, output, and metadata
    """
    api_logger.info(f'Executing command: {command_str}')

    if not init_udos_systems():
        api_logger.warning(f'Command execution failed - uDOS systems not available: {command_str}')
        return {
            "status": "error",
            "message": "uDOS systems not available",
            "output": ""
        }

    try:
        # Parse and execute command
        ucode = parser.parse(command_str)
        result = command_handler.handle_command(ucode, grid, parser)

        # Log command
        logger.log("API_COMMAND", command_str)
        command_history.append_string(command_str)

        api_logger.info(f'Command executed successfully: {command_str}')
        api_logger.debug(f'Command result: {result}')

        return {
            "status": "success",
            "command": command_str,
            "output": result or "",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.log("API_ERROR", f"{command_str}: {e}")
        api_logger.error(f'Command execution error: {command_str} - {e}', exc_info=True)
        return {
            "status": "error",
            "command": command_str,
            "message": str(e),
            "output": ""
        }


# ============================================================================
# CORE API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve Teletext interface."""
    teletext_dir = Path(__file__).parent
    return send_from_directory(teletext_dir, 'index.html')


@app.route('/api/health')
@app.route('/api/status')  # Alias for compatibility with terminal extension
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "1.0.19",
        "udos_available": UDOS_AVAILABLE,
        "systems_initialized": parser is not None,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/command', methods=['POST'])
def execute_command_api():
    """Execute any uDOS command."""
    data = request.get_json()
    command = data.get('command', '')

    if not command:
        return jsonify({"status": "error", "message": "No command provided"}), 400

    result = execute_command(command)
    return jsonify(result)


# ============================================================================
# SYSTEM COMMANDS (10 endpoints)
# ============================================================================

@app.route('/api/system/help')
def system_help():
    """Get help information."""
    return jsonify(execute_command("HELP"))


@app.route('/api/system/status')
def system_status():
    """Get system status."""
    return jsonify(execute_command("STATUS"))


@app.route('/api/system/config/list')
def config_list():
    """List configuration settings."""
    return jsonify(execute_command("CONFIG LIST"))


@app.route('/api/system/config/get/<key>')
def config_get(key):
    """Get specific config value."""
    return jsonify(execute_command(f"CONFIG GET {key}"))


@app.route('/api/system/config/set', methods=['POST'])
def config_set():
    """Set configuration value."""
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    return jsonify(execute_command(f"CONFIG SET {key} {value}"))


@app.route('/api/system/repair')
def system_repair():
    """Run system repair."""
    return jsonify(execute_command("REPAIR"))


@app.route('/api/system/reboot', methods=['POST'])
def system_reboot():
    """Reboot uDOS system."""
    return jsonify(execute_command("REBOOT"))


@app.route('/api/system/version')
def system_version():
    """Get uDOS version info."""
    return jsonify({
        "status": "success",
        "version": "1.0.19",
        "api_version": "1.0",
        "features": ["autocomplete", "option-selector", "teletext-gui"]
    })


@app.route('/api/system/usage')
def system_usage():
    """Get command usage statistics."""
    return jsonify(execute_command("USAGE"))


@app.route('/api/system/debug', methods=['POST'])
def system_debug():
    """Toggle debug mode."""
    data = request.get_json()
    mode = data.get('mode', 'on')
    return jsonify(execute_command(f"DEBUG {mode}"))


# ============================================================================
# FILE COMMANDS (15 endpoints)
# ============================================================================

@app.route('/api/files/list')
def files_list():
    """List all files in workspace."""
    path = request.args.get('path', '')
    return jsonify(execute_command(f"FILE LIST {path}"))


@app.route('/api/files/recent')
def files_recent():
    """Get recently accessed files."""
    count = request.args.get('count', '10')
    return jsonify(execute_command(f"FILE RECENT {count}"))


@app.route('/api/files/search')
def files_search():
    """Search for files."""
    query = request.args.get('q', '')
    return jsonify(execute_command(f"FILE SEARCH {query}"))


@app.route('/api/files/info/<path:filepath>')
def files_info(filepath):
    """Get file information."""
    return jsonify(execute_command(f"FILE INFO {filepath}"))


@app.route('/api/files/content/<path:filepath>')
def files_content(filepath):
    """Get file content."""
    return jsonify(execute_command(f"FILE READ {filepath}"))


@app.route('/api/files/create', methods=['POST'])
def files_create():
    """Create new file."""
    data = request.get_json()
    filepath = data.get('path')
    content = data.get('content', '')
    return jsonify(execute_command(f"FILE CREATE {filepath}"))


@app.route('/api/files/edit', methods=['POST'])
def files_edit():
    """Edit file (trigger editor)."""
    data = request.get_json()
    filepath = data.get('path')
    return jsonify(execute_command(f"FILE EDIT {filepath}"))


@app.route('/api/files/delete', methods=['DELETE'])
def files_delete():
    """Delete file."""
    data = request.get_json()
    filepath = data.get('path')
    return jsonify(execute_command(f"FILE DELETE {filepath}"))


@app.route('/api/files/copy', methods=['POST'])
def files_copy():
    """Copy file."""
    data = request.get_json()
    source = data.get('source')
    dest = data.get('dest')
    return jsonify(execute_command(f"FILE COPY {source} {dest}"))


@app.route('/api/files/move', methods=['POST'])
def files_move():
    """Move/rename file."""
    data = request.get_json()
    source = data.get('source')
    dest = data.get('dest')
    return jsonify(execute_command(f"FILE MOVE {source} {dest}"))


@app.route('/api/files/run', methods=['POST'])
def files_run():
    """Run script file."""
    data = request.get_json()
    filepath = data.get('path')
    return jsonify(execute_command(f"FILE RUN {filepath}"))


@app.route('/api/files/bookmark/add', methods=['POST'])
def files_bookmark_add():
    """Add file bookmark."""
    data = request.get_json()
    filepath = data.get('path')
    return jsonify(execute_command(f"FILE BOOKMARK {filepath}"))


@app.route('/api/files/bookmark/list')
def files_bookmark_list():
    """List bookmarked files."""
    return jsonify(execute_command("FILE BOOKMARKS"))


@app.route('/api/files/stats')
def files_stats():
    """Get workspace file statistics."""
    return jsonify(execute_command("FILE STATS"))


@app.route('/api/files/tree')
def files_tree():
    """Get directory tree."""
    return jsonify(execute_command("FILE TREE"))


# ============================================================================
# MAP COMMANDS (12 endpoints)
# ============================================================================

@app.route('/api/map/show')
def map_show():
    """Show current map."""
    return jsonify(execute_command("MAP SHOW"))


@app.route('/api/map/status')
def map_status():
    """Get current map position/status."""
    return jsonify(execute_command("MAP STATUS"))


@app.route('/api/map/goto', methods=['POST'])
def map_goto():
    """Go to specific location."""
    data = request.get_json()
    location = data.get('location')
    return jsonify(execute_command(f"MAP GOTO {location}"))


@app.route('/api/map/move', methods=['POST'])
def map_move():
    """Move in direction."""
    data = request.get_json()
    direction = data.get('direction')
    return jsonify(execute_command(f"MAP MOVE {direction}"))


@app.route('/api/map/zoom', methods=['POST'])
def map_zoom():
    """Zoom map."""
    data = request.get_json()
    level = data.get('level', 'in')
    return jsonify(execute_command(f"MAP ZOOM {level}"))


@app.route('/api/map/find')
def map_find():
    """Find location on map."""
    query = request.args.get('q', '')
    return jsonify(execute_command(f"MAP FIND {query}"))


@app.route('/api/map/legend')
def map_legend():
    """Get map legend."""
    return jsonify(execute_command("MAP LEGEND"))


@app.route('/api/map/save', methods=['POST'])
def map_save():
    """Save current map."""
    data = request.get_json()
    filename = data.get('filename')
    return jsonify(execute_command(f"MAP SAVE {filename}"))


@app.route('/api/map/load', methods=['POST'])
def map_load():
    """Load saved map."""
    data = request.get_json()
    filename = data.get('filename')
    return jsonify(execute_command(f"MAP LOAD {filename}"))


@app.route('/api/map/export', methods=['POST'])
def map_export():
    """Export map data."""
    data = request.get_json()
    format_type = data.get('format', 'json')
    return jsonify(execute_command(f"MAP EXPORT {format_type}"))


@app.route('/api/map/nearby')
def map_nearby():
    """Get nearby locations."""
    return jsonify(execute_command("MAP NEARBY"))


@app.route('/api/map/distance')
def map_distance():
    """Calculate distance between locations."""
    loc1 = request.args.get('from')
    loc2 = request.args.get('to')
    return jsonify(execute_command(f"MAP DISTANCE {loc1} {loc2}"))


# ============================================================================
# THEME COMMANDS (8 endpoints)
# ============================================================================

@app.route('/api/theme/list')
def theme_list():
    """List available themes."""
    return jsonify(execute_command("THEME LIST"))


@app.route('/api/theme/current')
def theme_current():
    """Get current theme."""
    return jsonify(execute_command("THEME CURRENT"))


@app.route('/api/theme/set', methods=['POST'])
def theme_set():
    """Set theme."""
    data = request.get_json()
    theme_name = data.get('theme')
    return jsonify(execute_command(f"THEME SET {theme_name}"))


@app.route('/api/theme/info/<theme_name>')
def theme_info(theme_name):
    """Get theme information."""
    return jsonify(execute_command(f"THEME INFO {theme_name}"))


@app.route('/api/theme/preview/<theme_name>')
def theme_preview(theme_name):
    """Preview theme."""
    return jsonify(execute_command(f"THEME PREVIEW {theme_name}"))


@app.route('/api/theme/random', methods=['POST'])
def theme_random():
    """Set random theme."""
    return jsonify(execute_command("THEME RANDOM"))


@app.route('/api/theme/export/<theme_name>')
def theme_export(theme_name):
    """Export theme configuration."""
    return jsonify(execute_command(f"THEME EXPORT {theme_name}"))


@app.route('/api/theme/import', methods=['POST'])
def theme_import():
    """Import theme configuration."""
    data = request.get_json()
    theme_data = data.get('theme_data')
    return jsonify(execute_command(f"THEME IMPORT {theme_data}"))


# ============================================================================
# GRID COMMANDS (8 endpoints)
# ============================================================================

@app.route('/api/grid/view')
def grid_view():
    """View grid layout."""
    return jsonify(execute_command("GRID VIEW"))


@app.route('/api/grid/status')
def grid_status():
    """Get grid status."""
    return jsonify(execute_command("GRID STATUS"))


@app.route('/api/grid/focus', methods=['POST'])
def grid_focus():
    """Focus on grid panel."""
    data = request.get_json()
    panel = data.get('panel')
    return jsonify(execute_command(f"GRID FOCUS {panel}"))


@app.route('/api/grid/split', methods=['POST'])
def grid_split():
    """Split grid panel."""
    data = request.get_json()
    direction = data.get('direction', 'horizontal')
    return jsonify(execute_command(f"GRID SPLIT {direction}"))


@app.route('/api/grid/merge', methods=['POST'])
def grid_merge():
    """Merge grid panels."""
    return jsonify(execute_command("GRID MERGE"))


@app.route('/api/grid/resize', methods=['POST'])
def grid_resize():
    """Resize grid panel."""
    data = request.get_json()
    panel = data.get('panel')
    size = data.get('size')
    return jsonify(execute_command(f"GRID RESIZE {panel} {size}"))


@app.route('/api/grid/clear', methods=['POST'])
def grid_clear():
    """Clear grid panel."""
    data = request.get_json()
    panel = data.get('panel', 'MAIN')
    return jsonify(execute_command(f"GRID CLEAR {panel}"))


@app.route('/api/grid/swap', methods=['POST'])
def grid_swap():
    """Swap grid panels."""
    data = request.get_json()
    panel1 = data.get('panel1')
    panel2 = data.get('panel2')
    return jsonify(execute_command(f"GRID SWAP {panel1} {panel2}"))


# ============================================================================
# ASSIST COMMANDS (6 endpoints)
# ============================================================================

@app.route('/api/assist/ask', methods=['POST'])
def assist_ask():
    """Ask AI assistant."""
    data = request.get_json()
    question = data.get('question')
    return jsonify(execute_command(f"OK {question}"))


@app.route('/api/assist/explain', methods=['POST'])
def assist_explain():
    """Get explanation."""
    data = request.get_json()
    topic = data.get('topic')
    return jsonify(execute_command(f"EXPLAIN {topic}"))


@app.route('/api/assist/debug', methods=['POST'])
def assist_debug():
    """Debug assistance."""
    data = request.get_json()
    error = data.get('error')
    return jsonify(execute_command(f"DEBUG {error}"))


@app.route('/api/assist/suggest')
def assist_suggest():
    """Get command suggestions."""
    context = request.args.get('context', '')
    return jsonify(execute_command(f"SUGGEST {context}"))


@app.route('/api/assist/history')
def assist_history():
    """Get command history."""
    limit = request.args.get('limit', '20')
    return jsonify(execute_command(f"HISTORY {limit}"))


@app.route('/api/assist/mode', methods=['POST'])
def assist_mode():
    """Toggle assist mode."""
    data = request.get_json()
    mode = data.get('mode', 'on')
    return jsonify(execute_command(f"ASSIST {mode}"))


# ============================================================================
# REAL-TIME UPDATE SYSTEM
# ============================================================================

def get_system_state():
    """Get current system state for change detection."""
    try:
        state = {
            'timestamp': datetime.now().isoformat(),
            'xp': 0,
            'level': 1,
            'health': 100,
            'energy': 100,
            'hydration': 100,
            'file_count': 0,
            'position': {'cell': 'A1', 'latitude': 0, 'longitude': 0}
        }

        if UDOS_AVAILABLE:
            # Get XP data from user manager
            if user_manager:
                user_data = user_manager.get_user_data()
                if user_data and 'xp' in user_data:
                    state['xp'] = user_data['xp'].get('total', 0)
                    state['level'] = user_data['xp'].get('level', 1)

                # Get survival stats
                if 'survival' in user_data:
                    survival = user_data['survival']
                    state['health'] = survival.get('health', 100)
                    state['energy'] = survival.get('energy', 100)
                    state['hydration'] = survival.get('hydration', 100)

            # Get workspace file count
            if workspace_manager:
                files = workspace_manager.list_files()
                state['file_count'] = len(files) if files else 0

            # Get map position (would need map manager integration)
            # For now, return default values

        return state
    except Exception as e:
        print(f"Error getting system state: {e}")
        return {}


def detect_changes(old_state, new_state):
    """Detect what changed between states."""
    changes = {}

    for key in ['xp', 'level', 'health', 'energy', 'hydration', 'file_count']:
        if key in old_state and key in new_state:
            if old_state[key] != new_state[key]:
                changes[key] = {
                    'old': old_state[key],
                    'new': new_state[key],
                    'delta': new_state[key] - old_state[key] if isinstance(new_state[key], (int, float)) else None
                }

    # Check position changes
    if 'position' in old_state and 'position' in new_state:
        if old_state['position'] != new_state['position']:
            changes['position'] = {
                'old': old_state['position'],
                'new': new_state['position']
            }

    return changes


def broadcast_updates():
    """Background thread to broadcast system updates to all connected clients."""
    global last_system_state, update_thread_running

    print("📡 Real-time update broadcaster started")

    while update_thread_running:
        try:
            # Get current system state
            current_state = get_system_state()

            # Detect changes
            if last_system_state:
                changes = detect_changes(last_system_state, current_state)

                if changes and update_subscribers:
                    # Broadcast changes to all subscribers
                    socketio.emit('system_update', {
                        'timestamp': current_state['timestamp'],
                        'changes': changes,
                        'state': current_state
                    })
                    print(f"📤 Broadcast update: {len(changes)} changes to {len(update_subscribers)} clients")

            # Update last known state
            last_system_state = current_state.copy()

            # Wait before next check (5 second interval)
            time.sleep(5)

        except Exception as e:
            print(f"Error in broadcast_updates: {e}")
            time.sleep(5)

    print("📡 Real-time update broadcaster stopped")


def start_update_broadcaster():
    """Start the background update broadcaster thread."""
    global update_thread, update_thread_running

    if update_thread is None or not update_thread.is_alive():
        update_thread_running = True
        update_thread = threading.Thread(target=broadcast_updates, daemon=True)
        update_thread.start()
        print("✅ Update broadcaster thread started")


def stop_update_broadcaster():
    """Stop the background update broadcaster thread."""
    global update_thread_running
    update_thread_running = False
    print("🛑 Stopping update broadcaster...")


# ============================================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('status', {'message': 'Connected to uDOS API', 'version': '1.0.19'})

    # Start broadcaster if not running
    if not update_thread_running:
        start_update_broadcaster()


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    # Remove from subscribers
    if request.sid in update_subscribers:
        update_subscribers.remove(request.sid)
        print(f'Client disconnected: {request.sid} ({len(update_subscribers)} remaining)')

    # Stop broadcaster if no clients
    if len(update_subscribers) == 0 and update_thread_running:
        stop_update_broadcaster()


@socketio.on('execute_command')
def handle_command(data):
    """Execute command via WebSocket."""
    command = data.get('command', '')
    result = execute_command(command)
    emit('command_result', result)


@socketio.on('subscribe_updates')
def handle_subscribe(data):
    """Subscribe to real-time updates."""
    types = data.get('types', ['all'])

    # Add to subscribers
    update_subscribers.add(request.sid)

    # Send initial state
    current_state = get_system_state()
    emit('subscribed', {
        'status': 'success',
        'types': types,
        'initial_state': current_state
    })

    print(f'Client subscribed: {request.sid} (total: {len(update_subscribers)})')

    # Start broadcaster if not running
    if not update_thread_running:
        start_update_broadcaster()


# ============================================================================
# KNOWLEDGE BANK API (v1.0.20 - 4-Tier Knowledge System)
# ============================================================================

@app.route('/api/knowledge/stats')
def api_knowledge_stats():
    """Get tier statistics."""
    result = execute_command('[KNOWLEDGE|STATS]')
    return jsonify(result)


@app.route('/api/knowledge/search')
def api_knowledge_search():
    """Search knowledge across tiers."""
    query = request.args.get('query', '*')
    tier = request.args.get('tier')
    tags = request.args.get('tags')

    cmd_parts = ['SEARCH', query]
    if tier:
        cmd_parts.extend(['--tier', tier])
    if tags:
        cmd_parts.extend(['--tags', tags])

    command = f"[KNOWLEDGE|{' '.join(cmd_parts)}]"
    result = execute_command(command)
    return jsonify(result)


@app.route('/api/knowledge/view/<knowledge_id>')
def api_knowledge_view(knowledge_id):
    """View specific knowledge item."""
    result = execute_command(f'[KNOWLEDGE|VIEW {knowledge_id}]')
    return jsonify(result)


@app.route('/api/knowledge/add', methods=['POST'])
def api_knowledge_add():
    """Add new knowledge item."""
    data = request.json
    tier = data.get('tier', 0)
    knowledge_type = data.get('type', 'note')
    title = data.get('title', '')
    content = data.get('content', '')
    tags = data.get('tags', [])

    command = f"[KNOWLEDGE|ADD {tier} {knowledge_type} {title}]"
    # Note: This is simplified - full implementation would need
    # multi-line content handling via API
    result = execute_command(command)
    return jsonify(result)


@app.route('/api/knowledge/tiers')
def api_knowledge_tiers():
    """List tier descriptions."""
    result = execute_command('[KNOWLEDGE|TIERS]')
    return jsonify(result)


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

def main():
    """Run the Teletext API server."""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    startup_msg = f"""\n{"="*70}
🌀 uDOS v1.0.20 - Teletext API Server
{"="*70}

🌐 Server: http://localhost:{port}
📡 API Endpoints: {len([rule for rule in app.url_map.iter_rules()])} routes
🔌 WebSocket: Enabled
🎨 CORS: Enabled
🔧 Debug: {debug}
📝 Logging: {LOG_FILE}

{"="*70}
API Documentation:
  System:    /api/system/*    (10 endpoints)
  Files:     /api/files/*     (15 endpoints)
  Map:       /api/map/*       (12 endpoints)
  Theme:     /api/theme/*     (8 endpoints)
  Grid:      /api/grid/*      (8 endpoints)
  Assist:    /api/assist/*    (6 endpoints)
  Knowledge: /api/knowledge/* (5 endpoints) [NEW]
  Core:      /api/command, /api/health
{"="*70}

✨ Press Ctrl+C to stop\n"""

    print(startup_msg)
    api_logger.info(f'Starting server on port {port}')
    api_logger.info(f'Debug mode: {debug}')
    api_logger.info(f'uDOS core available: {UDOS_AVAILABLE}')

    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        api_logger.info('Server stopped by user')
        print('\n👋 Server stopped')
    except Exception as e:
        api_logger.error(f'Server error: {e}', exc_info=True)
        print(f'\n❌ Server error: {e}')
        raise


if __name__ == '__main__':
    main()
