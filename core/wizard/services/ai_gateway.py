"""Lightweight AI Provider helpers for telemetry."""

from enum import Enum
from typing import List


class AIProvider(Enum):
    OPENAI = "openai"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"

    @property
    def value_display(self) -> str:
        return self.value

    @classmethod
    def list_providers(cls) -> List[str]:
        return [provider.value for provider in cls]

    @classmethod
    def from_value(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            return None
