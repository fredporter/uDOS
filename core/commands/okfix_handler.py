"""Coding assist handler for the v1.5 logic-assist runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("command-okfix")


class OkfixHandler(BaseCommandHandler):
    """Handler for OKFIX command - coding assist via GPT4All or Wizard network.

    Commands:
      OKFIX                           — show status / help
      OKFIX STATUS                    — show active model and backend
      OKFIX RUN <prompt>              — run a coding prompt
      OKFIX FIX <file> [issue]        — ask LLM to fix a file
      OKFIX REVIEW <file>             — ask LLM to review a file
      OKFIX MODEL <model_name>        — switch local GPT4All model
      OKFIX MODELS                    — show current configured local model
    """

    DEFAULT_MODEL = "mistral-7b-instruct-v0.2.Q4_0.gguf"

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        action = params[0].lower()

        if action in {"help", "?"}:
            return self._help()
        if action == "status":
            return self._status()
        if action == "run":
            return self._run_prompt(" ".join(params[1:]))
        if action == "fix":
            return self._fix(params[1:])
        if action == "review":
            return self._review(params[1:])
        if action == "model":
            return self._set_model(params[1:])
        if action == "models":
            return self._list_models()

        # Bare prompt
        return self._run_prompt(" ".join(params))

    # ------------------------------------------------------------------
    def _backend(self) -> str:
        """Return the preferred available backend."""
        return "gpt4all"

    def _model(self) -> str:
        return self._state.get("model", self.DEFAULT_MODEL)

    def _status(self) -> Dict:
        backend = self._backend()
        model = self._model()
        return {
            "status": "success",
            "backend": backend,
            "model": model,
            "gpt4all_preferred": True,
            "network_available": True,
            "message": f"OKFIX backend: {backend}, model: {model}" if backend != "none"
                       else "No local coding assist backend found.",
        }

    def _set_model(self, params: List[str]) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: OKFIX MODEL <model_name>"}
        self._state["model"] = params[0]
        return {"status": "success", "message": f"Model set to '{params[0]}'."}

    def _list_models(self) -> Dict:
        return {
            "status": "success",
            "output": self._model(),
            "models": [self._model()],
        }

    def _run_prompt(self, prompt: str) -> Dict:
        if not prompt:
            return {"status": "error", "message": "Usage: OKFIX RUN <prompt>"}
        model = self._model()
        logger.info(f"[OKFIX] prompt via gpt4all: {prompt[:80]}")
        try:
            from wizard.services.local_model_gpt4all import GPT4AllLocalAssist
            from wizard.services.logic_assist_profile import load_logic_assist_profile

            profile = load_logic_assist_profile()
            payload = profile.to_dict()
            payload["local_model_name"] = model
            profile = profile.__class__(**payload)
            result = GPT4AllLocalAssist(profile, Path(__file__).resolve().parents[2]).generate(prompt)
            return {"status": "success", "backend": "gpt4all", "model": model, "response": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _read_file(self, path_str: str) -> tuple[Path | None, str]:
        p = Path(path_str)
        if not p.is_absolute():
            p = get_repo_root() / p
        if not p.exists():
            return None, f"File not found: {p}"
        try:
            return p, p.read_text(errors="replace")[:4000]
        except Exception as e:
            return None, str(e)

    def _fix(self, params: List[str]) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: OKFIX FIX <file> [issue description]"}
        file_path, content_or_err = self._read_file(params[0])
        if file_path is None:
            return {"status": "error", "message": content_or_err}
        issue = " ".join(params[1:]) or "Fix any bugs or issues in this code."
        prompt = f"You are a coding assistant. Fix the following issue in this file.\n\nIssue: {issue}\n\nFile: {params[0]}\n\n```\n{content_or_err}\n```\n\nReturn only the corrected file content."
        return self._run_prompt(prompt)

    def _review(self, params: List[str]) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: OKFIX REVIEW <file>"}
        file_path, content_or_err = self._read_file(params[0])
        if file_path is None:
            return {"status": "error", "message": content_or_err}
        prompt = f"Review the following code for bugs, style issues, and improvements.\n\nFile: {params[0]}\n\n```\n{content_or_err}\n```\n\nProvide a concise review with specific suggestions."
        return self._run_prompt(prompt)

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": (
                "OKFIX - v1.5 coding assist (GPT4All / Wizard network)\n"
                "  OKFIX RUN <prompt>          Send a coding prompt\n"
                "  OKFIX FIX <file> [issue]    Ask LLM to fix a file\n"
                "  OKFIX REVIEW <file>         Ask LLM to review a file\n"
                "  OKFIX STATUS                Show backend and model\n"
                "  OKFIX MODEL <name>          Switch GPT4All model\n"
                "  OKFIX MODELS                Show configured GPT4All model\n"
            ),
        }
