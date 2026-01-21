"""
Feed Routes Blueprint
======================

Feed endpoints for streaming content to the uCode Markdown App.
Supports knowledge, logs, notifications, and other feed sources.
"""

from flask import Blueprint, jsonify, request
import logging
import os
from pathlib import Path
from datetime import datetime
import uuid

api_logger = logging.getLogger("uDOS.API")

# Create blueprint
feed_bp = Blueprint("feed", __name__, url_prefix="/api/feed")


# ============================================================================
# KNOWLEDGE FEED
# ============================================================================


@feed_bp.route("/knowledge")
def api_knowledge_feed():
    """
    Get knowledge articles as feed items.

    Query params:
    - category: Filter by category (survival, tech, medical, etc.)
    - limit: Max items (default 20)
    """
    category = request.args.get("category")
    limit = int(request.args.get("limit", 20))

    knowledge_root = Path(os.environ.get("UDOS_ROOT", ".")) / "knowledge"

    if not knowledge_root.exists():
        return jsonify({"items": [], "error": "Knowledge bank not found"})

    items = []

    # Determine search paths
    if category:
        search_paths = [knowledge_root / category]
    else:
        # All top-level categories
        search_paths = [
            p
            for p in knowledge_root.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Find markdown files
        for md_file in search_path.rglob("*.md"):
            if len(items) >= limit:
                break

            try:
                content = md_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                # Extract title from first heading
                title = md_file.stem
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                # Get first paragraph as preview
                preview = ""
                in_content = False
                for line in lines:
                    if line.startswith("# "):
                        in_content = True
                        continue
                    if in_content and line.strip() and not line.startswith("#"):
                        preview = line.strip()[:200]
                        break

                # Get file modification time
                mtime = md_file.stat().st_mtime
                timestamp = datetime.fromtimestamp(mtime).isoformat()

                items.append(
                    {
                        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, str(md_file))),
                        "title": title,
                        "content": preview or content[:300],
                        "fullContent": content,
                        "timestamp": timestamp,
                        "priority": "normal",
                        "metadata": {
                            "path": str(md_file.relative_to(knowledge_root)),
                            "category": search_path.name,
                            "size": len(content),
                        },
                    }
                )
            except Exception as e:
                api_logger.error(f"Error reading {md_file}: {e}")

    # Sort by modification time (newest first)
    items.sort(key=lambda x: x["timestamp"], reverse=True)

    return jsonify({"items": items[:limit], "total": len(items), "source": "knowledge"})


# ============================================================================
# LOG FEED
# ============================================================================


@feed_bp.route("/logs")
def api_log_feed():
    """
    Get system logs as feed items.

    Query params:
    - type: Log type (session, system, error, api) - default: session
    - lines: Number of lines (default 50)
    - level: Filter by level (INFO, WARNING, ERROR)
    """
    log_type = request.args.get("type", "session")
    lines = int(request.args.get("lines", 50))
    level_filter = request.args.get("level")

    logs_dir = Path(os.environ.get("UDOS_ROOT", ".")) / "memory" / "logs"

    # Find today's log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_patterns = {
        "session": f"session-commands-{today}.log",
        "system": f"system-{today}.log",
        "error": f"error-{today}.log",
        "api": "api_server.log",
        "debug": f"debug-{today}.log",
    }

    log_file = logs_dir / log_patterns.get(log_type, f"{log_type}-{today}.log")

    if not log_file.exists():
        return jsonify({"items": [], "error": f"Log file not found: {log_file.name}"})

    items = []

    try:
        # Read last N lines efficiently
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            # Read all and take last lines (simple approach for now)
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        for i, line in enumerate(recent_lines):
            line = line.strip()
            if not line:
                continue

            # Parse log line format: [TIMESTAMP] [LEVEL] MESSAGE
            level = "INFO"
            message = line
            timestamp = datetime.now().isoformat()

            # Try to extract level
            if "[ERROR]" in line:
                level = "ERROR"
            elif "[WARNING]" in line or "[WARN]" in line:
                level = "WARNING"
            elif "[DEBUG]" in line:
                level = "DEBUG"
            elif "[INFO]" in line:
                level = "INFO"

            # Filter by level if specified
            if level_filter and level != level_filter:
                continue

            # Try to extract timestamp
            if line.startswith("[") and "]" in line:
                try:
                    ts_end = line.index("]")
                    ts_str = line[1:ts_end]
                    # Try parsing common formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                        try:
                            dt = datetime.strptime(ts_str, fmt)
                            if fmt == "%H:%M:%S":
                                dt = dt.replace(
                                    year=datetime.now().year,
                                    month=datetime.now().month,
                                    day=datetime.now().day,
                                )
                            timestamp = dt.isoformat()
                            message = line[ts_end + 1 :].strip()
                            break
                        except ValueError:
                            continue
                except (ValueError, IndexError):
                    pass

            # Map level to priority
            priority = "normal"
            if level == "ERROR":
                priority = "high"
            elif level == "WARNING":
                priority = "normal"
            elif level == "DEBUG":
                priority = "low"

            items.append(
                {
                    "id": f"{log_type}-{i}-{uuid.uuid4().hex[:8]}",
                    "title": level,
                    "content": message,
                    "timestamp": timestamp,
                    "priority": priority,
                    "level": level,
                    "metadata": {
                        "logType": log_type,
                        "lineNumber": len(all_lines) - len(recent_lines) + i + 1,
                    },
                }
            )
    except Exception as e:
        api_logger.error(f"Error reading log {log_file}: {e}")
        return jsonify({"items": [], "error": str(e)})

    return jsonify(
        {"items": items, "total": len(items), "source": "logs", "logType": log_type}
    )


