from __future__ import annotations

from core.commands.ok_handler import OKHandler
from core.commands.okfix_handler import OkfixHandler
from core.services.provider_registry import CoreProviderRegistry, ProviderType


class _LogicAssistProvider:
    def complete(self, prompt: str, **kwargs):
        return {
            "success": True,
            "content": f"{prompt}|offline={kwargs.get('offline_required')}|network={kwargs.get('force_network')}",
        }


class _LocalCodeAssistProvider:
    def generate(self, prompt: str, *, model: str):
        return f"{model}:{prompt}"


def test_ok_handler_uses_registered_logic_assist_provider():
    CoreProviderRegistry.clear()
    CoreProviderRegistry.register(ProviderType.LOGIC_ASSIST, _LogicAssistProvider())

    handler = OKHandler()
    result = handler.handle("OK", ["ask", "hello"])

    assert result["status"] == "success"
    assert result["backend"] == "gpt4all"
    assert "hello" in result["response"]


def test_okfix_handler_uses_registered_local_code_provider():
    CoreProviderRegistry.clear()
    CoreProviderRegistry.register(ProviderType.LOCAL_CODE_ASSIST, _LocalCodeAssistProvider())

    handler = OkfixHandler()
    result = handler.handle("OKFIX", ["run", "ship", "it"])

    assert result["status"] == "success"
    assert result["backend"] == "gpt4all"
    assert "ship it" in result["response"]
