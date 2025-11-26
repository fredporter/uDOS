#!/usr/bin/env python3
"""Update logging paths from memory/logs to sandbox/logs"""

from pathlib import Path

files_to_update = [
    "core/uDOS_startup.py",
    "core/uDOS_logger.py",
    "core/services/session_replay.py",
    "core/services/api_audit.py",
    "core/services/session_analytics.py",
    "core/commands/tree_handler.py",
    "core/commands/feedback_handler.py",
    "core/commands/system_handler.py",
    "core/output/screen_manager.py",
    "core/ui/file_picker.py",
]

def update_file(filepath):
    """Update logging paths in a file"""
    path = Path(filepath)
    if not path.exists():
        print(f"⚠️  File not found: {filepath}")
        return

    content = path.read_text()
    original = content

    # Replace memory/logs with sandbox/logs
    content = content.replace('"memory/logs"', '"sandbox/logs"')
    content = content.replace("'memory/logs'", "'sandbox/logs'")
    content = content.replace("memory/logs/", "sandbox/logs/")
    content = content.replace("MEMORY/logs", "SANDBOX/logs")

    # Also update memory/sandbox references
    content = content.replace('"memory/sandbox"', '"sandbox"')
    content = content.replace("'memory/sandbox'", "'sandbox'")

    if content != original:
        path.write_text(content)
        print(f"✅ Updated: {filepath}")
    else:
        print(f"➖ No changes: {filepath}")

if __name__ == "__main__":
    print("🔧 Updating logging paths...")
    for file in files_to_update:
        update_file(file)
    print("\n✨ Logging path update complete!")
