"""Vault-MD validator for TUI startup.

Warns if VAULT_MD_ROOT is missing or expected folders are absent.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple


DEFAULT_VAULT_MD = Path.home() / "Documents" / "uDOS Vault"
REQUIRED_DIRS = [
    "bank",
    "inbox-dropbox",
    "sandbox",
    "public-open-published",
    "private-explicit",
    "private-shared",
    "05_DATA/sqlite",
    "_site",
    "06_RUNS",
    "07_LOGS",
    "01_KNOWLEDGE",
]


def ensure_vault_md_env() -> Path:
    """Ensure VAULT_MD_ROOT is set; returns resolved path."""
    env_root = os.getenv("VAULT_MD_ROOT") or os.getenv("VAULT_ROOT")
    if not env_root:
        os.environ["VAULT_MD_ROOT"] = str(DEFAULT_VAULT_MD)
        # Keep compatibility for any remaining VAULT_ROOT readers
        os.environ.setdefault("VAULT_ROOT", str(DEFAULT_VAULT_MD))
        return DEFAULT_VAULT_MD

    path = Path(env_root).expanduser()
    os.environ["VAULT_MD_ROOT"] = str(path)
    os.environ.setdefault("VAULT_ROOT", str(path))
    return path


def validate_vault_md() -> Tuple[Path, List[str]]:
    """Return vault path and list of warning strings."""
    warnings: List[str] = []
    vault_root = ensure_vault_md_env()

    if not vault_root.exists():
        warnings.append(
            f"vault-md path not found: {vault_root} (set VAULT_MD_ROOT in .env)"
        )
        return vault_root, warnings

    missing = [
        folder for folder in REQUIRED_DIRS if not (vault_root / folder).exists()
    ]
    if missing:
        warnings.append(
            "vault-md is missing folders: " + ", ".join(missing)
        )
        warnings.append(
            "Create missing folders or run setup to scaffold vault-md."
        )

    return vault_root, warnings
