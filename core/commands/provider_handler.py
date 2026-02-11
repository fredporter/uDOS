"""PROVIDER command handler - Provider management from TUI."""

from typing import List, Dict, Optional
import requests
from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_api import get_logger
from core.services.rate_limit_helpers import guard_wizard_endpoint

logger = get_logger("provider-handler")

WIZARD_API = "http://localhost:8765/api/v1"


class ProviderHandler(BaseCommandHandler):
    """Handler for PROVIDER command - Provider management from TUI."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """Handle PROVIDER commands."""

        if not params:
            return self._list_providers()

        subcommand = params[0].upper()
        args = params[1:] if len(params) > 1 else []

        if subcommand == "LIST":
            return self._list_providers()
        elif subcommand == "STATUS" and args:
            return self._provider_status(args[0])
        elif subcommand == "ENABLE" and args:
            return self._enable_provider(args[0])
        elif subcommand == "DISABLE" and args:
            return self._disable_provider(args[0])
        elif subcommand == "SETUP" and args:
            return self._setup_provider(args[0])
        elif subcommand == "GENSECRET" and args:
            return self._generate_secret(args[0])
        else:
            return {
                "status": "error",
                "message": f"Unknown PROVIDER subcommand: {subcommand}",
                "output": "Usage: PROVIDER [LIST|STATUS <id>|ENABLE <id>|DISABLE <id>|SETUP <id>|GENSECRET <id>]",
            }

    def _throttle_guard(self, endpoint: str) -> Optional[Dict]:
        return guard_wizard_endpoint(endpoint)

    def _list_providers(self) -> Dict:
        """List all providers with status."""
        try:
            guard = self._throttle_guard("/api/providers/list")
            if guard:
                return guard
            response = requests.get(f"{WIZARD_API}/providers/list", timeout=5)
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])

                output = [OutputToolkit.banner("AVAILABLE PROVIDERS"), ""]

                for provider in providers:
                    pid = provider["id"]
                    name = provider["name"]
                    configured = "OK" if provider.get("configured") else "X"
                    available = "OK" if provider.get("available") else "X"
                    cli_installed = "OK" if provider.get("cli_installed") else "X"

                    output.append(f"{name} ({pid})")
                    output.append(
                        f"  Config: {configured}  Available: {available}  CLI: {cli_installed}"
                    )
                    output.append(f"  {provider.get('description', '')}")
                    output.append("")

                output.append("Commands:")
                output.append("  PROVIDER STATUS <id>  - Detailed status")
                output.append("  PROVIDER ENABLE <id>  - Enable provider")
                output.append("  PROVIDER SETUP <id>   - Run setup")
                output.append("  PROVIDER GENSECRET <id> - Generate secrets (github)")

                return {"status": "success", "output": "\n".join(output)}
            else:
                return {
                    "status": "error",
                    "message": f"Failed to list providers: {response.status_code}",
                    "output": "Is Wizard Server running? (port 8765)",
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": (
                    "❌ Wizard Server is not running.\n\n"
                    "Start it with one of these launchers:\n"
                    "  • ./bin/Launch-uCODE.sh wizard (interactive)\n"
                    "  • ./bin/Launch-Dev-Mode.command (full dev stack)\n\n"
                    "Or manually:\n"
                    "  source .venv/bin/activate && python -m wizard.server\n\n"
                    "Then try: PROVIDER"
                ),
            }

    def _provider_status(self, provider_id: str) -> Dict:
        """Get detailed provider status."""
        try:
            guard = self._throttle_guard(f"/api/providers/{provider_id}/status")
            if guard:
                return guard
            response = requests.get(
                f"{WIZARD_API}/providers/{provider_id}/status", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                provider = data.get("provider", {})

                output = [
                    OutputToolkit.banner(
                        f"{provider.get('name', provider_id).upper()} STATUS"
                    ),
                    "",
                ]
                output.append(f"ID: {provider.get('id')}")
                output.append(f"Type: {provider.get('type')}")
                output.append(f"Automation: {provider.get('automation')}")
                output.append("")

                output.append("Status:")
                output.append(
                    f"  Configured: {'OK' if provider.get('configured') else 'X'}"
                )
                output.append(
                    f"  Available: {'OK' if provider.get('available') else 'X'}"
                )
                output.append(
                    f"  CLI Installed: {'OK' if provider.get('cli_installed') else 'X'}"
                )
                output.append("")

                if provider.get("cli_command"):
                    output.append(f"CLI Command: {provider['cli_command']}")

                if provider.get("config_file"):
                    output.append(f"Config File: {provider['config_file']}")

                if provider.get("web_url"):
                    output.append(f"Setup URL: {provider['web_url']}")

                output.append("")
                output.append(f"Description: {provider.get('description', '')}")

                return {"status": "success", "output": "\n".join(output)}
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": f"Provider not found: {provider_id}",
                    "output": "Use 'PROVIDER LIST' to see available providers",
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to get provider status: {response.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}",
            }

    def _enable_provider(self, provider_id: str) -> Dict:
        """Enable a provider."""
        try:
            guard = self._throttle_guard(f"/api/providers/{provider_id}/enable")
            if guard:
                return guard
            response = requests.post(
                f"{WIZARD_API}/providers/{provider_id}/enable", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                output = [f"OK Enabled {provider_id}", ""]

                if data.get("needs_restart"):
                    output.append("WARN Restart required for setup:")
                    output.append("   python -m wizard.check_provider_setup")
                    output.append("")
                    output.append("Or flag for next startup:")
                    flag_guard = self._throttle_guard(
                        f"/api/providers/{provider_id}/flag"
                    )
                    if flag_guard:
                        return flag_guard
                    response = requests.post(
                        f"{WIZARD_API}/providers/{provider_id}/flag", timeout=5
                    )
                    if response.status_code == 200:
                        output.append("OK Flagged for setup on next restart")

                return {"status": "success", "output": "\n".join(output)}
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": f"Provider not found: {provider_id}",
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to enable provider: {response.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}",
            }

    def _disable_provider(self, provider_id: str) -> Dict:
        """Disable a provider."""
        try:
            guard = self._throttle_guard(f"/api/providers/{provider_id}/disable")
            if guard:
                return guard
            response = requests.post(
                f"{WIZARD_API}/providers/{provider_id}/disable", timeout=5
            )
            if response.status_code == 200:
                return {"status": "success", "output": f"OK Disabled {provider_id}"}
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": f"Provider not found: {provider_id}",
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to disable provider: {response.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}",
            }

    def _setup_provider(self, provider_id: str) -> Dict:
        """Run setup for a provider."""
        import subprocess

        output = [OutputToolkit.banner(f"SETUP {provider_id.upper()}"), ""]

        try:
            # Run setup checker for specific provider
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "wizard.check_provider_setup",
                    "--provider",
                    provider_id,
                ],
                capture_output=False,  # Show interactive prompts
                text=True,
            )

            if result.returncode == 0:
                output.append(f"OK Setup completed for {provider_id}")
                return {"status": "success", "output": "\n".join(output)}
            else:
                output.append(f"WARN Setup had issues for {provider_id}")
                output.append("\nCheck the output above for details.")
                return {"status": "error", "output": "\n".join(output)}
        except Exception as e:
            return {"status": "error", "message": f"Failed to run setup: {str(e)}"}

    def _generate_secret(self, provider_id: str) -> Dict:
        """Generate secrets for a provider."""
        import subprocess
        import sys

        output = [OutputToolkit.banner(f"GENERATE SECRETS FOR {provider_id.upper()}"), ""]

        if provider_id == "github":
            try:
                # Run the secret generator
                result = subprocess.run(
                    [sys.executable, "-m", "wizard.tools.generate_github_secrets"],
                    capture_output=False,  # Show output directly
                    text=True,
                )

                if result.returncode == 0:
                    return {"status": "success", "output": "\n".join(output)}
                else:
                    output.append(f"WARN Secret generation had issues")
                    return {"status": "error", "output": "\n".join(output)}
            except Exception as e:
                return {"status": "error", "message": f"Failed to generate secret: {str(e)}"}
        else:
            output.append(f"Secret generation not available for {provider_id}")
            output.append("\nCurrently supported:")
            output.append("  • github - Generate webhook secret")
            return {"status": "error", "output": "\n".join(output)}
