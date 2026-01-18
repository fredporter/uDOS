"""
User Configuration Routes for uDOS API v1.0.0.41+

Provides user config access for Tauri app.
Single source of truth via UserConfigManager.
"""

from flask import Blueprint, jsonify, request
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core_beta.services.user_config import get_user_config

bp = Blueprint("user", __name__, url_prefix="/api/user")


@bp.route("/config", methods=["GET"])
def get_config():
    """
    Get user configuration.

    Returns:
        JSON: User config with schema v1.0.0
    """
    try:
        config_manager = get_user_config()
        config = config_manager.load()

        return jsonify({"success": True, "config": config})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/config", methods=["PUT"])
def update_config():
    """
    Update user configuration (deep merge).

    Body:
        JSON: Partial config updates

    Returns:
        JSON: Success status
    """
    try:
        updates = request.json
        if not updates:
            return jsonify({"success": False, "error": "No updates provided"}), 400

        config_manager = get_user_config()
        success = config_manager.update(updates)

        if success:
            return jsonify({"success": True, "message": "Config updated"})
        else:
            return jsonify({"success": False, "error": "Failed to save config"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/config/<path:key>", methods=["GET"])
def get_config_value(key):
    """
    Get specific config value by dot-notation key.

    Args:
        key: Dot-notation path (e.g., user_profile.username)

    Returns:
        JSON: Config value
    """
    try:
        config_manager = get_user_config()
        value = config_manager.get(key)

        if value is None:
            return jsonify({"success": False, "error": f"Key not found: {key}"}), 404

        return jsonify({"success": True, "key": key, "value": value})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/profile", methods=["GET"])
def get_profile():
    """
    Get user profile data.

    Returns:
        JSON: User profile section only
    """
    try:
        config_manager = get_user_config()
        config = config_manager.load()

        return jsonify({"success": True, "profile": config.get("user_profile", {})})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/profile", methods=["PUT"])
def update_profile():
    """
    Update user profile fields.

    Body:
        JSON: Profile field updates

    Returns:
        JSON: Success status
    """
    try:
        updates = request.json
        if not updates:
            return jsonify({"success": False, "error": "No updates provided"}), 400

        config_manager = get_user_config()
        success = config_manager.update({"user_profile": updates})

        if success:
            return jsonify({"success": True, "message": "Profile updated"})
        else:
            return jsonify({"success": False, "error": "Failed to save profile"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/settings", methods=["GET"])
def get_settings():
    """
    Get system settings.

    Returns:
        JSON: System settings section only
    """
    try:
        config_manager = get_user_config()
        config = config_manager.load()

        return jsonify({"success": True, "settings": config.get("system_settings", {})})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/settings", methods=["PUT"])
def update_settings():
    """
    Update system settings.

    Body:
        JSON: Settings updates

    Returns:
        JSON: Success status
    """
    try:
        updates = request.json
        if not updates:
            return jsonify({"success": False, "error": "No updates provided"}), 400

        config_manager = get_user_config()
        success = config_manager.update({"system_settings": updates})

        if success:
            return jsonify({"success": True, "message": "Settings updated"})
        else:
            return jsonify({"success": False, "error": "Failed to save settings"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
