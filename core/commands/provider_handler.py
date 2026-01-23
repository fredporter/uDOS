"""PROVIDER command handler - Provider management from TUI."""

from typing import List, Dict
import requests
from core.commands.base import BaseCommandHandler
from core.services.logging_manager import get_logger

logger = get_logger('provider-handler')

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
        else:
            return {
                "status": "error",
                "message": f"Unknown PROVIDER subcommand: {subcommand}",
                "output": "Usage: PROVIDER [LIST|STATUS <id>|ENABLE <id>|DISABLE <id>|SETUP <id>]"
            }

    def _list_providers(self) -> Dict:
        """List all providers with status."""
        try:
            response = requests.get(f"{WIZARD_API}/providers/list", timeout=5)
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])
                
                output = ["🔌 Available Providers", ""]
                
                for provider in providers:
                    pid = provider["id"]
                    name = provider["name"]
                    configured = "✓" if provider.get("configured") else "✗"
                    available = "✓" if provider.get("available") else "✗"
                    cli_installed = "✓" if provider.get("cli_installed") else "✗"
                    
                    output.append(f"{name} ({pid})")
                    output.append(f"  Config: {configured}  Available: {available}  CLI: {cli_installed}")
                    output.append(f"  {provider.get('description', '')}")
                    output.append("")
                
                output.append("Commands:")
                output.append("  PROVIDER STATUS <id>  - Detailed status")
                output.append("  PROVIDER ENABLE <id>  - Enable provider")
                output.append("  PROVIDER SETUP <id>   - Run setup")
                
                return {
                    "status": "success",
                    "output": "\n".join(output)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to list providers: {response.status_code}",
                    "output": "Is Wizard Server running? (port 8765)"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}\n\nStart Wizard: python -m wizard.server"
            }

    def _provider_status(self, provider_id: str) -> Dict:
        """Get detailed provider status."""
        try:
            response = requests.get(f"{WIZARD_API}/providers/{provider_id}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                provider = data.get("provider", {})
                
                output = [f"📊 {provider.get('name', provider_id)} Status", ""]
                output.append(f"ID: {provider.get('id')}")
                output.append(f"Type: {provider.get('type')}")
                output.append(f"Automation: {provider.get('automation')}")
                output.append("")
                
                output.append("Status:")
                output.append(f"  Configured: {'✓' if provider.get('configured') else '✗'}")
                output.append(f"  Available: {'✓' if provider.get('available') else '✗'}")
                output.append(f"  CLI Installed: {'✓' if provider.get('cli_installed') else '✗'}")
                output.append("")
                
                if provider.get("cli_command"):
                    output.append(f"CLI Command: {provider['cli_command']}")
                
                if provider.get("config_file"):
                    output.append(f"Config File: {provider['config_file']}")
                
                if provider.get("web_url"):
                    output.append(f"Setup URL: {provider['web_url']}")
                
                output.append("")
                output.append(f"Description: {provider.get('description', '')}")
                
                return {
                    "status": "success",
                    "output": "\n".join(output)
                }
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": f"Provider not found: {provider_id}",
                    "output": "Use 'PROVIDER LIST' to see available providers"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to get provider status: {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}"
            }

    def _enable_provider(self, provider_id: str) -> Dict:
        """Enable a provider."""
        try:
            response = requests.post(f"{WIZARD_API}/providers/{provider_id}/enable", timeout=5)
            if response.status_code == 200:
                data = response.json()
                output = [f"✓ Enabled {provider_id}", ""]
                
                if data.get("needs_restart"):
                    output.append("⚠️  Restart required for setup:")
                    output.append("   python -m wizard.check_provider_setup")
                    output.append("")
                    output.append("Or flag for next startup:")
                    response = requests.post(f"{WIZARD_API}/providers/{provider_id}/flag", timeout=5)
                    if response.status_code == 200:
                        output.append("✓ Flagged for setup on next restart")
                
                return {
                    "status": "success",
                    "output": "\n".join(output)
                }
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": f"Provider not found: {provider_id}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to enable provider: {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}"
            }

    def _disable_provider(self, provider_id: str) -> Dict:
        """Disable a provider."""
        try:
            response = requests.post(f"{WIZARD_API}/providers/{provider_id}/disable", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "output": f"✓ Disabled {provider_id}"
                }
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": f"Provider not found: {provider_id}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to disable provider: {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": "Cannot connect to Wizard Server",
                "output": f"Error: {str(e)}"
            }

    def _setup_provider(self, provider_id: str) -> Dict:
        """Run setup for a provider."""
        import subprocess
        
        output = [f"🔧 Setting up {provider_id}", ""]
        
        try:
            # Run setup checker for specific provider
            result = subprocess.run(
                ["python", "-m", "wizard.check_provider_setup", "--provider", provider_id],
                capture_output=False,  # Show interactive prompts
                text=True
            )
            
            if result.returncode == 0:
                output.append(f"✓ Setup completed for {provider_id}")
            else:
                output.append(f"⚠️  Setup had issues for {provider_id}")
            
            return {
                "status": "success",
                "output": "\n".join(output)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to run setup: {str(e)}"
            }
