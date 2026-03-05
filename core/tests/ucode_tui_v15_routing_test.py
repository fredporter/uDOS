from __future__ import annotations

from types import SimpleNamespace

from core.tui.ucode import UCODE


class _DispatcherStub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def dispatch(self, command_text: str, parser=None, game_state=None) -> dict:
        self.calls.append(command_text)
        return {
            "status": "success",
            "command": command_text.split()[0].upper(),
            "output": command_text,
        }


def _build_ucode(dev_mode: bool = False) -> tuple[UCODE, _DispatcherStub]:
    ucode = UCODE.__new__(UCODE)
    dispatcher = _DispatcherStub()
    ucode.dispatcher = dispatcher
    ucode.prompt = object()
    ucode.state = object()
    ucode.logger = SimpleNamespace(info=lambda *a, **k: None, debug=lambda *a, **k: None)
    ucode._dev_mode_active = lambda: dev_mode
    ucode._dispatch_with_vibe = lambda text: {
        "status": "dev_tool",
        "message": text,
        "routing": {"route": "dispatch.dev"},
    }
    ucode._route_to_operator = lambda prompt: {
        "status": "operator_plan",
        "output": prompt,
    }
    ucode._handle_operator_prefix = lambda text: {"status": "operator_prefix", "output": text}
    ucode._handle_logic_prefix = lambda text: {"status": "logic_prefix", "output": text}
    ucode._handle_slash_input = lambda text: {"status": "slash", "output": text}
    ucode._match_ucode_command = lambda text: (None, 0.0)
    ucode._execute_ucode_command = lambda cmd, rest: {
        "status": "success",
        "command": cmd,
        "output": f"{cmd} {rest}".strip(),
    }
    return ucode, dispatcher


def test_route_input_uses_workflow_contract():
    ucode, dispatcher = _build_ucode()

    result = ucode._route_input("workflow status wf-v15-001")

    assert dispatcher.calls == ["WORKFLOW STATUS wf-v15-001"]
    assert result["routing"]["route"] == "dispatch.workflow"
    assert result["routing"]["intent"] == "workflow.status"


def test_route_input_browses_template_family_from_knowledge_request():
    ucode, dispatcher = _build_ucode()

    result = ucode._route_input("browse knowledge missions")

    assert dispatcher.calls == ["UCODE TEMPLATE LIST missions"]
    assert result["routing"]["route"] == "dispatch.knowledge"
    assert result["routing"]["intent"] == "knowledge.browse"


def test_route_input_duplicates_seed_template_into_user_layer_command():
    ucode, dispatcher = _build_ucode()

    result = ucode._route_input(
        "duplicate template submissions/DEVICE-SUBMISSION-template to my-device-template"
    )

    assert dispatcher.calls == [
        "UCODE TEMPLATE DUPLICATE submissions DEVICE-SUBMISSION-template my-device-template"
    ]
    assert result["routing"]["route"] == "dispatch.knowledge"
    assert result["routing"]["intent"] == "knowledge.duplicate"


def test_route_input_researches_through_ucode_command_surface():
    ucode, dispatcher = _build_ucode()

    result = ucode._route_input("research local assist costs")

    assert dispatcher.calls == [
        "UCODE RESEARCH prompt shell://input research local assist costs"
    ]
    assert result["routing"]["route"] == "dispatch.knowledge"
    assert result["routing"]["intent"] == "knowledge.research"


def test_route_input_uses_operator_guidance_in_standard_runtime():
    ucode, dispatcher = _build_ucode(dev_mode=False)

    result = ucode._route_input("help me organise binder tasks")

    assert dispatcher.calls == []
    assert result["status"] == "operator_plan"
    assert result["routing"]["route"] == "dispatch.guidance"
    assert result["output"] == "help me organise binder tasks"


def test_route_input_keeps_dev_fallback_for_ambiguous_prompts():
    ucode, dispatcher = _build_ucode(dev_mode=True)

    result = ucode._route_input("help me organise binder tasks")

    assert dispatcher.calls == []
    assert result["status"] == "dev_tool"
    assert result["message"] == "help me organise binder tasks"
