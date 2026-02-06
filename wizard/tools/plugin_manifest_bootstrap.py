#!/usr/bin/env python3
"""Generate minimal manifest.json files from container.json for library plugins."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_ROOT = REPO_ROOT / "library"
DEFAULT_RUNTIME = ">=1.3.0"


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _build_manifest(container: Dict[str, Any]) -> Dict[str, Any]:
    meta = container.get("metadata") or {}
    integration = container.get("integration") or {}
    sysreq = container.get("system_requirements") or {}
    container_info = container.get("container") or {}

    plugin_id = container_info.get("id") or meta.get("id") or "unknown"
    name = container_info.get("name") or meta.get("name") or plugin_id
    version = container_info.get("version") or meta.get("version") or "0.0.0"
    description = container_info.get("description") or meta.get("description") or ""
    license_name = meta.get("license") or "MIT"
    maintainer = meta.get("maintainer") or "uDOS"
    homepage = meta.get("homepage")
    repository = container_info.get("source")

    main = integration.get("wrapper_path") or integration.get("service_path") or "container.json"

    platforms = sysreq.get("platforms") or ["any"]

    manifest = {
        "id": plugin_id,
        "name": name,
        "version": version,
        "description": description,
        "author": {"name": maintainer},
        "homepage": homepage,
        "repository": repository,
        "license": license_name,
        "main": main,
        "type": "container",
        "runtime": {
            "requires": DEFAULT_RUNTIME,
            "platform": platforms,
        },
        "permissions": {
            "filesystem": {"read": [], "write": []},
            "network": {"allowed": False, "domains": []},
            "ai": {"models": [], "max_tokens": 0},
        },
        "dependencies": {"containers": [], "plugins": []},
        "signature": {
            "algorithm": "UNSIGNED",
            "publicKey": "",
            "signature": "",
        },
    }

    return manifest


def main() -> int:
    if not LIB_ROOT.exists():
        print("library/ not found")
        return 1

    updated = 0
    for container_path in LIB_ROOT.rglob("container.json"):
        data = _load_json(container_path)
        manifest_path = container_path.parent / "manifest.json"
        if manifest_path.exists():
            continue
        manifest = _build_manifest(data)
        _write_json(manifest_path, manifest)
        updated += 1
        print(f"Created {manifest_path}")

    print(f"Generated manifests: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
