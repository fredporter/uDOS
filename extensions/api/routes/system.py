"""
System Routes Blueprint
=======================

Core system endpoints: health, status, version, config.
~15 endpoints for system management.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

from ..services import execute_command, init_udos_systems, UDOS_AVAILABLE

# Create blueprint
system_bp = Blueprint("system", __name__, url_prefix="/api")

# Track active viewport
active_viewport = {
    "type": None,
    "connected_at": None,
    "last_activity": None,
    "dimensions": {"width": 0, "height": 0, "lines": 0, "columns": 0},
}


# ============================================================================
# CORE ENDPOINTS
# ============================================================================


@system_bp.route("/health")
@system_bp.route("/status")  # Alias for compatibility
def health():
    """Health check endpoint with active viewport info."""
    from ..services.executor import _instances

    return jsonify(
        {
            "status": "healthy",
            "udos_available": UDOS_AVAILABLE,
            "systems_initialized": _instances["parser"] is not None,
            "active_viewport": active_viewport["type"],
            "viewport_dimensions": (
                active_viewport["dimensions"] if active_viewport["type"] else None
            ),
            "timestamp": datetime.now().isoformat(),
        }
    )


@system_bp.route("/command", methods=["POST"])
@system_bp.route("/execute", methods=["POST"])  # Frontend command endpoint
def execute_command_api():
    """Execute any uDOS command."""
    data = request.get_json()
    command = data.get("command", "")

    if not command:
        return jsonify({"status": "error", "message": "No command provided"}), 400

    result = execute_command(command)

    # Return standardized command response format (success, output, error)
    if result.get("status") == "success":
        return jsonify(
            {"success": True, "output": result.get("output", ""), "error": None}
        )
    else:
        return jsonify(
            {
                "success": False,
                "output": "",
                "error": result.get("message", "Unknown error"),
            }
        )


# ============================================================================
# SYSTEM COMMANDS
# ============================================================================


@system_bp.route("/system/help")
def system_help():
    """Get help information."""
    return jsonify(execute_command("HELP"))


@system_bp.route("/system/status")
def system_status():
    """Get system status."""
    return jsonify(execute_command("STATUS"))


@system_bp.route("/system/config/list")
def config_list():
    """List configuration settings."""
    return jsonify(execute_command("CONFIG LIST"))


@system_bp.route("/system/config/get/<key>")
def config_get(key):
    """Get specific config value."""
    return jsonify(execute_command(f"CONFIG GET {key}"))


@system_bp.route("/system/config/set", methods=["POST"])
def config_set():
    """Set configuration value."""
    data = request.get_json()
    key = data.get("key")
    value = data.get("value")
    return jsonify(execute_command(f"CONFIG SET {key} {value}"))


@system_bp.route("/system/repair")
def system_repair():
    """Run system repair."""
    return jsonify(execute_command("REPAIR"))


@system_bp.route("/system/reboot", methods=["POST"])
def system_reboot():
    """Reboot uDOS system."""
    return jsonify(execute_command("REBOOT"))


@system_bp.route("/system/version")
def system_version():
    """Get uDOS version info."""
    import json
    import os
    from pathlib import Path

    try:
        versions = {}
        root = Path(__file__).parent.parent.parent.parent
        
        # Read component versions from version.json files
        for component in ['core', 'api', 'wizard', 'knowledge']:
            version_file = root / component / 'version.json'
            if version_file.exists():
                with open(version_file) as f:
                    data = json.load(f)
                    versions[component] = data.get('display', 'unknown')
        
        return jsonify(
            {
                "status": "success",
                "components": versions,
            }
        )
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": str(e),
                "api": "v1.1.0.0",
            }
        )


@system_bp.route("/system/usage")
def system_usage():
    """Get command usage statistics."""
    return jsonify(execute_command("USAGE"))


@system_bp.route("/system/debug", methods=["POST"])
def system_debug():
    """Toggle debug mode."""
    data = request.get_json()
    mode = data.get("mode", "on")
    return jsonify(execute_command(f"DEBUG {mode}"))


# ============================================================================
# ASSIST COMMANDS
# ============================================================================


@system_bp.route("/assist/ask", methods=["POST"])
def assist_ask():
    """Ask AI assistant."""
    data = request.get_json()
    question = data.get("question")
    return jsonify(execute_command(f"OK {question}"))


@system_bp.route("/assist/explain", methods=["POST"])
def assist_explain():
    """Get explanation."""
    data = request.get_json()
    topic = data.get("topic")
    return jsonify(execute_command(f"EXPLAIN {topic}"))


@system_bp.route("/assist/debug", methods=["POST"])
def assist_debug():
    """Debug assistance."""
    data = request.get_json()
    error = data.get("error")
    return jsonify(execute_command(f"DEBUG {error}"))


@system_bp.route("/assist/suggest")
def assist_suggest():
    """Get command suggestions."""
    context = request.args.get("context", "")
    return jsonify(execute_command(f"SUGGEST {context}"))


@system_bp.route("/assist/history")
def assist_history():
    """Get command history."""
    limit = request.args.get("limit", "20")
    return jsonify(execute_command(f"HISTORY {limit}"))


@system_bp.route("/assist/mode", methods=["POST"])
def assist_mode():
    """Toggle assist mode."""
    data = request.get_json()
    mode = data.get("mode", "on")
    return jsonify(execute_command(f"ASSIST {mode}"))