# ============================================================================
# NOTIFICATION FEED
# ============================================================================

# In-memory notification store (would be persistent in production)
_notifications: list = []


@feed_bp.route("/notifications")
def api_notification_feed():
    """
    Get system notifications as feed items.

    Query params:
    - unread: Only show unread (true/false)
    - limit: Max items (default 20)
    """
    unread_only = request.args.get("unread", "false").lower() == "true"
    limit = int(request.args.get("limit", 20))

    items = _notifications

    if unread_only:
        items = [n for n in items if not n.get("read", False)]

    return jsonify(
        {
            "items": items[:limit],
            "total": len(items),
            "unread": sum(1 for n in _notifications if not n.get("read", False)),
            "source": "notifications",
        }
    )


@feed_bp.route("/notifications", methods=["POST"])
def api_add_notification():
    """
    Add a new notification.

    Body:
    - title: Notification title
    - message: Notification content
    - priority: low/normal/high/urgent (default: normal)
    """
    data = request.json or {}

    notification = {
        "id": str(uuid.uuid4()),
        "title": data.get("title", "Notification"),
        "content": data.get("message", ""),
        "timestamp": datetime.now().isoformat(),
        "priority": data.get("priority", "normal"),
        "read": False,
        "metadata": data.get("metadata", {}),
    }

    _notifications.insert(0, notification)

    # Keep only last 100 notifications
    if len(_notifications) > 100:
        _notifications.pop()

    return jsonify({"success": True, "notification": notification})


@feed_bp.route("/notifications/<notification_id>/read", methods=["POST"])
def api_mark_notification_read(notification_id: str):
    """Mark a notification as read."""
    for n in _notifications:
        if n["id"] == notification_id:
            n["read"] = True
            return jsonify({"success": True})

    return jsonify({"success": False, "error": "Notification not found"}), 404


@feed_bp.route("/notifications/clear", methods=["POST"])
def api_clear_notifications():
    """Clear all notifications."""
    global _notifications
    _notifications = []
    return jsonify({"success": True})


# ============================================================================
# COMMAND HISTORY FEED
# ============================================================================


