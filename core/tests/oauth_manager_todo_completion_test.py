"""Tests for OAuth manager token lifecycle behavior."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from core.sync.oauth_manager import OAuthManager


class OAuthManagerTodoCompletionTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_credentials_auto_refreshes_expired_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = Path(tmp) / "credentials.json"
            manager = OAuthManager(storage_path=str(storage))
            manager.credentials_cache["jira"] = {
                "access_token": "old",
                "refresh_token": "refresh",
                "expires_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
            }
            creds = await manager.get_credentials("jira")
            self.assertIsNotNone(creds)
            self.assertTrue(str(creds.get("access_token", "")).startswith("refresh-jira-"))

    async def test_handle_callback_parses_manual_token_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = Path(tmp) / "credentials.json"
            manager = OAuthManager(storage_path=str(storage))
            from core.services import unified_config_loader

            old_get_config = unified_config_loader.get_config
            unified_config_loader.get_config = lambda key, default="": "x" if key.endswith(("CLIENT_ID", "CLIENT_SECRET")) else default
            try:
                tokens = await manager.handle_callback("jira", "access:tok123|refresh:ref456")
            finally:
                unified_config_loader.get_config = old_get_config

            self.assertEqual(tokens.get("access_token"), "tok123")
            self.assertEqual(tokens.get("refresh_token"), "ref456")


if __name__ == "__main__":
    unittest.main()
