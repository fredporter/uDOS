from __future__ import annotations

import json
from pathlib import Path

from core.commands.health_handler import HealthHandler


def test_health_check_housekeeping_preview_and_apply(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    compost = repo / ".compost"
    compost.mkdir(parents=True, exist_ok=True)
    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    (vault / "keep.md").write_text("# keep\n", encoding="utf-8")
    (vault / "drop.exe").write_text("x", encoding="utf-8")

    monkeypatch.setattr("core.commands.health_handler.get_repo_root", lambda: repo)
    monkeypatch.setattr("core.services.maintenance_utils.get_repo_root", lambda: repo)
    monkeypatch.setattr("core.services.maintenance_utils.get_vault_root", lambda: vault)

    handler = HealthHandler()

    preview = handler.handle("HEALTH", ["CHECK", "housekeeping", "--scope", "vault"])
    assert preview["status"] == "warning"
    assert "HEALTH CHECK housekeeping" in preview["output"]

    applied = handler.handle(
        "HEALTH",
        ["CHECK", "housekeeping", "--scope", "vault", "--apply", "--format", "json"],
    )
    payload = json.loads(applied["output"])
    assert payload["moved"] >= 1
    assert not (vault / "drop.exe").exists()
    assert (vault / "keep.md").exists()
