"""
Settings Routes Blueprint
=========================

Configuration and settings endpoints: unified settings, env, user config, extensions.
~15 endpoints for configuration management.
"""

from flask import Blueprint, jsonify, request, g
from pathlib import Path
import json
import logging

from ..services import execute_command, init_udos_systems, get_project_root

api_logger = logging.getLogger("uDOS.API")
project_root = get_project_root()

# Create blueprint
settings_bp = Blueprint("settings", __name__, url_prefix="/api")


def get_settings_sync():
    """Get settings sync service."""
    from ..services.executor import _services

    return _services.get("settings_sync")


def get_extension_registry():
    """Get extension registry service."""
    from ..services.executor import _services

    return _services.get("extension_registry")


# ============================================================================
# CONFIG & ENVIRONMENT
# ============================================================================


@settings_bp.route("/config/env", methods=["GET", "POST"])
def config_env():
    """Get or set .env variables."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    env_path = project_root / "core" / ".env"

    if request.method == "GET":
        api_logger.info(f"[{correlation_id}] Loading .env file")
        try:
            if not env_path.exists():
                api_logger.warning(f"[{correlation_id}] .env file not found")
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": ".env file not found",
                            "data": {},
                        }
                    ),
                    404,
                )

            env_data = {}
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_data[key.strip()] = value.strip()

            api_logger.info(
                f"[{correlation_id}] Loaded {len(env_data)} environment variables"
            )
            return jsonify({"status": "success", "data": env_data})
        except Exception as e:
            api_logger.error(
                f"[{correlation_id}] Error reading .env: {e}", exc_info=True
            )
            return jsonify({"status": "error", "message": str(e), "data": {}}), 500

    else:  # POST
        data = request.get_json()
        key = data.get("key")
        value = data.get("value", "")

        api_logger.info(f"[{correlation_id}] Setting env var: {key}")

        if not key:
            return jsonify({"status": "error", "message": "Missing key parameter"}), 400

        try:
            env_lines = []
            key_found = False

            if env_path.exists():
                with open(env_path, "r") as f:
                    for line in f:
                        if line.strip().startswith(f"{key}="):
                            env_lines.append(f"{key}={value}\n")
                            key_found = True
                        else:
                            env_lines.append(line)

            if not key_found:
                env_lines.append(f"{key}={value}\n")

            with open(env_path, "w") as f:
                f.writelines(env_lines)

            api_logger.info(f"[{correlation_id}] ✓ Updated .env: {key}={value}")
            return jsonify(
                {"status": "success", "message": f"Environment variable {key} updated"}
            )
        except Exception as e:
            api_logger.error(
                f"[{correlation_id}] Error writing .env: {e}", exc_info=True
            )
            return jsonify({"status": "error", "message": str(e)}), 500


@settings_bp.route("/config/user", methods=["GET", "POST"])
def config_user():
    """Get or set user.json variables."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    user_json_path = project_root / "core" / "data" / "variables" / "user.json"

    if request.method == "GET":
        api_logger.info(f"[{correlation_id}] Loading user.json")
        try:
            if not user_json_path.exists():
                api_logger.warning(f"[{correlation_id}] user.json not found")
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "user.json not found",
                            "data": {},
                        }
                    ),
                    404,
                )

            with open(user_json_path, "r") as f:
                user_data = json.load(f)

            variables = {}
            if "variables" in user_data:
                for key, config in user_data["variables"].items():
                    variables[key] = config.get("default", "")

            api_logger.info(
                f"[{correlation_id}] Loaded {len(variables)} user variables"
            )
            return jsonify({"status": "success", "data": variables})
        except Exception as e:
            api_logger.error(
                f"[{correlation_id}] Error reading user.json: {e}", exc_info=True
            )
            return jsonify({"status": "error", "message": str(e), "data": {}}), 500

    else:  # POST
        data = request.get_json()
        key = data.get("key")
        value = data.get("value")

        api_logger.info(f"[{correlation_id}] Setting user var: {key}")

        if not key:
            return jsonify({"status": "error", "message": "Missing key parameter"}), 400

        try:
            with open(user_json_path, "r") as f:
                user_data = json.load(f)

            if "variables" in user_data and key in user_data["variables"]:
                user_data["variables"][key]["default"] = value
            else:
                api_logger.warning(
                    f"[{correlation_id}] Variable {key} not found in schema"
                )
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Variable {key} not found in user.json schema",
                        }
                    ),
                    404,
                )

            with open(user_json_path, "w") as f:
                json.dump(user_data, f, indent=2)

            api_logger.info(f"[{correlation_id}] ✓ Updated user.json: {key}={value}")
            return jsonify(
                {"status": "success", "message": f"User variable {key} updated"}
            )
        except Exception as e:
            api_logger.error(
                f"[{correlation_id}] Error writing user.json: {e}", exc_info=True
            )
            return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# UNIFIED SETTINGS
# ============================================================================


