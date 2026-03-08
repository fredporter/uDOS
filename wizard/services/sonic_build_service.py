"""Sonic Stick build service for Wizard platform routes."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.external_repo_service import ensure_sonic_python_paths, resolve_sonic_repo_root
from core.services.hash_utils import sha256_file
from core.services.json_utils import read_json_file
from core.services.packaging_build_metadata_service import (
    resolve_release_version,
    resolve_sonic_builds_root,
)
from core.services.packaging_manifest_service import load_packaging_manifest
from core.services.template_workspace_service import get_template_workspace_service
class SonicBuildService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.packaging_manifest = load_packaging_manifest(self.repo_root)
        platforms_linux = ((self.packaging_manifest.get("platforms") or {}).get("linux") or {})
        sonic_stick = dict(platforms_linux.get("app_bundle") or {})
        manifest_default_profile = str(
            sonic_stick.get("default_profile") or "alpine-core+sonic"
        )
        workspace_default_profile = self._workspace_default_profile()
        self.default_profile = workspace_default_profile or manifest_default_profile
        self.default_profile_source = (
            "template_workspace" if workspace_default_profile else "packaging_manifest"
        )
        self.sonic_root = resolve_sonic_repo_root(self.repo_root)
        self.build_script = self.sonic_root / str(
            sonic_stick.get("build_script") or "distribution/alpine-core/build-sonic-stick.sh"
        )
        self.builds_root = resolve_sonic_builds_root(self.repo_root)
        try:
            self.release_version = resolve_release_version(self.repo_root)
        except Exception:
            self.release_version = "unknown"

    def _workspace_default_profile(self) -> str | None:
        try:
            fields = get_template_workspace_service(self.repo_root).read_fields(
                "settings", "sonic"
            )
        except Exception:
            return None
        value = str(fields.get("preferred_profile") or "").strip()
        return value or None

    def _load_manifest(self, build_dir: Path) -> Dict[str, Any]:
        manifest_path = build_dir / "build-manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Build manifest not found: {manifest_path}")
        return read_json_file(manifest_path, default={})

    @staticmethod
    def _sha256(path: Path) -> str:
        return sha256_file(path)

    @staticmethod
    def _verify_detached_signature(payload_path: Path, signature_path: Path) -> Dict[str, Any]:
        ensure_sonic_python_paths()
        from installers.usb.verify import verify_detached_signature

        return verify_detached_signature(payload_path, signature_path)

    def start_build(
        self,
        profile: Optional[str] = None,
        build_id: Optional[str] = None,
        source_image: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.build_script.exists():
            raise FileNotFoundError(f"Build script not found: {self.build_script}")

        resolved_profile = profile or self.default_profile
        cmd = [str(self.build_script), "--profile", resolved_profile]
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

        build_dir = Path(output_dir).resolve() if output_dir else self._infer_build_dir(resolved_profile, build_id)
        manifest = self._load_manifest(build_dir)

        return {
            "success": True,
            "build_id": manifest.get("build_id"),
            "build_dir": str(build_dir),
            "profile": manifest.get("profile"),
            "version": manifest.get("version") or self.release_version,
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
                manifest = read_json_file(manifest_path, default={})
            except Exception:
                continue
            entries.append(
                {
                    "build_id": manifest.get("build_id") or build_dir.name,
                    "created_at": manifest.get("created_at"),
                    "profile": manifest.get("profile"),
                    "version": manifest.get("version") or self.release_version,
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

    def get_release_readiness(self, build_id: str) -> Dict[str, Any]:
        build_dir = self.builds_root / build_id
        if not build_dir.exists():
            raise FileNotFoundError(f"Build not found: {build_id}")
        ensure_sonic_python_paths(self.repo_root)
        from installers.usb.verify import verify_release_bundle

        return verify_release_bundle(build_dir, pubkey=os.environ.get("WIZARD_SONIC_SIGN_PUBKEY", "").strip() or None)


_sonic_build_service: Optional[SonicBuildService] = None


def get_sonic_build_service(repo_root: Optional[Path] = None) -> SonicBuildService:
    global _sonic_build_service
    if repo_root is not None:
        return SonicBuildService(repo_root=repo_root)
    if _sonic_build_service is None:
        _sonic_build_service = SonicBuildService(repo_root=repo_root)
    return _sonic_build_service
