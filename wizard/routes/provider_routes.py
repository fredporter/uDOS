"""
Provider Setup Routes
=====================

Manages API provider installation, configuration, and setup automation.
Tracks which providers need setup, runs CLI automations, and manages restart flags.
"""

import json
import os
import re
import subprocess
import shutil
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from wizard.services.secret_store import get_secret_store, SecretStoreError
from wizard.services.logging_manager import get_logger
from wizard.services.system_info_service import get_system_info_service
from wizard.services.path_utils import get_repo_root


def create_provider_routes(auth_guard=None):
    """Create provider management routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/providers", tags=["providers"], dependencies=dependencies
    )
    logger = get_logger("provider-routes")
    pull_status: Dict[str, Dict[str, Any]] = {}
    pull_lock = threading.Lock()

    CONFIG_PATH = Path(__file__).parent.parent / "config"
    SETUP_FLAGS_FILE = CONFIG_PATH / "provider_setup_flags.json"
    SCRIPT_DIR = Path(__file__).parent.parent.parent / "bin"

    def _ensure_path_export(bin_path: str) -> None:
        export_line = f'export PATH="{bin_path}:$PATH"'
        candidates = [
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.zshrc"),
            os.path.expanduser("~/.profile"),
        ]
        for path in candidates:
            try:
                if os.path.exists(path):
                    content = ""
                    try:
                        content = Path(path).read_text()
                    except Exception:
                        content = ""
                    if export_line in content:
                        continue
                with open(path, "a") as handle:
                    handle.write(f"\n# Added by uDOS HubSpot CLI install\n{export_line}\n")
            except Exception:
                continue

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
            "web_url": "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/overview",
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
        "hubspot_cli": {
            "name": "HubSpot CLI",
            "description": "HubSpot developer CLI (hs)",
            "type": "cli",
            "automation": "cli",
            "cli_required": True,
            "cli_name": "hs",
            "install_cmd": "npm install -g @hubspot/cli",
            "setup_cmd": "hs init",
            "check_cmd": "hs account list",
            "config_file": "hubspot_keys.json",
        },
    }

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

        if provider_id == "hubspot_cli":
            if shutil.which("npm"):
                return "npm install -g @hubspot/cli"
            return None

        return PROVIDERS.get(provider_id, {}).get("install_cmd")

    def _ollama_host() -> str:
        return (os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")

    def _ollama_api_request(path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{_ollama_host()}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(
            url,
            method="POST" if data is not None else "GET",
            data=data,
            headers={"Content-Type": "application/json"} if data is not None else {},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}

    def _set_pull_status(model: str, **fields: Any) -> None:
        with pull_lock:
            current = pull_status.get(model, {"model": model})
            current.update(fields)
            pull_status[model] = current

    def _pull_via_api(model: str) -> None:
        _set_pull_status(model, state="connecting", percent=0)
        try:
            url = f"{_ollama_host()}/api/pull"
            data = json.dumps({"name": model}).encode("utf-8")
            req = urllib.request.Request(
                url,
                method="POST",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                for raw in resp:
                    line = raw.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except Exception:
                        continue
                    if payload.get("error"):
                        _set_pull_status(
                            model,
                            state="error",
                            error=payload.get("error"),
                        )
                        return
                    total = payload.get("total")
                    completed = payload.get("completed")
                    percent = None
                    if isinstance(total, (int, float)) and total:
                        percent = int((completed or 0) / total * 100)
                    _set_pull_status(
                        model,
                        state="pulling",
                        status=payload.get("status"),
                        total=total,
                        completed=completed,
                        percent=percent,
                    )
            _set_pull_status(model, state="done", percent=100, status="complete")
        except Exception as exc:
            _set_pull_status(model, state="error", error=str(exc))

    def _start_pull(model: str) -> None:
        thread = threading.Thread(target=_pull_via_api, args=(model,), daemon=True)
        thread.start()

    def _pull_via_cli(model: str) -> None:
        _set_pull_status(model, state="pulling", percent=None)
        percent_re = re.compile(r"(\\d{1,3})%")
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for stream in (process.stdout, process.stderr):
                if not stream:
                    continue
                for line in stream:
                    match = percent_re.search(line)
                    if match:
                        pct = min(max(int(match.group(1)), 0), 100)
                        _set_pull_status(model, percent=pct, status=line.strip())
            code = process.wait()
            if code == 0:
                _set_pull_status(model, state="done", percent=100, status="complete")
            else:
                _set_pull_status(
                    model,
                    state="error",
                    error=f"ollama pull exited {code}",
                )
        except Exception as exc:
            _set_pull_status(model, state="error", error=str(exc))

    def _start_pull(model: str) -> None:
        # Prefer API for progress if reachable
        try:
            _ollama_api_request("/api/tags")
            thread = threading.Thread(target=_pull_via_api, args=(model,), daemon=True)
        except Exception:
            if shutil.which("ollama"):
                thread = threading.Thread(target=_pull_via_cli, args=(model,), daemon=True)
            else:
                _set_pull_status(
                    model,
                    state="error",
                    error="ollama CLI not found and Ollama API unreachable",
                )
                return
        thread.start()

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
                except:
                    pass

        if not status.get("configured"):
            secret_key_map = {
                "github": ["github_token", "github_webhook_secret"],
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
        try:
            response = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if response.returncode == 0:
                lines = response.stdout.strip().split("\n")
                if len(lines) < 2:
                    return {"success": True, "models": [], "count": 0}

                models = []
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            models.append(
                                {
                                    "name": parts[0],
                                    "id": parts[0],
                                    "size": parts[1] if len(parts) > 1 else "?",
                                    "modified": " ".join(parts[2:]) if len(parts) > 2 else "",
                                }
                            )

                return {
                    "success": True,
                    "models": models,
                    "count": len(models),
                }
            else:
                return {
                    "success": False,
                    "error": "Ollama not reachable. Is it running?",
                    "help": "Start Ollama: ollama serve",
                }
        except FileNotFoundError:
            try:
                data = _ollama_api_request("/api/tags")
                models = []
                for item in data.get("models", []):
                    name = item.get("name") or ""
                    models.append(
                        {
                            "name": name,
                            "id": name,
                            "size": item.get("size", "?"),
                            "modified": item.get("modified_at", ""),
                        }
                    )
                return {"success": True, "models": models, "count": len(models)}
            except Exception as exc:
                return {
                    "success": False,
                    "error": "ollama CLI not found",
                    "help": f"Install Ollama or set OLLAMA_HOST (current: {_ollama_host()})",
                    "detail": str(exc),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.post("/ollama/models/pull")
    async def pull_ollama_model(model: str = Query(..., description="Model name to pull")):
        """
        Pull (download) an Ollama model.
        Args: model - Model name (e.g., 'mistral', 'devstral-small-2')
        """
        if not model or not isinstance(model, str):
            raise HTTPException(status_code=400, detail="model parameter required")

        # Validate model name (prevent injection)
        if not all(c.isalnum() or c in "-_:." for c in model):
            raise HTTPException(status_code=400, detail="Invalid model name")

        try:
            _set_pull_status(model, state="queued", percent=0)
            _start_pull(model)
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
        with pull_lock:
            status = pull_status.get(model)
        if not status:
            return {"success": False, "error": "No pull status found", "model": model}
        return {"success": True, "status": status}

    @router.post("/ollama/models/remove")
    async def remove_ollama_model(model: str = Query(..., description="Model name to remove")):
        """Remove an installed Ollama model."""
        if not model or not isinstance(model, str):
            raise HTTPException(status_code=400, detail="model parameter required")

        # Validate model name
        if not all(c.isalnum() or c in "-_:." for c in model):
            raise HTTPException(status_code=400, detail="Invalid model name")

        try:
            result = subprocess.run(
                ["ollama", "rm", model],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return {"success": True, "message": f"Removed {model}"}
            else:
                return {"success": False, "error": result.stderr}
        except FileNotFoundError:
            return {
                "success": False,
                "error": "ollama CLI not found",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===========================
    # HUBSPOT CLI ENDPOINTS
    # ===========================

    @router.get("/hubspot/cli/status")
    async def get_hubspot_cli_status():
        """
        Check if HubSpot CLI is installed and get version.
        Returns: Installation status, version, and setup instructions
        """
        try:
            # Check if CLI is installed
            version_result = subprocess.run(
                ["hs", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if version_result.returncode == 0:
                version = version_result.stdout.strip()

                # Check if CLI is authenticated
                auth_result = subprocess.run(
                    ["hs", "account", "list"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                authenticated = auth_result.returncode == 0 and len(auth_result.stdout.strip()) > 0

                return {
                    "success": True,
                    "installed": True,
                    "version": version,
                    "authenticated": authenticated,
                    "message": f"HubSpot CLI {version} is installed",
                }
            else:
                return {
                    "success": False,
                    "installed": False,
                    "version": None,
                    "authenticated": False,
                    "message": "HubSpot CLI not installed",
                    "help": "Run: npm install -g @hubspot/cli && hs init",
                }
        except FileNotFoundError:
            return {
                "success": False,
                "installed": False,
                "version": None,
                "authenticated": False,
                "message": "HubSpot CLI not found",
                "help": "Install: npm install -g @hubspot/cli && hs init",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.post("/hubspot/cli/install")
    async def install_hubspot_cli():
        """
        Install HubSpot CLI via npm.
        Returns: Installation progress and result
        """
        try:
            # Check if npm is available
            npm_check = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                timeout=5,
            )

            if npm_check.returncode != 0:
                return {
                    "success": False,
                    "error": "npm not found",
                    "help": "Install Node.js and npm first",
                }

            # Install @hubspot/cli globally
            install_result = subprocess.run(
                ["npm", "install", "-g", "@hubspot/cli"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if install_result.returncode == 0:
                return {
                    "success": True,
                    "message": "HubSpot CLI installed successfully",
                    "next_step": "Run 'hs init' to authenticate",
                }
            if "EACCES" in (install_result.stderr or ""):
                user_prefix = os.path.expanduser("~/.local")
                fallback = subprocess.run(
                    [
                        "npm",
                        "install",
                        "-g",
                        "@hubspot/cli",
                        "--prefix",
                        user_prefix,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if fallback.returncode == 0:
                    _ensure_path_export(f"{user_prefix}/bin")
                    return {
                        "success": True,
                        "message": "HubSpot CLI installed to user prefix",
                        "next_step": f"PATH updated for {user_prefix}/bin; run 'hs init'",
                    }
            else:
                return {
                    "success": False,
                    "error": install_result.stderr or "Installation failed",
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timed out (>2 minutes)",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.post("/hubspot/cli/init")
    async def init_hubspot_cli():
        """
        Start HubSpot CLI authentication (hs init).
        Note: This will open browser for user to generate Personal Access Key.
        Returns: Instructions and status
        """
        return {
            "success": False,
            "message": "Interactive auth not supported via API",
            "instructions": [
                "Run in terminal: hs init",
                "Follow prompts to generate Personal Access Key",
                "Copy and paste the key when prompted",
                "Set as default account when asked",
            ],
            "help": "https://developers.hubspot.com/docs/getting-started/quickstart",
        }

    @router.get("/hubspot/cli/accounts")
    async def get_hubspot_accounts():
        """
        List authenticated HubSpot accounts.
        Returns: List of accounts configured in CLI
        """
        try:
            result = subprocess.run(
                ["hs", "account", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                # Parse account list output
                accounts = []
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if line and not line.startswith("=") and "Account" not in line:
                        accounts.append(line)

                return {
                    "success": True,
                    "accounts": accounts,
                    "count": len(accounts),
                }
            else:
                return {
                    "success": False,
                    "accounts": [],
                    "message": "No accounts configured or CLI error",
                    "help": "Run: hs init",
                }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "HubSpot CLI not installed",
                "help": "Install: npm install -g @hubspot/cli",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.post("/hubspot/cli/project/create")
    async def create_hubspot_project(project_name: str = Query(..., description="Project name")):
        """
        Create a new HubSpot project with hs get-started.
        Note: This is interactive and best done via terminal.
        Returns: Instructions for running via terminal
        """
        return {
            "success": False,
            "message": "Project creation is interactive",
            "instructions": [
                f"Run in terminal: hs get-started",
                "Select 'App' when prompted",
                f"Enter project name: {project_name}",
                "Set local directory path",
                "Confirm upload to HubSpot",
                "Install dependencies and build",
            ],
            "help": "https://developers.hubspot.com/docs/getting-started/quickstart#create-and-upload-a-project",
        }

    return router


def create_public_ollama_routes():
    """
    Create public Ollama routes that don't require authentication.
    These are local operations and don't expose sensitive data.
    """
    router = APIRouter(prefix="/api/providers/ollama", tags=["ollama-public"])
    pull_status: Dict[str, Dict[str, Any]] = {}
    pull_lock = threading.Lock()

    def _ollama_host() -> str:
        return (os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")

    def _ollama_api_request(path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{_ollama_host()}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(
            url,
            method="POST" if data is not None else "GET",
            data=data,
            headers={"Content-Type": "application/json"} if data is not None else {},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}

    def _set_pull_status(model: str, **fields: Any) -> None:
        with pull_lock:
            current = pull_status.get(model, {"model": model})
            current.update(fields)
            pull_status[model] = current

    def _pull_via_api(model: str) -> None:
        _set_pull_status(model, state="connecting", percent=0)
        try:
            url = f"{_ollama_host()}/api/pull"
            data = json.dumps({"name": model}).encode("utf-8")
            req = urllib.request.Request(
                url,
                method="POST",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                for raw in resp:
                    line = raw.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except Exception:
                        continue
                    if payload.get("error"):
                        _set_pull_status(
                            model,
                            state="error",
                            error=payload.get("error"),
                        )
                        return
                    total = payload.get("total")
                    completed = payload.get("completed")
                    percent = None
                    if isinstance(total, (int, float)) and total:
                        percent = int((completed or 0) / total * 100)
                    _set_pull_status(
                        model,
                        state="pulling",
                        status=payload.get("status"),
                        total=total,
                        completed=completed,
                        percent=percent,
                    )
            _set_pull_status(model, state="done", percent=100, status="complete")
        except Exception as exc:
            _set_pull_status(model, state="error", error=str(exc))

    def _pull_via_cli(model: str) -> None:
        _set_pull_status(model, state="pulling", percent=None)
        percent_re = re.compile(r"(\\d{1,3})%")
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for stream in (process.stdout, process.stderr):
                if not stream:
                    continue
                for line in stream:
                    match = percent_re.search(line)
                    if match:
                        pct = min(max(int(match.group(1)), 0), 100)
                        _set_pull_status(model, percent=pct, status=line.strip())
            code = process.wait()
            if code == 0:
                _set_pull_status(model, state="done", percent=100, status="complete")
            else:
                _set_pull_status(
                    model,
                    state="error",
                    error=f"ollama pull exited {code}",
                )
        except Exception as exc:
            _set_pull_status(model, state="error", error=str(exc))

    def _start_pull(model: str) -> None:
        # Prefer API for progress if reachable
        try:
            _ollama_api_request("/api/tags")
            thread = threading.Thread(target=_pull_via_api, args=(model,), daemon=True)
        except Exception:
            if shutil.which("ollama"):
                thread = threading.Thread(target=_pull_via_cli, args=(model,), daemon=True)
            else:
                _set_pull_status(
                    model,
                    state="error",
                    error="ollama CLI not found and Ollama API unreachable",
                )
                return
        thread.start()

    @router.get("/models/available")
    async def get_available_ollama_models_public():
        """Public endpoint: Get list of popular Ollama models."""
        popular_models = [
            {
                "name": "mistral",
                "description": "Fast general purpose 7B model from Mistral AI",
                "size": "4.1GB",
                "category": "general",
                "installed": False,
            },
            {
                "name": "devstral-small-2",
                "description": "Mistral's lightweight coding assistant (10.7B)",
                "size": "8.7GB",
                "category": "coding",
                "installed": False,
            },
            {
                "name": "llama2",
                "description": "Meta's open foundation model (7B)",
                "size": "3.8GB",
                "category": "general",
                "installed": False,
            },
            {
                "name": "codellama",
                "description": "Code-specialized variant of Llama 2",
                "size": "3.8GB",
                "category": "coding",
                "installed": False,
            },
            {
                "name": "neural-chat",
                "description": "Intel Neural Chat optimized (13B)",
                "size": "7.4GB",
                "category": "chat",
                "installed": False,
            },
            {
                "name": "openchat",
                "description": "Lightweight conversation model (7B)",
                "size": "4.1GB",
                "category": "chat",
                "installed": False,
            },
            {
                "name": "zephyr",
                "description": "Fine-tuned Mistral for chat (7B)",
                "size": "4.1GB",
                "category": "general",
                "installed": False,
            },
            {
                "name": "orca-mini",
                "description": "Tiny but capable model (3B)",
                "size": "1.9GB",
                "category": "general",
                "installed": False,
            },
        ]

        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                installed_names = set()
                for line in result.stdout.strip().split("\n")[1:]:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            installed_names.add(parts[0])

                for model in popular_models:
                    if model["name"] in installed_names:
                        model["installed"] = True
        except Exception:
            pass

        return {
            "success": True,
            "models": popular_models,
            "categories": ["coding", "general", "chat", "advanced"],
        }

    @router.get("/models/installed")
    async def get_installed_ollama_models_public():
        """Public endpoint: Get list of currently installed Ollama models."""
        try:
            response = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            if response.returncode == 0:
                lines = response.stdout.strip().split("\n")
                if len(lines) < 2:
                    return {"success": True, "models": [], "count": 0}

                models = []
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            models.append(
                                {
                                    "name": parts[0],
                                    "id": parts[0],
                                    "size": parts[1] if len(parts) > 1 else "?",
                                    "modified": (
                                        " ".join(parts[2:]) if len(parts) > 2 else ""
                                    ),
                                }
                            )

                return {"success": True, "models": models, "count": len(models)}
            else:
                return {
                    "success": False,
                    "error": "Ollama not reachable. Is it running?",
                    "help": "Start Ollama: ollama serve",
                }
        except FileNotFoundError:
            try:
                data = _ollama_api_request("/api/tags")
                models = []
                for item in data.get("models", []):
                    name = item.get("name") or ""
                    models.append(
                        {
                            "name": name,
                            "id": name,
                            "size": item.get("size", "?"),
                            "modified": item.get("modified_at", ""),
                        }
                    )
                return {"success": True, "models": models, "count": len(models)}
            except Exception as exc:
                return {
                    "success": False,
                    "error": "ollama CLI not found",
                    "help": f"Install Ollama or set OLLAMA_HOST (current: {_ollama_host()})",
                    "detail": str(exc),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.post("/models/pull")
    async def pull_ollama_model_public(
        model: str = Query(..., description="Model name to pull")
    ):
        """Public endpoint: Pull (download) an Ollama model."""
        if not model or not isinstance(model, str):
            raise HTTPException(status_code=400, detail="model parameter required")

        if not all(c.isalnum() or c in "-_:." for c in model):
            raise HTTPException(status_code=400, detail="Invalid model name")

        try:
            _set_pull_status(model, state="queued", percent=0)
            _start_pull(model)
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
        with pull_lock:
            status = pull_status.get(model)
        if not status:
            return {"success": False, "error": "No pull status found", "model": model}
        return {"success": True, "status": status}

    @router.post("/models/remove")
    async def remove_ollama_model_public(
        model: str = Query(..., description="Model name to remove")
    ):
        """Public endpoint: Remove an installed Ollama model."""
        if not model or not isinstance(model, str):
            raise HTTPException(status_code=400, detail="model parameter required")

        if not all(c.isalnum() or c in "-_:." for c in model):
            raise HTTPException(status_code=400, detail="Invalid model name")

        try:
            result = subprocess.run(
                ["ollama", "rm", model], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                return {"success": True, "message": f"Removed {model}"}
            else:
                return {"success": False, "error": result.stderr}
        except FileNotFoundError:
            return {"success": False, "error": "ollama CLI not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    return router
