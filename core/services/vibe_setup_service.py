"""Vibe Setup Service

Initializes uDOS configuration, including VAULT_ROOT in .env
Ensures all required environment variables are set for Vibe operations.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv, set_key

from core.services.logging_manager import get_logger
from core.services.paths import get_memory_root, get_vault_root
from core.services.path_service import get_repo_root
from core.services.unified_config_loader import get_config

_logger = get_logger(__name__)
_setup_service_instance = None


class VipeSetupService:
    """Handles uDOS initialization and configuration setup.
    Ensures VAULT_ROOT and other critical environment variables are set.
    """

    def __init__(self):
        """Initialize setup service."""
        self.logger = get_logger("vibe-setup-service")
        self.repo_root = get_repo_root()
        self.env_file = self.repo_root / ".env"

    def ensure_vault_root(self, vault_path: str | None = None) -> dict[str, Any]:
        """Ensure VAULT_ROOT is set in .env.

        Args:
            vault_path: Optional custom vault path. If not provided, uses default.

        Returns:
            Dict with status and vault root path
        """
        if vault_path is None:
            vault_path = str(get_vault_root())

        vault_root = Path(vault_path)
        vault_root.mkdir(parents=True, exist_ok=True)

        # Load existing .env
        load_dotenv(self.env_file)

        current_vault_root = get_config("VAULT_ROOT", "")

        if current_vault_root and current_vault_root == vault_path:
            self.logger.info(f"VAULT_ROOT already set: {vault_path}")
            return {
                "status": "success",
                "message": "VAULT_ROOT already configured",
                "vault_root": vault_path,
                "already_set": True,
            }

        # Set VAULT_ROOT in .env
        try:
            set_key(str(self.env_file), "VAULT_ROOT", vault_path)
            import os

            os.environ["VAULT_ROOT"] = vault_path
            self.logger.info(f"Set VAULT_ROOT in .env: {vault_path}")

            return {
                "status": "success",
                "message": "VAULT_ROOT configured in .env",
                "vault_root": vault_path,
                "already_set": False,
            }
        except Exception as e:
            self.logger.error(f"Failed to set VAULT_ROOT: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to configure VAULT_ROOT: {e}",
                "vault_root": None,
            }

    def ensure_binder_structure(self) -> dict[str, Any]:
        """Ensure vault/@binders/ directory structure exists.

        Returns:
            Dict with status and binder root path
        """
        vault_root = get_config("VAULT_ROOT", str(get_vault_root()))
        binder_root = Path(vault_root) / "@binders"

        try:
            binder_root.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Ensured binder structure: {binder_root}")

            return {
                "status": "success",
                "message": "Binder structure ready",
                "binder_root": str(binder_root),
            }
        except Exception as e:
            self.logger.error(f"Failed to create binder structure: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to ensure binder structure: {e}",
                "binder_root": None,
            }

    def initialize_uDOS(self, vault_path: str | None = None) -> dict[str, Any]:
        """Complete uDOS initialization.
        Sets up VAULT_ROOT and binder structure.

        Args:
            vault_path: Optional custom vault path

        Returns:
            Dict with initialization status
        """
        self.logger.info("Starting uDOS initialization...")

        # Ensure VAULT_ROOT
        vault_result = self.ensure_vault_root(vault_path)
        if vault_result["status"] == "error":
            return {
                "status": "error",
                "message": "Failed to initialize uDOS - VAULT_ROOT setup failed",
                "details": vault_result,
            }

        # Ensure binder structure
        binder_result = self.ensure_binder_structure()
        if binder_result["status"] == "error":
            return {
                "status": "error",
                "message": "Failed to initialize uDOS - binder structure failed",
                "details": binder_result,
            }

        self.logger.info("uDOS initialization complete")

        return {
            "status": "success",
            "message": "uDOS initialized successfully",
            "vault_root": vault_result.get("vault_root"),
            "binder_root": binder_result.get("binder_root"),
            "memory_root": str(get_memory_root()),
        }


def get_setup_service() -> VipeSetupService:
    """Returns the singleton instance of the SetupService.
    """
    global _setup_service_instance
    if _setup_service_instance is None:
        _setup_service_instance = VipeSetupService()
    return _setup_service_instance
