"""Tests for gameplay/thin-gui bridge service."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.services.thin_gui_bridge_service import ThinGuiBridgeService


class ThinGuiBridgeServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "core" / "config").mkdir(parents=True, exist_ok=True)
        (self.root / "memory" / "ucode").mkdir(parents=True, exist_ok=True)
        catalog = {
            "profiles": {
                "crawler3d": {
                    "container_id": "crawler3d",
                    "ui_mode": "advanced-gui-extension",
                    "extension_owner": "3dworld",
                }
            }
        }
        (self.root / "core" / "config" / "lens_skin_game_catalog_v1_5.json").write_text(
            json.dumps(catalog),
            encoding="utf-8",
        )
        self.service = ThinGuiBridgeService(repo_root=self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_resolve_target_uses_catalog_and_defaults(self) -> None:
        launch = self.service.resolve_target("crawler3d")
        self.assertEqual(launch.profile_id, "crawler3d")
        self.assertEqual(launch.target_url, "http://127.0.0.1:7424")
        self.assertEqual(launch.mode, "advanced-gui-extension")
        self.assertEqual(launch.extension_owner, "3dworld")

    def test_write_intent_persists_payload(self) -> None:
        launch = self.service.resolve_target("crawler3d")
        payload = self.service.write_intent(launch)
        self.assertEqual(payload["profile_id"], "crawler3d")
        self.assertTrue(self.service.intent_path.exists())

    def test_wizard_route_contains_thin_gui_hash(self) -> None:
        launch = self.service.resolve_target("crawler3d")
        route = self.service.wizard_route(launch)
        self.assertIn("#thin-gui", route)
        self.assertIn("target=http://127.0.0.1:7424", route)


if __name__ == "__main__":
    unittest.main()
