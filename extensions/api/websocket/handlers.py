"""
WebSocket Handlers
==================

Socket.IO event handlers for real-time communication.
"""

from flask import request
from flask_socketio import emit
import threading
import time
from datetime import datetime
from typing import Set

# Update subscribers
update_subscribers: Set[str] = set()
last_system_state = {}
update_thread = None
update_thread_running = False


def get_services():
    """Get services from executor."""
    from ..services.executor import _services, _instances

    return _services, _instances


def get_streaming_service():
    """Get streaming service."""
    services, _ = get_services()
    return services.get("streaming")


def get_predictor_service():
    """Get predictor service."""
    services, _ = get_services()
    return services.get("predictor")


def get_debug_panel_service():
    """Get debug panel service."""
    services, _ = get_services()
    return services.get("debug_panel")


def get_file_picker_service():
    """Get file picker service."""
    services, _ = get_services()
    return services.get("file_picker")


def get_menu_service():
    """Get menu service."""
    services, _ = get_services()
    return services.get("menu")


def get_user_manager():
    """Get user manager."""
    _, instances = get_services()
    return instances.get("user_manager")


def get_workspace_manager():
    """Get workspace manager."""
    _, instances = get_services()
    return instances.get("workspace_manager")


def get_system_state():
    """Get current system state for change detection."""
    from ..services import UDOS_AVAILABLE

    try:
        state = {
            "timestamp": datetime.now().isoformat(),
            "xp": 0,
            "level": 1,
            "health": 100,
            "energy": 100,
            "hydration": 100,
            "file_count": 0,
            "position": {"cell": "A1", "latitude": 0, "longitude": 0},
        }

        if UDOS_AVAILABLE:
            user_manager = get_user_manager()
            workspace_manager = get_workspace_manager()

            if user_manager:
                user_data = user_manager.get_user_data()
                if user_data and "xp" in user_data:
                    state["xp"] = user_data["xp"].get("total", 0)
                    state["level"] = user_data["xp"].get("level", 1)

                if "survival" in user_data:
                    survival = user_data["survival"]
                    state["health"] = survival.get("health", 100)
                    state["energy"] = survival.get("energy", 100)
                    state["hydration"] = survival.get("hydration", 100)

            if workspace_manager:
                files = workspace_manager.list_files()
                state["file_count"] = len(files) if files else 0

        return state
    except Exception as e:
        print(f"Error getting system state: {e}")
        return {}


def detect_changes(old_state, new_state):
    """Detect what changed between states."""
    changes = {}

    for key in ["xp", "level", "health", "energy", "hydration", "file_count"]:
        if key in old_state and key in new_state:
            if old_state[key] != new_state[key]:
                changes[key] = {
                    "old": old_state[key],
                    "new": new_state[key],
                    "delta": (
                        new_state[key] - old_state[key]
                        if isinstance(new_state[key], (int, float))
                        else None
                    ),
                }

    if "position" in old_state and "position" in new_state:
        if old_state["position"] != new_state["position"]:
            changes["position"] = {
                "old": old_state["position"],
                "new": new_state["position"],
            }

    return changes


def broadcast_updates(socketio):
    """Background thread to broadcast system updates."""
    global last_system_state, update_thread_running

    print("📡 Real-time update broadcaster started")

    while update_thread_running:
        try:
            current_state = get_system_state()

            if last_system_state:
                changes = detect_changes(last_system_state, current_state)

                if changes and update_subscribers:
                    socketio.emit(
                        "system_update",
                        {
                            "timestamp": current_state["timestamp"],
                            "changes": changes,
                            "state": current_state,
                        },
                    )
                    print(
                        f"📤 Broadcast update: {len(changes)} changes to {len(update_subscribers)} clients"
                    )

            last_system_state = current_state.copy()
            time.sleep(5)

        except Exception as e:
            print(f"Error in broadcast_updates: {e}")
            time.sleep(5)

    print("📡 Real-time update broadcaster stopped")


def start_update_broadcaster(socketio):
    """Start the background update broadcaster thread."""
    global update_thread, update_thread_running

    if update_thread is None or not update_thread.is_alive():
        update_thread_running = True
        update_thread = threading.Thread(
            target=broadcast_updates, args=(socketio,), daemon=True
        )
        update_thread.start()
        print("✅ Update broadcaster thread started")


