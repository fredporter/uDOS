#!/usr/bin/env python3
"""
Wizard Server Dev Mode Launcher with Integrated TUI
=====================================================

Launches Wizard Server with integrated terminal UI for development.
Provides real-time status, service control, and logging.

Usage:
  python wizard/launch_wizard_dev.py           # Start with TUI
  python wizard/launch_wizard_dev.py --no-tui  # Start server only
  python wizard/launch_wizard_dev.py --tui     # Start TUI only
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wizard.services.logging_manager import get_logger
from wizard.wizard_tui import WizardTUI
from wizard.server import WizardConfig

logger = get_logger("wizard-launcher")


def main():
    """Main launcher."""
    parser = argparse.ArgumentParser(description="Wizard Server Dev Mode")
    parser.add_argument(
        "--no-tui", action="store_true", help="Start server only without TUI"
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Start TUI only (server must be running separately)",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8765, help="Server port (default: 8765)"
    )

    args = parser.parse_args()

    # TUI only mode
    if args.tui:
        logger.info("[WIZ] Starting Wizard TUI (server-only mode)")
        try:
            tui = WizardTUI(host=args.host, port=args.port)
            tui.run()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            sys.exit(0)
        except Exception as e:
            logger.error(f"[WIZ] Fatal error: {e}")
            print(f"\n❌ Fatal error: {e}\n")
            sys.exit(1)

    # Server only mode
    elif args.no_tui:
        logger.info("[WIZ] Starting Wizard Server (no TUI)")
        logger.info("[WIZ] Note: Dev server archived. Use Goblin Dev Server for experimental features.")
        logger.info("[WIZ] Run: ./bin/Launch-Goblin-Dev.command")
        print("\n⚠️  Dev server has been moved to Goblin Dev Server")
        print("    Run: ./bin/Launch-Goblin-Dev.command\n")
        sys.exit(0)

    # Integrated mode (default): Server + TUI
    else:
        logger.info("[WIZ] Starting Wizard Dev Mode (server + TUI)")
        print("\n🧙 Starting Wizard Server + TUI...\n")

        try:
            # Create TUI instance
            tui = WizardTUI(host=args.host, port=args.port)

            # Start server from TUI
            print("▶ Starting server...")
            result = tui._start_server()
            print(result + "\n")

            if not tui.status.server_running:
                print("❌ Failed to start server\n")
                sys.exit(1)

            # Run TUI
            print("▶ Starting TUI...\n")
            tui.run()

            # Cleanup: Stop server on exit
            if tui.status.server_running:
                print("\n▶ Stopping server...")
                stop_result = tui._stop_server()
                print(stop_result)

        except KeyboardInterrupt:
            print("\n\n👋 Wizard Server stopped\n")
            sys.exit(0)
        except Exception as e:
            logger.error(f"[WIZ] Fatal error: {e}")
            print(f"\n❌ Fatal error: {e}\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
