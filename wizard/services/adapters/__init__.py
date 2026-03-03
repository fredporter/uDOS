"""Provider Adapters - __init__.py

Exposes all provider adapters for multi-provider routing.

Available adapters:
- OllamaAdapter: Local Ollama integration
- MistralAdapter: Mistral API integration
- (Future: OpenAI, Anthropic, Gemini)

Version: 1.0.0
Release baseline: v1.5 contributor routing
"""

from __future__ import annotations

from wizard.services.adapters.mistral_adapter import MistralAdapter, MistralConfig
from wizard.services.adapters.ollama_adapter import OllamaAdapter, OllamaConfig

__all__ = ["MistralAdapter", "MistralConfig", "OllamaAdapter", "OllamaConfig"]
