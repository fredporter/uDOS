"""
Dashboard Routes Blueprint
==========================

Dashboard data endpoints: status, missions, workflows, checklists, XP, system.
~6 endpoints for dashboard panels.
"""

from flask import Blueprint, jsonify, g
import logging

from ..services import init_udos_systems

api_logger = logging.getLogger("uDOS.API")

# Create blueprint
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


def get_dashboard_service():
    """Get dashboard data service."""
    from ..services.executor import _services

    return _services.get("dashboard")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================


@dashboard_bp.route("/status", methods=["GET"])
def get_dashboard_status_api():
    """Get complete dashboard status."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting dashboard status")

        dashboard_service = get_dashboard_service()
        if dashboard_service is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Dashboard data service not initialized",
                    }
                ),
                500,
            )

        status = dashboard_service.get_dashboard_status()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved dashboard status")
        return jsonify({"status": "success", "data": status})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting dashboard status: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@dashboard_bp.route("/missions", methods=["GET"])
def get_missions_panel():
    """Get missions panel data."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting missions panel data")

        dashboard_service = get_dashboard_service()
        if dashboard_service is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Dashboard data service not initialized",
                    }
                ),
                500,
            )

        data = dashboard_service.get_missions_panel_data()

        api_logger.info(
            f"[{correlation_id}] ✓ Retrieved {data['count']} active missions"
        )
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting missions: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@dashboard_bp.route("/workflows", methods=["GET"])
def get_workflows_panel():
    """Get workflows panel data."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting workflows panel data")

        dashboard_service = get_dashboard_service()
        if dashboard_service is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Dashboard data service not initialized",
                    }
                ),
                500,
            )

        data = dashboard_service.get_workflows_panel_data()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved workflow status")
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting workflows: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@dashboard_bp.route("/checklists", methods=["GET"])
def get_checklists_panel():
    """Get checklists panel data."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting checklists panel data")

        dashboard_service = get_dashboard_service()
        if dashboard_service is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Dashboard data service not initialized",
                    }
                ),
                500,
            )

        data = dashboard_service.get_checklists_panel_data()

        api_logger.info(
            f"[{correlation_id}] ✓ Retrieved {data['count']} active checklists"
        )
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting checklists: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@dashboard_bp.route("/xp", methods=["GET"])
def get_xp_panel():
    """Get XP and achievements panel data."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting XP panel data")

        dashboard_service = get_dashboard_service()
        if dashboard_service is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Dashboard data service not initialized",
                    }
                ),
                500,
            )

        data = dashboard_service.get_xp_panel_data()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved XP data")
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error getting XP: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@dashboard_bp.route("/system", methods=["GET"])
def get_system_panel():
    """Get system status panel data."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting system panel data")

        dashboard_service = get_dashboard_service()
        if dashboard_service is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Dashboard data service not initialized",
                    }
                ),
                500,
            )

        data = dashboard_service.get_system_panel_data()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved system status")
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting system status: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500
