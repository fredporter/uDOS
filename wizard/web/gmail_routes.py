"""
Gmail OAuth Web Routes for Wizard Server

Browser-based OAuth flow for Gmail authentication.
Serves HTML page with OAuth button and handles callback.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from wizard.services.gmail_auth import get_gmail_auth

gmail_oauth_bp = Blueprint("gmail_oauth", __name__, url_prefix="/gmail")


@gmail_oauth_bp.route("/")
def index():
    """Gmail OAuth dashboard."""
    auth = get_gmail_auth()

    # Check authentication status
    is_auth = auth.is_authenticated()
    status = auth.get_status() if is_auth else None

    return render_template("gmail_oauth.html", authenticated=is_auth, status=status)


@gmail_oauth_bp.route("/login")
def login():
    """Start OAuth flow - redirect to Google consent screen."""
    auth = get_gmail_auth()

    # Check if already authenticated
    if auth.is_authenticated():
        flash("Already authenticated with Gmail", "info")
        return redirect(url_for("gmail_oauth.index"))

    # Check for credentials file
    if not auth.credentials_path.exists():
        flash(f"Credentials file not found: {auth.credentials_path}", "error")
        return redirect(url_for("gmail_oauth.index"))

    try:
        # Start OAuth flow with web server
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            str(auth.credentials_path),
            scopes=auth.SCOPES,
            redirect_uri=url_for("gmail_oauth.callback", _external=True),
        )

        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )

        # Store state in session for verification
        session["oauth_state"] = state

        return redirect(authorization_url)

    except Exception as e:
        flash(f"Login failed: {str(e)}", "error")
        return redirect(url_for("gmail_oauth.index"))


@gmail_oauth_bp.route("/callback")
def callback():
    """Handle OAuth callback from Google."""
    auth = get_gmail_auth()

    try:
        # Verify state
        state = session.get("oauth_state")
        if not state:
            flash("Invalid state parameter", "error")
            return redirect(url_for("gmail_oauth.index"))

        # Create flow
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            str(auth.credentials_path),
            scopes=auth.SCOPES,
            redirect_uri=url_for("gmail_oauth.callback", _external=True),
            state=state,
        )

        # Fetch token
        flow.fetch_token(authorization_response=request.url)

        # Store credentials
        auth.credentials = flow.credentials
        auth.save_credentials()

        # Load user info
        auth._load_user_info()

        flash(f'Successfully authenticated as {auth.user_info.get("email")}', "success")
        return redirect(url_for("gmail_oauth.index"))

    except Exception as e:
        flash(f"Authentication failed: {str(e)}", "error")
        return redirect(url_for("gmail_oauth.index"))


@gmail_oauth_bp.route("/logout", methods=["POST"])
def logout():
    """Revoke OAuth tokens and logout."""
    auth = get_gmail_auth()

    try:
        result = auth.logout()
        if result["success"]:
            flash(result["message"], "success")
        else:
            flash(result["message"], "warning")
    except Exception as e:
        flash(f"Logout error: {str(e)}", "error")

    return redirect(url_for("gmail_oauth.index"))


@gmail_oauth_bp.route("/status")
def status():
    """API endpoint for authentication status."""
    auth = get_gmail_auth()
    return jsonify(auth.get_status())
