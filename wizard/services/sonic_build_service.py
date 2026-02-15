"""Sonic Stick build service for Wizard platform routes."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class SonicBuildService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.build_script = self.repo_root / "distribution" / "alpine-core" / "build-sonic-stick.sh"
        self.builds_root = self.repo_root / "distribution" / "builds"

    def _load_manifest(self, build_dir: Path) -> Dict[str, Any]:
        manifest_path = build_dir / "build-manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Build manifest not found: {manifest_path}")
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    def start_build(
        self,
        profile: str = "alpine-core+sonic",
        build_id: Optional[str] = None,
        source_image: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.build_script.exists():
            raise FileNotFoundError(f"Build script not found: {self.build_script}")

        cmd = [str(self.build_script), "--profile", profile]
        if build_id:
            cmd.extend(["--build-id", build_id])
        if source_image:
            cmd.extend(["--source-image", source_image])
        if output_dir:
            cmd.extend(["--output-dir", output_dir])

        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "build failed").strip()
            raise RuntimeError(detail)

        build_dir = Path(output_dir).resolve() if output_dir else self._infer_build_dir(profile, build_id)
        manifest = self._load_manifest(build_dir)

        return {
            "success": True,
            "build_id": manifest.get("build_id"),
            "build_dir": str(build_dir),
            "profile": manifest.get("profile"),
            "manifest": manifest,
            "logs": proc.stdout.strip().splitlines(),
        }

    def _infer_build_dir(self, profile: str, build_id: Optional[str]) -> Path:
        # If caller provided build_id, use direct path.
        if build_id:
            candidate = self.builds_root / build_id
            if candidate.exists():
                return candidate

        candidates = [
            item
            for item in self.builds_root.iterdir()
            if item.is_dir() and (item / "build-manifest.json").exists()
        ] if self.builds_root.exists() else []

        if not candidates:
            raise FileNotFoundError("No Sonic build directories found")

        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0]

    def list_builds(self, limit: int = 50) -> Dict[str, Any]:
        if not self.builds_root.exists():
            return {"count": 0, "builds": []}

        entries: List[Dict[str, Any]] = []
        for build_dir in sorted(self.builds_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not build_dir.is_dir():
                continue
            manifest_path = build_dir / "build-manifest.json"
            if not manifest_path.exists():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            entries.append(
                {
                    "build_id": manifest.get("build_id") or build_dir.name,
                    "created_at": manifest.get("created_at"),
                    "profile": manifest.get("profile"),
                    "version": manifest.get("version"),
                    "root_sha": (manifest.get("repository") or {}).get("root_sha"),
                    "sonic_sha": (manifest.get("repository") or {}).get("sonic_sha"),
                    "artifact_count": len(manifest.get("artifacts") or []),
                }
            )

        capped = entries[: max(1, min(limit, 500))]
        return {"count": len(capped), "total_found": len(entries), "builds": capped}

    def get_build(self, build_id: str) -> Dict[str, Any]:
        build_dir = self.builds_root / build_id
        if not build_dir.exists():
            raise FileNotFoundError(f"Build not found: {build_id}")
        manifest = self._load_manifest(build_dir)
        return {
            "build_id": manifest.get("build_id") or build_id,
            "build_dir": str(build_dir),
            "manifest": manifest,
        }

    def get_build_artifacts(self, build_id: str) -> Dict[str, Any]:
        build_dir = self.builds_root / build_id
        if not build_dir.exists():
            raise FileNotFoundError(f"Build not found: {build_id}")
        manifest = self._load_manifest(build_dir)
        artifacts = []
        for entry in manifest.get("artifacts") or []:
            rel = entry.get("path")
            if not rel:
                continue
            path = build_dir / rel
            artifacts.append(
                {
                    "name": entry.get("name") or path.name,
                    "path": rel,
                    "exists": path.exists(),
                    "size_bytes": entry.get("size_bytes"),
                    "sha256": entry.get("sha256"),
                }
            )

        return {
            "build_id": manifest.get("build_id") or build_id,
            "artifacts": artifacts,
            "checksums": str(build_dir / "checksums.txt"),
            "manifest": str(build_dir / "build-manifest.json"),
        }


_sonic_build_service: Optional[SonicBuildService] = None


def get_sonic_build_service(repo_root: Optional[Path] = None) -> SonicBuildService:
    global _sonic_build_service
    if repo_root is not None:
        return SonicBuildService(repo_root=repo_root)
    if _sonic_build_service is None:
        _sonic_build_service = SonicBuildService(repo_root=repo_root)
    return _sonic_build_service
