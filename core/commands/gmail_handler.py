"""
Gmail Cloud Integration Command Handler for uDOS v1.2.9

Handles Gmail authentication and cloud sync commands:
- LOGIN GMAIL - OAuth2 authentication
- LOGOUT GMAIL - Revoke tokens
- STATUS GMAIL - Show auth status
- SYNC GMAIL - Sync data to Drive (future)

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

from typing import Dict, Any, Optional
from pathlib import Path

from core.services.gmail_auth import get_gmail_auth
from core.services.gmail_service import get_gmail_service, get_drive_service


def handle_gmail_command(parts: list, config=None, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Handle Gmail-related commands.

    Commands:
    - LOGIN GMAIL - Start OAuth2 authentication flow
    - LOGOUT GMAIL - Revoke tokens and clear credentials
    - STATUS GMAIL - Show current authentication status
    - EMAIL LIST [query] - List emails (requires login)
    - EMAIL SEND <to> <subject> - Send email (requires login)

    Args:
        parts: Command parts (e.g., ['LOGIN', 'GMAIL'])
        config: Optional Config instance
        context: Optional execution context

    Returns:
        Formatted output string
    """
    if len(parts) < 2:
        return _show_help()

    subcommand = parts[1].upper()

    if subcommand == 'LOGIN':
        return _handle_login(config)
    elif subcommand == 'LOGOUT':
        return _handle_logout(config)
    elif subcommand == 'STATUS':
        return _handle_status(config)
    elif subcommand == 'EMAIL':
        return _handle_email(parts[2:], config)
    else:
        return f"❌ Unknown Gmail command: {subcommand}\n\n{_show_help()}"


def _handle_login(config) -> str:
    """
    Handle LOGIN GMAIL command.

    Starts OAuth2 flow, opens browser for consent,
    retrieves and saves encrypted tokens.

    Returns:
        Status message
    """
    auth = get_gmail_auth(config)

    # Check if already logged in
    if auth.is_authenticated():
        status = auth.get_status()
        return (
            f"✅ Already authenticated\n\n"
            f"Email: {status['email']}\n"
            f"Name: {status['name']}\n"
            f"Token expires: {status['token_expiry']}\n\n"
            f"Use 'LOGOUT GMAIL' to logout."
        )

    # Start login flow
    output = [
        "🔐 Starting Gmail authentication...\n",
        "A browser window will open for Google consent.\n",
        "Please authorize uDOS to access your Gmail and Drive.\n",
        ""
    ]

    result = auth.login()

    if result['success']:
        output.extend([
            f"✅ {result['message']}\n",
            f"Email: {result['email']}",
            f"Name: {result['name']}",
            "",
            "You can now use:",
            "  - EMAIL LIST - View emails",
            "  - EMAIL SEND - Send emails",
            "  - SYNC GMAIL - Sync to Drive (coming soon)"
        ])
    else:
        output.extend([
            f"❌ {result['message']}\n",
            "",
            "Make sure you have downloaded OAuth credentials from",
            "Google Cloud Console and saved as:",
            "  memory/system/user/gmail_credentials.json"
        ])

    return '\n'.join(output)


def _handle_logout(config) -> str:
    """
    Handle LOGOUT GMAIL command.

    Revokes tokens with Google and clears local credentials.

    Returns:
        Status message
    """
    auth = get_gmail_auth(config)

    if not auth.is_authenticated():
        return "ℹ️  Not currently logged in to Gmail."

    result = auth.logout()

    if result['success']:
        return f"✅ {result['message']}"
    else:
        return f"❌ {result['message']}"


def _handle_status(config) -> str:
    """
    Handle STATUS GMAIL command.

    Shows current authentication status, user info,
    token expiry, and quota usage.

    Returns:
        Formatted status information
    """
    auth = get_gmail_auth(config)
    status = auth.get_status()

    output = ["═══ Gmail Cloud Status ═══\n"]

    if status['authenticated']:
        output.extend([
            f"✅ Authenticated",
            f"Email: {status['email']}",
            f"Name: {status['name']}",
            f"Token expires: {status['token_expiry']}",
            ""
        ])

        # Get Drive quota
        drive = get_drive_service()
        if drive.is_available():
            quota = drive.get_quota_usage()
            used_mb = quota['used'] / (1024 * 1024)
            limit_mb = quota['limit'] / (1024 * 1024)
            available_mb = quota['available'] / (1024 * 1024)
            percent = (quota['used'] / quota['limit'] * 100) if quota['limit'] > 0 else 0

            output.extend([
                "Drive App Data Quota:",
                f"  Used: {used_mb:.2f} MB / {limit_mb:.2f} MB ({percent:.1f}%)",
                f"  Available: {available_mb:.2f} MB",
                ""
            ])

        output.extend([
            "OAuth Scopes:",
            "  ✓ drive.appdata - App folder (15MB)",
            "  ✓ gmail.readonly - Read emails",
            "  ✓ gmail.send - Send emails",
            "  ✓ userinfo.email - User profile"
        ])
    else:
        output.extend([
            "❌ Not authenticated",
            "",
            "Use 'LOGIN GMAIL' to authenticate."
        ])

    return '\n'.join(output)


