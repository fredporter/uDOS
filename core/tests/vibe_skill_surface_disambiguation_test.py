from core.services.vibe_cli_handler import VibeCliHandler
from core.services.vibe_skill_mapper import get_skill_contract, list_all_skills


def test_wizops_is_canonical_skill_name() -> None:
    skills = set(list_all_skills())
    assert "wizops" in skills
    assert "wizard" not in skills


def test_wizard_skill_name_is_not_registered() -> None:
    canonical = get_skill_contract("wizops")
    alias = get_skill_contract("wizard")
    assert canonical is not None
    assert alias is None
    assert canonical.name == "wizops"


def test_vibe_cli_accepts_wizops_only(monkeypatch) -> None:
    handler = VibeCliHandler()

    class _Service:
        def list_tasks(self):
            return {"status": "success", "message": "ok", "tasks": []}

    monkeypatch.setattr("core.services.vibe_cli_handler.get_wizard_service", lambda: _Service())

    canonical = handler.execute("WIZOPS LIST")
    alias = handler.execute("WIZARD LIST")

    assert canonical["status"] == "success"
    assert alias["status"] == "error"
