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
from core.services.email_parser import get_email_parser
from core.services.email_converter import get_email_converter


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
    elif subcommand == 'IMPORT':
        return _handle_import(parts[2:], config)
    elif subcommand == 'QUOTA':
        return _handle_quota(config)
    elif subcommand == 'CONFIG':
        return _handle_config(parts[2:], config)
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
    elif subcommand == 'DOWNLOAD':
        return _handle_email_download(parts[1:], config)
    elif subcommand == 'TASKS':
        return _handle_email_tasks(parts[1:], config)
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


def _handle_import(parts: list, config) -> str:
    """
    Handle EMAIL IMPORT subcommands.

    Commands:
    - IMPORT GMAIL [query] - Import emails as notes/tasks/missions
    - IMPORT GMAIL --preview [query] - Preview without importing
    - IMPORT GMAIL --type=<note|checklist|mission> [query]

    Args:
        parts: Command parts after IMPORT
        config: Config instance

    Returns:
        Formatted output
    """
    gmail = get_gmail_service()

    if not gmail.is_available():
        return "❌ Not authenticated. Use 'LOGIN GMAIL' first."

    parser = get_email_parser()
    converter = get_email_converter()

    # Parse options
    preview_only = False
    import_type = 'auto'  # auto, note, checklist, mission
    query = []
    max_results = 10

    for part in parts:
        if part.startswith('--preview'):
            preview_only = True
        elif part.startswith('--type='):
            import_type = part.split('=')[1].lower()
        elif part.startswith('--limit='):
            try:
                max_results = int(part.split('=')[1])
            except ValueError:
                pass
        else:
            query.append(part)

    query_str = ' '.join(query)

    # Get emails
    output = [f"📥 Importing emails{' (preview mode)' if preview_only else ''}"]
    if query_str:
        output.append(f"Query: {query_str}")
    output.append("")

    messages = gmail.get_messages(query=query_str, max_results=max_results)

    if not messages:
        return '\n'.join(output) + "No emails found."

    output.append(f"Found {len(messages)} email(s)\n")

    # Process each email
    results = {
        'note': 0,
        'checklist': 0,
        'mission': 0,
        'errors': 0
    }

    for i, msg in enumerate(messages, 1):
        subject = msg.get('subject', 'No Subject')
        from_addr = msg.get('from', 'Unknown')

        output.append(f"{i}. {subject}")
        output.append(f"   From: {from_addr}")

        if preview_only:
            # Just parse and show what would be created
            parsed = parser.parse_email(msg)
            task_count = len(parsed.get('tasks', []))

            if import_type == 'auto':
                if task_count >= 3:
                    suggested = 'mission'
                elif task_count > 0:
                    suggested = 'checklist'
                else:
                    suggested = 'note'
            else:
                suggested = import_type

            output.append(f"   → Would create: {suggested} ({task_count} tasks)")
        else:
            # Actually import
            try:
                if import_type == 'auto':
                    result = converter.auto_convert(msg)
                elif import_type == 'note':
                    result = converter.convert_to_note(msg)
                elif import_type == 'checklist':
                    result = converter.convert_to_checklist(msg)
                elif import_type == 'mission':
                    result = converter.convert_to_mission(msg)
                else:
                    result = {'success': False, 'error': f'Unknown type: {import_type}'}

                if result['success']:
                    conv_type = result['type']
                    results[conv_type] += 1
                    output.append(f"   ✅ Created {conv_type}: {result['filename']}")
                else:
                    results['errors'] += 1
                    output.append(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                results['errors'] += 1
                output.append(f"   ❌ Error: {e}")

        output.append("")

    # Summary
    if not preview_only:
        output.append("=" * 60)
        output.append("Import Summary:")
        output.append(f"  Notes: {results['note']}")
        output.append(f"  Checklists: {results['checklist']}")
        output.append(f"  Missions: {results['mission']}")
        if results['errors'] > 0:
            output.append(f"  Errors: {results['errors']}")

    return '\n'.join(output)


def _handle_quota(config) -> str:
    """
    Show Drive quota usage.

    Returns:
        Quota information
    """
    auth = get_gmail_auth(config)

    if not auth.is_authenticated():
        return "❌ Not authenticated. Use 'LOGIN GMAIL' first."

    drive = get_drive_service()

    if not drive.is_available():
        return "❌ Drive service not available"

    quota = drive.get_quota()

    if not quota:
        return "❌ Could not retrieve quota information"

    # Convert bytes to MB
    used_mb = quota.get('used', 0) / (1024 * 1024)
    total_mb = quota.get('total', 0) / (1024 * 1024)
    percent = (used_mb / total_mb * 100) if total_mb > 0 else 0

    # For uDOS sync, we recommend max 15 MB
    sync_limit = 15
    sync_percent = (used_mb / sync_limit * 100) if sync_limit > 0 else 0

    output = [
        "═══ Google Drive Quota ═══\n",
        f"Total Drive Storage: {total_mb:.1f} MB",
        f"Used: {used_mb:.1f} MB ({percent:.1f}%)",
        f"Available: {total_mb - used_mb:.1f} MB\n",
        f"uDOS Sync Limit: {sync_limit} MB (recommended)",
        f"Sync Usage: {used_mb:.2f} MB ({sync_percent:.1f}% of limit)"
    ]

    if used_mb > sync_limit:
        output.append(f"\n⚠️  Warning: Exceeding recommended sync limit by {used_mb - sync_limit:.1f} MB")
        output.append("   Consider cleaning up old files or increasing limit.")
    elif used_mb > sync_limit * 0.8:
        output.append(f"\n⚠️  Approaching sync limit ({sync_limit - used_mb:.1f} MB remaining)")

    return '\n'.join(output)


def _handle_config(parts: list, config) -> str:
    """
    Show or modify sync configuration.

    Commands:
    - CONFIG GMAIL - Show current config
    - CONFIG GMAIL SET <key> <value> - Update setting

    Returns:
        Config information
    """
    sync_mgr = get_sync_manager()

    if not parts:
        # Show current config
        cfg = sync_mgr.get_config()

        output = [
            "═══ Sync Configuration ═══\n",
            f"Enabled: {cfg['enabled']}",
            f"Mode: {cfg['mode']}",
            f"Interval: {cfg['interval']}s",
            f"Conflict strategy: {cfg['conflict_strategy']}\n",
            "Syncable directories:"
        ]

        for dir_path, enabled in cfg.get('paths', {}).items():
            status = "✓" if enabled else "✗"
            output.append(f"  {status} {dir_path}")

        output.extend([
            "",
            f"File types: {', '.join(cfg.get('file_types', []))}",
            f"Max file size: {cfg.get('max_file_size_mb', 1)} MB",
            f"Total quota: {cfg.get('total_quota_mb', 15)} MB"
        ])

        return '\n'.join(output)

    subcommand = parts[0].upper()

    if subcommand == 'SET':
        if len(parts) < 3:
            return "❌ Usage: CONFIG GMAIL SET <key> <value>"

        key = parts[1].lower()
        value = parts[2]

        # Update config
        try:
            if key == 'interval':
                sync_mgr.set_interval(int(value))
                return f"✅ Interval set to {value}s"
            elif key == 'strategy':
                if value in ['newest-wins', 'local-wins', 'cloud-wins', 'manual']:
                    sync_mgr.set_conflict_strategy(ConflictStrategy(value))
                    return f"✅ Conflict strategy set to {value}"
                else:
                    return f"❌ Invalid strategy. Use: newest-wins, local-wins, cloud-wins, or manual"
            else:
                return f"❌ Unknown config key: {key}"
        except Exception as e:
            return f"❌ Error updating config: {e}"
    else:
        return f"❌ Unknown CONFIG subcommand: {subcommand}"


def _handle_email_download(parts: list, config) -> str:
    """
    Download specific email by ID and convert to markdown.

    Args:
        parts: [message_id]
        config: Config instance

    Returns:
        Download status
    """
    if not parts:
        return "❌ Missing message ID\n\nUsage: EMAIL DOWNLOAD <message_id>"

    gmail = get_gmail_service()

    if not gmail.is_available():
        return "❌ Not authenticated. Use 'LOGIN GMAIL' first."

    message_id = parts[0]
    converter = get_email_converter()

    try:
        # Get full message
        msg = gmail.get_message(message_id)

        if not msg:
            return f"❌ Message not found: {message_id}"

        # Auto-convert
        result = converter.auto_convert(msg)

        if result['success']:
            return (
                f"✅ Email downloaded and converted\n\n"
                f"Type: {result['type']}\n"
                f"File: {result['filename']}\n"
                f"Path: {result['path']}\n\n"
                f"Subject: {msg['subject']}\n"
                f"From: {msg['from']}\n"
                f"Date: {msg['date']}"
            )
        else:
            return f"❌ Conversion failed: {result.get('error', 'Unknown error')}"

    except Exception as e:
        return f"❌ Error downloading email: {e}"


def _handle_email_tasks(parts: list, config) -> str:
    """
    Show tasks extracted from emails.

    Lists all tasks found in emails with source information.

    Returns:
        Task list
    """
    gmail = get_gmail_service()

    if not gmail.is_available():
        return "❌ Not authenticated. Use 'LOGIN GMAIL' first."

    parser = get_email_parser()

    # Get recent emails
    query = ' '.join(parts) if parts else "is:unread"
    messages = gmail.get_messages(query=query, max_results=20)

    if not messages:
        return f"No emails found for query: {query}"

    all_tasks = []

    for msg in messages:
        parsed = parser.parse_email(msg)
        tasks = parsed['tasks']

        if tasks:
            for task in tasks:
                all_tasks.append({
                    'text': task['text'],
                    'deadline': task.get('deadline'),
                    'priority': parsed.get('priority', 'medium'),
                    'email_subject': msg['subject'],
                    'email_from': msg['from'],
                    'email_date': msg['date']
                })

    if not all_tasks:
        return f"No tasks found in {len(messages)} email(s)"

    output = [f"📋 Found {len(all_tasks)} task(s) in {len(messages)} email(s)\n"]

    for i, task in enumerate(all_tasks, 1):
        output.append(f"{i}. {task['text']}")
        output.append(f"   From: {task['email_from']}")
        output.append(f"   Email: {task['email_subject']}")

        if task['deadline']:
            output.append(f"   Deadline: {task['deadline']}")

        if task['priority'] != 'medium':
            output.append(f"   Priority: {task['priority']}")

        output.append("")

    output.extend([
        "Use 'IMPORT GMAIL --type=checklist' to create task list",
        "Use 'IMPORT GMAIL --type=mission' to create mission workflow"
    ])

    return '\n'.join(output)


def _show_help() -> str:
    """
    Show Gmail command help.

    Returns:
        Help text
    """
    return """
Gmail Cloud Integration Commands - v1.2.9

Authentication:
  LOGIN GMAIL       - Start OAuth2 authentication
  LOGOUT GMAIL      - Revoke tokens and logout
  STATUS GMAIL      - Show auth status and Drive quota

Email Operations:
  EMAIL LIST [query]                - List recent emails
  EMAIL SEND <to> <subject>         - Send email
  EMAIL DOWNLOAD <id>               - Download and convert email
  EMAIL TASKS [query]               - Show tasks from emails

Email Import:
  IMPORT GMAIL [query]              - Import emails (auto-detect type)
  IMPORT GMAIL --preview [query]    - Preview without importing
  IMPORT GMAIL --type=<type> [query] - Force specific type
  IMPORT GMAIL --limit=<n> [query]  - Limit results

  Types: note, checklist, mission
  Auto-detection: 3+ tasks=mission, 1-2 tasks=checklist, 0 tasks=note

Cloud Sync:
  SYNC GMAIL                        - Run sync now
  SYNC GMAIL STATUS                 - Show sync status
  SYNC GMAIL ENABLE [mode]          - Enable auto-sync
  SYNC GMAIL DISABLE                - Disable auto-sync
  SYNC GMAIL CHANGES                - Show pending changes
  SYNC GMAIL HISTORY [limit]        - Show sync history

Quota & Configuration:
  QUOTA GMAIL                       - Show Drive quota usage
  CONFIG GMAIL                      - Show sync configuration
  CONFIG GMAIL SET <key> <value>    - Update setting

  Config keys: interval, strategy
  Strategies: newest-wins, local-wins, cloud-wins, manual

Examples:
  # Authentication
  LOGIN GMAIL
  STATUS GMAIL
  QUOTA GMAIL

  # Email operations
  EMAIL LIST is:unread from:boss
  EMAIL TASKS is:unread
  EMAIL DOWNLOAD msg_abc123

  # Import workflows
  IMPORT GMAIL --preview is:unread
  IMPORT GMAIL --type=mission from:boss subject:project
  IMPORT GMAIL --limit=5 is:starred

  # Sync operations
  SYNC GMAIL ENABLE auto --interval=300
  SYNC GMAIL CHANGES
  SYNC GMAIL STATUS
  SYNC GMAIL HISTORY 20

  # Configuration
  CONFIG GMAIL
  CONFIG GMAIL SET interval 600
  CONFIG GMAIL SET strategy local-wins

Syncable Directories:
  ✓ memory/missions
  ✓ memory/workflows
  ✓ memory/checklists
  ✓ memory/system/user
  ✓ memory/docs
  ✓ memory/drafts

Conflict Resolution:
  • newest-wins (default) - Use most recently modified
  • local-wins - Always prefer local version
  • cloud-wins - Always prefer cloud version
  • manual - Prompt user for each conflict

Security:
  • OAuth2 (no password storage)
  • Encrypted token storage
  • App-data-only Drive access
  • User controls all sync settings
"""


# Register command
GMAIL_COMMANDS = {
    'LOGIN': handle_gmail_command,
    'LOGOUT': handle_gmail_command,
    'STATUS': handle_gmail_command,
    'SYNC': handle_gmail_command,
    'EMAIL': handle_gmail_command,
    'IMPORT': handle_gmail_command,
    'QUOTA': handle_gmail_command,
    'CONFIG': handle_gmail_command
}
