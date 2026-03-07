from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from wizard.services.local_model_gpt4all import GPT4AllLocalAssist
from wizard.services.logic_assist_profile import load_logic_assist_profile
from wizard.services.logic_assist_service import LogicAssistRequest, get_logic_assist_service


class LogicAssistAdapter:
    """Sync adapter exposing Wizard logic assist through the core provider registry."""

    def __init__(self, repo_root: Path):
        self._repo_root = Path(repo_root)
        self._service = get_logic_assist_service(self._repo_root)

    def complete(
        self,
        prompt: str,
        *,
        offline_required: bool = False,
        force_network: bool = False,
        device_id: str = "local",
    ) -> dict[str, Any]:
        result = asyncio.run(
            self._service.complete(
                LogicAssistRequest(
                    prompt=prompt,
                    offline_required=offline_required,
                    force_network=force_network,
                ),
                device_id=device_id,
            )
        )
        return {
            "success": bool(result.success),
            "content": result.content,
            "error": result.error,
        }


class LocalCodeAssistAdapter:
    """Sync adapter for local code generation via GPT4All."""

    def __init__(self, repo_root: Path):
        self._repo_root = Path(repo_root)

    def generate(self, prompt: str, *, model: str) -> str:
        profile = load_logic_assist_profile()
        payload = profile.to_dict()
        payload["local_model_name"] = model
        resolved_profile = profile.__class__(**payload)
        return GPT4AllLocalAssist(
            resolved_profile,
            self._repo_root,
        ).generate(prompt)
