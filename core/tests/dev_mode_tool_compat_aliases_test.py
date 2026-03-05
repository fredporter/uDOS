"""Alias stability coverage for Dev Mode compatibility services."""

from core.services.dev_mode_compat import DevModeToolSyncService, DevModeToolVaultService
from core.services.vibe_sync_service import VibeSyncService
from core.services.vibe_vault_service import VibeVaultService


def test_canonical_sync_service_alias_is_stable() -> None:
    assert DevModeToolSyncService is VibeSyncService


def test_canonical_vault_service_alias_is_stable() -> None:
    assert DevModeToolVaultService is VibeVaultService
