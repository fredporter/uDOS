"""
Plugin manifest helpers
-----------------------

Centralizes manifest loading, checksum, and validation so every Wizard UI and
CLI flow shares the same expectations before handing a plugin off to
LibraryManagerService.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_manifest(plugin_path: Path) -> Dict[str, Any]:
    """Read manifest.json from a plugin directory."""
    manifest_path = plugin_path / "manifest.json"
    if not manifest_path.exists():
        return {}

    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    except Exception:
        return {}


def compute_manifest_checksum(manifest_path: Path) -> Optional[str]:
    """Return sha256 checksum for the manifest file if present."""
    if not manifest_path.exists():
        return None

    try:
        hasher = hashlib.sha256()
        with manifest_path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def validate_manifest(
    manifest: Dict[str, Any],
    plugin_id: str,
    repo_entry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Validate manifest metadata against expectations.

    Returns a dict with `valid`, `message`, and `issues`.
    """
    issues = []

    if not manifest:
        issues.append("Manifest missing")
        return {"valid": False, "message": "Manifest missing", "issues": issues}

    # Basic sanity checks
    if manifest.get("id") and manifest["id"] != plugin_id:
        issues.append(f"id mismatch ({manifest['id']} != {plugin_id})")

    for key in ("name", "version", "license", "author"):
        if not manifest.get(key):
            issues.append(f"missing {key}")

    if repo_entry:
        repo_version = repo_entry.get("version")
        manifest_version = manifest.get("version")
        if repo_version and manifest_version and repo_version != manifest_version:
            issues.append("Catalog version mismatch")

        repo_checksum = repo_entry.get("checksum")
        manifest_checksum = manifest.get("checksum")
        if repo_checksum and manifest_checksum and repo_checksum != manifest_checksum:
            issues.append("Checksum mismatch with catalog")

    return {
        "valid": not issues,
        "message": " | ".join(issues) if issues else "Manifest validated",
        "issues": issues,
    }
