"""CONFIG command handler - Wizard configuration management from TUI."""

from typing import List, Dict
import requests
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_manager import get_logger, LogTags

logger = get_logger("config-handler")

WIZARD_API = "http://localhost:8765/api/v1"


class ConfigHandler(BaseCommandHandler):
    """Handler for CONFIG command - Wizard configuration from TUI."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """Handle CONFIG commands."""

        if not params:
            return self._show_status()

        subcommand = params[0].upper()
        args = params[1:] if len(params) > 1 else []

        if subcommand == "SHOW":
            return self._show_status()
        elif subcommand == "LIST":
            return self._list_configs()
        elif subcommand == "EDIT" and args:
            return self._edit_config(args[0])
        elif subcommand == "SETUP":
            return self._run_setup()
        else:
            return {
                "status": "error",
                "message": f"Unknown CONFIG subcommand: {subcommand}",
                "output": "Usage: CONFIG [SHOW|LIST|EDIT <file>|SETUP]",
            }

    def _show_status(self) -> Dict:
        """Show current configuration status."""
        try:
            response = requests.get(f"{WIZARD_API}/config/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                output = [OutputToolkit.banner("WIZARD CONFIG STATUS"), ""]

                if "enabled_providers" in data:
                    providers = data.get("enabled_providers", [])
                    if providers:
                        output.append("Enabled Providers:")
                        for provider in providers:
                            output.append(f"  OK {provider}")
                    else:
                        output.append("Enabled Providers: (none)")
                    output.append("")

                if "config_files" in data:
                    output.append("Configuration Files:")
                    for name, info in data.get("config_files", {}).items():
                        status = "OK" if info.get("exists") else "X"
                        output.append(f"  {status} {name}")
                    output.append("")

                output.append("Use 'CONFIG LIST' to see all config files")
                output.append("Use 'PROVIDER LIST' to manage providers")

                return {"status": "success", "output": "\n".join(output)}
            else:
                return {
                    "status": "error",
                    "message": f"Failed to get config status: {response.status_code}",
                    "output": "Is Wizard Server running? (port 8765)",
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}",
            }

    def _list_configs(self) -> Dict:
        """List all configuration files."""
        try:
            response = requests.get(f"{WIZARD_API}/config/list", timeout=5)
            if response.status_code == 200:
                data = response.json()
                output = [OutputToolkit.banner("CONFIGURATION FILES"), ""]

                for name, info in data.get("config_files", {}).items():
                    status = "OK" if info.get("exists") else "X"
                    path = info.get("path", "")
                    output.append(f"{status} {name}")
                    output.append(f"   {path}")
                    output.append("")

                output.append("Use 'CONFIG EDIT <filename>' to edit a config file")

                return {"status": "success", "output": "\n".join(output)}
            else:
                return {
                    "status": "error",
                    "message": f"Failed to list configs: {response.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}",
            }

    def _edit_config(self, filename: str) -> Dict:
        """Open config file in editor."""
        config_dir = Path(__file__).parent.parent.parent / "wizard" / "config"
        config_file = config_dir / filename

        if not config_file.exists():
            return {
                "status": "error",
                "message": f"Config file not found: {filename}",
                "output": "Use 'CONFIG LIST' to see available files",
            }

        import subprocess
        import os

        editor = os.environ.get("EDITOR")
        if not editor:
            from core.services.editor_utils import pick_editor

            editor_name, editor_path = pick_editor()
            editor = str(editor_path) if editor_path else None

        try:
            if not editor:
                return {
                    "status": "error",
                    "message": "Editor not found",
                    "output": "Install micro or nano, or set EDITOR environment variable",
                }
            subprocess.run([editor, str(config_file)], check=True)
            return {
                "status": "success",
                "output": f"Edited {filename}\n\nNOTE: Restart Wizard Server to apply changes",
            }
        except subprocess.CalledProcessError:
            return {"status": "error", "message": f"Failed to open editor: {editor}"}
        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"Editor not found: {editor}",
                "output": "Install micro or nano, or set EDITOR environment variable",
            }

    def _run_setup(self) -> Dict:
        """Run provider setup check."""
        import subprocess

        output = [OutputToolkit.banner("PROVIDER SETUP CHECK"), ""]

        try:
            # Run setup checker interactively
            result = subprocess.run(
                ["python", "-m", "wizard.check_provider_setup"],
                capture_output=False,  # Show interactive prompts
                text=True,
            )

            if result.returncode == 0:
                output.append("OK Setup check completed")
            else:
                output.append("WARN Setup check had issues")

            return {"status": "success", "output": "\n".join(output)}
        except Exception as e:
            return {"status": "error", "message": f"Failed to run setup: {str(e)}"}
