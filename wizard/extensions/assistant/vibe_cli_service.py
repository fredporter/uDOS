"""
Dev Mode Tool CLI Service - contributor coding tool integration
==============================================================

Provides integration between uDOS and the external Dev Mode contributor tool.
This service is gated behind the v1.5 Dev Mode profile.

Features:
  - Code analysis and fixing (OK FIX)
  - Natural language code queries (OK ASK)
  - Project-aware context
  - Custom uDOS prompts

Security:
  - Runs on Wizard Server only (Realm B)
  - API key stored in KeyStore
  - Results returned via private transport to devices

Usage in TUI:
  OK FIX <file>       - Analyze and fix code
  OK FIX --context    - Include logs in analysis
  OK ASK <question>   - Ask coding questions
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from wizard.services.logging_api import get_logger
from wizard.services.dev_extension_service import get_dev_extension_service
from wizard.security.key_store import get_wizard_key

logger = get_logger("dev-mode-tool-service")


@dataclass
class DevModeToolCliConfig:
    """External Dev Mode contributor tool CLI configuration."""

    home_dir: Path = Path.home() / ".vibe"
    config_file: str = "config.toml"
    model: str = "devstral-small"
    agent: str = "udos"
    auto_approve: bool = False

    @property
    def config_path(self) -> Path:
        return self.home_dir / self.config_file

    @property
    def env_path(self) -> Path:
        return self.home_dir / ".env"


@dataclass
class DevModeToolCliResponse:
    """Response from the external Dev Mode contributor tool CLI."""

    success: bool
    output: str
    error: Optional[str] = None
    model: str = ""
    tokens_used: int = 0


class DevModeToolCliService:
    """
    Service for interacting with the external Dev Mode contributor tool.

    Provides a Python interface to the `vibe` command-line tool
    for code analysis, fixing, and natural language queries.
    """

    def __init__(self, config_manager=None):
        """
        Initialize the external Dev Mode contributor tool service.

        Args:
            config_manager: uDOS Config instance for settings
        """
        self.config = DevModeToolCliConfig()
        self._config_manager = config_manager
        self._api_key: Optional[str] = None
        self._vibe_path: Optional[str] = None

        # Check availability
        self._check_installation()
        self._load_api_key()

    def _check_installation(self):
        """Check if the external Dev Mode contributor tool is installed."""
        self._vibe_path = shutil.which("vibe")
        if self._vibe_path:
            logger.info(f"[WIZ] Dev Mode tool CLI found at: {self._vibe_path}")
        else:
            logger.warning("[WIZ] Dev Mode tool CLI not installed in the active Dev Mode lane")

    def _load_api_key(self):
        """Load the contributor tool provider key from KeyStore or environment."""
        # Try KeyStore first (secure)
        self._api_key = get_wizard_key("MISTRAL_API_KEY")

        if self._api_key:
            logger.debug("[WIZ] Loaded Mistral API key from KeyStore")
            return

        # Try environment variable
        self._api_key = os.environ.get("MISTRAL_API_KEY")

        if self._api_key:
            logger.debug("[WIZ] Loaded Mistral API key from environment")
            return

        # Try ~/.vibe/.env
        if self.config.env_path.exists():
            try:
                env_content = self.config.env_path.read_text()
                for line in env_content.splitlines():
                    if line.startswith("MISTRAL_API_KEY="):
                        self._api_key = line.split("=", 1)[1].strip()
                        logger.debug("[WIZ] Loaded Mistral API key from ~/.vibe/.env")
                        return
            except Exception as e:
                logger.error(f"[WIZ] Failed to read ~/.vibe/.env: {e}")

    @property
    def is_available(self) -> bool:
        """Check if the external Dev Mode contributor tool is available and configured."""
        return bool(self._vibe_path and self._api_key and self._dev_mode_error() is None)

    @property
    def status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "installed": bool(self._vibe_path),
            "path": self._vibe_path,
            "api_key_configured": bool(self._api_key),
            "home_dir": str(self.config.home_dir),
            "model": self.config.model,
            "agent": self.config.agent,
            "dev_mode_error": self._dev_mode_error(),
        }

    def _dev_mode_error(self) -> Optional[str]:
        """Return access error when the external Dev Mode contributor tool is unavailable."""
        return get_dev_extension_service().ensure_vibe_tool_access()

    def analyze_code(
        self,
        file_path: str,
        context: Optional[str] = None,
        include_logs: bool = False,
        auto_approve: bool = False,
    ) -> DevModeToolCliResponse:
        """
        Analyze a code file using the external Dev Mode contributor tool.

        Args:
            file_path: Path to file to analyze
            context: Additional context (error messages, logs)
            include_logs: Include recent session logs
            auto_approve: Auto-approve tool executions

        Returns:
            DevModeToolCliResponse with analysis results
        """
        if not self.is_available:
            return DevModeToolCliResponse(
                success=False,
                output="",
                error=self._dev_mode_error() or "Dev Mode contributor tool not available in the active Dev Mode lane",
            )

        # Build prompt
        prompt_parts = [f"Analyze and suggest fixes for the code in @{file_path}"]

        if context:
            prompt_parts.append(f"\n\nContext/Error:\n{context}")

        if include_logs:
            logs = self._get_recent_logs()
            if logs:
                prompt_parts.append(f"\n\nRecent logs:\n{logs}")

        prompt = "".join(prompt_parts)

        return self._run_vibe(prompt, auto_approve=auto_approve)

    def ask(
        self,
        question: str,
        file_context: Optional[str] = None,
        auto_approve: bool = False,
    ) -> DevModeToolCliResponse:
        """
        Ask a coding question using the external Dev Mode contributor tool.

        Args:
            question: Natural language question
            file_context: Optional file to reference
            auto_approve: Auto-approve tool executions

        Returns:
            DevModeToolCliResponse with answer
        """
        if not self.is_available:
            return DevModeToolCliResponse(
                success=False,
                output="",
                error=self._dev_mode_error() or "Dev Mode contributor tool not available in the active Dev Mode lane",
            )

        prompt = question
        if file_context:
            prompt = f"Looking at @{file_context}: {question}"

        return self._run_vibe(prompt, auto_approve=auto_approve)

    def fix_code(
        self,
        file_path: str,
        error_message: Optional[str] = None,
        auto_approve: bool = False,
    ) -> DevModeToolCliResponse:
        """
        Request a code fix using the external Dev Mode contributor tool.

        Args:
            file_path: Path to file to fix
            error_message: Error message to address
            auto_approve: Auto-approve tool executions

        Returns:
            DevModeToolCliResponse with fix suggestions
        """
        if not self.is_available:
            return DevModeToolCliResponse(
                success=False,
                output="",
                error=self._dev_mode_error() or "Dev Mode contributor tool not available in the active Dev Mode lane",
            )

        prompt = f"Fix the code in @{file_path}"

        if error_message:
            prompt += f"\n\nError to fix:\n{error_message}"

        return self._run_vibe(prompt, auto_approve=auto_approve)

    def _run_vibe(self, prompt: str, auto_approve: bool = False) -> DevModeToolCliResponse:
        """
        Run the external Dev Mode contributor tool with a given prompt.

        Args:
            prompt: The prompt to send
            auto_approve: Auto-approve tool executions

        Returns:
            DevModeToolCliResponse with results
        """
        try:
            # Build command
            cmd = [self._vibe_path]

            # Use uDOS agent if available
            udos_agent = self.config.home_dir / "agents" / "udos.toml"
            if udos_agent.exists():
                cmd.extend(["--agent", "udos"])

            # Auto-approve mode (non-interactive)
            if auto_approve:
                cmd.append("--auto-approve")

            # Add prompt
            cmd.extend(["--prompt", prompt])

            # Set environment
            env = os.environ.copy()
            env["MISTRAL_API_KEY"] = self._api_key

            logger.info(f"[WIZ] Running Vibe: {' '.join(cmd[:3])}...")

            # Run vibe
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,  # 5 minute timeout
                cwd=str(Path.cwd()),
            )

            if result.returncode == 0:
                return DevModeToolCliResponse(
                    success=True, output=result.stdout, model=self.config.model
                )
            else:
                return DevModeToolCliResponse(
                    success=False,
                    output=result.stdout,
                    error=result.stderr or "Dev Mode contributor tool command failed",
                )

        except subprocess.TimeoutExpired:
            return DevModeToolCliResponse(
                success=False, output="", error="Dev Mode contributor tool timed out after 5 minutes"
            )
        except Exception as e:
            logger.error(f"[WIZ] Dev Mode contributor tool error: {e}")
            return DevModeToolCliResponse(success=False, output="", error=str(e))


    def _get_recent_logs(self, lines: int = 50) -> str:
        """Get recent session logs for context."""
        from datetime import datetime

        log_dir = Path("memory/logs")
        if not log_dir.exists():
            return ""

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"session-commands-{today}.log"

        if not log_file.exists():
            return ""

        try:
            all_lines = log_file.read_text().splitlines()
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return "\n".join(recent)
        except Exception:
            return ""

    def ensure_udos_config(self):
        """Ensure uDOS-specific external contributor tool configuration exists."""
        prompts_dir = self.config.home_dir / "prompts"
        agents_dir = self.config.home_dir / "agents"

        prompts_dir.mkdir(parents=True, exist_ok=True)
        agents_dir.mkdir(parents=True, exist_ok=True)

        # Create uDOS prompt if missing
        udos_prompt = prompts_dir / "udos.md"
        if not udos_prompt.exists():
            udos_prompt.write_text(UDOS_PROMPT)
            logger.info("[WIZ] Created ~/.vibe/prompts/udos.md")

        # Create uDOS agent if missing
        udos_agent = agents_dir / "udos.toml"
        if not udos_agent.exists():
            udos_agent.write_text(UDOS_AGENT)
            logger.info("[WIZ] Created ~/.vibe/agents/udos.toml")


VibeConfig = DevModeToolCliConfig
VibeResponse = DevModeToolCliResponse
VibeCliService = DevModeToolCliService


# uDOS system prompt for Vibe
UDOS_PROMPT = """# uDOS Development Assistant

