from __future__ import annotations

import io
import json

from core.tui.protocol_bridge import ProtocolContext, UdosProtocolBridge, run_stdio
from core.tui.renderer import GridRenderer
from core.tui.state import GameState


class _DispatcherStub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def dispatch(self, command_text: str, parser=None, game_state=None) -> dict:
        self.calls.append(command_text)
        return {
            "status": "success",
            "message": "stub dispatched",
            "output": command_text,
        }


def _run_lines(*messages: dict) -> list[dict]:
    stdin = io.StringIO("".join(json.dumps(item) + "\n" for item in messages))
    stdout = io.StringIO()
    assert run_stdio(stdin, stdout) == 0
    return [json.loads(line) for line in stdout.getvalue().splitlines() if line.strip()]


def test_protocol_bridge_hello_returns_ready_and_banner() -> None:
    packets = _run_lines({"v": 1, "type": "hello", "id": "h-1"})
    assert packets[0]["type"] == "result"
    assert packets[0]["value"]["status"] == "ready"
    assert packets[0]["value"]["canvas_width"] == 78
    action_labels = [item["label"] for item in packets[0]["value"]["actions"]]
    assert "Wizard Start" in action_labels
    assert "Dev Mode Status" in action_labels
    assert "Wizard Status" in action_labels
    assert "Wizard GUI" in action_labels
    assert "Thin GUI (Direct)" in action_labels
    assert packets[0]["value"]["actions"][0]["job"] == "ucode.command"
    assert "command" in packets[0]["value"]["actions"][0]
    assert packets[1]["type"] == "event"
    assert packets[1]["event"]["kind"] == "teletext"


def test_protocol_bridge_run_emits_result_and_done_packets() -> None:
    packets = _run_lines(
        {
            "v": 1,
            "type": "run",
            "id": "r-1",
            "job": "ucode.command",
            "args": {"command": "HELP"},
        }
    )
    assert packets[0]["type"] == "result"
    assert packets[1]["event"]["kind"] == "progress"
    assert packets[1]["event"]["status"] == "running"
    assert any(packet.get("type") == "event" for packet in packets)
    assert packets[-2]["event"]["kind"] == "progress"
    assert packets[-2]["event"]["status"] == "done"
    assert packets[-1]["type"] == "done"
    assert packets[-1]["ok"] is True


def test_protocol_bridge_executes_plain_core_commands_before_guidance() -> None:
    dispatcher = _DispatcherStub()
    bridge = UdosProtocolBridge(
        ProtocolContext(
            dispatcher=dispatcher,
            game_state=GameState(),
            renderer=GridRenderer(),
        )
    )

    binder_result = bridge._route_input("BINDER CREATE @binder/new-mission")
    wizard_result = bridge._route_input("WIZARD START")
    play_result = bridge._route_input("PLAY STATUS")

    assert dispatcher.calls == [
        "BINDER CREATE @binder/new-mission",
        "WIZARD START",
        "PLAY STATUS",
    ]
    assert binder_result["status"] != "error"
    assert binder_result.get("routing") is None
    assert "operator_plan" not in binder_result

    assert wizard_result["status"] != "error"
    assert wizard_result.get("routing") is None
    assert "operator_plan" not in wizard_result

    assert play_result["status"] != "error"
    assert play_result.get("routing") is None
    assert "operator_plan" not in play_result


def test_protocol_bridge_formats_workflow_state_events() -> None:
    bridge = UdosProtocolBridge()
    events = bridge._result_to_events(
        {
            "status": "success",
            "routing": {
                "route": "dispatch.workflow",
                "input_class": "workflow",
                "intent": "workflow.status",
                "confidence": 0.9,
                "source": "deterministic-pattern",
                "command_text": "WORKFLOW STATUS wf-001",
            },
            "workflow_id": "wf-001",
            "workflow": {
                "state": {
                    "status": "awaiting_approval",
                    "current_phase_index": 0,
                    "phases": [{"name": "outline"}],
                    "next_run_at": "2026-03-04T00:00:00Z",
                    "total_tokens": 5,
                    "total_cost_usd": 0.0,
                }
            },
            "output": "Workflow: wf-001",
        }
    )
    titles = [event["title"] for event in events if event.get("kind") == "block"]
    assert "UCODE ROUTE" in titles
    assert "WORKFLOW STATE" in titles


def test_protocol_bridge_formats_knowledge_artifact_events() -> None:
    bridge = UdosProtocolBridge()
    events = bridge._result_to_events(
        {
            "status": "success",
            "routing": {
                "route": "dispatch.knowledge",
                "input_class": "knowledge",
                "intent": "knowledge.duplicate",
                "confidence": 0.85,
                "source": "deterministic-pattern",
                "command_text": "UCODE TEMPLATE DUPLICATE workflows WORKFLOW-template workflow-copy-md",
            },
            "duplicate": {
                "target_template": "workflow-copy-md",
                "target_path": "/tmp/workflow-copy-md.md",
            },
            "output": "Duplicated template",
        }
    )
    titles = [event["title"] for event in events if event.get("kind") == "block"]
    assert "UCODE ROUTE" in titles
    assert "KNOWLEDGE ARTIFACTS" in titles


def test_protocol_bridge_formats_helper_events() -> None:
    bridge = UdosProtocolBridge()
    events = bridge._result_to_events(
        {
            "status": "success",
            "source_path": "/tmp/dev/ops/tasks.json",
            "written": False,
            "format_helper": {
                "profile": "tasks-ledger",
                "profile_label": "Contributor Tasks",
                "valid": True,
                "changed": True,
                "errors": [],
            },
            "output": '{\n  "version": "1.0"\n}',
        }
    )

    titles = [event["title"] for event in events if event.get("kind") == "block"]
    assert "FORMAT HELPER" in titles


def test_protocol_bridge_adds_summary_block_when_result_has_no_output_text() -> None:
    bridge = UdosProtocolBridge()

    events = bridge._result_to_events(
        {
            "status": "ok",
            "message": "Wizard Server not running",
            "mode": "user",
            "flags": {"offline": True},
        }
    )

    summary = next(event for event in events if event.get("title") == "RESULT SUMMARY")
    assert "message: Wizard Server not running" in summary["lines"]
    assert "mode: user" in summary["lines"]


def test_protocol_bridge_slash_route_uses_bash_fallback_when_dispatch_fails() -> None:
    bridge = UdosProtocolBridge()
    bridge._dispatch_command = lambda *_args, **_kwargs: {  # type: ignore[assignment]
        "status": "error",
        "message": "unknown",
    }
    bridge._run_fallback_bash = lambda _cmd: {  # type: ignore[assignment]
        "status": "success",
        "message": "bash ok",
        "output": "hello",
    }

    result = bridge._route_input("/echo hello")

    assert result["status"] == "success"
    assert result["message"] == "bash ok"


def test_protocol_bridge_slash_route_falls_back_to_operator_guidance() -> None:
    bridge = UdosProtocolBridge()
    bridge._dispatch_command = lambda *_args, **_kwargs: {  # type: ignore[assignment]
        "status": "error",
        "message": "unknown",
    }
    bridge._run_fallback_bash = lambda _cmd: {  # type: ignore[assignment]
        "status": "error",
        "message": "bash failed",
    }

    result = bridge._route_input("/unknown command")

    assert result["status"] == "success"
    assert "operator guidance fallback" in result["message"].lower()
