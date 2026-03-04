"""Centralized path helpers for uDOS.

Use these helpers instead of hand-building paths across the codebase.
All paths resolve from UDOS_ROOT (or repo root fallback).
"""

from __future__ import annotations

from pathlib import Path

from core.services.logging_api import get_repo_root
from core.services.unified_config_loader import get_path_config


def get_udos_root() -> Path:
    """Return UDOS repository root."""
    return get_path_config("UDOS_ROOT") or get_repo_root()


def get_memory_root() -> Path:
    """Return UDOS memory root."""
    return (get_path_config("UDOS_MEMORY_ROOT") or (get_udos_root() / "memory")).resolve()


def get_vault_root() -> Path:
    """Return vault root (VAULT_ROOT or memory/vault)."""
    return (get_path_config("VAULT_ROOT") or (get_memory_root() / "vault")).resolve()


def get_vault_md_root() -> Path:
    """Return vault markdown root (VAULT_MD_ROOT or VAULT_ROOT)."""
    return (get_path_config("VAULT_MD_ROOT") or get_vault_root()).resolve()


def get_wizard_config_dir() -> Path:
    """Return Wizard config directory."""
    return get_udos_root() / "wizard" / "config"


def get_core_config_dir() -> Path:
    """Return core config directory."""
    return get_udos_root() / "core" / "config"


def get_private_memory_dir() -> Path:
    """Return private memory directory for sensitive files."""
    return (get_memory_root() / "private").resolve()
