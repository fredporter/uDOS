from __future__ import annotations

import json
from types import SimpleNamespace

from core.commands.skin_handler import SkinHandler


class _FakeUserManager:
    def current(self):
        return SimpleNamespace(username="alice")


class _FakeGameplayService:
    def __init__(self, active_lens: str):
        self._active_lens = active_lens

    def progression_snapshot(self, _username: str):
        return {
            "active_lens": self._active_lens,
            "stats": {"xp": 100, "gold": 20},
            "progress": {"achievement_level": 1},
            "blocked_requirements": [],
        }


def test_skin_policy_flags_mismatch(monkeypatch):
    handler = SkinHandler()
    monkeypatch.setattr("core.services.user_service.get_user_manager", lambda: _FakeUserManager())
    monkeypatch.setattr(
        "core.services.gameplay_service.get_gameplay_service",
        lambda: _FakeGameplayService(active_lens="elite"),
    )
    monkeypatch.setattr(handler, "_available_skins", lambda: ["teletext", "c64", "default"])

    progression, policy_flag, policy_note = handler._skin_policy_context("c64")
    assert progression is not None
    assert policy_flag == "skin_lens_mismatch"
    assert "Recommended for elite" in (policy_note or "")


def test_skin_policy_flags_unmapped_lens(monkeypatch):
    handler = SkinHandler()
    monkeypatch.setattr("core.services.user_service.get_user_manager", lambda: _FakeUserManager())
    monkeypatch.setattr(
        "core.services.gameplay_service.get_gameplay_service",
        lambda: _FakeGameplayService(active_lens="unknown_lens"),
    )
    monkeypatch.setattr(handler, "_available_skins", lambda: ["default"])

    _, policy_flag, policy_note = handler._skin_policy_context("default")
    assert policy_flag == "skin_lens_unmapped"
    assert "No skin recommendation map" in (policy_note or "")


def test_skin_check_returns_recommendations(monkeypatch):
    handler = SkinHandler()
    monkeypatch.setattr("core.services.user_service.get_user_manager", lambda: _FakeUserManager())
    monkeypatch.setattr(
        "core.services.gameplay_service.get_gameplay_service",
        lambda: _FakeGameplayService(active_lens="elite"),
    )
    monkeypatch.setattr(handler, "_active_skin", lambda: "c64")
    monkeypatch.setattr(handler, "_available_skins", lambda: ["teletext", "c64", "default"])

    result = handler.handle("SKIN", ["CHECK"])
    assert result["status"] == "success"
    assert "Recommended skins:" in result["output"]
    assert "Flag-only mode" in result["output"]


def test_skin_policy_flags_progression_drift(monkeypatch):
    class _BlockedEliteGameplay(_FakeGameplayService):
        def progression_snapshot(self, _username: str):
            return {
                "active_lens": "elite",
                "stats": {"xp": 10, "gold": 1},
                "progress": {"achievement_level": 0},
                "blocked_requirements": ["xp>=100"],
                "play_options": [
                    {"id": "dungeon", "available": True, "blocked_by": []},
                    {"id": "galaxy", "available": False, "blocked_by": ["xp>=100"]},
                    {"id": "social", "available": False, "blocked_by": ["achievement_level>=1"]},
                    {"id": "ascension", "available": False, "blocked_by": ["gate:dungeon_l32_amulet"]},
                ],
                "unlock_tokens": [],
            }

    handler = SkinHandler()
    monkeypatch.setattr("core.services.user_service.get_user_manager", lambda: _FakeUserManager())
    monkeypatch.setattr(
        "core.services.gameplay_service.get_gameplay_service",
        lambda: _BlockedEliteGameplay(active_lens="elite"),
    )
    monkeypatch.setattr(handler, "_available_skins", lambda: ["teletext", "c64", "default"])

    _, policy_flag, policy_note = handler._skin_policy_context("teletext")
    assert policy_flag == "skin_lens_progression_drift"
    assert "not enforce" in (policy_note or "").lower()


def test_skin_status_compact(monkeypatch):
    handler = SkinHandler()
    monkeypatch.setattr("core.services.user_service.get_user_manager", lambda: _FakeUserManager())
    monkeypatch.setattr(
        "core.services.gameplay_service.get_gameplay_service",
        lambda: _FakeGameplayService(active_lens="elite"),
    )
    monkeypatch.setattr(handler, "_active_skin", lambda: "teletext")

    result = handler.handle("SKIN", ["STATUS", "--compact"])
    assert result["status"] == "success"
    output = result["output"]
    assert output.startswith("SKIN:")
    assert "skin=" in output
    assert "lens=" in output
    assert "fit=" in output


def test_skin_check_compact(monkeypatch):
    handler = SkinHandler()
    monkeypatch.setattr("core.services.user_service.get_user_manager", lambda: _FakeUserManager())
    monkeypatch.setattr(
        "core.services.gameplay_service.get_gameplay_service",
        lambda: _FakeGameplayService(active_lens="elite"),
    )
    monkeypatch.setattr(handler, "_active_skin", lambda: "c64")
    monkeypatch.setattr(handler, "_available_skins", lambda: ["teletext", "c64", "default"])

    result = handler.handle("SKIN", ["CHECK", "--compact"])
    assert result["status"] == "success"
    output = result["output"]
    assert output.startswith("SKIN:")
    assert "recommended=" in output


def test_skin_meta_includes_explicit_gameplay_contract(tmp_path):
    handler = SkinHandler()
    skin_dir = tmp_path / "themes" / "contracted"
    skin_dir.mkdir(parents=True)
    (skin_dir / "theme.json").write_text(
        json.dumps(
            {
                "name": "contracted",
                "version": "1.0.0",
                "description": "explicit gameplay contract",
                "gameplay": {
                    "contract_version": "v1",
                    "compatible_lenses": ["any"],
                    "recommended_lenses": ["elite"],
                    "score_profile": "elite-score",
                    "checkpoint_profile": "elite-checkpoints",
                    "overlay_defaults": {},
                },
            }
        ),
        encoding="utf-8",
    )
    handler.skin_root = tmp_path / "themes"

    meta = handler._skin_meta("contracted")
    assert meta is not None
    contract = meta.get("gameplay_contract", {})
    assert contract.get("valid") is True
    assert contract.get("contract_version") == "v1"


def test_skin_meta_flags_invalid_gameplay_contract(tmp_path):
    handler = SkinHandler()
    skin_dir = tmp_path / "themes" / "broken"
    skin_dir.mkdir(parents=True)
    (skin_dir / "theme.json").write_text(
        json.dumps(
            {
                "name": "broken",
                "version": "1.0.0",
                "description": "invalid gameplay contract",
                "gameplay": {
                    "contract_version": "",
                    "compatible_lenses": ["unknown-lens"],
                    "recommended_lenses": [],
                    "score_profile": "",
                    "checkpoint_profile": "",
                },
            }
        ),
        encoding="utf-8",
    )
    handler.skin_root = tmp_path / "themes"

    meta = handler._skin_meta("broken")
    assert meta is not None
    contract = meta.get("gameplay_contract", {})
    assert contract.get("valid") is False
    assert "unknown_compatible_lens:unknown-lens" in contract.get("errors", [])