@settings_bp.route("/settings/unified", methods=["GET"])
def get_unified_settings():
    """Get unified settings from all sources."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting unified settings")
        settings_sync = get_settings_sync()

        if settings_sync is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Settings sync service not initialized",
                    }
                ),
                500,
            )

        settings = settings_sync.get_unified_settings()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved unified settings")
        return jsonify(
            {
                "status": "success",
                "data": settings,
                "last_sync": (
                    settings_sync._last_sync.isoformat()
                    if settings_sync._last_sync
                    else None
                ),
            }
        )
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting unified settings: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@settings_bp.route("/settings/unified", methods=["POST"])
def save_unified_settings():
    """Save unified settings to all configuration files."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.get_json()
        settings = data.get("settings")

        if not settings:
            return (
                jsonify({"status": "error", "message": "Missing settings parameter"}),
                400,
            )

        api_logger.info(f"[{correlation_id}] Saving unified settings")
        settings_sync = get_settings_sync()

        if settings_sync is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Settings sync service not initialized",
                    }
                ),
                500,
            )

        success = settings_sync.save_settings(settings)

        if success:
            api_logger.info(f"[{correlation_id}] ✓ Saved unified settings")
            return jsonify(
                {"status": "success", "message": "Settings saved successfully"}
            )
        else:
            api_logger.error(f"[{correlation_id}] Failed to save unified settings")
            return (
                jsonify({"status": "error", "message": "Failed to save settings"}),
                500,
            )
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error saving unified settings: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@settings_bp.route("/settings/user", methods=["GET"])
def get_user_settings():
    """Get user profile settings."""
    init_udos_systems()
    settings_sync = get_settings_sync()

    if settings_sync is None:
        return (
            jsonify(
                {"status": "error", "message": "Settings sync service not initialized"}
            ),
            500,
        )

    settings = settings_sync.get_unified_settings()
    return jsonify({"status": "success", "data": settings["user"]})


@settings_bp.route("/settings/ui", methods=["GET"])
def get_ui_settings():
    """Get UI preferences (Tauri-specific)."""
    init_udos_systems()
    settings_sync = get_settings_sync()

    if settings_sync is None:
        return (
            jsonify(
                {"status": "error", "message": "Settings sync service not initialized"}
            ),
            500,
        )

    settings = settings_sync.get_unified_settings()
    return jsonify({"status": "success", "data": settings["ui"]})


@settings_bp.route("/settings/workspace", methods=["GET"])
def get_workspace_settings():
    """Get workspace/file picker settings."""
    init_udos_systems()
    settings_sync = get_settings_sync()

    if settings_sync is None:
        return (
            jsonify(
                {"status": "error", "message": "Settings sync service not initialized"}
            ),
            500,
        )

    settings = settings_sync.get_unified_settings()
    return jsonify({"status": "success", "data": settings["workspace"]})


@settings_bp.route("/settings/extensions", methods=["GET"])
def get_extension_settings():
    """Get extension configuration."""
    init_udos_systems()
    settings_sync = get_settings_sync()

    if settings_sync is None:
        return (
            jsonify(
                {"status": "error", "message": "Settings sync service not initialized"}
            ),
            500,
        )

    settings = settings_sync.get_unified_settings()
    return jsonify({"status": "success", "data": settings["extensions"]})


# ============================================================================
# EXTENSION REGISTRY
# ============================================================================


@settings_bp.route("/extensions", methods=["GET"])
def get_extensions():
    """Get all extensions."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting extensions")
        extension_registry = get_extension_registry()

        if extension_registry is None:
            return (
                jsonify(
                    {"status": "error", "message": "Extension registry not initialized"}
                ),
                500,
            )

        extensions = extension_registry.get_all_extensions()
        extensions_dict = {
            ext_id: info.to_dict() for ext_id, info in extensions.items()
        }

        api_logger.info(f"[{correlation_id}] ✓ Retrieved {len(extensions)} extensions")
        return jsonify({"status": "success", "data": extensions_dict})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting extensions: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@settings_bp.route("/extensions/status", methods=["GET"])
def get_extensions_status():
    """Get system status with all extensions."""
    init_udos_systems()
    extension_registry = get_extension_registry()

    if extension_registry is None:
        return (
            jsonify(
                {"status": "error", "message": "Extension registry not initialized"}
            ),
            500,
        )

    status = extension_registry.get_system_status()
    return jsonify({"status": "success", "data": status})


@settings_bp.route("/extensions/boundaries", methods=["GET"])
def get_service_boundaries():
    """Get service boundaries for all extensions."""
    init_udos_systems()
    extension_registry = get_extension_registry()

    if extension_registry is None:
        return (
            jsonify(
                {"status": "error", "message": "Extension registry not initialized"}
            ),
            500,
        )

    boundaries = extension_registry.get_service_boundaries()
    return jsonify({"status": "success", "data": boundaries})


@settings_bp.route("/extensions/dataflow", methods=["GET"])
def get_data_flow():
    """Get data flow patterns."""
    init_udos_systems()
    extension_registry = get_extension_registry()

    if extension_registry is None:
        return (
            jsonify(
                {"status": "error", "message": "Extension registry not initialized"}
            ),
            500,
        )

    dataflow = extension_registry.get_data_flow()
    return jsonify({"status": "success", "data": dataflow})
