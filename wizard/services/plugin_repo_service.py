"""Filesystem-backed plugin repository service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class PluginRepoService:
    """Provide plugin listing/info/download data from distribution/plugins."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.repo_path.mkdir(parents=True, exist_ok=True)

    def list_plugins(self) -> Dict[str, Any]:
        plugins: List[Dict[str, Any]] = []

        if self.repo_path.exists():
            for item in self.repo_path.iterdir():
                if item.is_dir():
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        plugins.append(
                            {
                                "id": item.name,
                                "name": manifest.get("name", item.name),
                                "version": manifest.get("version", "0.0.0"),
                                "description": manifest.get("description", ""),
                            }
                        )

        return {"plugins": plugins, "count": len(plugins)}

    def get_plugin_info(self, plugin_id: str) -> Dict[str, Any]:
        from fastapi import HTTPException

        if not plugin_id or "/" in plugin_id or ".." in plugin_id:
            raise HTTPException(status_code=400, detail="Invalid plugin ID")

        plugin_path = self.repo_path / plugin_id

        if not plugin_path.exists():
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(
                status_code=404, detail=f"No manifest for plugin: {plugin_id}"
            )

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        packages = list(plugin_path.glob("*.tar.gz")) + list(plugin_path.glob("*.tcz"))
        package_info = None
        if packages:
            pkg = packages[0]
            package_info = {
                "filename": pkg.name,
                "size": pkg.stat().st_size,
            }

        return {
            "id": plugin_id,
            "manifest": manifest,
            "package": package_info,
        }

    def get_download_info(self, plugin_id: str) -> Dict[str, Any]:
        from fastapi import HTTPException

        if not plugin_id or "/" in plugin_id or ".." in plugin_id:
            raise HTTPException(status_code=400, detail="Invalid plugin ID")

        plugin_path = self.repo_path / plugin_id

        if not plugin_path.exists():
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

        packages = list(plugin_path.glob("*.tar.gz")) + list(plugin_path.glob("*.tcz"))
        if not packages:
            raise HTTPException(
                status_code=404, detail=f"No downloadable package for: {plugin_id}"
            )

        pkg = packages[0]

        return {
            "plugin_id": plugin_id,
            "filename": pkg.name,
            "size": pkg.stat().st_size,
            "download_method": "qr_relay",
            "message": "Use QR RECEIVE on device to download",
        }
