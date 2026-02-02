"""
Provider Setup Routes
=====================

Manages API provider installation, configuration, and setup automation.
Tracks which providers need setup, runs CLI automations, and manages restart flags.
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from wizard.services.secret_store import get_secret_store, SecretStoreError


def create_provider_routes(auth_guard=None):
    """Create provider management routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/providers", tags=["providers"], dependencies=dependencies
    )

    CONFIG_PATH = Path(__file__).parent.parent / "config"
    SETUP_FLAGS_FILE = CONFIG_PATH / "provider_setup_flags.json"
    SCRIPT_DIR = Path(__file__).parent.parent.parent / "bin"

    # Provider definitions
    PROVIDERS = {
        "ollama": {
            "name": "Ollama",
            "description": "Local AI models (Mistral, Llama, etc.)",
            "type": "local",
            "automation": "full",
            "cli_required": False,
            "install_cmd": None,
            "setup_cmd": "bin/setup_wizard.sh --auto --no-browser",
            "check_cmd": "curl -s http://localhost:11434/api/tags",
            "config_file": "assistant_keys.json",
        },
        "github": {
            "name": "GitHub",
            "description": "Code hosting and version control",
            "type": "oauth",
            "automation": "cli",
            "cli_required": True,
            "cli_name": "gh",
            "install_cmd": "brew install gh",  # macOS/Linux
            "setup_cmd": "gh auth login",
            "check_cmd": "gh auth status",
            "config_file": "github_keys.json",
        },
        "openai": {
            "name": "OpenAI",
            "description": "GPT-4, GPT-3.5, DALL-E",
            "type": "api_key",
            "automation": "manual",
            "cli_required": False,
            "web_url": "https://platform.openai.com/api-keys",
            "config_file": "assistant_keys.json",
            "config_key": "OPENAI_API_KEY",
        },
        "anthropic": {
            "name": "Anthropic",
            "description": "Claude AI models",
            "type": "api_key",
            "automation": "manual",
            "cli_required": False,
            "web_url": "https://console.anthropic.com/settings/keys",
            "config_file": "assistant_keys.json",
            "config_key": "ANTHROPIC_API_KEY",
        },
        "mistral": {
            "name": "Mistral AI",
            "description": "Mistral models via API",
            "type": "api_key",
            "automation": "manual",
            "cli_required": False,
            "web_url": "https://console.mistral.ai/api-keys",
            "config_file": "assistant_keys.json",
            "config_key": "MISTRAL_API_KEY",
        },
        "openrouter": {
            "name": "OpenRouter",
            "description": "Multi-model API gateway",
            "type": "api_key",
            "automation": "manual",
            "cli_required": False,
            "web_url": "https://openrouter.ai/keys",
            "config_file": "assistant_keys.json",
            "config_key": "OPENROUTER_API_KEY",
        },
        "hubspot": {
            "name": "HubSpot",
            "description": "HubSpot CRM API",
            "type": "api_key",
            "automation": "manual",
            "cli_required": False,
            "web_url": "https://app.hubspot.com/l/api-key",
            "config_file": "hubspot_keys.json",
            "config_key": "HUBSPOT_API_KEY",
        },
        "gemini": {
            "name": "Google Gemini",
            "description": "Google's AI models",
            "type": "api_key",
            "automation": "manual",
            "cli_required": False,
            "web_url": "https://makersuite.google.com/app/apikey",
            "config_file": "assistant_keys.json",
            "config_key": "GEMINI_API_KEY",
        },
        "notion": {
            "name": "Notion",
            "description": "Workspace integration",
            "type": "integration",
            "automation": "semi",
            "cli_required": False,
            "web_url": "https://www.notion.so/my-integrations",
            "config_file": "notion_keys.json",
            "config_key": "notion_token",
        },
        "slack": {
            "name": "Slack",
            "description": "Team communication",
            "type": "oauth",
            "automation": "cli",
            "cli_required": True,
            "cli_name": "slack",
            "install_cmd": "npm install -g @slack/cli",
            "setup_cmd": "slack auth",
            "check_cmd": "slack auth test",
            "config_file": "slack_keys.json",
        },
    }

    def load_setup_flags() -> Dict[str, Any]:
        """Load provider setup flags."""
        if SETUP_FLAGS_FILE.exists():
            with open(SETUP_FLAGS_FILE, "r") as f:
                return json.load(f)
        return {"flagged": [], "completed": [], "timestamp": None}

    def _load_wizard_config() -> Dict[str, Any]:
        wizard_config = CONFIG_PATH / "wizard.json"
        if wizard_config.exists():
            try:
                return json.loads(wizard_config.read_text())
            except Exception:
                return {}
        return {}

    def _get_enabled_providers() -> List[str]:
        config = _load_wizard_config()
        enabled = set(config.get("enabled_providers") or [])

        if config.get("github_push_enabled"):
            enabled.add("github")
        if config.get("notion_enabled"):
            enabled.add("notion")
        if config.get("hubspot_enabled"):
            enabled.add("hubspot")
        if config.get("ai_gateway_enabled"):
            enabled.update(
                ["openai", "anthropic", "mistral", "openrouter", "gemini", "ollama"]
            )

        return sorted(enabled)

    def _secret_available(key_id: str) -> bool:
        try:
            store = get_secret_store()
            try:
                store.unlock()
            except SecretStoreError:
                pass
            entry = store.get_entry(key_id)
            return entry is not None and bool(entry.value)
        except SecretStoreError:
            return False

    def save_setup_flags(flags: Dict[str, Any]):
        """Save provider setup flags."""
        flags["timestamp"] = datetime.utcnow().isoformat()
        with open(SETUP_FLAGS_FILE, "w") as f:
            json.dump(flags, f, indent=2)

    def check_provider_status(provider_id: str) -> Dict[str, Any]:
        """Check if a provider is configured and working."""
        provider = PROVIDERS.get(provider_id)
        if not provider:
            return {
                "configured": False,
                "available": False,
                "error": "Unknown provider",
            }

        config_file = CONFIG_PATH / provider["config_file"]
        enabled_ids = set(_get_enabled_providers())
        status = {
            "provider_id": provider_id,
            "name": provider["name"],
            "configured": False,
            "available": False,
            "cli_installed": None,
            "needs_restart": False,
            "enabled": provider_id in enabled_ids,
        }

        # Check if CLI is installed (for CLI providers)
        if provider.get("cli_required"):
            cli_name = provider.get("cli_name")
            status["cli_installed"] = shutil.which(cli_name) is not None

        # Special handling: GitHub can be considered configured if gh auth succeeds
        if provider_id == "github":
            if status.get("cli_installed"):
                try:
                    result = subprocess.run(
                        "gh auth status",
                        shell=True,
                        capture_output=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        status["configured"] = True
                        status["available"] = True
                except Exception:
                    pass

        # Check if config file exists and has keys
        if config_file.exists():
            with open(config_file, "r") as f:
                try:
                    config = json.load(f)
                    if provider["type"] == "api_key":
                        key = provider.get("config_key", "")
                        # Flat key (legacy) e.g., OPENAI_API_KEY
                        has_key = bool(config.get(key))

                        # Nested providers map (current pattern)
                        if not has_key:
                            providers_map = config.get("providers", {})
                            entry = providers_map.get(provider_id) or providers_map.get(
                                provider.get("config_key", "")
                            )
                            if isinstance(entry, dict):
                                has_key = bool(
                                    entry.get("api_key")
                                    or entry.get("key")
                                    or entry.get("key_id")
                                )
                            elif isinstance(entry, str):
                                has_key = bool(entry)

                        status["configured"] = has_key
                    elif provider["type"] == "integration":
                        # For integrations like Notion, check nested integration.key_id
                        has_key = False
                        integration = config.get("integration", {})
                        if isinstance(integration, dict):
                            has_key = bool(
                                integration.get("key_id")
                                or integration.get("api_key")
                                or integration.get("token")
                            )
                        status["configured"] = has_key
                    else:
                        # For OAuth/local services
                        status["configured"] = True
                except:
                    pass

        if not status.get("configured"):
            secret_key_map = {
                "github": ["github_token", "github_webhook_secret"],
                "slack": ["slack_bot_token"],
                "notion": ["notion_api_key"],
                "hubspot": ["hubspot_api_key"],
                "mistral": ["mistral_api_key"],
                "openrouter": ["openrouter_api_key"],
                "ollama": ["ollama_api_key"],
            }
            for key_id in secret_key_map.get(provider_id, []):
                if _secret_available(key_id):
                    status["configured"] = True
                    break

        # Check if service is available
        if provider.get("check_cmd"):
            try:
                result = subprocess.run(
                    provider["check_cmd"],
                    shell=True,
                    capture_output=True,
                    timeout=5,
                )
                status["available"] = result.returncode == 0
            except:
                status["available"] = False

        return status

    @router.get("/list")
    async def list_providers():
        """List all available providers with status."""
        providers_list = []
        enabled_ids = set(_get_enabled_providers())
        for provider_id, provider in PROVIDERS.items():
            status = check_provider_status(provider_id)
            providers_list.append(
                {
                    **provider,
                    "id": provider_id,
                    "status": status,
                    "enabled": provider_id in enabled_ids,
                }
            )
        return {"providers": providers_list}

    @router.get("/{provider_id}/status")
    async def get_provider_status(provider_id: str):
        """Get detailed status for a specific provider."""
        if provider_id not in PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")

        status = check_provider_status(provider_id)
        provider = PROVIDERS[provider_id]

        return {
            **provider,
            "id": provider_id,
            "status": status,
            "enabled": status.get("enabled", False),
        }

    @router.post("/{provider_id}/flag")
    async def flag_provider_for_setup(provider_id: str):
        """Flag a provider to be set up on next restart."""
        if provider_id not in PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")

        flags = load_setup_flags()
        if provider_id not in flags["flagged"]:
            flags["flagged"].append(provider_id)
        save_setup_flags(flags)

        return {
            "success": True,
            "message": f"{PROVIDERS[provider_id]['name']} flagged for setup on restart",
            "needs_restart": True,
        }

    @router.post("/{provider_id}/unflag")
    async def unflag_provider(provider_id: str):
        """Remove provider from setup queue."""
        flags = load_setup_flags()
        if provider_id in flags["flagged"]:
            flags["flagged"].remove(provider_id)
        save_setup_flags(flags)

        return {"success": True, "message": "Provider unflagged"}

    @router.get("/setup/flags")
    async def get_setup_flags():
        """Get current setup flags."""
        return load_setup_flags()

    @router.post("/setup/run")
    async def run_provider_setup(provider_id: str):
        """Run setup automation for a provider (if available)."""
        if provider_id not in PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")

        provider = PROVIDERS[provider_id]

        if provider["automation"] == "manual":
            return {
                "success": False,
                "message": f"{provider['name']} requires manual setup",
                "web_url": provider.get("web_url"),
            }

        # For automated/CLI providers, return commands to run
        commands = []
        if provider.get("install_cmd"):
            commands.append({"type": "install", "cmd": provider["install_cmd"]})
        if provider.get("setup_cmd"):
            commands.append({"type": "setup", "cmd": provider["setup_cmd"]})

        return {
            "success": True,
            "provider": provider["name"],
            "automation": provider["automation"],
            "commands": commands,
            "needs_confirmation": True,
        }

    @router.post("/{provider_id}/enable")
    async def enable_provider(provider_id: str):
        """Mark provider as enabled (adds to wizard.json)."""
        if provider_id not in PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")

        wizard_config = CONFIG_PATH / "wizard.json"
        if wizard_config.exists():
            with open(wizard_config, "r") as f:
                config = json.load(f)
        else:
            config = {}

        if "enabled_providers" not in config:
            config["enabled_providers"] = []

        if provider_id not in config["enabled_providers"]:
            config["enabled_providers"].append(provider_id)

        with open(wizard_config, "w") as f:
            json.dump(config, f, indent=2)

        return {"success": True, "message": f"{PROVIDERS[provider_id]['name']} enabled"}

    @router.post("/{provider_id}/disable")
    async def disable_provider(provider_id: str):
        """Mark provider as disabled."""
        wizard_config = CONFIG_PATH / "wizard.json"
        if wizard_config.exists():
            with open(wizard_config, "r") as f:
                config = json.load(f)

            if (
                "enabled_providers" in config
                and provider_id in config["enabled_providers"]
            ):
                config["enabled_providers"].remove(provider_id)

            with open(wizard_config, "w") as f:
                json.dump(config, f, indent=2)

        return {"success": True, "message": f"Provider disabled"}

    return router
