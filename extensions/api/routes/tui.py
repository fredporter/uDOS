"""
TUI Routes Blueprint
====================

TUI integration endpoints for Tauri app: viewport, predictor, pager, keypad, browser.
~15 endpoints for TUI-Tauri bridge.
"""

from flask import Blueprint, jsonify, request, g
from datetime import datetime
import logging

from ..services import execute_command, init_udos_systems

api_logger = logging.getLogger("uDOS.API")

# Create blueprint
tui_bp = Blueprint("tui", __name__, url_prefix="/api")

# Track active viewport
active_viewport = {
    "type": None,
    "connected_at": None,
    "last_activity": None,
    "dimensions": {"width": 0, "height": 0, "lines": 0, "columns": 0},
}


def get_tui_controller():
    """Get TUI controller from services."""
    from ..services.executor import _instances

    return _instances.get("tui_controller")


# ============================================================================
# VIEWPORT MANAGEMENT
# ============================================================================


@tui_bp.route("/viewport/register", methods=["POST"])
def register_viewport():
    """Register the active viewport (single interface at a time)."""
    try:
        data = request.json
        viewport_type = data.get("type", "unknown")
        dimensions = data.get("dimensions", {})

        active_viewport["type"] = viewport_type
        active_viewport["connected_at"] = datetime.now().isoformat()
        active_viewport["last_activity"] = datetime.now().isoformat()
        active_viewport["dimensions"] = dimensions

        api_logger.info(
            f"Viewport registered: {viewport_type} - "
            f'{dimensions.get("columns")}x{dimensions.get("lines")}'
        )

        return jsonify(
            {
                "status": "success",
                "message": f"{viewport_type.title()} viewport registered",
                "viewport": active_viewport,
            }
        )

    except Exception as e:
        api_logger.error(f"Viewport registration error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@tui_bp.route("/viewport/status")
def viewport_status():
    """Get current active viewport information."""
    try:
        return jsonify(
            {
                "status": "success",
                "active": active_viewport["type"] is not None,
                **active_viewport,
            }
        )
    except Exception as e:
        api_logger.error(f"Viewport status error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# TUI STATUS
# ============================================================================


@tui_bp.route("/tui/status")
def tui_status():
    """Get TUI component status and configuration."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "TUI not initialized",
                        "tui_initialized": False,
                    }
                ),
                503,
            )

        status = tui_controller.get_status()

        # Auto-discover TUI capabilities
        capabilities = []
        for attr in dir(tui_controller):
            if not attr.startswith("_") and callable(getattr(tui_controller, attr)):
                if any(
                    prefix in attr
                    for prefix in ["get_", "set_", "handle_", "open_", "close_", "is_"]
                ):
                    capabilities.append(attr)

        return jsonify(
            {
                "status": "success",
                "tui_initialized": True,
                "capabilities": capabilities,
                **status,
            }
        )

    except Exception as e:
        api_logger.error(f"TUI status error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# PREDICTOR
# ============================================================================


@tui_bp.route("/tui/predictor/suggest")
def tui_predictor_suggest():
    """Get command predictions for autocomplete."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        partial = request.args.get("partial", "")
        max_results = int(request.args.get("max", 10))

        predictions = tui_controller.get_predictions(partial, max_results)
        api_logger.debug(
            f'Predictor: partial="{partial}" returned {len(predictions)} predictions'
        )

        prediction_dicts = [
            {
                "text": p.text,
                "confidence": p.confidence,
                "source": p.source,
                "description": p.description,
                "syntax": p.syntax,
                "category": p.category,
            }
            for p in predictions
        ]

        return jsonify(
            {
                "status": "success",
                "partial": partial,
                "count": len(prediction_dicts),
                "predictions": prediction_dicts,
            }
        )

    except Exception as e:
        api_logger.error(f"Predictor suggest error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# PAGER
# ============================================================================


@tui_bp.route("/tui/pager/set_content", methods=["POST"])
def tui_pager_set_content():
    """Set content for pager display."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        data = request.get_json()
        lines = data.get("lines", [])

        result = tui_controller.set_pager_content(lines)

        return jsonify({"status": "success", "lines_set": len(lines), **result})

    except Exception as e:
        api_logger.error(f"Pager set content error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@tui_bp.route("/tui/pager/content")
def tui_pager_content():
    """Get current pager viewport content."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        content = tui_controller.get_pager_content()

        return jsonify({"status": "success", **content})

    except Exception as e:
        api_logger.error(f"Pager get content error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@tui_bp.route("/tui/pager/scroll", methods=["POST"])
def tui_pager_scroll():
    """Scroll pager viewport."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        data = request.get_json()
        direction = data.get("direction", "down")
        amount = data.get("amount", 1)

        result = tui_controller.scroll_pager(direction, amount)

        return jsonify({"status": "success", **result})

    except Exception as e:
        api_logger.error(f"Pager scroll error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# KEYPAD
# ============================================================================


@tui_bp.route("/tui/keypad/handle", methods=["POST"])
def tui_keypad_handle():
    """Process keypad input."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        data = request.get_json()
        key = data.get("key")

        if not key:
            return (
                jsonify({"status": "error", "message": "Key parameter required"}),
                400,
            )

        result = tui_controller.handle_keypad(key)

        return jsonify({"status": "success", **result})

    except Exception as e:
        api_logger.error(f"Keypad handle error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@tui_bp.route("/tui/keypad/toggle", methods=["POST"])
def tui_keypad_toggle():
    """Toggle keypad navigation on/off."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        data = request.get_json()
        enabled = data.get("enabled")

        if enabled is None:
            enabled = tui_controller.toggle_keypad()

        tui_controller.set_keypad_enabled(enabled)

        return jsonify({"status": "success", "keypad_enabled": enabled})

    except Exception as e:
        api_logger.error(f"Keypad toggle error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# BROWSER
# ============================================================================


@tui_bp.route("/tui/browser/list")
def tui_browser_list():
    """List files in browser workspace."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        workspace = request.args.get("workspace", "knowledge")
        path = request.args.get("path", "/")

        items = tui_controller.browser_list(workspace, path)

        return jsonify(
            {
                "status": "success",
                "workspace": workspace,
                "path": path,
                "items": items,
            }
        )

    except Exception as e:
        api_logger.error(f"Browser list error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@tui_bp.route("/tui/browser/navigate", methods=["POST"])
def tui_browser_navigate():
    """Navigate in file browser."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        data = request.get_json()
        workspace = data.get("workspace", "knowledge")
        path = data.get("path", "/")
        action = data.get("action", "enter")

        result = tui_controller.browser_navigate(workspace, path, action)

        return jsonify({"status": "success", "action": action, **result})

    except Exception as e:
        api_logger.error(f"Browser navigate error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# GENERIC INVOKE
# ============================================================================


@tui_bp.route("/tui/invoke", methods=["POST"])
def tui_invoke():
    """Generic TUI method invocation (future-proof)."""
    try:
        tui_controller = get_tui_controller()
        if not init_udos_systems() or tui_controller is None:
            return jsonify({"status": "error", "message": "TUI not initialized"}), 503

        data = request.get_json()
        method_name = data.get("method")
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})

        if not method_name:
            return jsonify({"status": "error", "message": "Method name required"}), 400

        # Security: Only allow public methods
        if method_name.startswith("_"):
            return (
                jsonify(
                    {"status": "error", "message": "Private methods not accessible"}
                ),
                403,
            )

        if not hasattr(tui_controller, method_name):
            return (
                jsonify(
                    {"status": "error", "message": f"Method '{method_name}' not found"}
                ),
                404,
            )

        method = getattr(tui_controller, method_name)

        if not callable(method):
            return (
                jsonify(
                    {"status": "error", "message": f"'{method_name}' is not a method"}
                ),
                400,
            )

        result = method(*args, **kwargs)

        api_logger.info(f"TUI method invoked: {method_name}")

        return jsonify({"status": "success", "method": method_name, "result": result})

    except TypeError as e:
        api_logger.error(f"TUI invoke argument error: {e}", exc_info=True)
        return (
            jsonify({"status": "error", "message": f"Invalid arguments: {str(e)}"}),
            400,
        )
    except Exception as e:
        api_logger.error(f"TUI invoke error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
