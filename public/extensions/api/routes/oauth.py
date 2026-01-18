"""
OAuth Routes
============

API routes for OAuth connection management.
Handles auth URLs, callbacks, and connection status.

Wizard Server only - these endpoints require network access.
"""

from flask import Blueprint, jsonify, request, redirect, url_for
import asyncio
import sys
from pathlib import Path

# Add wizard to path
wizard_path = Path(__file__).parent.parent.parent.parent / "wizard"
if str(wizard_path) not in sys.path:
    sys.path.insert(0, str(wizard_path))

try:
    from wizard.services.oauth_manager import (
        get_oauth_manager,
        OAuthProvider,
        list_connections,
    )

    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False


oauth_bp = Blueprint("oauth", __name__, url_prefix="/api/oauth")


def run_async(coro):
    """Run async function from sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@oauth_bp.route("/status", methods=["GET"])
def get_oauth_status():
    """
    Get status of all OAuth connections.

    Returns:
        {
            "google": {"status": "connected", "user": "user@gmail.com"},
            "github": {"status": "pending_auth", "user": null},
            ...
        }
    """
    if not OAUTH_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "OAuth manager not available",
                    "available": False,
                }
            ),
            503,
        )

    connections = list_connections()
    return jsonify(
        {
            "connections": connections,
            "available": True,
        }
    )


@oauth_bp.route("/connect/<provider>", methods=["GET"])
def get_auth_url(provider: str):
    """
    Get OAuth authorization URL for a provider.

    Args:
        provider: Provider name (google, github, spotify, etc.)

    Query params:
        scopes: Additional scopes (comma-separated)

    Returns:
        {"auth_url": "https://..."}
    """
    if not OAUTH_AVAILABLE:
        return jsonify({"error": "OAuth not available"}), 503

    try:
        provider_enum = OAuthProvider(provider.lower())
    except ValueError:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400

    manager = get_oauth_manager()

    # Parse extra scopes from query
    extra_scopes = []
    if request.args.get("scopes"):
        extra_scopes = request.args.get("scopes").split(",")

    auth_url = manager.get_auth_url(provider_enum, extra_scopes)

    if not auth_url:
        return (
            jsonify(
                {
                    "error": f"Provider {provider} not configured",
                    "hint": "Add client_id and client_secret to wizard/config/oauth_providers.json",
                }
            ),
            400,
        )

    return jsonify(
        {
            "auth_url": auth_url,
            "provider": provider,
        }
    )


@oauth_bp.route("/callback", methods=["GET"])
def oauth_callback():
    """
    Handle OAuth callback from provider.

    Query params:
        code: Authorization code
        state: CSRF state token
        error: Error from provider (if any)
    """
    if not OAUTH_AVAILABLE:
        return "OAuth not available", 503

    # Check for error
    if request.args.get("error"):
        error = request.args.get("error")
        error_desc = request.args.get("error_description", "Unknown error")
        return (
            f"""
        <html>
        <head><title>OAuth Error</title></head>
        <body style="font-family: sans-serif; padding: 2rem;">
            <h1>❌ Connection Failed</h1>
            <p><strong>Error:</strong> {error}</p>
            <p><strong>Description:</strong> {error_desc}</p>
            <p><a href="javascript:window.close()">Close this window</a></p>
        </body>
        </html>
        """,
            400,
        )

    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return "Missing code or state", 400

    manager = get_oauth_manager()

    try:
        connection = run_async(manager.handle_callback(code, state))

        return f"""
        <html>
        <head><title>Connected!</title></head>
        <body style="font-family: sans-serif; padding: 2rem; text-align: center;">
            <h1>✅ Connected to {connection.display_name}!</h1>
            <p>Logged in as: <strong>{connection.user_display}</strong></p>
            <p>You can close this window and return to uDOS.</p>
            <script>
                // Notify parent window if in popup
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'oauth_success',
                        provider: '{connection.provider.value}',
                        user: '{connection.user_display}'
                    }}, '*');
                    setTimeout(() => window.close(), 2000);
                }}
            </script>
        </body>
        </html>
        """

    except ValueError as e:
        return f"Error: {e}", 400
    except Exception as e:
        return f"Connection failed: {e}", 500


@oauth_bp.route("/disconnect/<provider>", methods=["POST", "DELETE"])
def disconnect_provider(provider: str):
    """
    Disconnect/revoke OAuth for a provider.

    Args:
        provider: Provider name
    """
    if not OAUTH_AVAILABLE:
        return jsonify({"error": "OAuth not available"}), 503

    try:
        provider_enum = OAuthProvider(provider.lower())
    except ValueError:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400

    manager = get_oauth_manager()
    result = run_async(manager.disconnect(provider_enum))

    return jsonify(
        {
            "disconnected": result,
            "provider": provider,
        }
    )


@oauth_bp.route("/refresh/<provider>", methods=["POST"])
def refresh_provider(provider: str):
    """
    Force refresh token for a provider.

    Args:
        provider: Provider name
    """
    if not OAUTH_AVAILABLE:
        return jsonify({"error": "OAuth not available"}), 503

    try:
        provider_enum = OAuthProvider(provider.lower())
    except ValueError:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400

    manager = get_oauth_manager()
    result = run_async(manager.refresh_token(provider_enum))

    return jsonify(
        {
            "refreshed": result,
            "provider": provider,
        }
    )


@oauth_bp.route("/providers", methods=["GET"])
def list_providers():
    """
    List available OAuth providers.

    Returns:
        List of provider names and their configuration status
    """
    if not OAUTH_AVAILABLE:
        return jsonify({"error": "OAuth not available"}), 503

    manager = get_oauth_manager()
    providers = []

    for provider in OAuthProvider:
        if provider != OAuthProvider.CUSTOM:
            conn = manager.get_connection(provider)
            providers.append(
                {
                    "id": provider.value,
                    "name": conn.display_name,
                    "status": conn.status.value,
                    "configured": conn.status.value != "not_configured",
                }
            )

    return jsonify({"providers": providers})
