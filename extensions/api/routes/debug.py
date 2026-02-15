"""
Debug Routes Blueprint
======================

Debug/logging endpoints: logs, debug TUI, log files.
~6 endpoints for debugging support.
"""

from flask import Blueprint, jsonify, request, g
from pathlib import Path
import logging
import subprocess
import platform

from ..services import get_project_root

api_logger = logging.getLogger("uDOS.API")
project_root = get_project_root()

# Create blueprint
debug_bp = Blueprint("debug", __name__, url_prefix="/api/debug")

# Try to import LogLang logger
try:
    from core_beta.services.loglang_logger import get_logger as get_loglang_logger

    api_log = get_loglang_logger("API")
    LOGLANG_AVAILABLE = True
except ImportError:
    api_log = None
    LOGLANG_AVAILABLE = False


# ============================================================================
# DEBUG LOG ENDPOINTS
# ============================================================================


@debug_bp.route("/logs", methods=["POST", "OPTIONS"])
def receive_debug_logs():
    """Receive debug logs from Tauri Dev Console."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.json or {}
        source = data.get("source", "unknown")
        logs = data.get("logs", [])
        formatted = data.get("formatted", "")

        from datetime import datetime

        log_dir = Path(project_root) / "memory" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"tauri-debug-{today}.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Source: {source}\n")
            f.write(f"Received: {datetime.now().isoformat()}\n")
            f.write(f"Correlation: {correlation_id}\n")
            f.write(f"{'='*60}\n")
            if formatted:
                f.write(formatted)
            else:
                for log in logs:
                    f.write(
                        f"[{log.get('timestamp', '')}] [{log.get('level', '').upper()}] {log.get('message', '')}\n"
                    )
            f.write("\n")

        api_logger.info(
            f"[{correlation_id}] Received {len(logs)} debug logs from {source}"
        )

        return jsonify(
            {"status": "success", "received": len(logs), "file": str(log_file.name)}
        )

    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error receiving debug logs: {e}")
        return jsonify({"error": str(e)}), 500


@debug_bp.route("/tui/open", methods=["POST", "OPTIONS"])
def open_debug_tui():
    """Request to open debug TUI in external terminal."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        udos_path = str(project_root)

        if platform.system() == "Darwin":
            script = f"""
            tell application "Terminal"
                activate
                do script "cd {udos_path} && source .venv/bin/activate && ./bin/ucli tui -c L"
            end tell
            """
            subprocess.Popen(["osascript", "-e", script])
            method = "terminal.app"

        elif platform.system() == "Linux":
            terminals = ["gnome-terminal", "konsole", "xfce4-terminal", "xterm"]
            for term in terminals:
                try:
                    cmd = f"cd {udos_path} && source .venv/bin/activate && ./bin/ucli tui -c L"
                    subprocess.Popen([term, "--", "bash", "-c", cmd])
                    method = term
                    break
                except FileNotFoundError:
                    continue
            else:
                return jsonify(
                    {
                        "status": "manual",
                        "command": f"cd {udos_path} && ./bin/ucli tui -c L",
                        "message": "No supported terminal found. Run command manually.",
                    }
                )
        else:
            return jsonify(
                {
                    "status": "manual",
                    "command": f"cd {udos_path} && ./bin/ucli tui -c L",
                    "message": "Platform not supported for auto-launch. Run command manually.",
                }
            )

        api_logger.info(f"[{correlation_id}] Opened debug TUI via {method}")

        return jsonify(
            {
                "status": "success",
                "method": method,
                "message": "Debug TUI opened in external terminal",
            }
        )

    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error opening debug TUI: {e}")
        return jsonify(
            {
                "status": "manual",
                "command": f"cd {project_root} && ./bin/ucli tui -c L",
                "error": str(e),
            }
        )


# ============================================================================
# LOG FILE MANAGEMENT
# ============================================================================


@debug_bp.route("/logs/files", methods=["GET"])
def list_log_files():
    """List available log files."""
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        log_dir = Path(project_root) / "memory" / "logs"

        files = []
        for log_file in sorted(log_dir.glob("*.log"), reverse=True):
            stat = log_file.stat()
            files.append(
                {
                    "name": log_file.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": str(log_file.relative_to(project_root)),
                }
            )

        return jsonify({"status": "success", "files": files, "count": len(files)})
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error listing log files: {e}")
        return jsonify({"error": str(e)}), 500


@debug_bp.route("/logs/read/<filename>", methods=["GET"])
def read_log_file(filename):
    """Read a log file."""
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        log_dir = Path(project_root) / "memory" / "logs"
        log_file = log_dir / filename

        if not str(log_file.resolve()).startswith(str(log_dir.resolve())):
            return jsonify({"error": "Invalid file path"}), 400

        if not log_file.exists():
            return jsonify({"error": "File not found"}), 404

        lines_param = request.args.get("lines", "1000")
        lines_limit = int(lines_param) if lines_param != "all" else None

        with open(log_file, "r", encoding="utf-8") as f:
            if lines_limit:
                from collections import deque

                lines = list(deque(f, maxlen=lines_limit))
            else:
                lines = f.readlines()

        return jsonify(
            {
                "status": "success",
                "filename": filename,
                "lines": [line.rstrip() for line in lines],
                "count": len(lines),
            }
        )
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error reading log file: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# LOG STREAMING (LogLang)
# ============================================================================


@debug_bp.route("/logs/recent", methods=["GET"])
def get_recent_logs():
    """Get recent logs from buffer."""
    correlation_id = getattr(g, "correlation_id", "N/A")

    if not LOGLANG_AVAILABLE or api_log is None:
        return jsonify({"error": "LogLang logger not available"}), 503

    try:
        count = int(request.args.get("count", 100))
        logs = api_log.get_recent(count)

        return jsonify({"status": "success", "logs": logs, "count": len(logs)})
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error getting recent logs: {e}")
        return jsonify({"error": str(e)}), 500


@debug_bp.route("/logs/search", methods=["POST"])
def search_logs():
    """Search logs with filters."""
    correlation_id = getattr(g, "correlation_id", "N/A")

    if not LOGLANG_AVAILABLE or api_log is None:
        return jsonify({"error": "LogLang logger not available"}), 503

    try:
        data = request.get_json() or {}
        query = data.get("query")
        level = data.get("level")
        category = data.get("category")
        cid = data.get("correlationId")
        limit = int(data.get("limit", 100))

        logs = api_log.search(
            query=query, level=level, category=category, cid=cid, limit=limit
        )

        return jsonify(
            {
                "status": "success",
                "logs": logs,
                "count": len(logs),
                "filters": {
                    "query": query,
                    "level": level,
                    "category": category,
                    "correlationId": cid,
                },
            }
        )
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error searching logs: {e}")
        return jsonify({"error": str(e)}), 500
