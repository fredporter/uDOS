"""Vibe contributor helper on the v1.5 logic-assist contract."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from wizard.services.ai_context_store import write_context_bundle
from wizard.services.local_model_gpt4all import GPT4AllLocalAssist
from wizard.services.logging_api import get_logger
from wizard.services.logic_assist_profile import load_logic_assist_profile
from wizard.services.path_utils import get_repo_root

logger = get_logger("vibe-service")


@dataclass
class VibeConfig:
    """Configuration for the contributor helper."""

    model: str | None = None
    temperature: float = 0.2
    context_window: int | None = None


class VibeService:
    """Run contributor prompts through the local GPT4All advisory lane."""

    def __init__(self, config: Optional[VibeConfig] = None):
        self.repo_root = get_repo_root()
        self.profile = load_logic_assist_profile(self.repo_root)
        self.config = config or VibeConfig()
        self.local = GPT4AllLocalAssist(self.profile, self.repo_root)
        self.conversation_history: List[Dict[str, str]] = []

    def _verify_connection(self) -> bool:
        status = self.local.status()
        if status.ready:
            logger.info(
                "[LOCAL] Vibe: Logic assist ready (%s)",
                status.model,
            )
            return True
        logger.warning(
            "[LOCAL] Vibe: Logic assist unavailable (%s)",
            status.issue or "unknown issue",
        )
        return False

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        format: str = "text",
        stream: bool = False,
        **_kwargs: Any,
    ) -> str | Generator[str, None, None]:
        del format  # Output shaping remains caller-owned in v1.5.

        response_text = self.local.generate(prompt=prompt, system=system or "")
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response_text})
        logger.info("[LOCAL] Vibe: Generated %s chars", len(response_text))

        if stream:
            return self._stream_response(response_text)
        return response_text

    def _stream_response(self, response_text: str) -> Generator[str, None, None]:
        for chunk in response_text.splitlines(keepends=True):
            yield chunk

    def load_context(self, context_files: List[Path]) -> str:
        context = []
        for file_path in context_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                context.append(f"# {file_path.name}\n\n{content}")
                logger.info("[LOCAL] Loaded context: %s", file_path)
            except Exception as exc:
                logger.warning("[LOCAL] Failed to load context %s: %s", file_path, exc)
        return "\n\n---\n\n".join(context)

    def load_default_context(self) -> str:
        context_path = write_context_bundle()
        try:
            data = json.loads(context_path.read_text(encoding="utf-8"))
        except Exception:
            return ""
        context = []
        for name, content in data.items():
            context.append(f"=== {name} ===\n{content}")
        return "\n\n".join(context)

    def clear_history(self) -> None:
        self.conversation_history = []
        logger.info("[LOCAL] Vibe: Conversation history cleared")

    def get_status(self) -> Dict[str, Any]:
        status = self.local.status()
        model = self.config.model or self.profile.local_model_name
        return {
            "runtime": "logic-assist-v1.5",
            "model": model,
            "connected": status.ready,
            "issue": status.issue,
            "model_path": status.model_path,
            "conversation_turns": len(self.conversation_history),
            "temperature": self.config.temperature,
            "context_window": self.config.context_window or self.profile.local_context_window,
        }