@feed_bp.route("/commands")
def api_command_feed():
    """
    Get recent command history as feed items.

    Query params:
    - limit: Max items (default 20)
    """
    limit = int(request.args.get("limit", 20))

    # Read from session commands log
    logs_dir = Path(os.environ.get("UDOS_ROOT", ".")) / "memory" / "logs"
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"session-commands-{today}.log"

    items = []

    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # Filter for INPUT lines (commands)
            for i, line in enumerate(reversed(lines)):
                if len(items) >= limit:
                    break

                if "[INPUT]" in line:
                    # Extract command from log line
                    parts = line.split("[INPUT]", 1)
                    if len(parts) > 1:
                        command = parts[1].strip()
                        items.append(
                            {
                                "id": f"cmd-{i}-{uuid.uuid4().hex[:8]}",
                                "title": "Command",
                                "content": command,
                                "timestamp": datetime.now().isoformat(),
                                "priority": "normal",
                                "metadata": {"type": "input"},
                            }
                        )
        except Exception as e:
            api_logger.error(f"Error reading command history: {e}")

    return jsonify({"items": items, "total": len(items), "source": "commands"})


# ============================================================================
# COMBINED FEED (ALL SOURCES)
# ============================================================================


@feed_bp.route("/all")
def api_combined_feed():
    """
    Get combined feed from all sources.

    Query params:
    - limit: Max items per source (default 10)
    - sources: Comma-separated list of sources to include
    """
    limit = int(request.args.get("limit", 10))
    sources = request.args.get("sources", "knowledge,logs,notifications").split(",")

    all_items = []

    # Collect from each source
    if "knowledge" in sources:
        try:
            knowledge = api_knowledge_feed().get_json()
            all_items.extend(
                [
                    {**item, "source": "knowledge"}
                    for item in knowledge.get("items", [])[:limit]
                ]
            )
        except Exception:
            pass

    if "logs" in sources:
        try:
            logs = api_log_feed().get_json()
            all_items.extend(
                [{**item, "source": "logs"} for item in logs.get("items", [])[:limit]]
            )
        except Exception:
            pass

    if "notifications" in sources:
        try:
            notifs = api_notification_feed().get_json()
            all_items.extend(
                [
                    {**item, "source": "notifications"}
                    for item in notifs.get("items", [])[:limit]
                ]
            )
        except Exception:
            pass

    if "commands" in sources:
        try:
            cmds = api_command_feed().get_json()
            all_items.extend(
                [
                    {**item, "source": "commands"}
                    for item in cmds.get("items", [])[:limit]
                ]
            )
        except Exception:
            pass

    # Sort by timestamp (newest first)
    all_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return jsonify({"items": all_items, "total": len(all_items), "sources": sources})


# ============================================================================
# MESH FEED
# ============================================================================


@feed_bp.route("/mesh")
def api_mesh_feed():
    """
    Get mesh network activity as feed items.

    Shows device connections, sync status, and mesh events.
    """
    limit = int(request.args.get("limit", 20))

    items = []

    # Try to get mesh status from wizard services
    try:
        from wizard.services.device_auth import get_device_auth
        from wizard.services.mesh_sync import get_mesh_sync

        auth = get_device_auth()
        sync = get_mesh_sync()

        # Add device status items
        for device in auth.list_devices():
            items.append(
                {
                    "id": f"device-{device.id}",
                    "title": f"📱 {device.name}",
                    "content": f"{device.status.value.title()} • {device.transport} • v{device.sync_version}",
                    "timestamp": device.last_seen or datetime.now().isoformat(),
                    "priority": "high" if device.status.value == "online" else "normal",
                    "metadata": {
                        "device_id": device.id,
                        "status": device.status.value,
                        "trust_level": device.trust_level.value,
                        "transport": device.transport,
                    },
                }
            )

        # Add sync status
        items.append(
            {
                "id": "sync-status",
                "title": "🔄 Sync Status",
                "content": f"Global version: {sync.global_version} • {len(sync.item_versions)} items tracked",
                "timestamp": datetime.now().isoformat(),
                "priority": "normal",
                "metadata": {
                    "global_version": sync.global_version,
                    "item_count": len(sync.item_versions),
                },
            }
        )

    except ImportError:
        # Wizard services not available (running standalone API)
        items.append(
            {
                "id": "mesh-unavailable",
                "title": "🔌 Mesh Unavailable",
                "content": "Wizard Server required for mesh features",
                "timestamp": datetime.now().isoformat(),
                "priority": "low",
                "metadata": {},
            }
        )
    except Exception as e:
        api_logger.error(f"Error getting mesh status: {e}")

    return jsonify({"items": items[:limit], "total": len(items), "source": "mesh"})
