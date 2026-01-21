#!/usr/bin/env python3
"""
uDOS API Server
===============

Modular REST API for uDOS command execution and services.
Routes are organized into blueprints in the routes/ package.

Architecture:
  - routes/       - Flask blueprints by domain
  - websocket/    - Socket.IO event handlers
  - services/     - Shared services (executor, etc.)

Endpoints: ~150 routes across domains:
  /api/system/*    - System commands, health, version
  /api/files/*     - File operations
  /api/tui/*       - TUI-Tauri bridge
  /api/settings/*  - Configuration management
  /api/dashboard/* - Dashboard data
  /api/knowledge/* - Knowledge bank
  /api/webhooks/*  - Webhook management
"""

import os
import sys
import uuid
import json
import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_socketio import SocketIO

# Add parent directory to path for uDOS imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# Import route blueprints - handle both module and script execution
try:
    from .routes import ALL_BLUEPRINTS
    from .websocket import register_socketio_handlers
    from .services import (
        execute_command,
        init_udos_systems,
        get_api_logger,
        get_project_root,
        UDOS_AVAILABLE,
        STREAMING_AVAILABLE,
    )
except ImportError:
    # Fallback for script execution
    from extensions.api.routes import ALL_BLUEPRINTS
    from extensions.api.websocket import register_socketio_handlers
    from extensions.api.services import (
        execute_command,
        init_udos_systems,
        get_api_logger,
        get_project_root,
        UDOS_AVAILABLE,
        STREAMING_AVAILABLE,
    )

# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)
app.config["SECRET_KEY"] = "udos-api-server"

# Enable CORS
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True,
)

socketio = SocketIO(app, cors_allowed_origins="*")

# ============================================================================
# LOGGING SETUP
# ============================================================================

LOG_DIR = project_root / "memory" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "api_server.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

api_logger = logging.getLogger("uDOS.API")
api_logger.addHandler(file_handler)
api_logger.setLevel(logging.DEBUG)

api_logger.info("=" * 70)
api_logger.info("uDOS API Server Starting (Modular)")
api_logger.info(f"Log file: {LOG_FILE}")
api_logger.info("=" * 70)

# ============================================================================
# REQUEST/RESPONSE LOGGING MIDDLEWARE
# ============================================================================


@app.before_request
def log_request():
    """Log all incoming requests with correlation ID."""
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    g.correlation_id = correlation_id

    api_logger.debug(f"[{correlation_id}] Request: {request.method} {request.path}")
    api_logger.debug(f"[{correlation_id}] Client: {request.remote_addr}")

    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            data = request.get_json()
            if data:
                api_logger.debug(
                    f"[{correlation_id}] Request data: {json.dumps(data, indent=2)}"
                )
        except:
            pass


@app.after_request
def log_response(response):
    """Log all responses and propagate correlation ID."""
    correlation_id = getattr(g, "correlation_id", None)

    if correlation_id:
        response.headers["X-Correlation-ID"] = correlation_id
        api_logger.debug(
            f"[{correlation_id}] Response: {request.path} - Status {response.status_code}"
        )
    else:
        api_logger.debug(f"Response: {request.path} - Status {response.status_code}")

    return response


@app.errorhandler(Exception)
def handle_error(error):
    """Log all errors with correlation ID."""
    correlation_id = getattr(g, "correlation_id", "N/A")
    api_logger.error(
        f"[{correlation_id}] Error on {request.path}: {error}", exc_info=True
    )

    return (
        jsonify(
            {
                "status": "error",
                "message": str(error),
                "path": request.path,
                "correlation_id": correlation_id,
            }
        ),
        500,
    )


# ============================================================================
# REGISTER BLUEPRINTS
# ============================================================================

for bp in ALL_BLUEPRINTS:
    app.register_blueprint(bp)
    api_logger.info(f"Registered blueprint: {bp.name}")

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================


@app.route("/")
def index():
    """API server info endpoint."""
    return jsonify(
        {
            "name": "uDOS API Server",
            "status": "running",
            "udos_available": UDOS_AVAILABLE,
            "architecture": "modular",
            "endpoints": {
                "health": "/api/health",
                "execute": "/api/execute",
                "files": "/api/files/list",
                "tui": "/api/tui/status",
                "settings": "/api/settings/unified",
            },
            "documentation": "https://github.com/fredporter/uDOS-dev/wiki",
            "message": "uDOS API Server is running. Use /api/* endpoints.",
        }
    )


