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
from core.services.sync_manager import get_sync_manager, SyncMode, ConflictStrategy


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
    elif subcommand == 'SYNC':
        return _handle_sync(parts[2:], config)
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


def _handle_sync(parts: list, config) -> str:
    """
    Handle SYNC GMAIL subcommands.
    
    Commands:
    - SYNC GMAIL - Run sync now
    - SYNC GMAIL STATUS - Show sync status
    - SYNC GMAIL ENABLE - Enable auto-sync
    - SYNC GMAIL DISABLE - Disable auto-sync
    - SYNC GMAIL CHANGES - Show pending changes
    - SYNC GMAIL HISTORY - Show sync history
    
    Args:
        parts: Command parts after SYNC
        config: Config instance
        
    Returns:
        Formatted output
    """
    auth = get_gmail_auth(config)
    
    if not auth.is_authenticated():
        return "❌ Not authenticated. Use 'LOGIN GMAIL' first."
    
    sync_mgr = get_sync_manager()
    
    if not parts:
        # Default: run sync now
        return _sync_now(sync_mgr)
    
    subcommand = parts[0].upper()
    
    if subcommand == 'NOW':
        return _sync_now(sync_mgr)
    elif subcommand == 'STATUS':
        return _sync_status(sync_mgr)
    elif subcommand == 'ENABLE':
        return _sync_enable(sync_mgr, parts[1:])
    elif subcommand == 'DISABLE':
        return _sync_disable(sync_mgr)
    elif subcommand == 'CHANGES':
        return _sync_changes(sync_mgr)
    elif subcommand == 'HISTORY':
        return _sync_history(sync_mgr, parts[1:])
    else:
        return f"❌ Unknown SYNC subcommand: {subcommand}\n\nUse 'SYNC GMAIL' for help."


def _sync_now(sync_mgr) -> str:
    """Run sync operation now."""
    output = ["🔄 Starting sync...\n"]
    
    result = sync_mgr.sync_now()
    
    if result['success']:
        stats = result['stats']
        output.extend([
            "✅ Sync completed successfully\n",
            f"Uploaded: {stats['uploaded']}",
            f"Downloaded: {stats['downloaded']}",
            f"Deleted: {stats['deleted']}",
            f"Conflicts resolved: {stats['conflicts']}"
        ])
    else:
        output.extend([
            "❌ Sync failed\n",
            f"Errors: {result.get('stats', {}).get('errors', 0)}"
        ])
        
        if result.get('errors'):
            output.append("\nDetails:")
            for error in result['errors'][:5]:  # Show first 5
                output.append(f"  • {error}")
    
    return '\n'.join(output)


def _sync_status(sync_mgr) -> str:
    """Show sync status."""
    status = sync_mgr.get_status()
    
    output = ["═══ Sync Status ═══\n"]
    
    if status['enabled']:
        output.append(f"✅ Auto-sync enabled ({status['mode']})")
        output.append(f"Interval: {status['interval']}s")
    else:
        output.append("❌ Auto-sync disabled")
    
    output.extend([
        f"Conflict strategy: {status['conflict_strategy']}",
        ""
    ])
    
    if status['last_sync']:
        output.extend([
            f"Last sync: {status['time_since_sync']} ago",
            ""
        ])
        
        if status['last_stats']:
            stats = status['last_stats']
            output.extend([
                "Last sync stats:",
                f"  Uploaded: {stats.get('uploaded', 0)}",
                f"  Downloaded: {stats.get('downloaded', 0)}",
                f"  Deleted: {stats.get('deleted', 0)}",
                f"  Conflicts: {stats.get('conflicts', 0)}",
                f"  Errors: {stats.get('errors', 0)}"
            ])
    else:
        output.append("No sync performed yet")
    
    output.append(f"\nTotal syncs: {status['total_syncs']}")
    
    if status['background_running']:
        output.append("🔄 Background sync active")
    
    return '\n'.join(output)


def _sync_enable(sync_mgr, parts: list) -> str:
    """Enable auto-sync."""
    mode = SyncMode.AUTO
    interval = 300  # 5 minutes default
    
    # Parse options
    if parts:
        if parts[0].upper() == 'SCHEDULED':
            mode = SyncMode.SCHEDULED
        
        # Check for interval
        for i, part in enumerate(parts):
            if part.startswith('--interval='):
                try:
                    interval = int(part.split('=')[1])
                except ValueError:
                    return "❌ Invalid interval value"
    
    sync_mgr.enable(mode)
    sync_mgr.set_interval(interval)
    
    return (
        f"✅ Auto-sync enabled\n"
        f"Mode: {mode.value}\n"
        f"Interval: {interval}s\n\n"
        f"Use 'SYNC GMAIL DISABLE' to stop."
    )


