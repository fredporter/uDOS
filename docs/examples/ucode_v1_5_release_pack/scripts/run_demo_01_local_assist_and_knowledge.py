from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys
from unittest.mock import patch

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import wizard.services.logic_assist_service as logic_service_module
from wizard.services.logic_assist_profile import LogicAssistProfile
from wizard.services.logic_assist_service import LogicAssistRequest, LogicAssistService

from demo_runtime import write_report

DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-01-local-assist-and-knowledge.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-01-runtime")


class _QuotaTracker:
    def get_all_quotas(self):
        return {}


class _LocalReady:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    def status(self):
        return type(
            "_Status",
            (),
            {
                "to_dict": lambda self: {
                    "ready": True,
                    "issue": None,
                    "model": "local.gguf",
                    "model_path": "/demo/local.gguf",
                    "context_window": 8192,
                    "runtime": "gpt4all",
                },
                "ready": True,
                "issue": None,
            },
        )()

    def generate(self, prompt: str, system: str = "") -> str:
        self.calls.append({"prompt": prompt, "system": system})
        return "local-demo-response"


def _profile() -> LogicAssistProfile:
    return LogicAssistProfile(
        component_id="logic-assist",
        local_runtime="gpt4all",
        local_role="advisory_only",
        local_model_name="local.gguf",
        local_model_path="memory/models/gpt4all",
        local_context_window=8192,
        local_prompt_style="markdown_runbook",
        network_enabled=False,
        network_primary_provider="mistral",
        network_tier0_provider="openrouter",
        network_tier1_provider="mistral",
        network_tier2_provider="openai",
        daily_limit_usd=10.0,
        tier0_daily_limit_usd=2.0,
        tier1_daily_limit_usd=4.0,
        tier2_daily_limit_usd=4.0,
        auto_defer_when_exceeded=True,
        response_cache_enabled=False,
        schema_version="udos-logic-assist-v1.5",
        effective_path="settings/logic-assist.md",
        effective_source="demo",
        fields={},
    )


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    runtime_root.mkdir(parents=True, exist_ok=True)
    local = _LocalReady()
    with (
        patch.object(logic_service_module, "load_logic_assist_profile", lambda repo_root=None: _profile()),
        patch.object(logic_service_module, "get_quota_tracker", lambda: _QuotaTracker()),
        patch.object(
            logic_service_module,
            "build_ok_context_payload",
            lambda workspace="core": {
                "workspace": workspace,
                "hash": "demo-knowledge-hash",
                "files": ["AGENTS.md", "core/AGENTS.md"],
                "count": 2,
                "bundle": {
                    "AGENTS.md": "Prefer OK Assistant terminology and canonical ucode command routing.",
                    "core/AGENTS.md": "Core stays deterministic and must not import from wizard.",
                },
            },
        ),
        patch.object(
            logic_service_module,
            "render_system_prompt",
            lambda mode="general": "\n".join(
                [
                    "uDOS v1.5 Logic Assist",
                    "You are an advisory-only local assist layer.",
                    f"Mode: {mode}",
                    "Execution authority belongs to uLogic.",
                ]
            ),
        ),
    ):
        service = LogicAssistService(runtime_root)
        service.local = local
        response = asyncio.run(
            service.complete(
                LogicAssistRequest(
                    prompt="Summarize the current offline guidance contract.",
                    workspace="core",
                    mode="general",
                    conversation_id="demo-01-thread",
                    offline_required=True,
                ),
                device_id="demo-device",
            )
        )
        status = service.get_status()
        conversation_path = runtime_root / "memory" / "wizard" / "logic_conversations" / "demo-01-thread.json"

    payload = {
        "demo": "01-local-assist-and-knowledge",
        "runtime_root": str(runtime_root.resolve()),
        "status": status,
        "response": response.to_dict(),
        "conversation_path": str(conversation_path),
        "conversation_exists": conversation_path.exists(),
        "local_calls": local.calls,
    }
    return write_report(output_path, payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--runtime-root", default=str(DEFAULT_RUNTIME))
    args = parser.parse_args()
    path = build_report(Path(args.output), Path(args.runtime_root))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
