"""Logic-assist command handler for the v1.5 runtime."""

from __future__ import annotations

from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger

logger = get_logger("command-ai")


class AIHandler(BaseCommandHandler):
    """Handler for logic-assist command flow.

    Commands:
      AI                        — show status / help
      AI ASK <prompt>           — send a prompt to the configured logic-assist lane
      AI STATUS                 — show which local/network path is active
      AI SWITCH gpt4all|mistral — switch preferred path
      AI HISTORY                — show recent conversation turns
      AI CLEAR                  — clear conversation history
    """

    BACKENDS = ("gpt4all", "mistral")

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
        backend = self._state.get("backend", "gpt4all")
        return {
            "status": "success",
            "backend": backend,
            "gpt4all_preferred": backend == "gpt4all",
            "network_preferred": backend == "mistral",
            "message": f"Active backend: {backend}",
        }

    def _switch(self, backend: str) -> Dict:
        if backend not in self.BACKENDS:
            return {
                "status": "error",
                "message": f"Unknown backend '{backend}'. Choose: {', '.join(self.BACKENDS)}",
            }
        self._state["backend"] = backend
        return {"status": "success", "message": f"Logic backend switched to '{backend}'."}

    def _ask(self, prompt: str) -> Dict:
        backend = self._state.get("backend", "gpt4all")
        logger.info(f"[AI] ask via {backend}: {prompt[:80]}")
        try:
            if backend == "gpt4all":
                from wizard.services.logic_assist_service import (
                    LogicAssistRequest,
                    get_logic_assist_service,
                )

                result = __import__("asyncio").run(
                    get_logic_assist_service().complete(
                        LogicAssistRequest(prompt=prompt, offline_required=True),
                        device_id="local",
                    )
                )
                if not result.success:
                    return {"status": "error", "message": result.error or "Logic assist failed."}
                output = result.content
            else:
                from wizard.services.logic_assist_service import (
                    LogicAssistRequest,
                    get_logic_assist_service,
                )

                result = __import__("asyncio").run(
                    get_logic_assist_service().complete(
                        LogicAssistRequest(prompt=prompt, force_network=True),
                        device_id="local",
                    )
                )
                if not result.success:
                    return {"status": "error", "message": result.error or "Network assist failed."}
                output = result.content
            history = self._state.setdefault("history", [])
            history.append({"prompt": prompt, "response": output[:500]})
            if len(history) > 20:
                history[:] = history[-20:]
            return {"status": "success", "backend": backend, "response": output}
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
                "AI - v1.5 logic assist integration\n"
                "  AI ASK <prompt>           Send a prompt to the active logic lane\n"
                "  AI STATUS                 Show active backend and availability\n"
                "  AI SWITCH gpt4all|mistral Switch logic backend\n"
                "  AI HISTORY                Show recent conversation turns\n"
                "  AI CLEAR                  Clear conversation history\n"
            ),
        }