@app.route("/ping", methods=["GET", "OPTIONS"])
def ping():
    """Simple ping endpoint for connection testing."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    return (
        jsonify(
            {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "server": "uDOS API",
            }
        ),
        200,
    )


# ============================================================================
# LEGACY SHORTCUT ENDPOINTS (backwards compatibility)
# ============================================================================


@app.route("/list", methods=["GET", "OPTIONS"])
def list_shortcut():
    """Shortcut for /api/files/list - list markdown files."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    path = request.args.get("path", "")
    correlation_id = getattr(g, "correlation_id", "N/A")

    api_logger.info(f"[{correlation_id}] List shortcut called for: {path}")
    init_udos_systems()

    try:
        dir_path = Path(path) if path else project_root
        if not dir_path.is_absolute():
            dir_path = project_root / path

        if not dir_path.exists():
            return jsonify({"error": f"Directory not found: {path}", "files": []}), 404

        if not dir_path.is_dir():
            return jsonify({"error": f"Not a directory: {path}", "files": []}), 400

        markdown_files = []
        for md_file in dir_path.rglob("*.md"):
            rel_path = md_file.relative_to(dir_path)
            markdown_files.append(
                {
                    "name": md_file.name,
                    "path": str(rel_path),
                    "full_path": str(md_file.relative_to(project_root)),
                    "size": md_file.stat().st_size,
                    "folder": (
                        str(rel_path.parent) if rel_path.parent != Path(".") else ""
                    ),
                }
            )

        markdown_files.sort(key=lambda x: (x["folder"], x["name"]))

        api_logger.info(
            f"[{correlation_id}] Found {len(markdown_files)} markdown files"
        )
        return jsonify({"files": markdown_files, "count": len(markdown_files)})

    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error listing directory: {e}", exc_info=True
        )
        return jsonify({"error": str(e), "files": []}), 500


@app.route("/read", methods=["GET", "OPTIONS"])
def read_shortcut():
    """Shortcut for /api/files/read - read file content."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    filepath = request.args.get("path", "")
    correlation_id = getattr(g, "correlation_id", "N/A")

    if not filepath:
        return jsonify({"error": "No path specified"}), 400

    try:
        file_path = Path(filepath)
        if not file_path.is_absolute():
            file_path = project_root / filepath

        if not file_path.exists():
            return jsonify({"error": f"File not found: {filepath}"}), 404

        if not file_path.is_file():
            return jsonify({"error": f"Not a file: {filepath}"}), 400

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return content, 200, {"Content-Type": "text/plain; charset=utf-8"}

    except UnicodeDecodeError:
        return jsonify({"error": "File is not valid UTF-8 text"}), 400
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error reading file: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# REGISTER WEBSOCKET HANDLERS
# ============================================================================

register_socketio_handlers(socketio)
api_logger.info("WebSocket handlers registered")

# ============================================================================
# SERVER INITIALIZATION
# ============================================================================


def main():
    """Run the API server."""
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("DEBUG", "False").lower() == "true"

    # Count routes
    route_count = len([rule for rule in app.url_map.iter_rules()])

    startup_msg = f"""
{"="*60}
🌐 uDOS API Server (Modular)
{"="*60}

🌐 Server: http://localhost:{port}
📡 Endpoints: {route_count} routes
🔌 WebSocket: Enabled
🎨 CORS: Enabled
🔧 Debug: {debug}
📝 Logging: {LOG_FILE}

Blueprints:
  - system   (/api/system/*, /api/health, /api/assist/*)
  - files    (/api/files/*, /api/file/*)
  - tui      (/api/tui/*, /api/viewport/*)
  - settings (/api/settings/*, /api/config/*, /api/extensions/*)

{"="*60}
✨ Press Ctrl+C to stop
"""

    print(startup_msg)
    api_logger.info(f"Starting server on port {port}")
    api_logger.info(f"Debug mode: {debug}")
    api_logger.info(f"uDOS core available: {UDOS_AVAILABLE}")
    api_logger.info(f"Routes registered: {route_count}")

    try:
        socketio.run(
            app, host="0.0.0.0", port=port, debug=debug, allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        api_logger.info("Server stopped by user")
        print("\n👋 Server stopped")
    except Exception as e:
        api_logger.error(f"Server error: {e}", exc_info=True)
        print(f"\n❌ Server error: {e}")
        raise


if __name__ == "__main__":
    main()
