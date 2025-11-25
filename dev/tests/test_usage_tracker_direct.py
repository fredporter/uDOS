#!/usr/bin/env python3
"""
Test UsageTracker service directly
"""

import sys
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

from core.utils.usage_tracker import UsageTracker

# Create tracker
tracker = UsageTracker(data_dir="memory/tests", max_recent=50)

# Track some commands
print("Tracking commands...")
tracker.track_command("HELP", [], success=True)
tracker.track_command("STATUS", [], success=True)
tracker.track_command("LIST", [], success=True)
tracker.track_command("HELP", ["STATUS"], success=True)
tracker.track_command("GRID", [], success=True)
tracker.track_command("HELP", [], success=True)
tracker.track_command("STATUS", [], success=True)
tracker.track_command("MAP", ["STATUS"], success=True)
tracker.track_command("HELP", ["SEARCH", "file"], success=True)
tracker.track_command("LIST", [], success=True)
tracker.track_command("STATUS", [], success=True)

print("\n" + "="*70)
print("TEST 1: Recent Commands")
print("="*70)
print(tracker.format_recent_commands(limit=10))

print("\n" + "="*70)
print("TEST 2: Most Used Commands")
print("="*70)
print(tracker.format_most_used(limit=10))

print("\n" + "="*70)
print("TEST 3: Session Statistics")
print("="*70)
print(tracker.format_session_stats())

print("\n" + "="*70)
print("TEST 4: Command Stats for HELP")
print("="*70)
stats = tracker.get_command_stats("HELP")
print(f"Command: {stats['command']}")
print(f"Total Uses: {stats['total_uses']}")
print(f"Successes: {stats['successes']}")
print(f"Failures: {stats['failures']}")
print(f"Success Rate: {stats['success_rate']:.1f}%")

print("\n✅ All tests complete!")