You are an OK coding assistant integrated with uDOS, an offline-first knowledge system.

## Context
- uDOS uses a shared `uv` + `/.venv` Python runtime targeting Alpine Linux
- Two-Realm Architecture: Device Mesh (offline) vs Wizard Server (online)
- Transport Policy: MeshCore, Bluetooth Private, NFC, QR, Audio (private only)
- Bluetooth Public = SIGNAL ONLY, never data

## Code Standards
- Always use version.json for versions (never hardcode)
- Route commands through uDOS_commands.py
- Use logging tags: [LOCAL] [MESH] [WIZ] [BT-PRIV] etc.
- Alpine Linux compatible (no systemd assumptions; OpenRC)

## Key Paths
- core/ - Python TUI system
- extensions/ - API, transport, cloud
- knowledge/ - Markdown knowledge bank
- memory/ - User workspace (gitignored)

## When Fixing Code
1. Check session-commands log first for errors
2. Verify imports and method signatures
3. Consider offline/online separation
4. Test with OK FIX shakedown
"""

# uDOS agent config for Vibe
UDOS_AGENT = """# uDOS Development Agent
# Usage: vibe --agent udos

active_model = "devstral-small"
system_prompt_id = "udos"

# Enable all dev tools
[tools.bash]
permission = "ask"

[tools.write_file]
permission = "ask"

[tools.search_replace]
permission = "ask"
"""