def _sync_disable(sync_mgr) -> str:
    """Disable auto-sync."""
    sync_mgr.disable()
    return "✅ Auto-sync disabled"


def _sync_changes(sync_mgr) -> str:
    """Show pending changes."""
    changes = sync_mgr.get_changes()
    
    total = sum(len(v) for v in changes.values())
    
    if total == 0:
        return "✅ No pending changes - everything in sync"
    
    output = [f"📋 Found {total} pending change(s)\n"]
    
    if changes['new_local']:
        output.append(f"New local files ({len(changes['new_local'])}):")
        for path in changes['new_local'][:5]:
            output.append(f"  • {path}")
        if len(changes['new_local']) > 5:
            output.append(f"  ... and {len(changes['new_local']) - 5} more")
        output.append("")
    
    if changes['modified_local']:
        output.append(f"Modified local files ({len(changes['modified_local'])}):")
        for path in changes['modified_local'][:5]:
            output.append(f"  • {path}")
        if len(changes['modified_local']) > 5:
            output.append(f"  ... and {len(changes['modified_local']) - 5} more")
        output.append("")
    
    if changes['new_cloud']:
        output.append(f"New cloud files ({len(changes['new_cloud'])}):")
        for name in changes['new_cloud'][:5]:
            output.append(f"  • {name}")
        if len(changes['new_cloud']) > 5:
            output.append(f"  ... and {len(changes['new_cloud']) - 5} more")
        output.append("")
    
    if changes['modified_cloud']:
        output.append(f"Modified cloud files ({len(changes['modified_cloud'])}):")
        for path in changes['modified_cloud'][:5]:
            output.append(f"  • {path}")
        if len(changes['modified_cloud']) > 5:
            output.append(f"  ... and {len(changes['modified_cloud']) - 5} more")
        output.append("")
    
    if changes['conflicts']:
        output.append(f"⚠️  Conflicts ({len(changes['conflicts'])}):")
        for path in changes['conflicts'][:5]:
            output.append(f"  • {path}")
        if len(changes['conflicts']) > 5:
            output.append(f"  ... and {len(changes['conflicts']) - 5} more")
        output.append("")
    
    output.append("Use 'SYNC GMAIL' to sync now")
    
    return '\n'.join(output)


def _sync_history(sync_mgr, parts: list) -> str:
    """Show sync history."""
    limit = 10
    if parts:
        try:
            limit = int(parts[0])
        except ValueError:
            pass
    
    history = sync_mgr.get_history(limit)
    
    if not history:
        return "No sync history yet"
    
    output = [f"📜 Last {len(history)} sync operation(s)\n"]
    
    for i, entry in enumerate(history, 1):
        timestamp = entry['timestamp'][:19]  # Remove timezone
        success = "✅" if entry['success'] else "❌"
        stats = entry['stats']
        
        output.append(f"{i}. {timestamp} {success}")
        output.append(f"   Up:{stats.get('uploaded', 0)} Down:{stats.get('downloaded', 0)} Del:{stats.get('deleted', 0)} Err:{stats.get('errors', 0)}")
        
        if entry.get('errors'):
            output.append(f"   Errors: {len(entry['errors'])}")
        
        output.append("")
    
    return '\n'.join(output)


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
  EMAIL LIST [query]          - List recent emails
  EMAIL SEND <to> <subject>   - Send email

Cloud Sync (NEW in Part 2):
  SYNC GMAIL                  - Run sync now
  SYNC GMAIL STATUS           - Show sync status
  SYNC GMAIL ENABLE [mode]    - Enable auto-sync
  SYNC GMAIL DISABLE          - Disable auto-sync
  SYNC GMAIL CHANGES          - Show pending changes
  SYNC GMAIL HISTORY [limit]  - Show sync history

Coming Soon (Parts 3-4):
  EMAIL IMPORT           - Convert emails to tasks
  DRIVE UPLOAD <file>    - Upload to App Data
  DRIVE LIST             - List cloud files

Examples:
  LOGIN GMAIL
  STATUS GMAIL
  EMAIL LIST is:unread from:boss
  SYNC GMAIL ENABLE auto --interval=300
  SYNC GMAIL CHANGES
  SYNC GMAIL HISTORY 20

Syncable Directories:
  - memory/missions
  - memory/workflows
  - memory/checklists
  - memory/system/user
  - memory/docs
  - memory/drafts

Conflict Resolution:
  - newest-wins (default)
  - local-wins
  - cloud-wins
  - manual
"""

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
    'SYNC': handle_gmail_command,
    'EMAIL': handle_gmail_command
}
