#!/usr/bin/env python3
"""
uDOS Display Server
Modern web interface backend with WebSocket support for real-time terminal emulation
"""

import asyncio
import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import psutil

# uDOS paths
UDOS_ROOT = Path(__file__).parent.parent.parent.parent
UDOS_MEMORY = UDOS_ROOT / "uMEMORY"
UDOS_SANDBOX = UDOS_ROOT / "sandbox"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(UDOS_ROOT / "wizard" / "logs" / "display-server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__,
           template_folder=str(UDOS_ROOT / "uNETWORK" / "display" / "templates"),
           static_folder=str(UDOS_ROOT / "uNETWORK" / "display" / "static"))
app.config['SECRET_KEY'] = 'udos-v14-display-secret'

# WebSocket setup
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class TerminalSession:
    """Manages individual terminal sessions for browser clients"""

    def __init__(self, session_id: str, user_role: str = "user"):
        self.session_id = session_id
        self.user_role = user_role
        self.process = None
        self.is_active = False
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def start_session(self):
        """Start a new terminal session"""
        try:
            # Source UTF-8 and display systems first
            init_script = f"""
source {UDOS_ROOT}/uSCRIPT/library/shell/ensure-utf8.sh
source {UDOS_ROOT}/uCORE/system/display/glyph-detector.sh
source {UDOS_ROOT}/uCORE/system/polaroid-colors.sh
cd {UDOS_SANDBOX if self.user_role != 'wizard' else UDOS_ROOT}
export UDOS_BROWSER_SESSION=1
export UDOS_USER_ROLE={self.user_role}
echo "🌐 uDOS Browser Terminal Ready"
echo "   Role: {self.user_role}"
echo "   Session: {self.session_id}"
echo "   Location: $(pwd)"
exec /bin/bash --login
"""

            self.process = subprocess.Popen(
                ['/bin/bash'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                preexec_fn=os.setsid
            )

            # Send initialization script
            self.process.stdin.write(init_script)
            self.process.stdin.flush()
            self.is_active = True

            logger.info(f"Started terminal session {self.session_id} for role {self.user_role}")
            return True

        except Exception as e:
            logger.error(f"Failed to start terminal session {self.session_id}: {e}")
            return False

    def send_command(self, command: str) -> bool:
        """Send command to terminal"""
        if not self.is_active or not self.process:
            return False

        try:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()
            self.last_activity = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Failed to send command to session {self.session_id}: {e}")
            return False

    def read_output(self) -> Optional[str]:
        """Read output from terminal (non-blocking)"""
        if not self.is_active or not self.process:
            return None

        try:
            # Use select for non-blocking read
            import select
            if select.select([self.process.stdout], [], [], 0)[0]:
                output = self.process.stdout.readline()
                return output
        except Exception as e:
            logger.error(f"Failed to read output from session {self.session_id}: {e}")

        return None

    def terminate(self):
        """Terminate terminal session"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), 9)
                self.process = None
                self.is_active = False
                logger.info(f"Terminated terminal session {self.session_id}")
            except Exception as e:
                logger.error(f"Failed to terminate session {self.session_id}: {e}")

# Global session manager
terminal_sessions: Dict[str, TerminalSession] = {}

@app.route('/')
def index():
    """Main dashboard interface"""
    return render_template('dashboard.html')

@app.route('/terminal')
def terminal():
    """Terminal emulator interface"""
    return render_template('terminal.html')

@app.route('/memory')
def memory_browser():
    """uMEMORY browser interface"""
    return render_template('memory.html')

@app.route('/api/system/status')
def system_status():
    """Get system status information"""
    try:
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(UDOS_ROOT))

        # Get uDOS specific info
        active_sessions = len([s for s in terminal_sessions.values() if s.is_active])

        # Check uMEMORY status
        memory_status = "available" if UDOS_MEMORY.exists() else "not_configured"

        return jsonify({
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            },
            "udos": {
                "version": "1.4.0-beta",
                "active_sessions": active_sessions,
                "memory_status": memory_status,
                "root_path": str(UDOS_ROOT),
                "uptime": "calculated_from_start_time"  # TODO: Implement
            }
        })
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/browse')
def browse_memory():
    """Browse uMEMORY structure"""
    path = request.args.get('path', '')
    try:
        memory_path = UDOS_MEMORY / path
        if not memory_path.exists():
            return jsonify({"error": "Path not found"}), 404

        items = []
        if memory_path.is_dir():
            for item in memory_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })

        return jsonify({
            "path": path,
            "items": sorted(items, key=lambda x: (x["type"] != "directory", x["name"]))
        })

    except Exception as e:
        logger.error(f"Failed to browse memory path {path}: {e}")
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'session_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = request.sid
    if session_id in terminal_sessions:
        terminal_sessions[session_id].terminate()
        del terminal_sessions[session_id]
    logger.info(f"Client disconnected: {session_id}")

@socketio.on('terminal_start')
def handle_terminal_start(data):
    """Start a new terminal session"""
    session_id = request.sid
    user_role = data.get('role', 'user')

    if session_id in terminal_sessions:
        terminal_sessions[session_id].terminate()

    session = TerminalSession(session_id, user_role)
    if session.start_session():
        terminal_sessions[session_id] = session
        emit('terminal_ready', {'session_id': session_id})

        # Start output monitoring
        socketio.start_background_task(monitor_terminal_output, session_id)
    else:
        emit('terminal_error', {'error': 'Failed to start terminal session'})

@socketio.on('terminal_input')
def handle_terminal_input(data):
    """Handle input from browser terminal"""
    session_id = request.sid
    command = data.get('command', '')

    if session_id in terminal_sessions:
        if terminal_sessions[session_id].send_command(command):
            emit('terminal_ack', {'received': True})
        else:
            emit('terminal_error', {'error': 'Failed to send command'})
    else:
        emit('terminal_error', {'error': 'No active terminal session'})

def monitor_terminal_output(session_id):
    """Background task to monitor terminal output"""
    while session_id in terminal_sessions:
        session = terminal_sessions[session_id]
        if not session.is_active:
            break

        output = session.read_output()
        if output:
            socketio.emit('terminal_output', {'data': output}, room=session_id)

        socketio.sleep(0.1)  # Small delay to prevent excessive CPU usage

if __name__ == '__main__':
    logger.info("Starting uDOS Display Server v1.4")
    logger.info(f"uDOS Root: {UDOS_ROOT}")
    logger.info(f"Memory Path: {UDOS_MEMORY}")

    # Ensure required directories exist
    os.makedirs(UDOS_ROOT / "wizard" / "logs", exist_ok=True)

    # Start server
    socketio.run(app,
                host='0.0.0.0',
                port=8080,
                debug=False,
                allow_unsafe_werkzeug=True)
