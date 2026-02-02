"""
Webhooks Routes Blueprint
==========================

Webhook management: register, list, delete, receive, test, events, analytics.
~10 endpoints for webhook integration.
"""

from flask import Blueprint, jsonify, request, g
import time
import logging

from ..services import execute_command, init_udos_systems, get_project_root

api_logger = logging.getLogger("uDOS.API")

# Create blueprint
webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/api/webhooks")

# Try to import webhook services
try:
    from core_beta.services.webhook_manager import get_webhook_manager
    from core_beta.services.github_webhook_handler import get_github_handler
    from core_beta.services.platform_webhook_handlers import (
        get_notion_handler,
        get_clickup_handler,
    )
    from core_beta.services.webhook_event_store import get_event_store

    WEBHOOKS_AVAILABLE = True
except ImportError:
    WEBHOOKS_AVAILABLE = False


# ============================================================================
# WEBHOOK MANAGEMENT
# ============================================================================


@webhooks_bp.route("/register", methods=["POST"])
def webhook_register():
    """Register a new webhook."""
    try:
        data = request.get_json()
        platform = data.get("platform")
        events = data.get("events", [])
        actions = data.get("actions", [])

        if not platform or not events:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Missing required fields: platform, events",
                    }
                ),
                400,
            )

        wh_manager = get_webhook_manager()
        webhook = wh_manager.register_webhook(platform, events, actions)

        api_logger.info(f"Registered webhook: {webhook.id} for {platform}")

        return jsonify(
            {
                "status": "success",
                "webhook": {
                    "id": webhook.id,
                    "platform": webhook.platform,
                    "url": f"http://localhost:5001{webhook.url}",
                    "secret": webhook.secret,
                    "events": webhook.events,
                    "created": webhook.created,
                },
            }
        )
    except Exception as e:
        api_logger.error(f"Webhook registration error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@webhooks_bp.route("/list")
def webhook_list():
    """List all registered webhooks."""
    try:
        platform = request.args.get("platform")
        wh_manager = get_webhook_manager()
        webhooks = wh_manager.list_webhooks(platform)

        return jsonify(
            {
                "status": "success",
                "count": len(webhooks),
                "webhooks": [
                    {
                        "id": wh.id,
                        "platform": wh.platform,
                        "url": wh.url,
                        "events": wh.events,
                        "enabled": wh.enabled,
                        "trigger_count": wh.trigger_count,
                        "last_triggered": wh.last_triggered,
                        "created": wh.created,
                    }
                    for wh in webhooks
                ],
            }
        )
    except Exception as e:
        api_logger.error(f"Webhook list error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@webhooks_bp.route("/delete/<webhook_id>", methods=["DELETE"])
def webhook_delete(webhook_id):
    """Delete a webhook."""
    try:
        wh_manager = get_webhook_manager()
        success = wh_manager.delete_webhook(webhook_id)

        if success:
            api_logger.info(f"Deleted webhook: {webhook_id}")
            return jsonify({"status": "success", "message": "Webhook deleted"})
        else:
            return jsonify({"status": "error", "message": "Webhook not found"}), 404
    except Exception as e:
        api_logger.error(f"Webhook deletion error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@webhooks_bp.route("/receive/<platform>", methods=["POST"])
def webhook_receive(platform):
    """Receive webhook events from external platforms."""
    start_time = time.time()
    event_store = get_event_store()

    try:
        wh_manager = get_webhook_manager()
        payload = request.get_data()
        data = request.get_json()

        webhooks = wh_manager.list_webhooks(platform)
        if not webhooks:
            api_logger.warning(f"No webhooks registered for platform: {platform}")
            return (
                jsonify({"status": "error", "message": "No webhooks configured"}),
                404,
            )

        webhook = webhooks[0]
        webhook_secret = webhook.secret
        results = []

        # Platform-specific processing
        if platform == "github":
            signature = request.headers.get("X-Hub-Signature-256", "")
            signature_valid = wh_manager.validate_signature_github(
                payload, signature, webhook_secret
            )
            event_type = request.headers.get("X-GitHub-Event", "unknown")

            github_handler = get_github_handler()
            github_result = github_handler.process_event(event_type, data)
            api_logger.info(f'GitHub event processed: {github_result.get("status")}')

        # Additional platform handling...

        if not signature_valid:
            api_logger.warning(f"Invalid webhook signature from {platform}")
            return jsonify({"status": "error", "message": "Invalid signature"}), 401

        wh_manager.record_trigger(webhook.id)
        actions = wh_manager.get_actions_for_event(webhook.id, event_type)

        response_data = {
            "status": "success",
            "platform": platform,
            "event": event_type,
            "actions_triggered": len(results),
            "results": results,
        }

        return jsonify(response_data)

    except Exception as e:
        api_logger.error(f"Webhook receive error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@webhooks_bp.route("/test/<webhook_id>", methods=["POST"])
def webhook_test(webhook_id):
    """Test a webhook with sample data."""
    try:
        data = request.get_json()
        event = data.get("event", "test")
        test_data = data.get("test_data", {})

        wh_manager = get_webhook_manager()
        webhook = wh_manager.get_webhook(webhook_id)

        if not webhook:
            return jsonify({"status": "error", "message": "Webhook not found"}), 404

        actions = wh_manager.get_actions_for_event(webhook_id, event)

        api_logger.info(f"Testing webhook {webhook_id} with event {event}")

        return jsonify(
            {
                "status": "success",
                "webhook_id": webhook_id,
                "event": event,
                "actions_found": len(actions),
                "actions": actions,
                "test_data": test_data,
            }
        )

    except Exception as e:
        api_logger.error(f"Webhook test error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# WEBHOOK EVENTS & ANALYTICS
# ============================================================================


@webhooks_bp.route("/events", methods=["GET"])
def list_webhook_events():
    """List webhook event history with filtering."""
    try:
        event_store = get_event_store()

        platform = request.args.get("platform")
        webhook_id = request.args.get("webhook_id")
        event_type = request.args.get("event_type")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        events = event_store.list_events(
            platform=platform,
            webhook_id=webhook_id,
            event_type=event_type,
            limit=limit,
            offset=offset,
        )

        return jsonify(
            {
                "status": "success",
                "events": events,
                "count": len(events),
                "limit": limit,
                "offset": offset,
            }
        )

    except Exception as e:
        api_logger.error(f"List events error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@webhooks_bp.route("/events/<event_id>", methods=["GET"])
def get_webhook_event(event_id):
    """Get specific webhook event details."""
    try:
        event_store = get_event_store()
        event = event_store.get_event(event_id)

        if not event:
            return jsonify({"status": "error", "message": "Event not found"}), 404

        return jsonify({"status": "success", "event": event})

    except Exception as e:
        api_logger.error(f"Get event error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@webhooks_bp.route("/analytics", methods=["GET"])
def get_webhook_analytics():
    """Get webhook analytics and metrics."""
    try:
        event_store = get_event_store()
        days = int(request.args.get("days", 7))

        analytics = event_store.get_analytics(days=days)

        return jsonify(
            {"status": "success", "analytics": analytics, "period_days": days}
        )

    except Exception as e:
        api_logger.error(f"Get analytics error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
