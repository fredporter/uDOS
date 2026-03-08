"""Linux packaging adapter executor."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.services.external_repo_service import resolve_sonic_repo_root
from core.services.hash_utils import sha256_file
from core.services.packaging_adapters.manifest_reader import read_platform
from core.services.packaging_build_metadata_service import (
    resolve_build_id,
    resolve_release_version,
    resolve_sonic_artifact_basename,
    resolve_sonic_builds_root,
)


def _manifest_linux(repo_root: Path) -> dict[str, Any]:
    return read_platform(repo_root, "linux")


def sonic_default_profile(repo_root: Path) -> str:
    linux = _manifest_linux(repo_root)
    app_bundle = linux.get("app_bundle")
    if not isinstance(app_bundle, dict) or not isinstance(app_bundle.get("default_profile"), str):
        raise ValueError("linux.app_bundle.default_profile is required")
    return app_bundle["default_profile"]


def _git_sha(path: Path) -> str:
    proc = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return "missing"
    return proc.stdout.strip() or "missing"


def _write_seed_image(path: Path, *, profile: str, build_id: str, root_sha: str, sonic_sha: str) -> None:
    seed = "\n".join(
        [
            "uDOS Sonic Stick deterministic image",
            f"profile={profile}",
            f"build_id={build_id}",
            f"root_sha={root_sha}",
            f"sonic_sha={sonic_sha}",
        ]
    ) + "\n"
    seed_bytes = seed.encode("utf-8")
    out = bytearray(1024 * 1024)
    for offset in range(0, len(out), len(seed_bytes)):
        chunk = seed_bytes[: min(len(seed_bytes), len(out) - offset)]
        out[offset : offset + len(chunk)] = chunk
    path.write_bytes(out)


def build_sonic_stick(
    repo_root: Path,
    *,
    profile: str | None = None,
    build_id: str | None = None,
    source_image: str | None = None,
    output_dir: str | None = None,
    sign_key: str | None = None,
) -> dict[str, Any]:
    profile = profile or sonic_default_profile(repo_root)
    build_id = resolve_build_id(repo_root, explicit=build_id)

    builds_root = resolve_sonic_builds_root(repo_root)
    out_dir = Path(output_dir) if output_dir else (builds_root / build_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    version = resolve_release_version(repo_root)
    root_sha = _git_sha(repo_root)
    sonic_repo = resolve_sonic_repo_root(repo_root)
    sonic_sha = _git_sha(sonic_repo) if sonic_repo.exists() else "missing"
    basename = resolve_sonic_artifact_basename(repo_root, build_id=build_id, version=version)
    img_name = f"{basename}.img"
    iso_name = f"{basename}.iso"
    img_path = out_dir / img_name
    iso_path = out_dir / iso_name
    manifest_path = out_dir / "build-manifest.json"
    checksums_path = out_dir / "checksums.txt"

    if source_image:
        source_path = Path(source_image)
        if not source_path.is_absolute():
            source_path = (repo_root / source_path).resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")
        img_path.write_bytes(source_path.read_bytes())
    else:
        _write_seed_image(img_path, profile=profile, build_id=build_id, root_sha=root_sha, sonic_sha=sonic_sha)

    iso_path.write_bytes(img_path.read_bytes())

    artifacts = []
    for artifact in (img_path, iso_path):
        artifacts.append(
            {
                "name": artifact.name,
                "path": artifact.name,
                "kind": artifact.suffix.lstrip("."),
                "size_bytes": artifact.stat().st_size,
                "sha256": sha256_file(artifact),
            }
        )

    manifest_payload = {
        "schema": "udos.sonic-stick.build-manifest.v1",
        "build_id": build_id,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "profile": profile,
        "version": version,
        "repository": {"root_sha": root_sha, "sonic_sha": sonic_sha},
        "artifacts": artifacts,
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksum_rows: list[str] = []
    for item in (img_path, iso_path, manifest_path):
        checksum_rows.append(f"{sha256_file(item)}  {item.name}")
    checksums_path.write_text("\n".join(checksum_rows) + "\n", encoding="utf-8")

    if sign_key:
        key_path = Path(sign_key)
        if not key_path.exists():
            raise FileNotFoundError(f"Signing key not found: {key_path}")
        subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(key_path), "-out", str(manifest_path) + ".sig", str(manifest_path)],
            check=True,
        )
        subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(key_path), "-out", str(checksums_path) + ".sig", str(checksums_path)],
            check=True,
        )

    return {
        "status": "ok",
        "output_dir": str(out_dir),
        "profile": profile,
        "build_id": build_id,
        "root_sha": root_sha,
        "sonic_sha": sonic_sha,
        "manifest": str(manifest_path),
        "checksums": str(checksums_path),
    }
