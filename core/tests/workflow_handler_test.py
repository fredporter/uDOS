from __future__ import annotations

import shutil
from pathlib import Path

from core.services.path_service import get_repo_root
from core.tui.dispatcher import CommandDispatcher


def _cleanup(workflow_id: str) -> None:
    path = Path(get_repo_root()) / "memory" / "vault" / "workflows" / workflow_id
    if path.exists():
        shutil.rmtree(path)


def test_dispatcher_supports_workflow_command() -> None:
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("WORKFLOW LIST TEMPLATES")

    assert result["status"] == "success"
    assert "WRITING-article" in result["templates"]


def test_workflow_handler_new_status_run() -> None:
    workflow_id = "wf-handler-001"
    _cleanup(workflow_id)
    dispatcher = CommandDispatcher()

    try:
        created = dispatcher.dispatch(
            'WORKFLOW NEW WRITING-article wf-handler-001 goal="Write release note" audience=operators tone=plain word_limit=600'
        )
        assert created["status"] == "success"

        status = dispatcher.dispatch("WORKFLOW STATUS wf-handler-001")
        assert status["status"] == "success"
        assert "Current phase: outline" in status["output"]

        run = dispatcher.dispatch("WORKFLOW RUN wf-handler-001")
        assert run["status"] == "success"
        assert "Status: awaiting_approval" in run["output"]
    finally:
        _cleanup(workflow_id)
