"""
Vibe Service - Devstral Small 2 Integration

Integrates Mistral's Vibe CLI (Devstral Small 2 via Ollama) for offline-first
agent development and code generation.

Features:
  - Local Ollama endpoint management
  - Devstral model loading and inference
  - Streaming response handling
  - Context management (repo files, instructions)
  - Conversation history tracking
  - Output format handling (JSON, Markdown, plain text)

Configuration:
  - Ollama endpoint (default: http://127.0.0.1:11434)
  - Model name (default: devstral-small-2)
  - Context window (default: 8K tokens)
  - Temperature (default: 0.2 for deterministic)

Usage:
    from wizard.services.vibe_service import VibeService

    vibe = VibeService()
    response = vibe.generate(
        prompt="refactor this code",
        context="code_snippet",
        format="markdown"
    )

Version: 1.0.0
"""

import json
import subprocess
from typing import Optional, Dict, Any, List, Generator
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import requests

from wizard.services.logging_api import get_logger
from wizard.services.ai_context_store import write_context_bundle

logger = get_logger("vibe-service")


@dataclass
class VibeConfig:
    """Configuration for Vibe service."""

    endpoint: str = "http://127.0.0.1:11434"
    model: str = "devstral-small-2"
    temperature: float = 0.2  # Deterministic for code
    context_window: int = 8192
    top_p: float = 0.95
    timeout_seconds: int = 30


class VibeService:
    """Manages interactions with Devstral via Ollama."""

    def __init__(self, config: Optional[VibeConfig] = None):
        """Initialize Vibe service.

        Args:
            config: VibeConfig with endpoint, model, etc.
        """
        self.config = config or VibeConfig()
        self.conversation_history: List[Dict[str, str]] = []
        self._verify_connection()

    def _verify_connection(self) -> bool:
        """Verify Ollama endpoint is reachable.

        Returns:
            True if connection successful
        """
        try:
            resp = requests.get(f"{self.config.endpoint}/api/tags", timeout=5)
            resp.raise_for_status()
            tags = resp.json()
            models = [m["name"].split(":")[0] for m in tags.get("models", [])]

            if self.config.model.split(":")[0] in models:
                logger.info(
                    f"[LOCAL] Vibe: Connected to Ollama. Available: {', '.join(models[:3])}"
                )
                return True
            else:
                logger.warning(
                    f"[LOCAL] Vibe: Model {self.config.model} not found. "
                    f"Available: {', '.join(models)}"
                )
                return False
        except Exception as e:
            logger.error(
                f"[LOCAL] Vibe: Failed to connect to Ollama at {self.config.endpoint}: {e}"
            )
            return False

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        format: str = "text",
        stream: bool = False,
        **kwargs,
    ) -> str:
        """Generate response from Devstral.

        Args:
            prompt: User prompt
            system: System message (optional)
            format: Output format ("text", "json", "markdown")
            stream: Return as generator if True
            **kwargs: Additional parameters to pass to model

        Returns:
            Generated response (or generator if stream=True)
        """
        try:
            # Prepare messages
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            # Add conversation history if present
            if self.conversation_history:
                messages = self.conversation_history + messages

            # Ollama has two API formats:
            # /api/chat - Chat completion (messages array) - newer
            # /api/generate - Simple prompt - legacy
            # Try chat first, fallback to generate

            logger.info(f"[LOCAL] Vibe: Generating with {self.config.model}...")

            temperature = kwargs.pop("temperature", None)
            top_p = kwargs.pop("top_p", None)
            max_tokens = kwargs.pop("max_tokens", None)

            options = {
                "temperature": self.config.temperature if temperature is None else temperature,
                "top_p": self.config.top_p if top_p is None else top_p,
            }
            if max_tokens is not None:
                options["num_predict"] = max_tokens

            # Try /api/chat endpoint first (newer format)
            try:
                payload = {
                    "model": self.config.model,
                    "messages": messages,
                    "stream": stream,
                    "options": options,
                    **kwargs,
                }

                resp = requests.post(
                    f"{self.config.endpoint}/api/chat",
                    json=payload,
                    timeout=self.config.timeout_seconds,
                )
                resp.raise_for_status()

                if stream:
                    return self._stream_response(resp)
                else:
                    data = resp.json()
                    response_text = data["message"]["content"]

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # Fallback to /api/generate (older Ollama versions)
                    logger.info("[LOCAL] Vibe: /api/chat not available, using /api/generate")

                    # Convert messages to single prompt
                    prompt_parts = []
                    for msg in messages:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        if role == "system":
                            prompt_parts.append(f"System: {content}")
                        elif role == "user":
                            prompt_parts.append(f"User: {content}")
                        elif role == "assistant":
                            prompt_parts.append(f"Assistant: {content}")

                    combined_prompt = "\n\n".join(prompt_parts)

                    payload = {
                        "model": self.config.model,
                        "prompt": combined_prompt,
                        "stream": False,
                        "options": options,
                    }

                    resp = requests.post(
                        f"{self.config.endpoint}/api/generate",
                        json=payload,
                        timeout=self.config.timeout_seconds,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    response_text = data.get("response", "")
                else:
                    raise

            # Update history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append(
                {"role": "assistant", "content": response_text}
            )

            logger.info(f"[LOCAL] Vibe: Generated {len(response_text)} chars")
            return response_text

        except Exception as e:
            logger.error(f"[LOCAL] Vibe: Generation failed: {e}")
            raise

    def _stream_response(self, resp: requests.Response) -> Generator[str, None, None]:
        """Stream response chunks.

        Args:
            resp: HTTP response with streaming data

        Yields:
            Response chunks as strings
        """
        buffer = ""
        for line in resp.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    buffer += content
                    yield content
                except json.JSONDecodeError:
                    pass

        # Record in history at end
        if buffer:
            self.conversation_history.append({"role": "assistant", "content": buffer})

    def load_context(self, context_files: List[Path]) -> str:
        """Load context from files for the model.

        Args:
            context_files: Paths to context files (markdown, code, etc.)

        Returns:
            Concatenated context
        """
        context = []
        for file_path in context_files:
            try:
                with open(file_path) as f:
                    content = f.read()
                    context.append(f"# {file_path.name}\n\n{content}")
                    logger.info(f"[LOCAL] Loaded context: {file_path}")
            except Exception as e:
                logger.warning(f"[LOCAL] Failed to load context {file_path}: {e}")

        return "\n\n---\n\n".join(context)

    def load_default_context(self) -> str:
        """Load normalized context bundle from memory/ai."""
        context_path = write_context_bundle()
        try:
            data = json.loads(context_path.read_text())
        except Exception:
            return ""
        context = []
        for name, content in data.items():
            context.append(f"=== {name} ===\n{content}")
        return "\n\n".join(context)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("[LOCAL] Vibe: Conversation history cleared")

    def get_status(self) -> Dict[str, Any]:
        """Get Vibe service status.

        Returns:
            Dict with connection status, history length, etc.
        """
        return {
            "endpoint": self.config.endpoint,
            "model": self.config.model,
            "connected": self._verify_connection(),
            "conversation_turns": len(self.conversation_history),
            "temperature": self.config.temperature,
            "context_window": self.config.context_window,
        }
