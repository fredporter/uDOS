from __future__ import annotations

from core.ulogic import parse_input, parse_primary_input


def test_parse_primary_ucode_command() -> None:
    frame = parse_primary_input("UCODE HELP")

    assert frame is not None
    assert frame.input_class == "command"
    assert frame.intent == "ucode.raw"
    assert frame.slots["command_text"] == "UCODE HELP"
    assert frame.routing_outcome().route == "dispatch.command"


def test_parse_workflow_run() -> None:
    frame = parse_primary_input("workflow run writer-001")

    assert frame is not None
    assert frame.input_class == "workflow"
    assert frame.intent == "workflow.run"
    assert frame.slots["workflow_id"] == "writer-001"
    assert frame.routing_outcome().route == "dispatch.workflow"


def test_parse_workflow_new() -> None:
    frame = parse_primary_input("create workflow WORKFLOW-template as wf-101")

    assert frame is not None
    assert frame.intent == "workflow.new"
    assert frame.slots["template_id"] == "WORKFLOW-template"
    assert frame.slots["workflow_id"] == "wf-101"


def test_parse_knowledge_browse() -> None:
    frame = parse_primary_input("browse knowledge devices/audio")

    assert frame is not None
    assert frame.input_class == "knowledge"
    assert frame.intent == "knowledge.browse"
    assert frame.slots["knowledge_path"] == "devices/audio"
    assert frame.routing_outcome().route == "dispatch.knowledge"


def test_parse_knowledge_duplicate() -> None:
    frame = parse_primary_input(
        "duplicate template seeds/runbook.md into local/topics/runbook.md"
    )

    assert frame is not None
    assert frame.intent == "knowledge.duplicate"
    assert frame.slots["source_path"] == "seeds/runbook.md"
    assert frame.slots["target_path"] == "local/topics/runbook.md"


def test_parse_unknown_as_guidance_plan() -> None:
    frames = parse_input("help me organize notes for my synth rack")

    assert len(frames) == 1
    assert frames[0].input_class == "guidance"
    assert frames[0].intent == "guidance.plan"
    assert frames[0].slots["text"] == "help me organize notes for my synth rack"
