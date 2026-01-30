"""CONFIG command handler - Wizard configuration and variable management from TUI."""

from typing import List, Dict, Optional
import requests
import json
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.logging_manager import get_logger, get_repo_root, LogTags

logger = get_logger("config-handler")

WIZARD_API = "http://localhost:8765/api/v1"


class ConfigHandler(BaseCommandHandler, HandlerLoggingMixin):
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
                # No params = list all variables
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
        try:
            response = requests.get(f"{WIZARD_API}/config/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                from core.tui.output import OutputToolkit

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
                from core.tui.output import OutputToolkit

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
        """List all variables from Wizard."""
        try:
            token = self._get_admin_token()
            if not token:
                return self._offline_message()

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{WIZARD_API}/config/variables", headers=headers, timeout=5
            )

            if response.status_code != 200:
                error_detail = ""
                try:
                    error_detail = response.json().get("detail", "")
                except:
                    error_detail = response.text[:200] if response.text else ""
                return {
                    "status": "error",
                    "message": f"Failed to list variables: HTTP {response.status_code}",
                    "output": f"Detail: {error_detail}" if error_detail else "Check Wizard Server logs",
                }

            try:
                variables = response.json().get("variables", [])
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "message": "Invalid response from Wizard Server",
                    "output": "Response was not valid JSON. Check Wizard Server logs.",
                }

            # Group by type
            system_vars = [v for v in variables if v["type"] == "system"]
            user_vars = [v for v in variables if v["type"] == "user"]
            feature_vars = [v for v in variables if v["type"] == "feature"]

            from core.tui.output import OutputToolkit

            lines = [OutputToolkit.banner("CONFIGURATION"), ""]

            if system_vars:
                lines.append("System Variables ($):")
                for var in system_vars:
                    key = var["key"]
                    value = self._mask_value(var["value"])
                    desc = var.get("description", "")
                    lines.append(f"  {key} = {value}")
                    if desc:
                        lines.append(f"    └─ {desc}")
                lines.append("")

            if user_vars:
                lines.append("User Variables (@):")
                for var in user_vars:
                    key = var["key"]
                    value = var["value"]
                    desc = var.get("description", "")
                    lines.append(f"  {key} = {value}")
                    if desc:
                        lines.append(f"    └─ {desc}")
                lines.append("")

            if feature_vars:
                lines.append("Feature Flags:")
                for var in feature_vars:
                    key = var["key"]
                    value = var["value"]
                    status = "OK" if value else "X"
                    desc = var.get("description", "")
                    lines.append(f"  {status} {key} = {value}")
                    if desc:
                        lines.append(f"    └─ {desc}")
                lines.append("")

            lines.append("Use: CONFIG <key> to view details")
            lines.append("Use: CONFIG <key> <value> to update")

            return {"status": "success", "output": "\n".join(lines)}

        except requests.exceptions.RequestException:
            return self._offline_message()
        except Exception as e:
            return {"status": "error", "message": f"Failed to list variables: {e}"}

    def _get_variable(self, key: str) -> Dict:
        """Get a specific variable."""
        try:
            token = self._get_admin_token()
            if not token:
                return self._offline_message()

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{WIZARD_API}/config/get/{key}", headers=headers, timeout=5
            )

            if response.status_code == 404:
                return {
                    "status": "error",
                    "message": f"Variable not found: {key}",
                    "output": "Use CONFIG to list all variables",
                }

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Failed to get variable: HTTP {response.status_code}",
                }

            data = response.json()
            var = data.get("variable", {})

            from core.tui.output import OutputToolkit

            lines = [OutputToolkit.banner(f"VARIABLE: {var['key']}"), ""]
            lines.append(
                f"Value: {self._mask_value(var['value']) if var['type'] == 'system' else var['value']}"
            )
            lines.append(f"Type: {var['type']}")
            lines.append(f"Tier: {var['tier']}")
            if var.get("description"):
                lines.append(f"Description: {var['description']}")
            if var.get("updated_at"):
                lines.append(f"Updated: {var['updated_at']}")

            return {"status": "success", "output": "\n".join(lines)}

        except requests.exceptions.RequestException:
            return self._offline_message()
        except Exception as e:
            return {"status": "error", "message": f"Failed to get variable: {e}"}

    def _set_variable(self, key: str, value: str) -> Dict:
        """Set a variable value."""
        try:
            token = self._get_admin_token()
            if not token:
                return self._offline_message()

            # Parse boolean values
            if value.lower() in ["true", "yes", "1", "on"]:
                parsed_value = True
            elif value.lower() in ["false", "no", "0", "off"]:
                parsed_value = False
            else:
                parsed_value = value

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{WIZARD_API}/config/set",
                headers=headers,
                json={"key": key, "value": parsed_value, "sync": True},
                timeout=5,
            )

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Failed to set variable: HTTP {response.status_code}",
                    "output": response.json().get("detail", ""),
                }

            return {
                "status": "success",
                "output": f"OK Set {key} = {parsed_value}\n\nChanges synchronized across all components",
            }

        except requests.exceptions.RequestException:
            return self._offline_message()
        except Exception as e:
            return {"status": "error", "message": f"Failed to set variable: {e}"}

    def _delete_variable(self, key: str) -> Dict:
        """Delete a variable."""
        try:
            token = self._get_admin_token()
            if not token:
                return self._offline_message()

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.delete(
                f"{WIZARD_API}/config/delete/{key}", headers=headers, timeout=5
            )

            if response.status_code == 404:
                return {"status": "error", "message": f"Variable not found: {key}"}

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Failed to delete variable: HTTP {response.status_code}",
                }

            return {"status": "success", "output": f"OK Deleted variable: {key}"}

        except requests.exceptions.RequestException:
            return self._offline_message()
        except Exception as e:
            return {"status": "error", "message": f"Failed to delete variable: {e}"}

    def _sync_variables(self) -> Dict:
        """Sync all variables across tiers."""
        try:
            token = self._get_admin_token()
            if not token:
                return self._offline_message()

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{WIZARD_API}/config/sync", headers=headers, timeout=10
            )

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Failed to sync: HTTP {response.status_code}",
                }

            data = response.json()
            counts = data.get("counts", {})

            from core.tui.output import OutputToolkit

            lines = [OutputToolkit.banner("SYNC COMPLETE"), ""]
            lines.append(f"  .env → secrets: {counts.get('env_to_secret', 0)}")
            lines.append(f"  secrets → .env: {counts.get('secret_to_env', 0)}")
            lines.append(f"  Config synced: {counts.get('config_synced', 0)}")

            return {"status": "success", "output": "\n".join(lines)}

        except requests.exceptions.RequestException:
            return self._offline_message()
        except Exception as e:
            return {"status": "error", "message": f"Failed to sync: {e}"}

    def _export_config(self) -> Dict:
        """Export configuration for backup."""
        try:
            token = self._get_admin_token()
            if not token:
                return self._offline_message()

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{WIZARD_API}/config/export", headers=headers, timeout=5
            )

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Failed to export: HTTP {response.status_code}",
                }

            data = response.json()
            export_path = get_repo_root() / "memory" / "config-backup.json"
            export_path.parent.mkdir(parents=True, exist_ok=True)
            export_path.write_text(json.dumps(data, indent=2))

            return {
                "status": "success",
                "output": f"OK Config exported to: {export_path}\n\nNOTE: This backup does NOT include secrets",
            }

        except requests.exceptions.RequestException:
            return self._offline_message()
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
    $NOTION_API_KEY         Notion integration
    
  @variable                 User variables (encrypted secrets)
    @username               Your username
    @timezone               Your timezone
    @location               Your location
    
  flag_name                 Feature flags (wizard.json)
    notion_enabled          Enable Notion
    ai_gateway_enabled      Enable AI gateway

EXAMPLES:
  CONFIG                    Show all variables
  CONFIG @username          Show your username
  CONFIG @timezone PST      Set your timezone
  CONFIG notion_enabled true    Enable Notion integration
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

    def _get_admin_token(self) -> Optional[str]:
        """Get admin token from file."""
        token_path = get_repo_root() / "memory" / "private" / "wizard_admin_token.txt"
        if not token_path.exists():
            # Try .env
            env_path = get_repo_root() / ".env"
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith("WIZARD_ADMIN_TOKEN="):
                        return line.split("=", 1)[1].strip()
            return None
        return token_path.read_text().strip()

    def _mask_value(self, value: str) -> str:
        """Mask sensitive values."""
        if not value or len(value) < 8:
            return "***"
        return value[:4] + "..." + value[-4:]

    def _offline_message(self) -> Dict:
        """Message when Wizard is not available."""
        return {
            "status": "error",
            "message": "Wizard Server not available",
            "output": "Start Wizard: ./bin/start_wizard.sh",
        }
