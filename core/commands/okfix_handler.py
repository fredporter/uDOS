"""OKFIX command handler - Local LLM coding assistant (Ollama / Mistral-Vibe)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("command-okfix")


class OkfixHandler(BaseCommandHandler):
    """Handler for OKFIX command - AI-assisted code fix / vibe-coding via local LLM.

    Delegates to Ollama (offline) or Mistral CLI depending on availability.

    Commands:
      OKFIX                           — show status / help
      OKFIX STATUS                    — show active model and backend
      OKFIX RUN <prompt>              — run a coding prompt
      OKFIX FIX <file> [issue]        — ask LLM to fix a file
      OKFIX REVIEW <file>             — ask LLM to review a file
      OKFIX MODEL <model_name>        — switch Ollama model
      OKFIX MODELS                    — list available Ollama models
    """

    DEFAULT_MODEL = "mistral"

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
        if shutil.which("ollama"):
            return "ollama"
        if shutil.which("mistral"):
            return "mistral"
        return "none"

    def _model(self) -> str:
        return self._state.get("model", self.DEFAULT_MODEL)

    def _status(self) -> Dict:
        backend = self._backend()
        model = self._model()
        return {
            "status": "success",
            "backend": backend,
            "model": model,
            "ollama_available": shutil.which("ollama") is not None,
            "mistral_available": shutil.which("mistral") is not None,
            "message": f"OKFIX backend: {backend}, model: {model}" if backend != "none"
                       else "No local LLM backend found. Install Ollama (https://ollama.ai) or Mistral CLI.",
        }

    def _set_model(self, params: List[str]) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: OKFIX MODEL <model_name>"}
        self._state["model"] = params[0]
        return {"status": "success", "message": f"Model set to '{params[0]}'."}

    def _list_models(self) -> Dict:
        if not shutil.which("ollama"):
            return {"status": "error", "message": "Ollama not found. Install from https://ollama.ai"}
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            return {"status": "success", "output": result.stdout.strip()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _ollama_prompt(self, prompt: str) -> Dict:
        model = self._model()
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                return {"status": "error", "message": result.stderr.strip()[:300]}
            return {"status": "success", "backend": "ollama", "model": model, "response": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Ollama request timed out (120s)."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _run_prompt(self, prompt: str) -> Dict:
        if not prompt:
            return {"status": "error", "message": "Usage: OKFIX RUN <prompt>"}
        backend = self._backend()
        if backend == "none":
            return {"status": "error", "message": "No local LLM available. Install Ollama or Mistral CLI."}
        logger.info(f"[OKFIX] prompt via {backend}: {prompt[:80]}")
        return self._ollama_prompt(prompt)

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
                "OKFIX - Local LLM coding assistant (Ollama / Mistral)\n"
                "  OKFIX RUN <prompt>          Send a coding prompt\n"
                "  OKFIX FIX <file> [issue]    Ask LLM to fix a file\n"
                "  OKFIX REVIEW <file>         Ask LLM to review a file\n"
                "  OKFIX STATUS                Show backend and model\n"
                "  OKFIX MODEL <name>          Switch Ollama model\n"
                "  OKFIX MODELS                List available Ollama models\n"
            ),
        }
