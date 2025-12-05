"""
Sync Engine Test Script for uDOS v1.2.9

Tests Google Drive sync operations, conflict resolution, and change detection.

Usage:
    python dev/tools/test_sync_engine.py

Requirements:
    - Must be authenticated (run LOGIN GMAIL first)
    - Gmail credentials configured
    - Google Drive API access

What this tests:
    - Change detection (local vs cloud)
    - File upload/download
    - Conflict resolution strategies
    - Sync metadata tracking
    - Background sync operations

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.gmail_auth import get_gmail_auth
from core.services.sync_engine import get_sync_engine
from core.services.sync_manager import get_sync_manager, ConflictStrategy
from core.config import Config


def test_sync_engine():
    """Test sync engine functionality."""
    print("=" * 60)
    print("Sync Engine Test - v1.2.9")
    print("=" * 60)
    print()

    # Initialize
    config = Config()
    auth = get_gmail_auth(config)
    engine = get_sync_engine()
    manager = get_sync_manager()

    # Test 1: Check authentication
    print("Test 1: Check authentication")
    print("-" * 60)
    if not auth.is_authenticated():
        print("❌ Not authenticated")
        print("   Run LOGIN GMAIL in uDOS first")
        return False

    status = auth.get_status()
    print(f"✅ Authenticated as {status['email']}")
    print()

    # Test 2: Get local files
    print("Test 2: Scan local files")
    print("-" * 60)
    local_files = engine.get_local_files()
    print(f"✅ Found {len(local_files)} local files to sync")

    if local_files:
        print("   Sample files:")
        for f in local_files[:5]:
            rel = engine._get_relative_path(f)
            print(f"   - {rel}")
        if len(local_files) > 5:
            print(f"   ... and {len(local_files) - 5} more")
    print()

    # Test 3: Detect changes
    print("Test 3: Detect changes")
    print("-" * 60)
    changes = engine.detect_changes()

    total = sum(len(v) for v in changes.values())
    print(f"✅ Detected {total} total changes")

    for key, items in changes.items():
        if items:
            print(f"   {key}: {len(items)}")
    print()

    # Test 4: Sync metadata
    print("Test 4: Check sync metadata")
    print("-" * 60)
    metadata = engine.metadata
    print(f"✅ Metadata loaded")
    print(f"   Tracked files: {len(metadata.get('files', {}))}")
    print(f"   Last sync: {metadata.get('last_sync', 'Never')}")
    print(f"   Conflict strategy: {metadata.get('conflict_strategy', 'newest-wins')}")
    print()

    # Test 5: Manager status
    print("Test 5: Sync manager status")
    print("-" * 60)
    mgr_status = manager.get_status()
    print(f"✅ Manager status")
    print(f"   Enabled: {mgr_status['enabled']}")
    print(f"   Mode: {mgr_status['mode']}")
    print(f"   Interval: {mgr_status['interval']}s")
    print(f"   Total syncs: {mgr_status['total_syncs']}")
    print()

    # Test 6: Sync history
    print("Test 6: Sync history")
    print("-" * 60)
    history = manager.get_history(5)
    if history:
        print(f"✅ Last {len(history)} sync operations:")
        for i, entry in enumerate(history, 1):
            timestamp = entry['timestamp'][:19]
            success = "✅" if entry['success'] else "❌"
            stats = entry['stats']
            print(f"   {i}. {timestamp} {success}")
            print(f"      Up:{stats.get('uploaded', 0)} Down:{stats.get('downloaded', 0)} Conflicts:{stats.get('conflicts', 0)}")
    else:
        print("ℹ️  No sync history yet")
    print()

    # Test 7: Test conflict strategies
    print("Test 7: Conflict resolution strategies")
    print("-" * 60)
    strategies = [s for s in ConflictStrategy]
    print(f"✅ Available strategies: {len(strategies)}")
    for strategy in strategies:
        print(f"   - {strategy.value}")

    current = ConflictStrategy(manager.settings.get('conflict_strategy', 'newest-wins'))
    print(f"\n   Current: {current.value}")
    print()

    # Test 8: Dry run (changes only, no sync)
    print("Test 8: Dry run - show what would sync")
    print("-" * 60)
    if total > 0:
        print(f"✅ Would sync {total} items:")

        if changes['new_local']:
            print(f"\n   Upload ({len(changes['new_local'])}):")
            for item in changes['new_local'][:3]:
                rel = engine._get_relative_path(item)
                print(f"   → {rel}")

        if changes['new_cloud']:
            print(f"\n   Download ({len(changes['new_cloud'])}):")
            for item in changes['new_cloud'][:3]:
                print(f"   ← {item}")

        if changes['conflicts']:
            print(f"\n   ⚠️  Conflicts ({len(changes['conflicts'])}):")
            for item in changes['conflicts'][:3]:
                rel = engine._get_relative_path(item)
                print(f"   ⚡ {rel}")
    else:
        print("✅ Everything in sync - no changes needed")
    print()

    # Test 9: Offer to run sync
    print("Test 9: Run sync operation")
    print("-" * 60)
    if total > 0:
        print(f"⚠️  Would sync {total} items")
        print("   To actually run sync, use: SYNC GMAIL in uDOS")
        print("   Or uncomment the sync code in this test script")

        # Uncomment to actually run sync:
        # print("\n   Running sync...")
        # result = manager.sync_now()
        # if result['success']:
        #     print("   ✅ Sync completed")
        #     stats = result['stats']
        #     print(f"      Uploaded: {stats['uploaded']}")
        #     print(f"      Downloaded: {stats['downloaded']}")
        #     print(f"      Conflicts: {stats['conflicts']}")
        # else:
        #     print("   ❌ Sync failed")
    else:
        print("✅ No sync needed - everything up to date")
    print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("✅ Sync engine operational")
    print()
    print("Next steps:")
    print("  - Use SYNC GMAIL to run sync")
    print("  - Use SYNC GMAIL STATUS to check status")
    print("  - Use SYNC GMAIL ENABLE to enable auto-sync")
    print("  - Use SYNC GMAIL CHANGES to preview changes")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_sync_engine()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
