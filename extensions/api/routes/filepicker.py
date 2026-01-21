"""
FilePicker Routes Blueprint
============================

File picker service endpoints: workspaces, list, recent, bookmarks, search.
~6 endpoints for file navigation.
"""

from flask import Blueprint, jsonify, request, g
import logging

from ..services import init_udos_systems

api_logger = logging.getLogger("uDOS.API")

# Create blueprint
filepicker_bp = Blueprint("filepicker", __name__, url_prefix="/api/filepicker")


def get_file_picker_service():
    """Get file picker service."""
    from ..services.executor import _services

    return _services.get("file_picker")


# ============================================================================
# FILE PICKER ENDPOINTS
# ============================================================================


@filepicker_bp.route("/workspaces", methods=["GET"])
def get_workspaces():
    """Get available workspaces."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting workspaces")

        file_picker = get_file_picker_service()
        if file_picker is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "File picker service not initialized",
                    }
                ),
                500,
            )

        workspaces = file_picker.get_workspaces()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved {len(workspaces)} workspaces")
        return jsonify({"status": "success", "data": workspaces})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting workspaces: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@filepicker_bp.route("/list", methods=["POST"])
def list_files():
    """List files in a directory."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.get_json()
        workspace = data.get("workspace", "scripts")
        path = data.get("path", "")
        extensions = data.get("extensions", [".upy", ".md", ".json"])
        show_hidden = data.get("show_hidden", False)

        api_logger.info(f"[{correlation_id}] Listing files: {workspace}/{path}")

        file_picker = get_file_picker_service()
        if file_picker is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "File picker service not initialized",
                    }
                ),
                500,
            )

        file_picker.set_workspace(workspace)
        if path:
            file_picker.navigate_to_path(path)

        entries = file_picker.get_entries(
            filter_extensions=extensions if extensions else None,
            show_hidden=show_hidden,
        )

        entries_dict = [e.to_dict() for e in entries]

        api_logger.info(f"[{correlation_id}] ✓ Listed {len(entries_dict)} entries")
        return jsonify(
            {
                "status": "success",
                "data": {
                    "workspace": workspace,
                    "path": str(file_picker.state.current_path),
                    "entries": entries_dict,
                    "count": len(entries_dict),
                },
            }
        )
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error listing files: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@filepicker_bp.route("/recent", methods=["GET"])
def get_recent_files():
    """Get recently accessed files."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        limit = request.args.get("limit", 10, type=int)

        api_logger.info(f"[{correlation_id}] Getting recent files (limit={limit})")

        file_picker = get_file_picker_service()
        if file_picker is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "File picker service not initialized",
                    }
                ),
                500,
            )

        recent = file_picker.get_recent_files(limit=limit)

        api_logger.info(f"[{correlation_id}] ✓ Retrieved {len(recent)} recent files")
        return jsonify({"status": "success", "data": recent, "count": len(recent)})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting recent files: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@filepicker_bp.route("/recent", methods=["POST"])
def add_recent_file():
    """Add file to recent files list."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.get_json()
        file_path = data.get("path")

        if not file_path:
            return (
                jsonify({"status": "error", "message": "Missing path parameter"}),
                400,
            )

        api_logger.info(f"[{correlation_id}] Adding to recent: {file_path}")

        file_picker = get_file_picker_service()
        if file_picker is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "File picker service not initialized",
                    }
                ),
                500,
            )

        file_picker.add_recent_file(file_path)

        api_logger.info(f"[{correlation_id}] ✓ Added to recent files")
        return jsonify({"status": "success", "message": "File added to recent list"})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error adding recent file: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@filepicker_bp.route("/bookmarks", methods=["GET"])
def get_bookmarks():
    """Get bookmarked files/folders."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting bookmarks")

        file_picker = get_file_picker_service()
        if file_picker is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "File picker service not initialized",
                    }
                ),
                500,
            )

        bookmarks = file_picker.get_bookmarks()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved {len(bookmarks)} bookmarks")
        return jsonify(
            {"status": "success", "data": bookmarks, "count": len(bookmarks)}
        )
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting bookmarks: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@filepicker_bp.route("/search", methods=["POST"])
def search_files():
    """Search files by fuzzy matching."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.get_json()
        query = data.get("query", "")
        workspace = data.get("workspace")
        limit = data.get("limit", 20)

        if not query:
            return (
                jsonify({"status": "error", "message": "Missing query parameter"}),
                400,
            )

        api_logger.info(f"[{correlation_id}] Searching files: {query}")

        file_picker = get_file_picker_service()
        if file_picker is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "File picker service not initialized",
                    }
                ),
                500,
            )

        results = file_picker.fuzzy_search(
            query=query, workspace=workspace, limit=limit
        )

        api_logger.info(f"[{correlation_id}] ✓ Found {len(results)} matches")
        return jsonify(
            {
                "status": "success",
                "data": results,
                "count": len(results),
                "query": query,
            }
        )
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error searching files: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500
