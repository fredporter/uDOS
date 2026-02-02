"""
SEED command handler - Install or reset framework seed data.

Allows users to bootstrap or refresh seed data in memory/bank/ directory.
Useful for first-run initialization or REPAIR operations.
"""

from typing import Dict, List
from core.commands.base import BaseCommandHandler
from core.framework.seed_installer import SeedInstaller
from core.services.logging_service import get_logger

logger = get_logger("seed_handler")


class SeedHandler(BaseCommandHandler):
    """Install framework seed data."""

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        """
        Handle SEED command.

        Usage:
            SEED                    # Check status
            SEED INSTALL            # Install seed data
            SEED INSTALL --force    # Reinstall (overwrite)
            SEED STATUS             # Show seed status
            SEED HELP               # Show help

        Args:
            command: "SEED"
            params: Optional subcommand (INSTALL, STATUS, HELP)
            grid: TUI grid
            parser: Command parser

        Returns:
            Dict with status and result
        """
        subcommand = params[0].upper() if params else "STATUS"
        force = "--force" in params

        installer = SeedInstaller()

        if subcommand == "INSTALL":
            success, messages = installer.install_all(force=force)
            return {
                "status": "ok" if success else "error",
                "output": "\n".join(messages),
                "type": "text",
            }

        elif subcommand == "STATUS":
            status = installer.status()
            output = "Seed Installation Status:\n"
            output += "-" * 40 + "\n"
            output += f"Directories:       {'✅' if status['directories_exist'] else '❌'}\n"
            output += f"Locations seeded:  {'✅' if status['locations_seeded'] else '❌'}\n"
            output += f"Timezones seeded:  {'✅' if status['timezones_seeded'] else '❌'}\n"
            output += f"System seeds:     {'✅' if status.get('system_seeds') else '❌'}\n"
            output += f"Framework seed dir: {'✅' if status['framework_seed_dir_exists'] else '❌'}\n"

            return {
                "status": "ok",
                "output": output,
                "type": "text",
            }

        elif subcommand == "HELP":
            output = """SEED - Install Framework Seed Data

Usage:
  SEED                    Show installation status
  SEED INSTALL            Install seed data (skip existing)
  SEED INSTALL --force    Reinstall seed data (overwrite)
  SEED STATUS             Show installation status
  SEED HELP               Show this help

Seed data includes:
  - locations-seed.json (minimal location database)
  - timezones-seed.json (timezone examples)
  - Bank seeds (help templates, graphics, workflows)

First run automatically bootstraps seed data.
Use SEED INSTALL to manually bootstrap if needed.
"""
            return {
                "status": "ok",
                "output": output,
                "type": "text",
            }

        else:
            return {
                "status": "error",
                "output": f"Unknown SEED subcommand: {subcommand}\nUse 'SEED HELP' for usage.",
                "type": "text",
            }
