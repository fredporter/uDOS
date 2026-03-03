"""Local GPT4All advisory runtime for v1.5 logic assist."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wizard.services.logic_assist_profile import LogicAssistProfile
from wizard.services.logging_api import get_logger

logger = get_logger("wizard.logic-local")


@dataclass(frozen=True)
class GPT4AllStatus:
    ready: bool
    issue: str | None
    model: str
    model_path: str
    context_window: int
    runtime: str = "gpt4all"
    package_available: bool = False
    model_present: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "issue": self.issue,
            "model": self.model,
            "model_path": self.model_path,
            "context_window": self.context_window,
            "runtime": self.runtime,
            "package_available": self.package_available,
            "model_present": self.model_present,
        }


class GPT4AllLocalAssist:
    def __init__(self, profile: LogicAssistProfile, repo_root: Path):
        self.profile = profile
        self.repo_root = repo_root

    def _model_dir(self) -> Path:
        configured = Path(self.profile.local_model_path)
        if configured.is_absolute():
            return configured
        return self.repo_root / configured

    def _model_file(self) -> Path:
        return self._model_dir() / self.profile.local_model_name

    def status(self) -> GPT4AllStatus:
        package_available = self._package_available()
        model_file = self._model_file()
        model_present = model_file.exists()
        issue = None
        ready = package_available and model_present
        if not package_available:
            issue = "gpt4all package unavailable"
        elif not model_present:
            issue = "gpt4all model missing"
        return GPT4AllStatus(
            ready=ready,
            issue=issue,
            model=self.profile.local_model_name,
            model_path=str(model_file),
            context_window=self.profile.local_context_window,
            package_available=package_available,
            model_present=model_present,
        )

    def generate(self, prompt: str, system: str = "") -> str:
        try:
            from gpt4all import GPT4All  # type: ignore
        except Exception as exc:
            raise RuntimeError("gpt4all package unavailable") from exc

        model_dir = self._model_dir()
        model_file = self._model_file()
        if not model_file.exists():
            raise RuntimeError(f"gpt4all model missing: {model_file}")

        prompt_text = prompt if not system else f"{system}\n\nUser request:\n{prompt}"
        model = GPT4All(
            model_name=self.profile.local_model_name,
            model_path=str(model_dir),
            allow_download=False,
        )
        with model.chat_session(system_prompt=system or ""):
            return str(
                model.generate(
                    prompt_text,
                    max_tokens=min(self.profile.local_context_window, 2048),
                    temp=0.2,
                )
            ).strip()

    @staticmethod
    def _package_available() -> bool:
        try:
            import gpt4all  # type: ignore  # noqa: F401

            return True
        except Exception:
            return False
