"""
Docs Routes Blueprint
=====================

Document listing and reading endpoints.
~2 endpoints for document access.
"""

from flask import Blueprint, jsonify, request, g
from pathlib import Path
import logging

from ..services import get_project_root

api_logger = logging.getLogger("uDOS.API")
project_root = get_project_root()

# Create blueprint
docs_bp = Blueprint("docs", __name__, url_prefix="/api/docs")


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================


@docs_bp.route("/list", methods=["GET"])
def api_list_files():
    """List files in a workspace directory (wiki, knowledge, memory)."""
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        workspace = request.args.get("workspace", "wiki")
        path = request.args.get("path", "")
        extensions = request.args.get("extensions", ".md,.txt").split(",")
        recursive = request.args.get("recursive", "true").lower() == "true"

        api_logger.debug(
            f"[{correlation_id}] Listing files: workspace={workspace} path={path} recursive={recursive}"
        )

        workspace_map = {
            "wiki": project_root / "wiki",
            "docs": project_root / "wiki",
            "knowledge": project_root / "knowledge",
            "memory": project_root / "memory",
        }

        base_path = workspace_map.get(workspace, project_root / workspace)
        full_path = base_path / path if path else base_path

        if not full_path.exists():
            api_logger.warning(f"[{correlation_id}] Path not found: {full_path}")
            return jsonify({"error": "Path not found", "path": str(full_path)}), 404

        files = []

        if recursive:
            for ext in extensions:
                ext = ext.strip()
                if not ext.startswith("."):
                    ext = "." + ext
                for item in full_path.rglob(f"*{ext}"):
                    if item.is_file():
                        rel_path = str(item.relative_to(project_root))
                        rel_from_base = item.relative_to(full_path)
                        folder = (
                            str(rel_from_base.parent)
                            if rel_from_base.parent != Path(".")
                            else ""
                        )
                        files.append(
                            {
                                "name": item.name,
                                "path": rel_path,
                                "size": item.stat().st_size,
                                "modified": item.stat().st_mtime,
                                "folder": folder,
                            }
                        )
        else:
            for item in sorted(full_path.iterdir()):
                if item.is_file():
                    if any(item.name.endswith(ext) for ext in extensions):
                        rel_path = str(item.relative_to(project_root))
                        files.append(
                            {
                                "name": item.name,
                                "path": rel_path,
                                "size": item.stat().st_size,
                                "modified": item.stat().st_mtime,
                            }
                        )
                elif item.is_dir():
                    rel_path = str(item.relative_to(project_root))
                    files.append(
                        {"name": item.name, "path": rel_path, "type": "directory"}
                    )

        api_logger.info(
            f"[{correlation_id}] Listed {len(files)} items from {workspace}"
        )

        return jsonify(
            {
                "status": "success",
                "workspace": workspace,
                "path": str(full_path.relative_to(project_root)),
                "files": files,
                "count": len(files),
            }
        )

    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error listing files: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@docs_bp.route("/read", methods=["GET"])
def api_read_file():
    """Read file content (returns plain text)."""
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        path = request.args.get("path")
        if not path:
            return jsonify({"error": "Missing path parameter"}), 400

        api_logger.debug(f"[{correlation_id}] Reading file: {path}")

        file_path = (project_root / path).resolve()
        if not str(file_path).startswith(str(project_root)):
            api_logger.warning(
                f"[{correlation_id}] Security: Path outside project - {path}"
            )
            return jsonify({"error": "Access denied"}), 403

        if not file_path.exists():
            api_logger.warning(f"[{correlation_id}] File not found: {path}")
            return jsonify({"error": "File not found"}), 404

        content = file_path.read_text(encoding="utf-8")
        size = len(content)

        api_logger.info(f"[{correlation_id}] Read file: {path} ({size} bytes)")

        return content, 200, {"Content-Type": "text/plain; charset=utf-8"}

    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error reading file: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
