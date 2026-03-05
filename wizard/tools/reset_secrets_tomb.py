#!/usr/bin/env python3
"""
Reset Secrets Tomb
==================

This script helps you reset the secrets.tomb file when the encryption key
doesn't match. After running this, you'll need to re-submit the setup story
in the TUI to re-populate the profiles.

Usage:
    python wizard/tools/reset_secrets_tomb.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    print("\n🔄 SECRETS TOMB RESET TOOL\n")

    tomb_path = Path(__file__).parent.parent / "secrets.tomb"

    if not tomb_path.exists():
        print("ℹ️  No secrets.tomb file found. Nothing to reset.")
        print("   The file will be created when you submit the setup story.")
        return 0

    # Backup existing tomb
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = tomb_path.parent / f"secrets.tomb.backup.{timestamp}"

    print(f"⚠️  Current secrets.tomb will be backed up to:")
    print(f"   {backup_path.name}")
    print()
    print("⚠️  WARNING: This will DELETE your current encrypted profiles!")
    print("   You will need to re-run the TUI setup story to restore them.")
    print()

    response = input("Continue? [y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("\n❌ Cancelled. No changes made.")
        return 0

    # Create backup
    print(f"\n📦 Creating backup...")
    tomb_path.rename(backup_path)
    print(f"   ✅ Backed up to: {backup_path.name}")

    print(f"\n✅ secrets.tomb has been removed.")
    print()
    print("📝 Next steps:")
    print("   1. Start uDOS TUI: ./bin/Launch-uCODE.sh")
    print("   2. Run the setup story (if prompted)")
    print("   3. Your answers will create a new secrets.tomb with the current WIZARD_KEY")
    print()
    print("💡 Or manually trigger setup via Wizard API:")
    print("   POST http://127.0.0.1:8765/api/setup/story/submit")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
