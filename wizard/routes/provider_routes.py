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
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from wizard.services.secret_store import get_secret_store, SecretStoreError
from wizard.services.logging_api import get_logger
from wizard.services.system_info_service import get_system_info_service
from wizard.services.path_utils import get_repo_root
from wizard.services.quota_tracker import get_quota_tracker
from wizard.services.ollama_service import (
    ollama_host,
    get_pull_tracker,
    start_pull,
    get_popular_models,
)
from wizard.routes.ollama_route_utils import (
    get_installed_ollama_models_payload,
    remove_ollama_model_payload,
    validate_model_name,
)
from core.services.integration_registry import get_provider_definitions


def create_provider_routes(auth_guard=None):
    """Create provider management routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/providers", tags=["providers"], dependencies=dependencies
    )
    logger = get_logger("provider-routes")
    pull_tracker = get_pull_tracker()

    CONFIG_PATH = Path(__file__).parent.parent / "config"
    SETUP_FLAGS_FILE = CONFIG_PATH / "provider_setup_flags.json"
    SCRIPT_DIR = Path(__file__).parent.parent.parent / "bin"

    # Provider definitions
    PROVIDERS = get_provider_definitions()

    def _get_os_info():
        return get_system_info_service(get_repo_root()).get_os_info()

    def _resolve_install_cmd(provider_id: str) -> Optional[str]:
        """Choose an OS-appropriate install command when possible."""
        os_info = _get_os_info()

        if provider_id == "github":
            if os_info.is_macos and shutil.which("brew"):
                return "brew install gh"
            if os_info.is_ubuntu and shutil.which("apt-get"):
                return "sudo apt-get update && sudo apt-get install -y gh"
            if os_info.is_alpine and shutil.which("apk"):
                return "apk add github-cli"
            if shutil.which("dnf"):
                return "sudo dnf install -y gh"
            if shutil.which("yum"):
                return "sudo yum install -y gh"
            if shutil.which("pacman"):
                return "sudo pacman -S --noconfirm github-cli"
            if os_info.is_windows and shutil.which("winget"):
                return "winget install --id GitHub.cli -e"
            if os_info.is_windows and shutil.which("choco"):
                return "choco install gh -y"
            return None

        return PROVIDERS.get(provider_id, {}).get("install_cmd")

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
        if config.get("ok_gateway_enabled"):
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
                        # For integrations with nested credentials.
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
                except Exception:
                    pass

        if not status.get("configured"):
            secret_key_map = {
                "github": ["github_token", "github_webhook_secret"],
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
            except Exception:
                status["available"] = False

        return status

    def _build_provider_list() -> List[Dict[str, Any]]:
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
        return providers_list

    @router.get("")
    async def list_providers_root():
        """List all available providers (alias for /list)."""
        return {"providers": _build_provider_list()}

    @router.get("/list")
    async def list_providers():
        """List all available providers with status."""
        return {"providers": _build_provider_list()}

    @router.get("/dashboard")
    async def providers_dashboard():
        """Aggregate provider list + status + quota summaries."""
        quotas = get_quota_tracker().get_all_quotas()
        return {
            "providers": _build_provider_list(),
            "quotas": quotas,
        }

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

    @router.get("/{provider_id}/config")
    async def get_provider_config(provider_id: str):
        """Get provider config file presence and keys (no secrets)."""
        if provider_id not in PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")

        provider = PROVIDERS[provider_id]
        config_file = provider.get("config_file")
        config_key = provider.get("config_key")
        config_path = (CONFIG_PATH / config_file) if config_file else None

        payload = {
            "provider_id": provider_id,
            "config_file": str(config_path) if config_path else None,
            "config_key": config_key,
            "exists": False,
            "keys": [],
        }

        if config_path and config_path.exists():
            payload["exists"] = True
            try:
                data = json.loads(config_path.read_text())
                if isinstance(data, dict):
                    payload["keys"] = list(data.keys())
            except Exception:
                payload["keys"] = []

        return payload

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
        if provider.get("cli_required"):
            cli_name = provider.get("cli_name")
            if cli_name and shutil.which(cli_name) is None:
                install_cmd = _resolve_install_cmd(provider_id)
                if install_cmd:
                    commands.append({"type": "install", "cmd": install_cmd})
        elif provider.get("install_cmd"):
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

    # ─────────────────────────────────────────────────────────────
    # Ollama Model Management
    # ─────────────────────────────────────────────────────────────

    @router.get("/ollama/models/available")
    async def get_available_ollama_models():
        """
        Get list of popular Ollama models.
        Returns: List of recommended models with sizes and descriptions
        """
        popular_models = [
            {
                "name": "devstral-small-2",
                "size": "10.7B",
                "category": "coding",
                "description": "Mistral's lightweight coding assistant (8GB RAM)",
                "command": "ollama pull devstral-small-2",
                "installed": False,
            },
            {
                "name": "mistral",
                "size": "7.3B",
                "category": "general",
                "description": "Mistral 7B - fast general purpose model (4GB RAM)",
                "command": "ollama pull mistral",
                "installed": False,
            },
            {
                "name": "neural-chat",
                "size": "13B",
                "category": "chat",
                "description": "Intel Neural Chat - conversation optimized (8GB RAM)",
                "command": "ollama pull neural-chat",
                "installed": False,
            },
            {
                "name": "llama2",
                "size": "7B",
                "category": "general",
                "description": "Llama 2 - Meta's open foundation model (4GB RAM)",
                "command": "ollama pull llama2",
                "installed": False,
            },
            {
                "name": "openchat",
                "size": "7B",
                "category": "chat",
                "description": "OpenChat - lightweight conversation model (4GB RAM)",
                "command": "ollama pull openchat",
                "installed": False,
            },
            {
                "name": "zephyr",
                "size": "7B",
                "category": "general",
                "description": "Zephyr - fine-tuned Mistral (4GB RAM)",
                "command": "ollama pull zephyr",
                "installed": False,
            },
            {
                "name": "orca-mini",
                "size": "3B",
                "category": "general",
                "description": "Orca Mini - tiny but capable (2GB RAM)",
                "command": "ollama pull orca-mini",
                "installed": False,
            },
            {
                "name": "dolphin-mixtral",
                "size": "46.7B",
                "category": "advanced",
                "description": "Dolphin Mixtral - mixture of experts (24GB+ RAM)",
                "command": "ollama pull dolphin-mixtral",
                "installed": False,
            },
        ]

        # Check which models are installed locally
        try:
            response = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if response.returncode == 0:
                installed_lines = response.stdout.strip().split("\n")[1:]  # Skip header
                installed_names = set()
                for line in installed_lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            # Extract base model name (e.g., "mistral" from "mistral:latest")
                            model_name = parts[0].split(":")[0]
                            installed_names.add(model_name)

                # Mark installed models
                for model in popular_models:
                    if model["name"] in installed_names:
                        model["installed"] = True
        except Exception:
            pass  # Ollama may not be running, that's OK

        return {
            "success": True,
            "models": popular_models,
            "categories": ["coding", "general", "chat", "advanced"],
        }

    @router.get("/ollama/models/installed")
    async def get_installed_ollama_models():
        """
        Get list of currently installed Ollama models.
        Returns: List of installed models with details
        """
        return get_installed_ollama_models_payload()

    @router.post("/ollama/models/pull")
    async def pull_ollama_model(model: str = Query(..., description="Model name to pull")):
        """
        Pull (download) an Ollama model.
        Args: model - Model name (e.g., 'mistral', 'devstral-small-2')
        """
        validate_model_name(model)

        try:
            pull_tracker.set(model, state="queued", percent=0)
            start_pull(model, pull_tracker)
            return {
                "success": True,
                "message": f"Started pulling {model}...",
                "model": model,
                "note": "Poll /api/providers/ollama/models/pull/status for progress",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.get("/ollama/models/pull/status")
    async def pull_ollama_status(model: str = Query(..., description="Model name")):
        """Get pull progress for an Ollama model."""
        status = pull_tracker.get(model)
        if not status:
            return {"success": False, "error": "No pull status found", "model": model}
        return {"success": True, "status": status}

    @router.post("/ollama/models/remove")
    async def remove_ollama_model(model: str = Query(..., description="Model name to remove")):
        """Remove an installed Ollama model."""
        return remove_ollama_model_payload(model)

    return router


def create_public_ollama_routes():
    """
    Create public Ollama routes that don't require authentication.
    These are local operations and don't expose sensitive data.
    """
    router = APIRouter(prefix="/api/providers/ollama", tags=["ollama-public"])
    pull_tracker = get_pull_tracker()

    @router.get("/models/available")
    async def get_available_ollama_models_public():
        """Public endpoint: Get list of popular Ollama models."""
        popular_models = get_popular_models(include_installed=True)

        return {
            "success": True,
            "models": popular_models,
            "categories": ["coding", "general", "chat", "advanced"],
        }

    @router.get("/models/installed")
    async def get_installed_ollama_models_public():
        """Public endpoint: Get list of currently installed Ollama models."""
        return get_installed_ollama_models_payload()

    @router.post("/models/pull")
    async def pull_ollama_model_public(
        model: str = Query(..., description="Model name to pull")
    ):
        """Public endpoint: Pull (download) an Ollama model."""
        validate_model_name(model)

        try:
            pull_tracker.set(model, state="queued", percent=0)
            start_pull(model, pull_tracker)
            return {
                "success": True,
                "message": f"Started pulling {model} via Ollama API...",
                "model": model,
                "note": "Poll /api/providers/ollama/models/pull/status for progress",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.get("/models/pull/status")
    async def pull_ollama_status_public(
        model: str = Query(..., description="Model name")
    ):
        """Public endpoint: Get pull progress for an Ollama model."""
        status = pull_tracker.get(model)
        if not status:
            return {"success": False, "error": "No pull status found", "model": model}
        return {"success": True, "status": status}

    @router.post("/models/remove")
    async def remove_ollama_model_public(
        model: str = Query(..., description="Model name to remove")
    ):
        """Public endpoint: Remove an installed Ollama model."""
        return remove_ollama_model_payload(model)

    return router
