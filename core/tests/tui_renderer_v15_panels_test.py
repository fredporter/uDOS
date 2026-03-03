from __future__ import annotations

from core.tui.renderer import GridRenderer


def test_renderer_formats_routed_workflow_state_panel() -> None:
    renderer = GridRenderer()

    output = renderer.render(
        {
            "status": "success",
            "routing": {
                "route": "dispatch.workflow",
                "input_class": "workflow",
                "intent": "workflow.status",
                "confidence": 0.8,
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
                    "total_tokens": 120,
                    "total_cost_usd": 0.0,
                }
            },
            "output": "Workflow: wf-001\nStatus: awaiting_approval",
        }
    )

    assert "UCODE ROUTE" in output
    assert "WORKFLOW STATE" in output
    assert "workflow:" in output
    assert "wf-001" in output
    assert "awaiting_approval" in output


def test_renderer_formats_operator_plan_panel() -> None:
    renderer = GridRenderer()

    output = renderer.render(
        {
            "status": "success",
            "routing": {
                "route": "dispatch.guidance",
                "input_class": "guidance",
                "intent": "guidance.plan",
                "confidence": 0.2,
                "source": "deterministic-pattern",
            },
            "operator_plan": {
                "summary": "Use workflow and binder review steps",
                "intent": {
                    "label": "organize",
                    "confidence": 0.72,
                    "reason": "binder and workflow terms detected",
                },
                "actions": [
                    {
                        "command": "WORKFLOW LIST TEMPLATES",
                        "description": "Inspect standard workflow templates",
                    }
                ],
            },
            "output": "Operator intent: organize",
        }
    )

    assert "OPERATOR PLAN" in output
    assert "WORKFLOW LIST TEMPLATES" in output
    assert "organize" in output


def test_renderer_formats_knowledge_artifact_panel() -> None:
    renderer = GridRenderer()

    output = renderer.render(
        {
            "status": "success",
            "routing": {
                "route": "dispatch.knowledge",
                "input_class": "knowledge",
                "intent": "knowledge.research",
                "confidence": 0.8,
                "source": "deterministic-pattern",
            },
            "saved_path": "/tmp/research-note.md",
            "imported": {
                "note_id": "note-001",
                "target_path": "/tmp/workflow/inputs/note-001.md",
                "processed_snapshot": "/tmp/.compost/note-001.md",
            },
            "output": "Saved: /tmp/research-note.md",
        }
    )

    assert "KNOWLEDGE ARTIFACTS" in output
    assert "/tmp/research-note.md" in output
    assert "note-001" in output
