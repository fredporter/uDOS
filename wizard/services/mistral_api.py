"""
Mistral API Client
==================

Minimal client for Mistral Chat Completions.
"""

from __future__ import annotations

import os
from typing import Optional

import requests

from wizard.services.logging_manager import get_logger
from wizard.services.ai_context_store import write_context_bundle

logger = get_logger("wizard.mistral-api")


class MistralAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY", "")
        self.endpoint = "https://api.mistral.ai/v1/chat/completions"

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, model: str = "mistral-large-latest") -> str:
        if not self.api_key:
            raise RuntimeError("MISTRAL_API_KEY not configured")

        context_path = write_context_bundle()
        context = ""
        try:
            context = context_path.read_text()
        except Exception:
            context = ""

        system = (
            "You are the uDOS Wizard Dev Mode assistant. Use the provided context."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"{context}\n\nUser request: {prompt}"},
        ]
        resp = requests.post(
            self.endpoint,
            json={"model": model, "messages": messages},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
