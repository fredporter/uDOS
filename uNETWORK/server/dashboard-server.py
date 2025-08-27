#!/usr/bin/env python3
"""
uDOS Web Dashboard Server
Flask-based web interface leveraging the integrated variable system and command router
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# Add uDOS Python library to path
udos_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(udos_root / 'uSCRIPT' / 'library' / 'python'))

try:
    from udos_variables import UDOSVariables, get_user_role, get_user_level, get_display_mode
except ImportError:
    print("uDOS variable library not found. Please run variable system optimizer.")
    sys.exit(1)

# Initialize Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'udos-dashboard-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize uDOS variable access
udos_vars = UDOSVariables()

# Configuration
UDOS_ROOT = str(udos_root)
COMMAND_ROUTER = os.path.join(UDOS_ROOT, 'uCORE', 'code', 'command-router.sh')

class UDOSDashboard:
    """Main dashboard controller"""

    def __init__(self):
        self.active_sessions = {}

    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            # Get role information
            user_role = get_user_role()
            user_level = get_user_level()
            display_mode = get_display_mode()

            # Get all variables
            all_vars = udos_vars.get_all_variables()

            # Get role-specific information
            role_info = self.get_role_info(user_role)

            return {
                'timestamp': datetime.now().isoformat(),
                'role': {
                    'name': user_role,
                    'level': user_level,
                    'display_mode': display_mode,
                    'capabilities': role_info['capabilities'],
                    'color': role_info['color'],
                    'icon': role_info['icon']
                },
                'variables': all_vars,
                'system': {
                    'version': '1.0.4.1',
                    'router_status': 'active' if os.path.exists(COMMAND_ROUTER) else 'unavailable',
                    'variable_count': len(all_vars),
                    'udos_root': UDOS_ROOT
                }
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_role_info(self, role):
        """Get role-specific display information"""
        role_data = {
            'GHOST': {
                'color': '#E5E7EB',
                'icon': '👻',
                'capabilities': ['Demo Mode', 'Read-only Access', 'Basic Commands']
            },
            'TOMB': {
                'color': '#F59E0B',
                'icon': '🗿',
                'capabilities': ['Storage Management', 'Variable Operations', 'Archive Functions']
            },
            'CRYPT': {
                'color': '#8B5CF6',
                'icon': '🔐',
                'capabilities': ['Secure Storage', 'Enhanced Security', 'Protected Operations']
            },
            'DRONE': {
                'color': '#3B82F6',
                'icon': '🤖',
                'capabilities': ['Automation', 'ASSIST Basic', 'Workflow Management']
            },
            'KNIGHT': {
                'color': '#06B6D4',
                'icon': '⚔️',
                'capabilities': ['Role Management', 'System Protection', 'Guardian Functions']
            },
            'IMP': {
                'color': '#EF4444',
                'icon': '😈',
                'capabilities': ['Development Tools', 'ASSIST Advanced', 'Creative Functions']
            },
            'SORCERER': {
                'color': '#A855F7',
                'icon': '🧙‍♂️',
                'capabilities': ['System Configuration', 'Advanced Administration', 'Magic Functions']
            },
            'WIZARD': {
                'color': '#10B981',
                'icon': '✨',
                'capabilities': ['Full System Access', 'Core Modification', 'Master Control']
            }
        }
        return role_data.get(role, role_data['GHOST'])

    def execute_command(self, command):
        """Execute uCODE command via router"""
        try:
            if not os.path.exists(COMMAND_ROUTER):
                return {'error': 'Command router not available', 'success': False}

            result = subprocess.run(
                [COMMAND_ROUTER, command],
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {'error': 'Command timeout', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def get_available_stories(self):
        """Get list of available stories"""
        try:
            stories_dir = Path(UDOS_ROOT) / 'uMEMORY' / 'system' / 'stories'
            if not stories_dir.exists():
                return []

            stories = []
            for story_file in stories_dir.rglob('*.json'):
                try:
                    with open(story_file, 'r') as f:
                        story_data = json.load(f)
                        stories.append({
                            'name': story_file.stem,
                            'title': story_data.get('metadata', {}).get('title', 'Unknown'),
                            'role': story_data.get('metadata', {}).get('role'),
                            'level': story_data.get('metadata', {}).get('level'),
                            'path': str(story_file.relative_to(udos_root))
                        })
                except Exception:
                    continue

            return sorted(stories, key=lambda x: x.get('level', 0))
        except Exception:
            return []

# Initialize dashboard
dashboard = UDOSDashboard()

# Web Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """System status API endpoint"""
    return jsonify(dashboard.get_system_status())

@app.route('/api/variables')
def api_variables():
    """Variables API endpoint"""
    try:
        variables = udos_vars.get_all_variables()
        return jsonify({'success': True, 'variables': variables})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stories')
def api_stories():
    """Stories API endpoint"""
    stories = dashboard.get_available_stories()
    return jsonify({'success': True, 'stories': stories})

@app.route('/api/execute', methods=['POST'])
def api_execute():
    """Command execution API endpoint"""
    try:
        data = request.get_json()
        command = data.get('command', '')

        if not command:
            return jsonify({'success': False, 'error': 'No command provided'})

        result = dashboard.execute_command(command)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# SocketIO Events
@socketio.on('connect')
def on_connect():
    """Handle client connection"""
    emit('status', dashboard.get_system_status())

@socketio.on('execute_command')
def on_execute_command(data):
    """Handle command execution via WebSocket"""
    command = data.get('command', '')
    result = dashboard.execute_command(command)
    emit('command_result', result)

@socketio.on('request_status')
def on_request_status():
    """Handle status request"""
    emit('status', dashboard.get_system_status())

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)

    print("🌐 Starting uDOS Web Dashboard...")
    print(f"📁 uDOS Root: {UDOS_ROOT}")
    print(f"👤 Current Role: {get_user_role()}")
    print(f"🔧 Command Router: {'Available' if os.path.exists(COMMAND_ROUTER) else 'Not Found'}")
    print("🚀 Server starting on http://localhost:8080")

    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
