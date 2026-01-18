"""
Files Routes Blueprint
======================

File operations: list, read, write, search, copy, move, delete.
~20 endpoints for file management.
"""

from flask import Blueprint, jsonify, request, g
from pathlib import Path
import json
import logging

from ..services import execute_command, init_udos_systems, get_project_root

api_logger = logging.getLogger("uDOS.API")
project_root = get_project_root()

# Create blueprint
files_bp = Blueprint("files", __name__, url_prefix="/api")


# ============================================================================
# FILE COMMANDS
# ============================================================================


@files_bp.route("/files/list")
def files_list():
    """List all files in workspace using file picker service."""
    init_udos_systems()
    from ..services.executor import _services

    file_picker_service = _services.get("file_picker")

    path = request.args.get("path", "")
    correlation_id = getattr(g, "correlation_id", "N/A")

    api_logger.info(f"[{correlation_id}] Listing directory: {path}")

    if file_picker_service is None:
        api_logger.error(f"[{correlation_id}] File picker service not available")
        return (
            jsonify(
                {
                    "error": "File picker service not available",
                    "files": [],
                    "folders": [],
                }
            ),
            503,
        )

    try:
        result = file_picker_service.list_directory(path if path else None)
        api_logger.info(
            f'[{correlation_id}] Found {len(result.get("files", []))} files, '
            f'{len(result.get("folders", []))} folders'
        )
        return jsonify(result)
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error listing directory: {e}", exc_info=True
        )
        return jsonify({"error": str(e), "files": [], "folders": []}), 500


@files_bp.route("/files/recent")
def files_recent():
    """Get recently accessed files."""
    count = request.args.get("count", "10")
    return jsonify(execute_command(f"FILE RECENT {count}"))


@files_bp.route("/files/search")
def files_search():
    """Search for files."""
    query = request.args.get("q", "")
    return jsonify(execute_command(f"FILE SEARCH {query}"))


@files_bp.route("/files/info/<path:filepath>")
def files_info(filepath):
    """Get file information."""
    return jsonify(execute_command(f"FILE INFO {filepath}"))


@files_bp.route("/files/content/<path:filepath>")
def files_content(filepath):
    """Get file content."""
    return jsonify(execute_command(f"FILE READ {filepath}"))


@files_bp.route("/files/read")
def files_read():
    """Read file content as plain text."""
    filepath = request.args.get("path", "")
    correlation_id = getattr(g, "correlation_id", "N/A")

    if not filepath:
        return jsonify({"error": "No path specified"}), 400

    try:
        file_path = Path(filepath)
        if not file_path.is_absolute():
            file_path = project_root / filepath

        api_logger.info(f"[{correlation_id}] Reading file: {file_path}")

        if not file_path.exists():
            api_logger.error(f"[{correlation_id}] File not found: {file_path}")
            return jsonify({"error": f"File not found: {filepath}"}), 404

        if not file_path.is_file():
            api_logger.error(f"[{correlation_id}] Not a file: {file_path}")
            return jsonify({"error": f"Not a file: {filepath}"}), 400

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        api_logger.info(
            f"[{correlation_id}] Successfully read file: {filepath} ({len(content)} chars)"
        )
        return content, 200, {"Content-Type": "text/plain; charset=utf-8"}

    except UnicodeDecodeError:
        api_logger.error(f"[{correlation_id}] File is not valid UTF-8: {filepath}")
        return jsonify({"error": "File is not valid UTF-8 text"}), 400
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error reading file: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@files_bp.route("/files/create", methods=["POST"])
def files_create():
    """Create new file."""
    data = request.get_json()
    filepath = data.get("path")
    return jsonify(execute_command(f"FILE CREATE {filepath}"))


@files_bp.route("/files/edit", methods=["POST"])
def files_edit():
    """Edit file (trigger editor)."""
    data = request.get_json()
    filepath = data.get("path")
    return jsonify(execute_command(f"FILE EDIT {filepath}"))


@files_bp.route("/files/append", methods=["POST", "OPTIONS"])
def files_append():
    """Append content to a file."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    filepath = data.get("path", "")
    content = data.get("content", "")

    if not filepath:
        return jsonify({"status": "error", "message": "No filepath provided"}), 400

    try:
        full_path = Path(project_root) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "a") as f:
            f.write(content)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Appended to {filepath}",
                    "bytes_written": len(content),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@files_bp.route("/files/delete", methods=["DELETE"])
def files_delete():
    """Delete file."""
    data = request.get_json()
    filepath = data.get("path")
    return jsonify(execute_command(f"FILE DELETE {filepath}"))


@files_bp.route("/files/copy", methods=["POST"])
def files_copy():
    """Copy file."""
    data = request.get_json()
    source = data.get("source")
    dest = data.get("dest")
    return jsonify(execute_command(f"FILE COPY {source} {dest}"))


@files_bp.route("/files/move", methods=["POST"])
def files_move():
    """Move/rename file."""
    data = request.get_json()
    source = data.get("source")
    dest = data.get("dest")
    return jsonify(execute_command(f"FILE MOVE {source} {dest}"))


@files_bp.route("/files/run", methods=["POST"])
def files_run():
    """Run script file."""
    data = request.get_json()
    filepath = data.get("path")
    return jsonify(execute_command(f"FILE RUN {filepath}"))


@files_bp.route("/files/bookmark/add", methods=["POST"])
def files_bookmark_add():
    """Add file bookmark."""
    data = request.get_json()
    filepath = data.get("path")
    return jsonify(execute_command(f"FILE BOOKMARK {filepath}"))


@files_bp.route("/files/bookmark/list")
def files_bookmark_list():
    """List bookmarked files."""
    return jsonify(execute_command("FILE BOOKMARKS"))


@files_bp.route("/files/stats")
def files_stats():
    """Get workspace file statistics."""
    return jsonify(execute_command("FILE STATS"))


@files_bp.route("/files/tree")
def files_tree():
    """Get directory tree."""
    return jsonify(execute_command("FILE TREE"))


# ============================================================================
# FILE API ENDPOINTS - Direct File Operations
# ============================================================================


@files_bp.route("/file/read")
def file_read_direct():
    """Direct file read with path parameter."""
    filepath = request.args.get("path", "")
    if not filepath:
        return jsonify({"error": "No path specified"}), 400

    return files_read()  # Delegate to files_read


@files_bp.route("/file/write", methods=["POST"])
def file_write():
    """Write content to file."""
    data = request.get_json()
    filepath = data.get("path", "")
    content = data.get("content", "")

    if not filepath:
        return jsonify({"status": "error", "message": "No filepath provided"}), 400

    try:
        full_path = Path(project_root) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Written to {filepath}",
                    "bytes_written": len(content),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@files_bp.route("/file/list")
def file_list_dir():
    """List directory contents."""
    path = request.args.get("path", "")

    try:
        dir_path = Path(project_root) / path if path else project_root

        if not dir_path.exists():
            return jsonify({"error": f"Directory not found: {path}"}), 404

        if not dir_path.is_dir():
            return jsonify({"error": f"Not a directory: {path}"}), 400

        items = []
        for item in sorted(dir_path.iterdir()):
            items.append(
                {
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                }
            )

        return jsonify(
            {
                "status": "success",
                "path": str(path),
                "items": items,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
