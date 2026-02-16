#!/usr/bin/env python3
"""
Seed Installation Tool - Bootstrap uDOS seed data

Standalone script to initialize framework seed data for fresh uDOS installations.

Usage:
    python install-seed.py                  # Install to ./memory/
    python install-seed.py /path/to/udos    # Install to custom uDOS root
    python install-seed.py --help           # Show help
    python install-seed.py --status         # Check installation status
"""

import sys
import json
import argparse
from pathlib import Path


def main():
    """Main entry point for seed installer."""
    parser = argparse.ArgumentParser(
        description="Bootstrap uDOS framework seed data"
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory of uDOS installation (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing seed data",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check installation status without installing",
    )

    args = parser.parse_args()

    # Normalize path
    root = Path(args.root).resolve()
    framework_dir = root / "core" / "framework"

    if not framework_dir.exists():
        print(f"❌ Framework directory not found: {framework_dir}")
        print("   Please run this from a valid uDOS installation root.")
        sys.exit(1)

    # Import seed installer
    try:
        sys.path.insert(0, str(root))
        from core.framework.seed_installer import SeedInstaller
    except ImportError as e:
        print(f"❌ Failed to import SeedInstaller: {e}")
        sys.exit(1)

    # Create installer
    installer = SeedInstaller(
        framework_dir=framework_dir,
        memory_dir=root / "memory",
    )

    if args.status:
        # Just show status
        status = installer.status()
        print("Seed Installation Status:")
        print("-" * 40)
        print(f"Directories:        {'✅' if status['directories_exist'] else '❌'}")
        print(f"Locations seeded:   {'✅' if status['locations_seeded'] else '❌'}")
        print(f"Timezones seeded:   {'✅' if status['timezones_seeded'] else '❌'}")
        print(f"Vault seeded:       {'✅' if status['vault_seeded'] else '❌'}")
        print(f"Framework dir:      {'✅' if status['framework_seed_dir_exists'] else '❌'}")
        return 0

    # Install seeds
    print("Bootstrapping uDOS Seed Data")
    print("=" * 40)

    success, messages = installer.install_all(force=args.force)

    for msg in messages:
        print(msg)

    if success:
        print("\n✅ Seed installation complete!")
        return 0
    else:
        print("\n❌ Seed installation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
