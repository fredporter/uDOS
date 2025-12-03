"""
Mission Control Dashboard Handler
Provides REST API and WebSocket endpoints for the mission control dashboard.
"""

from flask import Blueprint, jsonify, send_file
from flask_socketio import SocketIO, emit
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from core.config import Config
from core.services.mission_manager import get_mission_manager
from core.services.scheduler import get_scheduler
from core.services.resource_manager import get_resource_manager


# Blueprint for dashboard routes
dashboard_bp = Blueprint('mission_control', __name__)

# WebSocket instance (will be set by extension manager)
socketio: SocketIO = None


def init_socketio(app_socketio: SocketIO):
    """Initialize WebSocket instance."""
    global socketio
    socketio = app_socketio


# Static file serving
@dashboard_bp.route('/dashboard')
def serve_dashboard():
    """Serve the main dashboard HTML."""
    dashboard_path = Path(__file__).parent / 'dashboard.html'
    return send_file(dashboard_path)


@dashboard_bp.route('/dashboard.css')
def serve_css():
    """Serve dashboard CSS."""
    css_path = Path(__file__).parent / 'dashboard.css'
    return send_file(css_path, mimetype='text/css')


@dashboard_bp.route('/dashboard.js')
def serve_js():
    """Serve dashboard JavaScript."""
    js_path = Path(__file__).parent / 'dashboard.js'
    return send_file(js_path, mimetype='application/javascript')


# API Endpoints
@dashboard_bp.route('/api/missions')
def get_missions():
    """Get all missions with current status."""
    try:
        mm = get_mission_manager()

        # Get active missions
        active_missions = []
        for mission_id, mission in mm.missions.items():
            if mission.status in ['active', 'paused']:
                active_missions.append({
                    'id': mission.id,
                    'name': mission.name,
                    'status': mission.status,
                    'priority': mission.priority.name,
                    'completed_steps': len(mission.completed_steps),
                    'total_steps': len(mission.steps),
                    'created_at': mission.created_at.isoformat(),
                    'updated_at': mission.updated_at.isoformat() if mission.updated_at else None
                })

        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        active_missions.sort(key=lambda m: priority_order.get(m['priority'], 4))

        # Get next queued mission
        next_mission = None
        for mission_id, mission in mm.missions.items():
            if mission.status == 'pending':
                next_mission = {
                    'id': mission.id,
                    'name': mission.name,
                    'priority': mission.priority.name,
                    'total_steps': len(mission.steps)
                }
                break

        return jsonify({
            'success': True,
            'missions': active_missions,
            'next_mission': next_mission,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/missions/<mission_id>')
def get_mission_details(mission_id: str):
    """Get detailed information about a specific mission."""
    try:
        mm = get_mission_manager()
        mission = mm.get_mission(mission_id)

        if not mission:
            return jsonify({
                'success': False,
                'error': 'Mission not found'
            }), 404

        return jsonify({
            'success': True,
            'mission': {
                'id': mission.id,
                'name': mission.name,
                'description': mission.description,
                'status': mission.status,
                'priority': mission.priority.name,
                'steps': [
                    {
                        'id': step.id,
                        'description': step.description,
                        'status': step.status,
                        'dependencies': step.dependencies
                    }
                    for step in mission.steps
                ],
                'completed_steps': [s.id for s in mission.completed_steps],
                'checkpoints': [
                    {
                        'id': cp.id,
                        'state': cp.state,
                        'timestamp': cp.timestamp.isoformat()
                    }
                    for cp in mission.checkpoints
                ],
                'created_at': mission.created_at.isoformat(),
                'updated_at': mission.updated_at.isoformat() if mission.updated_at else None,
                'completed_at': mission.completed_at.isoformat() if mission.completed_at else None
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/schedules')
def get_schedules():
    """Get all scheduled tasks."""
    try:
        scheduler = get_scheduler()

        schedules = []
        for task_id, task in scheduler.tasks.items():
            schedules.append({
                'id': task.id,
                'name': task.name,
                'pattern': task.pattern,
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'enabled': task.enabled,
                'command': task.command
            })

        # Sort by next run time
        schedules.sort(key=lambda t: t['next_run'] or '')

        return jsonify({
            'success': True,
            'schedules': schedules,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/resources')
def get_resources():
    """Get resource usage summary."""
    try:
        rm = get_resource_manager()

        # API quotas
        api_quotas = {}
        for provider in ['gemini', 'github']:
            status = rm.check_api_quota(provider)
            api_quotas[provider] = {
                'used': status['used'],
                'limit': status['limit'],
                'available': status['available'],
                'reset_time': status['reset_time'].isoformat() if status.get('reset_time') else None
            }

        # Disk usage
        disk_usage = rm.get_disk_usage()

        # System stats
        system_stats = rm.get_system_stats()

        # Active allocations
        allocations = []
        for mission_id, alloc in rm.allocations.items():
            allocations.append({
                'mission_id': mission_id,
                'api_calls': alloc['api_calls'],
                'disk_mb': alloc['disk_mb'],
                'priority': alloc['priority']
            })

        return jsonify({
            'success': True,
            'resources': {
                'api_quotas': api_quotas,
                'disk': disk_usage,
                'system': system_stats,
                'allocations': allocations
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# WebSocket Event Handlers
@socketio.on('connect', namespace='/ws/updates')
def handle_connect():
    """Handle WebSocket connection."""
    print("Dashboard connected via WebSocket")
    emit('connected', {'message': 'Connected to Mission Control'})


@socketio.on('disconnect', namespace='/ws/updates')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print("Dashboard disconnected from WebSocket")


@socketio.on('subscribe', namespace='/ws/updates')
def handle_subscribe(data):
    """Handle subscription requests."""
    subscription_type = data.get('type', 'all')
    print(f"Dashboard subscribed to: {subscription_type}")
    emit('subscribed', {'type': subscription_type})


# Push notification functions (called by mission system)
def broadcast_mission_update(mission_data: Dict[str, Any]):
    """Broadcast mission update to all connected clients."""
    if socketio:
        socketio.emit('mission_update', {
            'type': 'mission_update',
            'mission': mission_data,
            'timestamp': datetime.now().isoformat()
        }, namespace='/ws/updates')


def broadcast_mission_completed(mission_data: Dict[str, Any]):
    """Broadcast mission completion to all connected clients."""
    if socketio:
        socketio.emit('mission_completed', {
            'type': 'mission_completed',
            'mission': mission_data,
            'timestamp': datetime.now().isoformat()
        }, namespace='/ws/updates')


def broadcast_schedule_update(schedule_data: Dict[str, Any]):
    """Broadcast schedule update to all connected clients."""
    if socketio:
        socketio.emit('schedule_update', {
            'type': 'schedule_update',
            'schedule': schedule_data,
            'timestamp': datetime.now().isoformat()
        }, namespace='/ws/updates')


def broadcast_resource_update(resource_data: Dict[str, Any]):
    """Broadcast resource update to all connected clients."""
    if socketio:
        socketio.emit('resource_update', {
            'type': 'resource_update',
            'resources': resource_data,
            'timestamp': datetime.now().isoformat()
        }, namespace='/ws/updates')


# Extension metadata
__extension_info__ = {
    'name': 'Mission Control Dashboard',
    'version': '1.1.2',
    'description': 'Web-based mission control and monitoring dashboard',
    'blueprint': dashboard_bp,
    'socketio_handlers': True,
    'init_function': init_socketio
}
