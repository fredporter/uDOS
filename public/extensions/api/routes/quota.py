"""
Quota Routes
============

API routes for quota management dashboard.
Displays usage, limits, costs, and queue status.
"""

from flask import Blueprint, jsonify, request
import sys
from pathlib import Path

# Add wizard to path
wizard_path = Path(__file__).parent.parent.parent.parent / "wizard"
if str(wizard_path) not in sys.path:
    sys.path.insert(0, str(wizard_path))

try:
    from wizard.services.quota_tracker import (
        get_quota_tracker,
        APIProvider,
        RequestPriority,
    )

    QUOTA_AVAILABLE = True
except ImportError:
    QUOTA_AVAILABLE = False


quota_bp = Blueprint("quota", __name__, url_prefix="/api/quota")


@quota_bp.route("/status", methods=["GET"])
def get_quota_status():
    """
    Get overall quota status and summary.

    Returns dashboard-ready summary of all providers.
    """
    if not QUOTA_AVAILABLE:
        return jsonify({"error": "Quota tracker not available"}), 503

    tracker = get_quota_tracker()
    return jsonify(
        {
            "summary": tracker.get_dashboard_summary(),
            "all_providers": tracker.get_all_quotas(),
        }
    )


@quota_bp.route("/provider/<provider>", methods=["GET"])
def get_provider_quota(provider: str):
    """
    Get detailed quota for a specific provider.

    Args:
        provider: Provider name (gemini, anthropic, github, etc.)
    """
    if not QUOTA_AVAILABLE:
        return jsonify({"error": "Quota tracker not available"}), 503

    try:
        provider_enum = APIProvider(provider.lower())
    except ValueError:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400

    tracker = get_quota_tracker()
    return jsonify(tracker.get_quota_status(provider_enum))


@quota_bp.route("/provider/<provider>/limits", methods=["PUT", "PATCH"])
def update_provider_limits(provider: str):
    """
    Update quota limits for a provider.

    JSON body:
        {
            "daily_budget": 10.0,
            "monthly_budget": 100.0,
            "requests_per_day": 2000
        }
    """
    if not QUOTA_AVAILABLE:
        return jsonify({"error": "Quota tracker not available"}), 503

    try:
        provider_enum = APIProvider(provider.lower())
    except ValueError:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400

    data = request.get_json() or {}

    tracker = get_quota_tracker()
    tracker.update_provider_limits(
        provider_enum,
        daily_budget=data.get("daily_budget"),
        monthly_budget=data.get("monthly_budget"),
        requests_per_day=data.get("requests_per_day"),
    )

    return jsonify(
        {
            "updated": True,
            "provider": provider,
            "status": tracker.get_quota_status(provider_enum),
        }
    )


@quota_bp.route("/queue", methods=["GET"])
def get_queue_status():
    """
    Get request queue status.

    Shows pending requests by priority and provider.
    """
    if not QUOTA_AVAILABLE:
        return jsonify({"error": "Quota tracker not available"}), 503

    tracker = get_quota_tracker()
    return jsonify(tracker.get_queue_status())


@quota_bp.route("/queue", methods=["POST"])
def queue_request():
    """
    Queue a new API request.

    JSON body:
        {
            "provider": "gemini",
            "endpoint": "/v1/models/gemini-pro:generateContent",
            "payload": {...},
            "priority": "normal",
            "workflow_id": "wf-123",
            "estimated_tokens": 1000
        }
    """
    if not QUOTA_AVAILABLE:
        return jsonify({"error": "Quota tracker not available"}), 503

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    try:
        provider = APIProvider(data.get("provider", "").lower())
    except ValueError:
        return jsonify({"error": f"Unknown provider: {data.get('provider')}"}), 400

    # Parse priority
    priority_str = data.get("priority", "normal").upper()
    try:
        priority = RequestPriority[priority_str]
    except KeyError:
        priority = RequestPriority.NORMAL

    tracker = get_quota_tracker()
    request_id = tracker.queue_request(
        provider=provider,
        endpoint=data.get("endpoint", ""),
        payload=data.get("payload", {}),
        priority=priority,
        workflow_id=data.get("workflow_id"),
        objective_id=data.get("objective_id"),
        estimated_tokens=data.get("estimated_tokens", 0),
    )

    return jsonify(
        {
            "queued": True,
            "request_id": request_id,
            "queue_position": len([r for r in tracker._queue if r.status == "pending"]),
        }
    )


@quota_bp.route("/summary", methods=["GET"])
def get_summary():
    """
    Get simple summary for dashboard widget.

    Returns minimal data for quick display.
    """
    if not QUOTA_AVAILABLE:
        return jsonify(
            {
                "cost_today": "$0.00",
                "requests_today": 0,
                "warnings": ["Quota tracker not available"],
            }
        )

    tracker = get_quota_tracker()
    return jsonify(tracker.get_dashboard_summary())


@quota_bp.route("/history", methods=["GET"])
def get_history():
    """
    Get recent request history.

    Query params:
        limit: Number of records (default 50)
        provider: Filter by provider
    """
    if not QUOTA_AVAILABLE:
        return jsonify({"error": "Quota tracker not available"}), 503

    limit = request.args.get("limit", 50, type=int)
    provider_filter = request.args.get("provider")

    tracker = get_quota_tracker()
    history = tracker._history[-limit:]

    if provider_filter:
        history = [h for h in history if h["provider"] == provider_filter]

    return jsonify(
        {
            "history": history,
            "count": len(history),
        }
    )


@quota_bp.route("/check/<provider>", methods=["GET"])
def check_can_request(provider: str):
    """
    Check if a request can be made to a provider.

    Query params:
        tokens: Estimated token count
    """
    if not QUOTA_AVAILABLE:
        return jsonify({"can_request": True, "reason": "Quota tracker unavailable"})

    try:
        provider_enum = APIProvider(provider.lower())
    except ValueError:
        return jsonify({"can_request": True, "reason": "Unknown provider"})

    tokens = request.args.get("tokens", 0, type=int)

    tracker = get_quota_tracker()
    can_request = tracker.can_request(provider_enum, tokens)

    status = tracker.get_quota_status(provider_enum)

    return jsonify(
        {
            "can_request": can_request,
            "provider": provider,
            "status": status.get("status", "unknown"),
            "daily_usage_percent": status.get("daily", {}).get("usage_percent", 0),
        }
    )
