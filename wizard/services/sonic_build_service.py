"""Sonic Stick build service for Wizard platform routes."""

from __future__ import annotations

import json
import subprocess
import hashlib
import os
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

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _verify_detached_signature(payload_path: Path, signature_path: Path) -> Dict[str, Any]:
        if not payload_path.exists():
            return {"present": signature_path.exists(), "verified": False, "detail": "payload missing"}
        if not signature_path.exists():
            return {"present": False, "verified": False, "detail": "signature missing"}

        pubkey = os.environ.get("WIZARD_SONIC_SIGN_PUBKEY", "").strip()
        if not pubkey:
            return {
                "present": True,
                "verified": False,
                "detail": "WIZARD_SONIC_SIGN_PUBKEY not configured",
            }
        pubkey_path = Path(pubkey)
        if not pubkey_path.exists():
            return {
                "present": True,
                "verified": False,
                "detail": f"public key not found: {pubkey_path}",
            }

        verify = subprocess.run(
            [
                "openssl",
                "dgst",
                "-sha256",
                "-verify",
                str(pubkey_path),
                "-signature",
                str(signature_path),
                str(payload_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if verify.returncode == 0:
            return {"present": True, "verified": True, "detail": "signature verified via openssl"}
        detail = (verify.stderr or verify.stdout or "openssl verify failed").strip()
        return {"present": True, "verified": False, "detail": detail}

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

    def get_release_readiness(self, build_id: str) -> Dict[str, Any]:
        build_dir = self.builds_root / build_id
        if not build_dir.exists():
            raise FileNotFoundError(f"Build not found: {build_id}")

        manifest = self._load_manifest(build_dir)
        checksums_path = build_dir / "checksums.txt"
        manifest_sig_path = build_dir / "build-manifest.json.sig"
        checksums_sig_path = build_dir / "checksums.txt.sig"

        issues: List[str] = []
        artifacts_status: List[Dict[str, Any]] = []
        for entry in manifest.get("artifacts") or []:
            rel_path = entry.get("path")
            if not rel_path:
                continue
            artifact_path = build_dir / rel_path
            exists = artifact_path.exists()
            expected_sha = entry.get("sha256")
            actual_sha = self._sha256(artifact_path) if exists else None
            sha_match = bool(exists and expected_sha and actual_sha == expected_sha)
            if not exists:
                issues.append(f"artifact missing: {rel_path}")
            elif expected_sha and not sha_match:
                issues.append(f"artifact checksum mismatch: {rel_path}")

            artifacts_status.append(
                {
                    "path": rel_path,
                    "exists": exists,
                    "expected_sha256": expected_sha,
                    "actual_sha256": actual_sha,
                    "checksum_match": sha_match,
                }
            )

        checksum_file_verified = False
        checksum_entries_checked = 0
        if not checksums_path.exists():
            issues.append("checksums.txt missing")
        else:
            checksum_rows = [
                line.strip()
                for line in checksums_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            checksum_file_verified = True
            for line in checksum_rows:
                try:
                    expected, name = line.split(None, 1)
                    name = name.strip()
                    if name.startswith("*") or name.startswith(" "):
                        name = name.lstrip("* ").strip()
                except ValueError:
                    checksum_file_verified = False
                    issues.append(f"invalid checksum row: {line}")
                    continue
                checksum_entries_checked += 1
                target = build_dir / name
                if not target.exists():
                    checksum_file_verified = False
                    issues.append(f"checksum target missing: {name}")
                    continue
                actual = self._sha256(target)
                if actual != expected:
                    checksum_file_verified = False
                    issues.append(f"checksum mismatch: {name}")

        signing = {
            "manifest": self._verify_detached_signature(build_dir / "build-manifest.json", manifest_sig_path),
            "checksums": self._verify_detached_signature(checksums_path, checksums_sig_path),
        }
        signing["manifest_signature_present"] = signing["manifest"]["present"]
        signing["checksums_signature_present"] = signing["checksums"]["present"]
        signing["manifest_signature_verified"] = signing["manifest"]["verified"]
        signing["checksums_signature_verified"] = signing["checksums"]["verified"]
        signing["ready"] = (
            signing["manifest_signature_verified"] and signing["checksums_signature_verified"]
        )
        if not signing["ready"]:
            issues.append("release signatures incomplete")

        release_ready = checksum_file_verified and signing["ready"] and not issues
        return {
            "build_id": manifest.get("build_id") or build_id,
            "release_ready": release_ready,
            "checksums": {
                "path": str(checksums_path),
                "present": checksums_path.exists(),
                "verified": checksum_file_verified,
                "entries_checked": checksum_entries_checked,
            },
            "signing": signing,
            "artifacts": artifacts_status,
            "issues": issues,
        }


_sonic_build_service: Optional[SonicBuildService] = None


def get_sonic_build_service(repo_root: Optional[Path] = None) -> SonicBuildService:
    global _sonic_build_service
    if repo_root is not None:
        return SonicBuildService(repo_root=repo_root)
    if _sonic_build_service is None:
        _sonic_build_service = SonicBuildService(repo_root=repo_root)
    return _sonic_build_service
