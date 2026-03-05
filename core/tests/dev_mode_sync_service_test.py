"""Tests for DevModeToolSyncService completion paths."""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock

from core.services.dev_mode_compat.sync_service import DevModeToolSyncService


class _FakeBinderService:
    def __init__(self) -> None:
        self.binders: dict[str, dict] = {}
        self.added: list[tuple[str, dict]] = []

    def initialize_project(self, mission_id: str, name: str):
        self.binders[mission_id] = {"mission": {"id": mission_id}, "moves": [], "milestones": []}
        return {"status": "success"}

    def add_move(self, mission_id: str, title: str, description: str, **kwargs):
        self.added.append(
            (mission_id, {"title": title, "description": description, **kwargs})
        )
        move_id = f"move-{len(self.added)}"
        return {"status": "success", "move_id": move_id}


class DevModeSyncServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_persist_transformed_task_creates_mission_and_move(self) -> None:
        svc = DevModeToolSyncService()
        svc.binder_service = _FakeBinderService()

        move_id = svc._persist_transformed_task(
            mission_id="sync-inbox",
            task_item={
                "title": "Sync Item",
                "description": "Imported from provider",
                "tags": ["sync"],
                "metadata": {"external_id": "abc-123"},
            },
            source="jira",
        )

        self.assertEqual(move_id, "move-1")
        self.assertIn("sync-inbox", svc.binder_service.binders)
        self.assertEqual(svc.binder_service.added[0][1]["source"], "jira")

    async def test_trigger_full_sync_skips_without_credentials(self) -> None:
        svc = DevModeToolSyncService()
        svc.oauth_manager.get_credentials = AsyncMock(return_value=None)

        result = await svc.trigger_full_sync(["calendar", "email", "jira", "linear", "slack"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["results"]["calendar"]["status"], "skipped")
        self.assertEqual(result["results"]["email"]["status"], "skipped")
        self.assertEqual(result["results"]["jira"]["status"], "skipped")
        self.assertEqual(result["results"]["linear"]["status"], "skipped")
        self.assertEqual(result["results"]["slack"]["status"], "skipped")

    async def test_trigger_full_sync_runs_selected_system_when_credentials_exist(self) -> None:
        svc = DevModeToolSyncService()

        async def _cred(provider: str):
            if provider == "jira":
                return {"token": "x"}
            return None

        svc.oauth_manager.get_credentials = AsyncMock(side_effect=_cred)
        svc.sync_jira = AsyncMock(return_value={"status": "success", "provider": "jira"})

        result = await svc.trigger_full_sync(["jira"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["results"]["jira"]["status"], "success")
        svc.sync_jira.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
