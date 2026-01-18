"""
Global Config Framework
=======================

Unified config management service for all Wizard modules.
Supports:
  - API registry with status indicators
  - Micro editor integration for .env and config files
  - Dropdown file selection for editing
  - Extensible for any module config

Architecture:
  ConfigFramework (service)
    ├── ConfigRegistry (list available APIs/modules)
    ├── ConfigEditor (Micro editor routes)
    └── ConfigValidator (validate config formats)
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ConfigStatus(str, Enum):
    """Configuration status indicators."""
    CONNECTED = "CONNECTED"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    ERROR = "ERROR"


@dataclass
class APIRegistry:
    """Registry entry for an API/service."""
    name: str
    category: str
    env_key: str  # Which env var to check
    required: bool = True
    docs_url: Optional[str] = None
    status: ConfigStatus = ConfigStatus.MISSING
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "env_key": self.env_key,
            "required": self.required,
            "docs_url": self.docs_url,
            "status": self.status.value,
            "description": self.description,
        }


class ConfigFramework:
    """Global configuration framework for all Wizard modules."""

    def __init__(self):
        """Initialize config framework."""
        self.config_dir = Path.home() / ".uDOS" / "config"
        self.env_file = self.config_dir / ".env"
        self.env_local_file = self.config_dir / ".env-local"
        self.registry = self._build_registry()
        self._update_statuses()

    def _build_registry(self) -> List[APIRegistry]:
        """Build registry of available APIs."""
        return [
            # AI Providers
            APIRegistry(
                name="OpenAI",
                category="AI Providers",
                env_key="OPENAI_API_KEY",
                docs_url="https://platform.openai.com/api-keys",
                description="GPT models API access"
            ),
            APIRegistry(
                name="Anthropic (Claude)",
                category="AI Providers",
                env_key="ANTHROPIC_API_KEY",
                docs_url="https://console.anthropic.com/",
                description="Claude API access"
            ),
            APIRegistry(
                name="Google (Gemini)",
                category="AI Providers",
                env_key="GOOGLE_API_KEY",
                docs_url="https://ai.google.dev/",
                description="Gemini API access"
            ),
            APIRegistry(
                name="Mistral AI",
                category="AI Providers",
                env_key="MISTRAL_API_KEY",
                docs_url="https://console.mistral.ai/",
                description="Mistral API access"
            ),

            # Code/Dev Services
            APIRegistry(
                name="GitHub",
                category="Developer Services",
                env_key="GITHUB_TOKEN",
                docs_url="https://github.com/settings/tokens",
                description="GitHub API token"
            ),
            APIRegistry(
                name="GitLab",
                category="Developer Services",
                env_key="GITLAB_TOKEN",
                docs_url="https://gitlab.com/-/profile/personal_access_tokens",
                required=False,
                description="GitLab API token"
            ),

            # Cloud Services
            APIRegistry(
                name="AWS",
                category="Cloud Services",
                env_key="AWS_ACCESS_KEY_ID",
                docs_url="https://console.aws.amazon.com/",
                required=False,
                description="AWS credentials"
            ),
            APIRegistry(
                name="Google Cloud",
                category="Cloud Services",
                env_key="GOOGLE_CLOUD_PROJECT",
                docs_url="https://console.cloud.google.com/",
                required=False,
                description="GCP project config"
            ),

            # Integrations
            APIRegistry(
                name="Notion",
                category="Integrations",
                env_key="NOTION_API_KEY",
                docs_url="https://www.notion.so/my-integrations",
                required=False,
                description="Notion workspace integration"
            ),
            APIRegistry(
                name="Slack",
                category="Integrations",
                env_key="SLACK_BOT_TOKEN",
                docs_url="https://api.slack.com/",
                required=False,
                description="Slack bot token"
            ),
            APIRegistry(
                name="Gmail",
                category="Integrations",
                env_key="GMAIL_APP_PASSWORD",
                docs_url="https://myaccount.google.com/apppasswords",
                required=False,
                description="Gmail app password"
            ),
        ]

    def _update_statuses(self) -> None:
        """Update status of all API entries."""
        env_vars = self._load_env()

        for entry in self.registry:
            if entry.env_key in env_vars:
                value = env_vars[entry.env_key]
                if value and value.strip():
                    entry.status = ConfigStatus.CONNECTED
                else:
                    entry.status = ConfigStatus.PARTIAL
            else:
                entry.status = ConfigStatus.MISSING if entry.required else ConfigStatus.MISSING

    def _load_env(self) -> Dict[str, str]:
        """Load .env and .env-local files into dict.

        Priority: .env < .env-local (local overrides global)
        """
        env = {}

        # Load .env first (global secrets)
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env[key.strip()] = value.strip()

        # Load .env-local (local overrides)
        if self.env_local_file.exists():
            with open(self.env_local_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env[key.strip()] = value.strip()

        return env

    def get_registry_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registry organized by category."""
        result = {}
        for entry in self.registry:
            if entry.category not in result:
                result[entry.category] = []
            result[entry.category].append(entry.to_dict())
        return result

    def read_env_file(self) -> str:
        """Read .env file content."""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                return f.read()
        return "# No .env file yet\n"

    def write_env_file(self, content: str) -> bool:
        """Write to .env file."""
        try:
            self.env_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.env_file, 'w') as f:
                f.write(content)
            # Reload statuses after write
            self._update_statuses()
            return True
        except Exception as e:
            print(f"Error writing .env file: {e}")
            return False

    def get_config_files(self) -> Dict[str, str]:
        """Get list of available config files for editing.

        Returns:
            Dict of {filename: filepath} for editable configs
        """
        files = {}

        # .env file (global secrets)
        if self.env_file.exists():
            files[".env (secrets)"] = str(self.env_file)
        else:
            files[".env (empty)"] = str(self.env_file)

        # .env-local (local overrides, optional)
        if self.env_local_file.exists():
            files[".env-local (overrides)"] = str(self.env_local_file)

        # wizard.json (committed configuration)
        wizard_config = Path(__file__).parent.parent / "config" / "wizard.json"
        if wizard_config.exists():
            files["wizard.json (config)"] = str(wizard_config)

        return files

    def read_config_file(self, filename: str) -> Optional[str]:
        """Read a config file safely."""
        allowed_files = self.get_config_files()
        if filename not in allowed_files:
            return None

        filepath = Path(allowed_files[filename])
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return f.read()
            except Exception:
                return None
        return None

    def write_config_file(self, filename: str, content: str) -> bool:
        """Write a config file safely."""
        allowed_files = self.get_config_files()
        if filename not in allowed_files:
            return False

        filepath = Path(allowed_files[filename])
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        except Exception:
            return False


# Global instance
_config_framework: Optional[ConfigFramework] = None


def get_config_framework() -> ConfigFramework:
    """Get or create global config framework instance."""
    global _config_framework
    if _config_framework is None:
        _config_framework = ConfigFramework()
    return _config_framework
