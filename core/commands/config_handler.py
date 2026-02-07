"""CONFIG command handler - local configuration and variable management from TUI."""

from typing import List, Dict
import json
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.commands.interactive_menu_mixin import InteractiveMenuMixin
from core.services.logging_api import get_logger, get_repo_root, LogTags

logger = get_logger("config-handler")


class ConfigHandler(BaseCommandHandler, HandlerLoggingMixin, InteractiveMenuMixin):
    """Handler for CONFIG command - Wizard configuration and variables from TUI."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle CONFIG commands for file config and variable management.

        Usage:
            CONFIG                     List all variables
            CONFIG <key>               Get specific variable
            CONFIG <key> <value>       Set variable value
            CONFIG --delete <key>      Delete variable
            CONFIG --sync              Sync all variables
            CONFIG --export            Export config backup
            CONFIG SHOW                Show Wizard status (legacy)
            CONFIG LIST                List config files (legacy)
            CONFIG EDIT <file>         Edit config file (legacy)
        """
        with self.trace_command(command, params) as trace:
            if not params:
                choice = self.show_menu(
                    "CONFIG",
                    [
                        ("List variables", "list_vars", "Show all .env variables"),
                        ("Get variable", "get_var", "Look up a variable"),
                        ("Set variable", "set_var", "Update a variable"),
                        ("Delete variable", "delete_var", "Remove a variable"),
                        ("Sync variables", "sync", "Sync .env and wizard config"),
                        ("Export config", "export", "Create a masked backup"),
                        ("Status", "status", "Show config status"),
                        ("List config files", "list_files", "Show wizard config files"),
                        ("Edit config file", "edit_file", "Open a config file"),
                        ("Help", "help", "Show CONFIG help"),
                    ],
                )
                if choice is None:
                    result = self._list_variables()
                    trace.set_status(result.get("status", "success"))
                    return result

                if choice == "list_vars":
                    result = self._list_variables()
                elif choice == "get_var":
                    key = input("Variable key: ").strip()
                    result = self._get_variable(key) if key else {"status": "warning", "message": "Key required"}
                elif choice == "set_var":
                    key = input("Variable key: ").strip()
                    value = input("Value: ").strip()
                    result = self._set_variable(key, value) if key else {"status": "warning", "message": "Key required"}
                elif choice == "delete_var":
                    key = input("Variable key to delete: ").strip()
                    result = self._delete_variable(key) if key else {"status": "warning", "message": "Key required"}
                elif choice == "sync":
                    result = self._sync_variables()
                elif choice == "export":
                    result = self._export_config()
                elif choice == "status":
                    result = self._show_status()
                elif choice == "list_files":
                    result = self._list_configs()
                elif choice == "edit_file":
                    filename = input("Config filename: ").strip()
                    result = self._edit_config(filename) if filename else {"status": "warning", "message": "Filename required"}
                elif choice == "help":
                    result = self._show_help()
                else:
                    result = self._list_variables()

                trace.set_status(result.get("status", "success"))
                return result

            first_param = params[0]
            args = params[1:] if len(params) > 1 else []

            # Handle flag-style commands
            if first_param.startswith("--"):
                flag = first_param[2:].lower()
                trace.add_event("flag_parsed", {"flag": flag})

                if flag == "sync":
                    result = self._sync_variables()
                elif flag == "export":
                    result = self._export_config()
                elif flag == "delete" and args:
                    result = self._delete_variable(args[0])
                elif flag == "help":
                    result = self._show_help()
                else:
                    trace.set_status("error")
                    return {
                        "status": "error",
                        "message": f"Unknown flag: --{flag}",
                        "output": "Usage: CONFIG --sync | --export | --delete <key> | --help",
                    }

                trace.set_status(result.get("status", "success"))
                return result

            # Handle legacy subcommands (SHOW, LIST, EDIT, SETUP)
            subcommand = first_param.upper()

            if subcommand in ["SHOW", "STATUS"]:
                result = self._show_status()
            elif subcommand == "LIST":
                result = self._list_configs()
            elif subcommand == "EDIT" and args:
                result = self._edit_config(args[0])
            elif subcommand == "SETUP":
                result = self._run_setup()
            elif subcommand == "VARS" or subcommand == "VARIABLES":
                result = self._list_variables()
            else:
                # Treat as variable get/set
                key = first_param
                if args:
                    # Set variable
                    value = " ".join(args)
                    result = self._set_variable(key, value)
                else:
                    # Get variable
                    result = self._get_variable(key)

            trace.set_status(result.get("status", "success"))
            return result

    def _show_status(self) -> Dict:
        """Show current configuration status."""
        from core.tui.output import OutputToolkit

        output = [OutputToolkit.banner("LOCAL CONFIG STATUS"), ""]

        env_path = get_repo_root() / ".env"
        env_status = "OK" if env_path.exists() else "X"
        output.append("Environment File:")
        output.append(f"  {env_status} .env")
        output.append("")

        config_dir = get_repo_root() / "wizard" / "config"
        output.append("Configuration Files:")
        if config_dir.exists():
            files = sorted([p for p in config_dir.iterdir() if p.is_file()])
            if files:
                for file_path in files:
                    output.append(f"  OK {file_path.name}")
            else:
                output.append("  (none)")
        else:
            output.append("  (config directory not found)")
        output.append("")

        output.append("Use 'CONFIG LIST' to see all config files")
        output.append("Use 'CONFIG EDIT <file>' to edit locally")

        return {"status": "success", "output": "\n".join(output)}

    def _list_configs(self) -> Dict:
        """List all configuration files."""
        from core.tui.output import OutputToolkit

        config_dir = get_repo_root() / "wizard" / "config"
        if not config_dir.exists():
            return {
                "status": "error",
                "message": "Config directory not found",
                "output": "Expected: wizard/config",
            }

        output = [OutputToolkit.banner("CONFIGURATION FILES"), ""]
        files = sorted([p for p in config_dir.iterdir() if p.is_file()])

        if not files:
            output.append("(no config files found)")
        else:
            for file_path in files:
                output.append(f"OK {file_path.name}")
                output.append(f"   {file_path}")
                output.append("")

        output.append("Use 'CONFIG EDIT <filename>' to edit a config file")

        return {"status": "success", "output": "\n".join(output)}

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

        from core.tui.output import OutputToolkit

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

    # ========================================================================
    # Variable Management Methods
    # ========================================================================

    def _list_variables(self) -> Dict:
        """List all variables from local .env."""
        try:
            env_data = self._load_env_file()
            return self._format_env_variables(env_data)
        except Exception as e:
            return {"status": "error", "message": f"Failed to list variables: {e}"}

    def _get_variable(self, key: str) -> Dict:
        """Get a specific variable."""
        try:
            env_data = self._load_env_file()
            if not env_data:
                return {
                    "status": "error",
                    "message": "No local configuration found",
                    "output": "Create .env or use CONFIG <key> <value>",
                }

            if key not in env_data:
                return {
                    "status": "error",
                    "message": f"Variable not found: {key}",
                    "output": "Use CONFIG to list all variables",
                }

            value = env_data.get(key)
            from core.tui.output import OutputToolkit

            lines = [OutputToolkit.banner(f"VARIABLE: {key}"), ""]
            lines.append(f"Value: {self._mask_value(value)}")
            lines.append("Source: .env")

            return {"status": "success", "output": "\n".join(lines)}

        except Exception as e:
            return {"status": "error", "message": f"Failed to get variable: {e}"}

    def _set_variable(self, key: str, value: str) -> Dict:
        """Set a variable value."""
        try:
            # Parse boolean values
            if value.lower() in ["true", "yes", "1", "on"]:
                parsed_value = True
            elif value.lower() in ["false", "no", "0", "off"]:
                parsed_value = False
            else:
                parsed_value = value

            env_path = get_repo_root() / ".env"
            lines = env_path.read_text().splitlines() if env_path.exists() else []
            new_lines = []
            updated = False

            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in line:
                    new_lines.append(line)
                    continue

                existing_key = line.split("=", 1)[0].strip()
                if existing_key == key:
                    new_lines.append(f"{key}={self._serialize_env_value(parsed_value)}")
                    updated = True
                else:
                    new_lines.append(line)

            if not updated:
                if new_lines and new_lines[-1].strip() != "":
                    new_lines.append("")
                new_lines.append(f"{key}={self._serialize_env_value(parsed_value)}")

            env_path.write_text("\n".join(new_lines) + ("\n" if new_lines else ""))

            return {
                "status": "success",
                "output": f"OK Set {key} = {self._serialize_env_value(parsed_value)}\n\nStored in .env",
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to set variable: {e}"}

    def _delete_variable(self, key: str) -> Dict:
        """Delete a variable."""
        try:
            env_path = get_repo_root() / ".env"
            if not env_path.exists():
                return {
                    "status": "error",
                    "message": "No local configuration found",
                    "output": "Create .env or use CONFIG <key> <value>",
                }

            lines = env_path.read_text().splitlines()
            new_lines = []
            removed = False

            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in line:
                    new_lines.append(line)
                    continue

                existing_key = line.split("=", 1)[0].strip()
                if existing_key == key:
                    removed = True
                    continue

                new_lines.append(line)

            if not removed:
                return {"status": "error", "message": f"Variable not found: {key}"}

            env_path.write_text("\n".join(new_lines) + ("\n" if new_lines else ""))

            return {"status": "success", "output": f"OK Deleted variable: {key}"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to delete variable: {e}"}

    def _sync_variables(self) -> Dict:
        """Sync all variables across tiers."""
        try:
            from core.tui.output import OutputToolkit

            env_path = get_repo_root() / ".env"
            if not env_path.exists():
                return {
                    "status": "error",
                    "message": "No local configuration found",
                    "output": "Create .env or use CONFIG <key> <value>",
                }

            lines = [OutputToolkit.banner("SYNC COMPLETE"), ""]
            lines.append("  Local .env is authoritative")
            lines.append("  No remote sync required")

            return {"status": "success", "output": "\n".join(lines)}

        except Exception as e:
            return {"status": "error", "message": f"Failed to sync: {e}"}

    def _export_config(self) -> Dict:
        """Export configuration for backup."""
        try:
            env_data = self._load_env_file()
            safe_env = {}
            masked_keys = []
            for key, value in env_data.items():
                if self._is_sensitive_key(key):
                    safe_env[key] = "***"
                    masked_keys.append(key)
                else:
                    safe_env[key] = value

            data = {
                "env": safe_env,
                "masked_keys": sorted(masked_keys),
            }
            export_path = get_repo_root() / "memory" / "config-backup.json"
            export_path.parent.mkdir(parents=True, exist_ok=True)
            export_path.write_text(json.dumps(data, indent=2))

            return {
                "status": "success",
                "output": f"OK Config exported to: {export_path}\n\nNOTE: This backup does NOT include secrets",
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to export: {e}"}

    def _show_help(self) -> Dict:
        """Show detailed help."""
        from core.tui.output import OutputToolkit

        return {
            "status": "success",
            "output": OutputToolkit.banner("CONFIG HELP")
            + """

USAGE:
  CONFIG                    List all variables
  CONFIG <key>              Get specific variable
  CONFIG <key> <value>      Set variable value
  CONFIG --delete <key>     Delete variable
  CONFIG --sync             Sync all variables
  CONFIG --export           Export config (backup)
  CONFIG --help             Show this help

LEGACY COMMANDS:
  CONFIG SHOW               Show Wizard status
  CONFIG LIST               List config files
  CONFIG EDIT <file>        Edit config file

VARIABLE TYPES:
  $VARIABLE                 System variables (stored in .env)
    $WIZARD_KEY             Encryption key
    $GITHUB_TOKEN           GitHub API token
        $OPENAI_API_KEY         OpenAI API token

  @variable                 User variables (encrypted secrets)
    @username               Your username
    @timezone               Your timezone
    @location               Your location

  flag_name                 Feature flags (wizard.json)
    ok_gateway_enabled      Enable OK gateway

EXAMPLES:
  CONFIG                    Show all variables
  CONFIG @username          Show your username
  CONFIG @timezone PST      Set your timezone
  CONFIG --sync             Sync everything

SECURITY:
  • System variables are masked in output
  • Secrets are encrypted at rest
  • Export does NOT include sensitive secrets
""",
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _mask_value(self, value: str) -> str:
        """Mask sensitive values."""
        if not value or len(value) < 8:
            return "***"
        return value[:4] + "..." + value[-4:]

    def _serialize_env_value(self, value) -> str:
        """Serialize values for .env storage."""
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _is_sensitive_key(self, key: str) -> bool:
        """Basic heuristic for sensitive keys."""
        upper_key = key.upper()
        sensitive_markers = ["SECRET", "TOKEN", "PASSWORD", "KEY"]
        return any(marker in upper_key for marker in sensitive_markers)
    def _load_env_file(self) -> Dict:
        """Load variables from .env file (offline fallback)."""
        try:
            env_path = get_repo_root() / ".env"
            if not env_path.exists():
                return {}

            variables = {}
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    variables[key.strip()] = value.strip()
            return variables
        except Exception:
            return {}

    def _format_env_variables(self, variables: Dict) -> Dict:
        """Format .env variables for display."""
        try:
            from core.tui.output import OutputToolkit

            lines = [OutputToolkit.banner("LOCAL CONFIGURATION (.env)"), ""]

            # Separate local setup vs other config
            setup_keys = {'USER_NAME', 'USER_DOB', 'USER_ROLE', 'USER_PASSWORD',
                         'USER_LOCATION', 'USER_TIMEZONE', 'OS_TYPE', 'WIZARD_KEY'}
            setup_vars = {k: v for k, v in variables.items() if k in setup_keys}
            other_vars = {k: v for k, v in variables.items() if k not in setup_keys}

            if setup_vars:
                lines.append("LOCAL USER SETUP:")
                lines.append("-" * 60)
                for key in sorted(setup_keys):
                    if key in setup_vars:
                        value = setup_vars[key]
                        if key == 'WIZARD_KEY':
                            value = value[:8] + "..." if len(value) > 8 else "***"
                        elif key == 'USER_PASSWORD':
                            value = "***" if value else "(none)"
                        lines.append(f"  {key} = {value}")
                lines.append("")

            if other_vars:
                lines.append("OTHER CONFIGURATION:")
                lines.append("-" * 60)
                for key, value in sorted(other_vars.items()):
                    masked = self._mask_value(value)
                    lines.append(f"  {key} = {masked}")
                lines.append("")

            if not setup_vars and not other_vars:
                lines.append("(no configuration found in .env)")

            lines.append("-" * 60)
            lines.append("Local settings stored in: .env")
            lines.append("Extended settings stored in local config files when present")
            lines.append("")
            lines.append("To edit: nano .env")

            return {"status": "success", "output": "\n".join(lines)}
        except Exception as e:
            return {"status": "error", "message": f"Failed to format variables: {e}"}
