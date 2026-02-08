"""Shared integration registry definitions for Core/Wizard."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


PUBLIC_PROVIDER_DEFINITIONS: Dict[str, Dict[str, Any]] = {
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
        "install_cmd": "brew install gh",
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
}


OAUTH_PROVIDER_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "api_base_url": "https://www.googleapis.com",
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "default_scopes": [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        "extra_params": {"access_type": "offline", "prompt": "consent"},
    },
    "github": {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "api_base_url": "https://api.github.com",
        "user_info_url": "https://api.github.com/user",
        "default_scopes": ["read:user", "user:email"],
    },
    "spotify": {
        "auth_url": "https://accounts.spotify.com/authorize",
        "token_url": "https://accounts.spotify.com/api/token",
        "api_base_url": "https://api.spotify.com/v1",
        "user_info_url": "https://api.spotify.com/v1/me",
        "default_scopes": ["user-read-private", "user-read-email"],
    },
    "discord": {
        "auth_url": "https://discord.com/api/oauth2/authorize",
        "token_url": "https://discord.com/api/oauth2/token",
        "api_base_url": "https://discord.com/api/v10",
        "user_info_url": "https://discord.com/api/v10/users/@me",
        "default_scopes": ["identify", "email"],
    },
}


WIZARD_SECRET_SYNC_MAP: Dict[str, Dict[str, Any]] = {
    "github_token": {"providers": ["github"], "toggles": ["github_push_enabled"]},
    "github_webhook_secret": {"providers": ["github"], "toggles": ["github_push_enabled"]},
    "mistral_api_key": {"providers": ["mistral"], "toggles": ["ok_gateway_enabled"]},
    "openrouter_api_key": {"providers": ["openrouter"], "toggles": ["ok_gateway_enabled"]},
    "ollama_api_key": {"providers": ["ollama"], "toggles": ["ok_gateway_enabled"]},
}


ASSISTANT_CONFIG_KEY_MAP: Dict[str, str] = {
    "OPENAI_API_KEY": "openai",
    "ANTHROPIC_API_KEY": "anthropic",
    "MISTRAL_API_KEY": "mistral",
    "OPENROUTER_API_KEY": "openrouter",
    "GEMINI_API_KEY": "gemini",
    "OLLAMA_HOST": "ollama",
}


WIZARD_REQUIRED_VARIABLES: Dict[str, Dict[str, Any]] = {
    "github_token": {
        "name": "GitHub API Token",
        "description": "Personal access token for GitHub API access",
        "env_var": "GITHUB_TOKEN",
        "required": False,
        "documentation": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token",
    },
    "mistral_api_key": {
        "name": "Mistral API Key (Optional)",
        "description": "API key for cloud AI features via Mistral",
        "env_var": "MISTRAL_API_KEY",
        "required": False,
        "documentation": "https://docs.mistral.ai/",
    },
}


def get_provider_definitions() -> Dict[str, Dict[str, Any]]:
    return deepcopy(PUBLIC_PROVIDER_DEFINITIONS)


def get_oauth_provider_definitions() -> Dict[str, Dict[str, Any]]:
    return deepcopy(OAUTH_PROVIDER_DEFINITIONS)


def get_wizard_secret_sync_map() -> Dict[str, Dict[str, Any]]:
    return deepcopy(WIZARD_SECRET_SYNC_MAP)


def get_assistant_config_key_map() -> Dict[str, str]:
    return deepcopy(ASSISTANT_CONFIG_KEY_MAP)


def get_wizard_required_variables() -> Dict[str, Dict[str, Any]]:
    return deepcopy(WIZARD_REQUIRED_VARIABLES)
