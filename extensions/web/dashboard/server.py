"""
uDOS Dashboard - Flask Server
v1.1.14 - Real-time retro dashboard with NES.css styling

Features:
- Mission progress tracking
- Checklist completion meters
- Workflow phase indicators
- XP and achievement display
- 5-second auto-refresh
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
PORT = 5050
HOST = '127.0.0.1'
REFRESH_INTERVAL = 5  # seconds


def load_json_safe(filepath: Path, default=None):
    """Safely load JSON file with fallback."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default or {}


def get_mission_status():
    """Get current mission status from workflow state."""
    state_file = Path("memory/workflows/state/current.json")
    state = load_json_safe(state_file, {
        "current_mission": None,
        "status": "IDLE",
        "missions_total": 0,
        "missions_completed": 0,
        "missions_failed": 0
    })
    
    missions = []
    if state.get('current_mission'):
        mission_file = Path(f"memory/workflows/missions/{state['current_mission']}.json")
        mission_data = load_json_safe(mission_file)
        if mission_data:
            # Calculate progress
            total_steps = sum(len(move.get('steps', [])) for move in mission_data.get('moves', []))
            completed_steps = sum(
                1 for move in mission_data.get('moves', [])
                for step in move.get('steps', [])
                if step.get('status') == 'completed'
            )
            progress_pct = int((completed_steps / total_steps * 100)) if total_steps > 0 else 0
            
            missions.append({
                'id': mission_data.get('id'),
                'title': mission_data.get('title'),
                'status': mission_data.get('status', 'unknown'),
                'priority': mission_data.get('priority', 'medium'),
                'progress': progress_pct,
                'completed_steps': completed_steps,
                'total_steps': total_steps
            })
    
    return {
        'active_missions': missions,
        'total_missions': state.get('missions_total', 0),
        'completed_missions': state.get('missions_completed', 0),
        'failed_missions': state.get('missions_failed', 0)
    }


def get_checklist_status():
    """Get checklist completion status."""
    state_file = Path("memory/system/user/checklist_state.json")
    state = load_json_safe(state_file, {"checklists": {}})
    
    checklists = []
    for checklist_id, checklist_data in state.get('checklists', {}).items():
        completed = len(checklist_data.get('completed_items', []))
        total = checklist_data.get('total_items', 1)
        progress_pct = int((completed / total * 100)) if total > 0 else 0
        
        checklists.append({
            'id': checklist_id,
            'title': checklist_id.replace('-', ' ').title(),
            'completed_items': completed,
            'total_items': total,
            'progress': progress_pct
        })
    
    return {
        'active_checklists': checklists,
        'total_completed': sum(c['completed_items'] for c in checklists),
        'total_items': sum(c['total_items'] for c in checklists)
    }


def get_workflow_status():
    """Get workflow execution status."""
    state_file = Path("memory/workflows/state/current.json")
    state = load_json_safe(state_file, {
        "current_mission": None,
        "status": "IDLE"
    })
    
    return {
        'current_workflow': state.get('current_mission'),
        'phase': state.get('status', 'IDLE'),
        'checkpoints_saved': state.get('checkpoints_saved', 0),
        'perfect_streak': state.get('perfect_streak', 0)
    }


def get_xp_status():
    """Get XP and achievement status."""
    state_file = Path("memory/workflows/state/current.json")
    state = load_json_safe(state_file, {
        "total_xp_earned": 0,
        "achievements_unlocked": []
    })
    
    return {
        'total_xp': state.get('total_xp_earned', 0),
        'achievements': state.get('achievements_unlocked', []),
        'perfect_streak': state.get('perfect_streak', 0)
    }


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html', refresh_interval=REFRESH_INTERVAL)


@app.route('/api/status')
def api_status():
    """API endpoint for real-time status updates."""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'missions': get_mission_status(),
        'checklists': get_checklist_status(),
        'workflow': get_workflow_status(),
        'xp': get_xp_status()
    })


@app.route('/api/missions')
def api_missions():
    """Get detailed mission data."""
    return jsonify(get_mission_status())


@app.route('/api/checklists')
def api_checklists():
    """Get detailed checklist data."""
    return jsonify(get_checklist_status())


@app.route('/api/workflow')
def api_workflow():
    """Get workflow execution data."""
    return jsonify(get_workflow_status())


@app.route('/api/xp')
def api_xp():
    """Get XP and achievements."""
    return jsonify(get_xp_status())


def run_dashboard(port=PORT, host=HOST, debug=False):
    """Run the dashboard server."""
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                     🎮 uDOS DASHBOARD                             ║
╠═══════════════════════════════════════════════════════════════════╣
║  Dashboard running at http://{host}:{port}                 ║
║  Press Ctrl+C to stop                                             ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()