def _handle_email(parts: list, config) -> str:
    """
    Handle EMAIL subcommands.

    Commands:
    - EMAIL LIST [query] - List emails
    - EMAIL SEND <to> <subject> - Send email

    Args:
        parts: Command parts after EMAIL
        config: Config instance

    Returns:
        Formatted output
    """
    if not parts:
        return (
            "❌ Missing EMAIL subcommand\n\n"
            "Usage:\n"
            "  EMAIL LIST [query] - List emails\n"
            "  EMAIL SEND <to> <subject> - Send email"
        )

    subcommand = parts[0].upper()

    if subcommand == 'LIST':
        return _handle_email_list(parts[1:], config)
    elif subcommand == 'SEND':
        return _handle_email_send(parts[1:], config)
    else:
        return f"❌ Unknown EMAIL subcommand: {subcommand}"


def _handle_email_list(parts: list, config) -> str:
    """
    Handle EMAIL LIST command.

    Lists recent emails with optional search query.

    Args:
        parts: Command parts (optional query)
        config: Config instance

    Returns:
        Formatted email list
    """
    gmail = get_gmail_service()

    if not gmail.is_available():
        return "❌ Not authenticated. Use 'LOGIN GMAIL' first."

    # Build query
    query = ' '.join(parts) if parts else ""

    # Get messages
    messages = gmail.get_messages(query=query, max_results=10)

    if not messages:
        return f"No emails found{' for query: ' + query if query else ''}."

    output = [f"📧 Found {len(messages)} email(s){' for: ' + query if query else ''}\n"]

    for i, msg in enumerate(messages, 1):
        output.extend([
            f"{i}. {msg['subject']}",
            f"   From: {msg['from']}",
            f"   Date: {msg['date']}",
            f"   {msg['snippet'][:80]}...",
            ""
        ])

    return '\n'.join(output)


def _handle_email_send(parts: list, config) -> str:
    """
    Handle EMAIL SEND command.

    Interactive email composition and sending.

    Args:
        parts: Command parts (to, subject)
        config: Config instance

    Returns:
        Send status
    """
    gmail = get_gmail_service()

    if not gmail.is_available():
        return "❌ Not authenticated. Use 'LOGIN GMAIL' first."

    if len(parts) < 2:
        return (
            "❌ Missing required arguments\n\n"
            "Usage: EMAIL SEND <to> <subject>\n"
            "Example: EMAIL SEND boss@company.com \"Weekly Update\""
        )

    to = parts[0]
    subject = ' '.join(parts[1:])

    # In interactive mode, this would prompt for body
    # For now, return instructions
    return (
        f"📧 Compose email:\n"
        f"To: {to}\n"
        f"Subject: {subject}\n\n"
        f"[Interactive composition coming in Part 3 - Email to Markdown]\n\n"
        f"For now, use gmail_service.send_message() directly in scripts."
    )


def _show_help() -> str:
    """
    Show Gmail command help.

    Returns:
        Help text
    """
    return """
Gmail Cloud Integration Commands

Authentication:
  LOGIN GMAIL       - Start OAuth2 authentication
  LOGOUT GMAIL      - Revoke tokens and logout
  STATUS GMAIL      - Show auth status and quota

Email Operations:
  EMAIL LIST [query]     - List recent emails
  EMAIL SEND <to> <subject> - Send email

Coming Soon (Parts 2-4):
  SYNC GMAIL             - Sync data to Drive
  EMAIL IMPORT           - Convert emails to tasks
  DRIVE UPLOAD <file>    - Upload to App Data
  DRIVE LIST             - List cloud files

Examples:
  LOGIN GMAIL
  STATUS GMAIL
  EMAIL LIST is:unread from:boss
  EMAIL SEND colleague@company.com "Meeting Notes"
"""


# Register command
GMAIL_COMMANDS = {
    'LOGIN': handle_gmail_command,
    'LOGOUT': handle_gmail_command,
    'STATUS': handle_gmail_command,
    'EMAIL': handle_gmail_command
}
