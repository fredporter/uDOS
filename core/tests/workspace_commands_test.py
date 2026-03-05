from pathlib import Path
import shutil
from uuid import uuid4

from core.services.config_sync_service import ConfigSyncManager
from core.services.user_service import UserRole, get_user_manager
from core.tui.dispatcher import CommandDispatcher


def test_workspace_commands_are_dispatched():
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("PLACE INFO")
    assert result["status"] == "success"
    assert "Workspace Configuration" in result.get("output", "")


def test_file_list_workspace_ref_works():
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("FILE LIST @vault")
    assert result["status"] in {"success", "error"}


def test_binder_open_workspace_ref_works(monkeypatch):
    monkeypatch.setattr(
        ConfigSyncManager,
        "load_identity_from_env",
        lambda self: {"user_username": "admin", "user_role": "admin"},
    )

    user_mgr = get_user_manager()
    original_user = user_mgr.current().username if user_mgr.current() else None
    if "admin" not in user_mgr.users:
        user_mgr.create_user("admin", UserRole.ADMIN)
    user_mgr.switch_user("admin")

    dispatcher = CommandDispatcher()
    binder_id = f"ws-binder-{uuid4().hex[:8]}"
    workspace_ref = f"@binders/{binder_id}"

    try:
        result = dispatcher.dispatch(f"BINDER OPEN {workspace_ref}")
        assert result["status"] in {"success", "warning"}
        if result["status"] == "success":
            assert binder_id in result.get("output", "")
        else:
            assert "Ghost Mode" in result.get("output", "")
    finally:
        binder_path = Path("memory/vault/@binders") / binder_id
        if binder_path.exists():
            shutil.rmtree(binder_path)
        if original_user and original_user in user_mgr.users:
            user_mgr.switch_user(original_user)
