#!/usr/bin/env python3
"""
uDOS Task Manager API v1.0.4.1
RESTful API interface for task management system
Location: uNETWORK/server/task_manager_api.py
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from functools import wraps
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get uDOS root path
UDOS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TASK_MANAGER_SCRIPT = os.path.join(UDOS_ROOT, 'uCORE', 'code', 'task-manager.sh')
HEALTH_DAEMON_SCRIPT = os.path.join(UDOS_ROOT, 'uCORE', 'code', 'health-monitor-daemon.sh')

# Create Blueprint
task_api = Blueprint('task_api', __name__, url_prefix='/api/tasks')

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def run_task_manager_command(command_args):
    """Execute task manager script with given arguments"""
    try:
        cmd = [TASK_MANAGER_SCRIPT] + command_args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def run_health_daemon_command(command_args):
    """Execute health daemon script with given arguments"""
    try:
        cmd = [HEALTH_DAEMON_SCRIPT] + command_args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def load_json_file(filepath):
    """Load JSON file safely"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading JSON file {filepath}: {e}")
        return None

def require_auth(f):
    """Authentication decorator (placeholder for future implementation)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement authentication
        # For now, allow all requests
        return f(*args, **kwargs)
    return decorated_function

def api_response(success=True, data=None, message=None, status_code=200):
    """Standardized API response format"""
    response = {
        'success': success,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': data,
        'message': message
    }
    return jsonify(response), status_code

# ═══════════════════════════════════════════════════════════════════════
# TASK MANAGEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@task_api.route('/create', methods=['POST'])
@require_auth
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'command' not in data:
            return api_response(
                success=False,
                message='Missing required fields: name, command',
                status_code=400
            )

        task_name = data['name']
        task_command = data['command']
        task_type = data.get('type', 'manual')
        priority = data.get('priority', 'normal')
        timeout = data.get('timeout', 300)

        # Create task
        result = run_task_manager_command([
            'create', task_name, task_command, task_type
        ])

        if result['success']:
            # Extract task ID from output
            task_id = result['stdout'].split('ID: ')[-1].rstrip(')')
            return api_response(
                data={'task_id': task_id},
                message=f'Task created successfully: {task_name}'
            )
        else:
            return api_response(
                success=False,
                message=f'Failed to create task: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/execute/<task_id>', methods=['POST'])
@require_auth
def execute_task(task_id):
    """Execute a specific task"""
    try:
        data = request.get_json() or {}
        background = data.get('background', True)

        result = run_task_manager_command([
            'execute', task_id, str(background).lower()
        ])

        if result['success']:
            return api_response(
                data={'task_id': task_id, 'background': background},
                message=f'Task execution started: {task_id}'
            )
        else:
            return api_response(
                success=False,
                message=f'Failed to execute task: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error executing task {task_id}: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/list/<list_type>', methods=['GET'])
@require_auth
def list_tasks(list_type):
    """List tasks by type (active, completed, failed)"""
    try:
        if list_type not in ['active', 'completed', 'failed']:
            return api_response(
                success=False,
                message='Invalid list type. Use: active, completed, failed',
                status_code=400
            )

        result = run_task_manager_command(['list', list_type])

        if result['success']:
            try:
                tasks = json.loads(result['stdout'])
                return api_response(
                    data={'tasks': tasks, 'count': len(tasks)},
                    message=f'Retrieved {len(tasks)} {list_type} tasks'
                )
            except json.JSONDecodeError:
                return api_response(
                    data={'tasks': [], 'count': 0},
                    message=f'No {list_type} tasks found'
                )
        else:
            return api_response(
                success=False,
                message=f'Failed to list tasks: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error listing {list_type} tasks: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/status', methods=['GET'])
@require_auth
def task_status():
    """Get overall task status summary"""
    try:
        # Get active tasks
        active_result = run_task_manager_command(['list', 'active'])
        completed_result = run_task_manager_command(['list', 'completed'])
        failed_result = run_task_manager_command(['list', 'failed'])

        active_tasks = []
        completed_tasks = []
        failed_tasks = []

        if active_result['success']:
            try:
                active_tasks = json.loads(active_result['stdout'])
            except json.JSONDecodeError:
                pass

        if completed_result['success']:
            try:
                completed_tasks = json.loads(completed_result['stdout'])
            except json.JSONDecodeError:
                pass

        if failed_result['success']:
            try:
                failed_tasks = json.loads(failed_result['stdout'])
            except json.JSONDecodeError:
                pass

        # Calculate statistics
        total_tasks = len(active_tasks) + len(completed_tasks) + len(failed_tasks)
        running_tasks = len([t for t in active_tasks if t.get('status') == 'running'])
        queued_tasks = len([t for t in active_tasks if t.get('status') == 'queued'])

        status_data = {
            'summary': {
                'total_tasks': total_tasks,
                'active_tasks': len(active_tasks),
                'running_tasks': running_tasks,
                'queued_tasks': queued_tasks,
                'completed_tasks': len(completed_tasks),
                'failed_tasks': len(failed_tasks)
            },
            'active_tasks': active_tasks[:10],  # Limit to 10 for performance
            'recent_completed': completed_tasks[-5:] if completed_tasks else [],
            'recent_failed': failed_tasks[-3:] if failed_tasks else []
        }

        return api_response(
            data=status_data,
            message='Task status retrieved successfully'
        )

    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/kill/<task_id>', methods=['POST'])
@require_auth
def kill_task(task_id):
    """Terminate a running task"""
    try:
        result = run_task_manager_command(['kill', task_id])

        if result['success']:
            return api_response(
                data={'task_id': task_id},
                message=f'Termination signal sent to task: {task_id}'
            )
        else:
            return api_response(
                success=False,
                message=f'Failed to kill task: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error killing task {task_id}: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

# ═══════════════════════════════════════════════════════════════════════
# HEALTH MONITORING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@task_api.route('/health', methods=['GET'])
@require_auth
def system_health():
    """Get system health status"""
    try:
        # Collect fresh metrics
        metrics_result = run_task_manager_command(['metrics'])

        # Load health status
        health_file = os.path.join(UDOS_ROOT, 'sandbox', 'health', 'status.json')
        health_data = load_json_file(health_file)

        # Load current metrics
        metrics_file = os.path.join(UDOS_ROOT, 'sandbox', 'metrics', 'current.json')
        metrics_data = load_json_file(metrics_file)

        if health_data and metrics_data:
            response_data = {
                'health_status': health_data,
                'system_metrics': metrics_data,
                'last_updated': health_data.get('timestamp'),
                'daemon_status': get_daemon_status()
            }

            return api_response(
                data=response_data,
                message='System health retrieved successfully'
            )
        else:
            return api_response(
                success=False,
                message='Health data not available',
                status_code=503
            )

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/health/daemon/start', methods=['POST'])
@require_auth
def start_health_daemon():
    """Start the health monitoring daemon"""
    try:
        result = run_health_daemon_command(['start'])

        if result['success']:
            return api_response(
                message='Health monitoring daemon started'
            )
        else:
            return api_response(
                success=False,
                message=f'Failed to start daemon: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error starting health daemon: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/health/daemon/stop', methods=['POST'])
@require_auth
def stop_health_daemon():
    """Stop the health monitoring daemon"""
    try:
        result = run_health_daemon_command(['stop'])

        if result['success']:
            return api_response(
                message='Health monitoring daemon stopped'
            )
        else:
            return api_response(
                success=False,
                message=f'Failed to stop daemon: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error stopping health daemon: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/health/daemon/status', methods=['GET'])
@require_auth
def get_daemon_status():
    """Get health daemon status"""
    try:
        result = run_health_daemon_command(['status'])

        # Parse daemon status
        is_running = 'is running' in result['stdout']
        status_info = {
            'running': is_running,
            'message': result['stdout'],
            'last_check': datetime.now(timezone.utc).isoformat()
        }

        if is_running:
            # Extract PID if available
            import re
            pid_match = re.search(r'PID: (\d+)', result['stdout'])
            if pid_match:
                status_info['pid'] = int(pid_match.group(1))

        return api_response(
            data=status_info,
            message='Daemon status retrieved successfully'
        )

    except Exception as e:
        logger.error(f"Error getting daemon status: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

# ═══════════════════════════════════════════════════════════════════════
# SCHEDULING ENDPOINTS (FUTURE CRON FUNCTIONALITY)
# ═══════════════════════════════════════════════════════════════════════

@task_api.route('/schedule', methods=['POST'])
@require_auth
def create_scheduled_task():
    """Create a scheduled task (cron-like functionality)"""
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'command' not in data or 'schedule' not in data:
            return api_response(
                success=False,
                message='Missing required fields: name, command, schedule',
                status_code=400
            )

        task_name = data['name']
        task_command = data['command']
        schedule = data['schedule']

        result = run_task_manager_command([
            'schedule', task_name, task_command, schedule
        ])

        if result['success']:
            # Extract schedule ID from output
            schedule_id = result['stdout'].split('Schedule: ')[-1].rstrip(')')
            return api_response(
                data={'schedule_id': schedule_id},
                message=f'Scheduled task created successfully: {task_name}'
            )
        else:
            return api_response(
                success=False,
                message=f'Failed to create scheduled task: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error creating scheduled task: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/schedules', methods=['GET'])
@require_auth
def list_scheduled_tasks():
    """List all scheduled tasks"""
    try:
        cron_dir = os.path.join(UDOS_ROOT, 'sandbox', 'cron', 'jobs')
        schedules = []

        if os.path.exists(cron_dir):
            for filename in os.listdir(cron_dir):
                if filename.endswith('.json'):
                    schedule_file = os.path.join(cron_dir, filename)
                    schedule_data = load_json_file(schedule_file)
                    if schedule_data:
                        schedules.append(schedule_data)

        return api_response(
            data={'schedules': schedules, 'count': len(schedules)},
            message=f'Retrieved {len(schedules)} scheduled tasks'
        )

    except Exception as e:
        logger.error(f"Error listing scheduled tasks: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

# ═══════════════════════════════════════════════════════════════════════
# METRICS AND REPORTING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@task_api.route('/metrics', methods=['GET'])
@require_auth
def get_system_metrics():
    """Get current system metrics"""
    try:
        # Collect fresh metrics
        result = run_task_manager_command(['metrics'])

        # Load current metrics
        metrics_file = os.path.join(UDOS_ROOT, 'sandbox', 'metrics', 'current.json')
        metrics_data = load_json_file(metrics_file)

        if metrics_data:
            return api_response(
                data=metrics_data,
                message='System metrics retrieved successfully'
            )
        else:
            return api_response(
                success=False,
                message='Metrics data not available',
                status_code=503
            )

    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/metrics/history', methods=['GET'])
@require_auth
def get_metrics_history():
    """Get historical metrics data"""
    try:
        metrics_dir = os.path.join(UDOS_ROOT, 'sandbox', 'metrics')
        history = []

        if os.path.exists(metrics_dir):
            # Get last 24 hours of metrics files
            now = time.time()
            day_ago = now - (24 * 60 * 60)

            for filename in os.listdir(metrics_dir):
                if filename.endswith('.json') and filename != 'current.json':
                    filepath = os.path.join(metrics_dir, filename)
                    file_mtime = os.path.getmtime(filepath)

                    if file_mtime >= day_ago:
                        metrics_data = load_json_file(filepath)
                        if metrics_data:
                            history.append(metrics_data)

            # Sort by timestamp
            history.sort(key=lambda x: x.get('timestamp', ''))

        return api_response(
            data={'metrics_history': history, 'count': len(history)},
            message=f'Retrieved {len(history)} historical metrics entries'
        )

    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

@task_api.route('/cleanup', methods=['POST'])
@require_auth
def cleanup_tasks():
    """Clean up old tasks and logs"""
    try:
        result = run_task_manager_command(['cleanup'])

        if result['success']:
            return api_response(
                message='Cleanup completed successfully'
            )
        else:
            return api_response(
                success=False,
                message=f'Cleanup failed: {result["stderr"]}',
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD DATA ENDPOINT
# ═══════════════════════════════════════════════════════════════════════

@task_api.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        # Get task status
        task_status_result = task_status()
        task_data = task_status_result[0].get_json()['data'] if task_status_result[0].status_code == 200 else {}

        # Get health status
        health_result = system_health()
        health_data = health_result[0].get_json()['data'] if health_result[0].status_code == 200 else {}

        # Get scheduled tasks
        schedules_result = list_scheduled_tasks()
        schedules_data = schedules_result[0].get_json()['data'] if schedules_result[0].status_code == 200 else {}

        dashboard_data = {
            'tasks': task_data,
            'health': health_data,
            'schedules': schedules_data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        return api_response(
            data=dashboard_data,
            message='Dashboard data retrieved successfully'
        )

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return api_response(
            success=False,
            message=f'Internal error: {str(e)}',
            status_code=500
        )

# ═══════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════

@task_api.errorhandler(404)
def not_found(error):
    return api_response(
        success=False,
        message='Endpoint not found',
        status_code=404
    )

@task_api.errorhandler(405)
def method_not_allowed(error):
    return api_response(
        success=False,
        message='Method not allowed',
        status_code=405
    )

@task_api.errorhandler(500)
def internal_error(error):
    return api_response(
        success=False,
        message='Internal server error',
        status_code=500
    )

# Initialize task manager on import
def initialize_task_manager():
    """Initialize task manager if not already done"""
    try:
        result = run_task_manager_command(['init'])
        if result['success']:
            logger.info("Task manager initialized successfully")
        else:
            logger.warning(f"Task manager initialization warning: {result['stderr']}")
    except Exception as e:
        logger.error(f"Failed to initialize task manager: {e}")

# Initialize when module is imported
initialize_task_manager()
