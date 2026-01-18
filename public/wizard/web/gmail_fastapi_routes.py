"""
Gmail OAuth Routes for FastAPI Wizard Server

Browser-based OAuth flow for Gmail authentication.
Converted from Flask blueprint to FastAPI.
"""

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from wizard.services.gmail_auth import get_gmail_auth

# Router
gmail_router = APIRouter(prefix="/gmail", tags=["gmail"])

# Templates
WIZARD_ROOT = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(WIZARD_ROOT / "web" / "templates"))


@gmail_router.get("/", response_class=HTMLResponse)
async def gmail_oauth_page(request: Request):
    """Gmail OAuth dashboard page."""
    auth = get_gmail_auth()

    # Check authentication status
    is_auth = auth.is_authenticated()
    status = auth.get_status() if is_auth else None

    # Get and clear flash message
    flash = request.session.pop("flash_message", None)
    message = flash[1] if flash else None
    message_type = flash[0] if flash else None

    return templates.TemplateResponse(
        "gmail_oauth.html",
        {
            "request": request,
            "authenticated": is_auth,
            "status": status,
            "message": message,
            "message_type": message_type,
        },
    )


@gmail_router.get("/login")
async def gmail_login(request: Request):
    """Start OAuth flow - redirect to Google consent screen."""
    auth = get_gmail_auth()

    # Check if already authenticated
    if auth.is_authenticated():
        request.session["flash_messages"] = [
            ("info", "Already authenticated with Gmail")
        ]
        return RedirectResponse(url="/gmail/", status_code=303)

    # Check for credentials file
    if not auth.credentials_path.exists():
        request.session["flash_messages"] = [
            (
                "error",
                f"Credentials file not found: {auth.credentials_path}. "
                "Please follow the setup guide in wiki/Google-Cloud-Console-Setup.md",
            )
        ]
        return RedirectResponse(url="/gmail/", status_code=303)

    try:
        # Start OAuth flow with web server
        from google_auth_oauthlib.flow import Flow

        # Build redirect URI
        redirect_uri = str(request.url_for("gmail_callback"))

        flow = Flow.from_client_secrets_file(
            str(auth.credentials_path), scopes=auth.SCOPES, redirect_uri=redirect_uri
        )

        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )

        # Store state in session for verification
        request.session["oauth_state"] = state

        return RedirectResponse(url=authorization_url, status_code=303)

    except Exception as e:
        request.session["flash_messages"] = [("error", f"Login failed: {str(e)}")]
        return RedirectResponse(url="/gmail/", status_code=303)


@gmail_router.get("/callback")
async def gmail_callback(request: Request):
    """Handle OAuth callback from Google."""
    auth = get_gmail_auth()

    try:
        # Verify state
        state = request.session.get("oauth_state")
        if not state:
            request.session["flash_messages"] = [("error", "Invalid state parameter")]
            return RedirectResponse(url="/gmail/", status_code=303)

        # Create flow
        from google_auth_oauthlib.flow import Flow

        redirect_uri = str(request.url_for("gmail_callback"))

        flow = Flow.from_client_secrets_file(
            str(auth.credentials_path),
            scopes=auth.SCOPES,
            redirect_uri=redirect_uri,
            state=state,
        )

        # Fetch token
        authorization_response = str(request.url)
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials
        auth.credentials = flow.credentials
        auth.save_credentials()

        # Load user info
        auth._load_user_info()

        request.session["flash_message"] = (
            "success",
            f'✅ Successfully authenticated as {auth.user_info.get("email")}',
        )
        return RedirectResponse(url="/gmail/", status_code=303)

    except Exception as e:
        request.session["flash_message"] = ("error", f"Authentication failed: {str(e)}")
        return RedirectResponse(url="/gmail/", status_code=303)


@gmail_router.post("/logout")
async def gmail_logout(request: Request):
    """Revoke OAuth tokens and logout."""
    auth = get_gmail_auth()

    try:
        result = auth.logout()
        if result["success"]:
            request.session["flash_messages"] = [("success", result["message"])]
        else:
            request.session["flash_messages"] = [("warning", result["message"])]
    except Exception as e:
        request.session["flash_messages"] = [("error", f"Logout error: {str(e)}")]

    return RedirectResponse(url="/gmail/", status_code=303)


@gmail_router.get("/status")
async def gmail_status():
    """API endpoint for authentication status."""
    auth = get_gmail_auth()
    return JSONResponse(auth.get_status())
