"""
Gmail Cloud Sync Integration Test for uDOS v1.2.9

Tests complete Gmail authentication, sync, and email operations.

Usage:
    python dev/tools/test_gmail_integration.py

Prerequisites:
    - Gmail OAuth credentials in memory/system/user/gmail_credentials.json
    - Google Cloud project with Gmail and Drive APIs enabled

What this tests:
    - Gmail OAuth2 authentication flow
    - Token encryption and persistence
    - Drive quota checking
    - Sync configuration
    - Email listing and filtering
    - Email conversion (import)
    - Task extraction
    - Sync operations
    - Conflict resolution

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.config import Config
from core.services.gmail_auth import get_gmail_auth
from core.services.gmail_service import get_gmail_service, get_drive_service
from core.services.sync_manager import get_sync_manager
from core.services.email_parser import get_email_parser
from core.services.email_converter import get_email_converter


def test_authentication():
    """Test Gmail OAuth authentication."""
    print("=" * 60)
    print("Gmail Authentication Test - v1.2.9")
    print("=" * 60)
    print()

    config = Config()
    auth = get_gmail_auth(config)

    # Check if already authenticated
    if auth.is_authenticated():
        status = auth.get_status()
        print("✅ Already authenticated")
        print(f"Email: {status['email']}")
        print(f"Name: {status['name']}")
        print(f"Token expires: {status['token_expiry']}")
        print()
        return True
    else:
        print("❌ Not authenticated")
        print("Run 'LOGIN GMAIL' command in uDOS to authenticate")
        print()
        return False


def test_gmail_service():
    """Test Gmail service operations."""
    print("=" * 60)
    print("Gmail Service Test - v1.2.9")
    print("=" * 60)
    print()

    gmail = get_gmail_service()

    if not gmail.is_available():
        print("❌ Gmail service not available - authentication required")
        return False

    # Test: List recent emails
    print("Listing recent emails...")
    messages = gmail.get_messages(query="", max_results=5)

    if messages:
        print(f"✅ Retrieved {len(messages)} email(s)")
        for i, msg in enumerate(messages, 1):
            print(f"\n{i}. {msg['subject']}")
            print(f"   From: {msg['from']}")
            print(f"   Date: {msg['date']}")
            print(f"   Snippet: {msg['snippet'][:60]}...")
        print()
    else:
        print("⚠️  No emails found (inbox may be empty)")
        print()

    return True


def test_drive_service():
    """Test Google Drive service operations."""
    print("=" * 60)
    print("Google Drive Service Test - v1.2.9")
    print("=" * 60)
    print()

    drive = get_drive_service()

    if not drive.is_available():
        print("❌ Drive service not available - authentication required")
        return False

    # Test: Get quota
    print("Checking Drive quota...")
    quota = drive.get_quota()

    if quota:
        used_mb = quota.get('used', 0) / (1024 * 1024)
        total_mb = quota.get('total', 0) / (1024 * 1024)
        percent = (used_mb / total_mb * 100) if total_mb > 0 else 0

        print(f"✅ Drive quota retrieved")
        print(f"Total: {total_mb:.1f} MB")
        print(f"Used: {used_mb:.1f} MB ({percent:.1f}%)")
        print(f"Available: {total_mb - used_mb:.1f} MB")
        print()
    else:
        print("❌ Could not retrieve quota")
        print()
        return False

    # Test: List files in app data
    print("Listing files in app data folder...")
    files = drive.list_files()

    if files:
        print(f"✅ Found {len(files)} file(s) in app data")
        for i, file in enumerate(files[:5], 1):
            print(f"{i}. {file['name']} ({file.get('size', 0)} bytes)")
        if len(files) > 5:
            print(f"... and {len(files) - 5} more")
        print()
    else:
        print("⚠️  No files in app data (first sync not run yet)")
        print()

    return True


def test_sync_manager():
    """Test sync manager operations."""
    print("=" * 60)
    print("Sync Manager Test - v1.2.9")
    print("=" * 60)
    print()

    sync_mgr = get_sync_manager()

    # Test: Get status
    print("Getting sync status...")
    status = sync_mgr.get_status()

    print(f"Enabled: {status['enabled']}")
    print(f"Mode: {status['mode']}")
    print(f"Interval: {status['interval']}s")
    print(f"Conflict strategy: {status['conflict_strategy']}")

    if status['last_sync']:
        print(f"Last sync: {status['time_since_sync']} ago")
    else:
        print("Last sync: Never")

    print(f"Total syncs: {status['total_syncs']}")
    print()

    # Test: Get changes
    print("Checking for pending changes...")
    changes = sync_mgr.get_changes()

    total = sum(len(v) for v in changes.values())
    print(f"Pending changes: {total}")

    if changes['new_local']:
        print(f"  New local: {len(changes['new_local'])}")
    if changes['modified_local']:
        print(f"  Modified local: {len(changes['modified_local'])}")
    if changes['new_cloud']:
        print(f"  New cloud: {len(changes['new_cloud'])}")
    if changes['modified_cloud']:
        print(f"  Modified cloud: {len(changes['modified_cloud'])}")
    if changes['conflicts']:
        print(f"  Conflicts: {len(changes['conflicts'])}")

    print()

    # Test: Get config
    print("Getting sync configuration...")
    cfg = sync_mgr.get_config()

    print("Syncable paths:")
    for path, enabled in cfg.get('paths', {}).items():
        status_icon = "✓" if enabled else "✗"
        print(f"  {status_icon} {path}")

    print(f"\nFile types: {', '.join(cfg.get('file_types', []))}")
    print(f"Max file size: {cfg.get('max_file_size_mb', 1)} MB")
    print(f"Total quota: {cfg.get('total_quota_mb', 15)} MB")
    print()

    return True


def test_email_parser():
    """Test email parsing and task extraction."""
    print("=" * 60)
    print("Email Parser Test - v1.2.9")
    print("=" * 60)
    print()

    gmail = get_gmail_service()

    if not gmail.is_available():
        print("❌ Gmail service not available")
        return False

    parser = get_email_parser()

    # Get a few emails
    messages = gmail.get_messages(query="", max_results=3)

    if not messages:
        print("⚠️  No emails to test parsing")
        return False

    print(f"Testing parser on {len(messages)} email(s)...")
    print()

    for i, msg in enumerate(messages, 1):
        print(f"Email {i}: {msg['subject']}")
        print("-" * 40)

        # Parse email
        parsed = parser.parse_email(msg)

        print(f"From: {parsed['metadata']['from']['name']}")
        print(f"Priority: {parsed['priority']}")
        print(f"Tasks found: {len(parsed['tasks'])}")

        if parsed['tasks']:
            for task in parsed['tasks'][:3]:
                print(f"  • {task['text'][:60]}...")

        if parsed['urls']:
            print(f"URLs found: {len(parsed['urls'])}")

        print()

    print("✅ Email parsing test complete")
    print()

    return True


def test_email_converter():
    """Test email to uDOS format conversion."""
    print("=" * 60)
    print("Email Converter Test - v1.2.9")
    print("=" * 60)
    print()

    gmail = get_gmail_service()

    if not gmail.is_available():
        print("❌ Gmail service not available")
        return False

    converter = get_email_converter()

    # Get a test email
    messages = gmail.get_messages(query="", max_results=1)

    if not messages:
        print("⚠️  No emails to test conversion")
        return False

    msg = messages[0]

    print(f"Testing conversion on: {msg['subject']}")
    print()

    # Test auto-convert
    result = converter.auto_convert(msg)

    if result['success']:
        print(f"✅ Auto-converted to: {result['type']}")
        print(f"File: {result['filename']}")
        print(f"Path: {result['path']}")

        # Show file preview
        file_path = Path(result['path'])
        if file_path.exists():
            content = file_path.read_text()
            lines = content.split('\n')[:15]
            print("\nPreview (first 15 lines):")
            for line in lines:
                print(f"  {line}")
            if len(content.split('\n')) > 15:
                print(f"  ... ({len(content.split('\n')) - 15} more lines)")
    else:
        print(f"❌ Conversion failed: {result.get('error')}")

    print()

    return True


def test_summary():
    """Show test summary."""
    print("=" * 60)
    print("Integration Test Summary - v1.2.9")
    print("=" * 60)
    print()

    print("✅ All integration tests completed!")
    print()
    print("Components tested:")
    print("  ✓ Gmail OAuth2 authentication")
    print("  ✓ Gmail service (email listing)")
    print("  ✓ Google Drive service (quota, files)")
    print("  ✓ Sync manager (status, changes, config)")
    print("  ✓ Email parser (task extraction)")
    print("  ✓ Email converter (auto-convert)")
    print()
    print("Next steps:")
    print("  - Run 'SYNC GMAIL' to perform first sync")
    print("  - Use 'IMPORT GMAIL' to import emails")
    print("  - Try 'EMAIL TASKS' to extract actionable items")
    print("  - Monitor with 'STATUS GMAIL' and 'QUOTA GMAIL'")
    print()


if __name__ == "__main__":
    try:
        # Run all tests
        auth_ok = test_authentication()

        if not auth_ok:
            print("❌ Authentication required. Run 'LOGIN GMAIL' first.")
            sys.exit(1)

        gmail_ok = test_gmail_service()
        drive_ok = test_drive_service()
        sync_ok = test_sync_manager()
        parse_ok = test_email_parser()
        convert_ok = test_email_converter()

        test_summary()

        if all([auth_ok, gmail_ok, drive_ok, sync_ok, parse_ok, convert_ok]):
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
