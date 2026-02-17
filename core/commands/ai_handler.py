"""AI command handler - Gemini CLI and local AI assistant integration."""

from __future__ import annotations

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger

logger = get_logger("command-ai")


class AIHandler(BaseCommandHandler):
    """Handler for AI command - delegates to Gemini CLI or local LLM.

    Commands:
      AI                        — show status / help
      AI ASK <prompt>           — send a prompt to the configured AI
      AI STATUS                 — show which AI backend is active
      AI SWITCH gemini|ollama   — switch active backend
      AI HISTORY                — show recent conversation turns
      AI CLEAR                  — clear conversation history
    """

    BACKENDS = ("gemini", "ollama", "mistral")

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        action = params[0].lower()

        if action in {"help", "?"}:
            return self._help()

        if action == "status":
            return self._status()

        if action == "switch":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: AI SWITCH <gemini|ollama|mistral>"}
            return self._switch(params[1].lower())

        if action == "ask":
            prompt = " ".join(params[1:])
            if not prompt:
                return {"status": "error", "message": "Usage: AI ASK <prompt>"}
            return self._ask(prompt)

        if action == "history":
            return self._history()

        if action == "clear":
            self._state.pop("history", None)
            return {"status": "success", "message": "AI conversation history cleared."}

        # Treat unrecognised first token as a bare prompt
        prompt = " ".join(params)
        return self._ask(prompt)

    # ------------------------------------------------------------------
    def _status(self) -> Dict:
        backend = self._state.get("backend", "gemini")
        gemini_ok = shutil.which("gemini") is not None
        ollama_ok = shutil.which("ollama") is not None
        return {
            "status": "success",
            "backend": backend,
            "gemini_available": gemini_ok,
            "ollama_available": ollama_ok,
            "message": f"Active backend: {backend}",
        }

    def _switch(self, backend: str) -> Dict:
        if backend not in self.BACKENDS:
            return {"status": "error", "message": f"Unknown backend '{backend}'. Choose: {', '.join(self.BACKENDS)}"}
        self._state["backend"] = backend
        return {"status": "success", "message": f"AI backend switched to '{backend}'."}

    def _ask(self, prompt: str) -> Dict:
        backend = self._state.get("backend", "gemini")
        logger.info(f"[AI] ask via {backend}: {prompt[:80]}")

        cli = shutil.which(backend)
        if not cli:
            return {
                "status": "error",
                "message": f"'{backend}' CLI not found in PATH. Install it or switch backends with AI SWITCH.",
                "suggestion": f"Try: AI SWITCH ollama  (if Ollama is running locally)",
            }

        try:
            result = subprocess.run(
                [cli, prompt],
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = (result.stdout or result.stderr or "").strip()
            history = self._state.setdefault("history", [])
            history.append({"prompt": prompt, "response": output[:500]})
            if len(history) > 20:
                history[:] = history[-20:]
            return {"status": "success", "backend": backend, "response": output}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": f"AI request timed out after 60s."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _history(self) -> Dict:
        history = self._state.get("history", [])
        if not history:
            return {"status": "success", "message": "No AI conversation history yet."}
        lines = [f"[{i+1}] Q: {h['prompt'][:60]}\n    A: {h['response'][:80]}" for i, h in enumerate(history)]
        return {"status": "success", "history": history, "output": "\n".join(lines)}

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": (
                "AI - AI assistant integration\n"
                "  AI ASK <prompt>           Send a prompt to the active AI\n"
                "  AI STATUS                 Show active backend and availability\n"
                "  AI SWITCH gemini|ollama   Switch AI backend\n"
                "  AI HISTORY                Show recent conversation turns\n"
                "  AI CLEAR                  Clear conversation history\n"
            ),
        }
