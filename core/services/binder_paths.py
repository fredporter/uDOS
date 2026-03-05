"""Canonical binder path helpers for per-binder sandbox layout."""

from __future__ import annotations

from pathlib import Path

from core.services.paths import get_vault_root


def get_binders_root() -> Path:
    """Return the @binders root under VAULT_ROOT."""
    root = (get_vault_root() / "@binders").resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_binder_root(binder_id: str) -> Path:
    """Return the canonical root path for a binder."""
    return (get_binders_root() / binder_id).resolve()


def get_binder_sandbox_root(binder_id: str) -> Path:
    """Return binder-local sandbox/ path."""
    path = (get_binder_root(binder_id) / "sandbox").resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_binder_compost_root(binder_id: str) -> Path:
    """Return binder-local .compost/ path."""
    path = (get_binder_root(binder_id) / ".compost").resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path