def stop_update_broadcaster():
    """Stop the background update broadcaster thread."""
    global update_thread_running
    update_thread_running = False
    print("🛑 Stopping update broadcaster...")


def register_socketio_handlers(socketio):
    """Register all Socket.IO event handlers."""
    from ..services import execute_command, init_udos_systems

    @socketio.on("connect")
    def handle_connect():
        """Handle client connection."""
        init_udos_systems()
        emit("status", {"message": "Connected to uDOS API"})

        streaming_service = get_streaming_service()
        if streaming_service:
            streaming_service.connect(request.sid)

        if not update_thread_running:
            start_update_broadcaster(socketio)

    @socketio.on("disconnect")
    def handle_disconnect():
        """Handle client disconnection."""
        streaming_service = get_streaming_service()
        if streaming_service:
            streaming_service.disconnect(request.sid)

        if request.sid in update_subscribers:
            update_subscribers.remove(request.sid)
            print(
                f"Client disconnected: {request.sid} ({len(update_subscribers)} remaining)"
            )

        if len(update_subscribers) == 0 and update_thread_running:
            stop_update_broadcaster()

    @socketio.on("execute_command")
    def handle_command(data):
        """Execute command via WebSocket."""
        command = data.get("command", "")
        correlation_id = data.get("correlation_id")

        streaming_service = get_streaming_service()
        if streaming_service:
            streaming_service.emit_command_start(command, correlation_id)

        result = execute_command(command)

        if streaming_service:
            streaming_service.emit_command_complete(result, correlation_id)

        emit("command_result", result)

    @socketio.on("subscribe_updates")
    def handle_subscribe(data):
        """Subscribe to real-time updates."""
        types = data.get("types", ["all"])
        filters = data.get("filters", {})

        update_subscribers.add(request.sid)

        streaming_service = get_streaming_service()
        if streaming_service:
            streaming_service.subscribe(
                request.sid, types if types != ["all"] else "all", filters
            )

        current_state = get_system_state()
        emit(
            "subscribed",
            {
                "status": "success",
                "types": types,
                "initial_state": current_state,
            },
        )

        print(f"Client subscribed: {request.sid} (total: {len(update_subscribers)})")

        if not update_thread_running:
            start_update_broadcaster(socketio)

    @socketio.on("ping")
    def handle_ping(timestamp):
        """Handle latency measurement ping."""
        emit("pong", timestamp)

    @socketio.on("predictor_input")
    def handle_predictor_input(data):
        """Handle predictor input for autocomplete."""
        predictor_service = get_predictor_service()
        if not predictor_service:
            emit("predictor_error", {"error": "Predictor service not available"})
            return

        input_text = data.get("input", "")
        max_suggestions = data.get("max", 5)
        correlation_id = data.get("correlation_id")

        predictions = predictor_service.predict(input_text, max_suggestions)

        result = {
            "input": input_text,
            "predictions": [p.to_dict() for p in predictions],
            "correlation_id": correlation_id,
        }

        emit("predictor_suggest", result)

        streaming_service = get_streaming_service()
        if streaming_service:
            streaming_service.emit_predictor_suggestions(
                input_text, [p.to_dict() for p in predictions], correlation_id
            )

    @socketio.on("predictor_highlight")
    def handle_predictor_highlight(data):
        """Tokenize and highlight command input."""
        predictor_service = get_predictor_service()
        if not predictor_service:
            emit("predictor_error", {"error": "Predictor service not available"})
            return

        input_text = data.get("input", "")
        correlation_id = data.get("correlation_id")

        tokens = predictor_service.tokenize(input_text)

        emit(
            "predictor_tokens",
            {
                "input": input_text,
                "tokens": [t.to_dict() for t in tokens],
                "correlation_id": correlation_id,
            },
        )

    @socketio.on("debug_subscribe")
    def handle_debug_subscribe(data):
        """Subscribe to debug panel logs."""
        debug_panel_service = get_debug_panel_service()
        if not debug_panel_service:
            emit("debug_error", {"error": "Debug panel service not available"})
            return

        sources = data.get("sources", ["all"])
        min_level = data.get("min_level", "DEBUG")
        correlation_id = data.get("correlation_id")

        streaming_service = get_streaming_service()

        def log_callback(entry):
            entry_dict = entry.to_dict()
            emit("debug_log", entry_dict)
            if streaming_service:
                streaming_service.emit_debug_log(entry_dict, correlation_id)

        debug_panel_service.add_streaming_callback(f"ws_{request.sid}", log_callback)

        emit(
            "debug_subscribed",
            {
                "sources": sources,
                "min_level": min_level,
                "correlation_id": correlation_id,
            },
        )

    @socketio.on("debug_unsubscribe")
    def handle_debug_unsubscribe(data):
        """Unsubscribe from debug panel logs."""
        debug_panel_service = get_debug_panel_service()
        if debug_panel_service:
            debug_panel_service.remove_streaming_callback(f"ws_{request.sid}")

        emit("debug_unsubscribed", {"status": "ok"})

    @socketio.on("files_navigate")
    def handle_files_navigate(data):
        """Navigate file picker."""
        file_picker_service = get_file_picker_service()
        if not file_picker_service:
            emit("files_error", {"error": "File picker service not available"})
            return

        path = data.get("path", "")
        workspace = data.get("workspace")
        correlation_id = data.get("correlation_id")

        if workspace:
            file_picker_service.set_workspace(workspace)

        file_picker_service.navigate_to(path)
        entries = file_picker_service.list_entries()

        result = {
            "path": str(file_picker_service.current_path),
            "workspace": (
                file_picker_service.current_workspace.value
                if file_picker_service.current_workspace
                else None
            ),
            "entries": [e.to_dict() for e in entries],
            "correlation_id": correlation_id,
        }

        emit("files_list", result)

        streaming_service = get_streaming_service()
        if streaming_service:
            streaming_service.emit_files_list(
                result["path"],
                [e.to_dict() for e in entries if not e.is_directory],
                [e.to_dict() for e in entries if e.is_directory],
                correlation_id,
            )

    @socketio.on("files_search")
    def handle_files_search(data):
        """Search files in current workspace."""
        file_picker_service = get_file_picker_service()
        if not file_picker_service:
            emit("files_error", {"error": "File picker service not available"})
            return

        query = data.get("query", "")
        correlation_id = data.get("correlation_id")

        results = file_picker_service.search(query)

        emit(
            "files_search_results",
            {
                "query": query,
                "results": [e.to_dict() for e in results],
                "correlation_id": correlation_id,
            },
        )

    @socketio.on("menu_get")
    def handle_menu_get(data):
        """Get menu definition."""
        menu_service = get_menu_service()
        if not menu_service:
            emit("menu_error", {"error": "Menu service not available"})
            return

        menu_name = data.get("menu", "file")
        format_type = data.get("format", "html")
        correlation_id = data.get("correlation_id")

        menu_def = menu_service.get_menu(menu_name)

        if menu_def:
            if format_type == "html":
                content = menu_service.render_menu_html(menu_name)
            else:
                content = menu_def.to_dict()

            emit(
                "menu_definition",
                {
                    "menu": menu_name,
                    "format": format_type,
                    "content": content,
                    "correlation_id": correlation_id,
                },
            )
        else:
            emit("menu_error", {"error": f"Menu not found: {menu_name}"})

    @socketio.on("menu_action")
    def handle_menu_action(data):
        """Execute menu action."""
        action_id = data.get("action")
        metadata = data.get("metadata", {})
        correlation_id = data.get("correlation_id")

        streaming_service = get_streaming_service()
        if streaming_service:
            streaming_service.emit_menu_action(action_id, metadata, correlation_id)

        if action_id.startswith("cmd:"):
            command = action_id[4:]
            result = execute_command(command)
            emit(
                "menu_action_result",
                {
                    "action": action_id,
                    "result": result,
                    "correlation_id": correlation_id,
                },
            )
        else:
            emit(
                "menu_action_ack",
                {
                    "action": action_id,
                    "metadata": metadata,
                    "correlation_id": correlation_id,
                },
            )
