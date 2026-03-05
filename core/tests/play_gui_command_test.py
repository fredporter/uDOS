"""Tests for PLAY GUI gameplay consolidation bridge."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.commands.gameplay_handler import GameplayHandler


class _FakeGameplayService:
    def tick(self, username: str):
        return {"ok": True}

    def get_active_toybox(self) -> str:
        return "crawler3d"


class PlayGuiCommandTest(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = GameplayHandler()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "core" / "config").mkdir(parents=True, exist_ok=True)
        (self.root / "memory" / "ucode").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _mock_user_mgr(self):
        return SimpleNamespace(
            current=lambda: SimpleNamespace(username="admin", role=SimpleNamespace(value="admin"))
        )

    @patch("core.services.gameplay_service.get_gameplay_service", return_value=_FakeGameplayService())
    @patch("core.services.user_service.get_user_manager")
    def test_play_gui_status(self, mock_user_mgr, _mock_gameplay):
        mock_user_mgr.return_value = self._mock_user_mgr()
        with patch("core.services.thin_gui_bridge_service.get_repo_root", return_value=self.root):
            result = self.handler.handle("PLAY", ["gui", "status"])
        self.assertEqual(result["status"], "success")
        self.assertIn("PLAY GUI STATUS", result["output"])

    @patch("core.services.gameplay_service.get_gameplay_service", return_value=_FakeGameplayService())
    @patch("core.services.user_service.get_user_manager")
    def test_play_gui_intent_writes_file(self, mock_user_mgr, _mock_gameplay):
        mock_user_mgr.return_value = self._mock_user_mgr()
        with patch("core.services.thin_gui_bridge_service.get_repo_root", return_value=self.root):
            result = self.handler.handle("PLAY", ["gui", "intent", "crawler3d"])
        self.assertEqual(result["status"], "success")
        self.assertIn("Intent saved:", result["output"])
        intent_path = self.root / "memory" / "ucode" / "thin_gui_intent.json"
        self.assertTrue(intent_path.exists())


if __name__ == "__main__":
    unittest.main()
