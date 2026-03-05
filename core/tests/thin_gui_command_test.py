"""Tests for THINGUI command handler."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from core.commands.thin_gui_handler import ThinGuiHandler
from core.services.error_contract import CommandError


class ThinGuiHandlerTest(unittest.TestCase):
    """Validate THINGUI extension bridge behavior."""

    def setUp(self) -> None:
        self.handler = ThinGuiHandler()
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.handler.repo_root = self.root
        self.handler.extension_dir = self.root / "extensions" / "thin-gui"
        self.handler.intent_path = self.root / "memory" / "ucode" / "thin_gui_intent.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_status_reports_missing_extension(self) -> None:
        result = self.handler.handle("THINGUI", ["status"])
        self.assertEqual(result["status"], "success")
        self.assertIn("Available: no", result["output"])
        self.assertFalse(result["thin_gui"]["available"])

    def test_intent_writes_payload(self) -> None:
        result = self.handler.handle(
            "THINGUI",
            ["intent", "http://127.0.0.1:7424", "Crawler3D", "Crawler"],
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(self.handler.intent_path.exists())

        payload = json.loads(self.handler.intent_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["target"], "http://127.0.0.1:7424")
        self.assertEqual(payload["title"], "Crawler3D")
        self.assertEqual(payload["label"], "Crawler")
        self.assertEqual(payload["extension"], "thin-gui")

    def test_open_uses_wizard_base_url(self) -> None:
        previous = os.environ.get("WIZARD_BASE_URL")
        os.environ["WIZARD_BASE_URL"] = "http://127.0.0.1:9999"
        try:
            result = self.handler.handle("THINGUI", ["open", "http://127.0.0.1:7424"])
        finally:
            if previous is None:
                os.environ.pop("WIZARD_BASE_URL", None)
            else:
                os.environ["WIZARD_BASE_URL"] = previous

        self.assertEqual(result["status"], "success")
        self.assertIn("#thin-gui", result["route"])
        self.assertIn("target=http://127.0.0.1:7424", result["route"])

    def test_unknown_action_raises(self) -> None:
        with self.assertRaises(CommandError):
            self.handler.handle("THINGUI", ["oops"])

    def test_install_requires_extension_dir(self) -> None:
        with self.assertRaises(CommandError):
            self.handler.handle("THINGUI", ["install"])


if __name__ == "__main__":
    unittest.main()
