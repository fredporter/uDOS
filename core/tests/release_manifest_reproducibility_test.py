"""Release manifest/signing/checksum consistency and reproducibility checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from wizard.services.sonic_build_service import SonicBuildService


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_fixture_build(build_dir: Path) -> None:
    artifact_data = b"artifact-bytes"
    artifact_name = "sonic-stick.img"
    artifact_path = build_dir / artifact_name
    artifact_path.write_bytes(artifact_data)
    artifact_sha = _sha256_bytes(artifact_data)

    manifest_payload = {
        "schema": "udos.sonic-stick.build-manifest.v1",
        "build_id": build_dir.name,
        "created_at": "2026-02-22T00:00:00Z",
        "profile": "alpine-core+sonic",
        "version": "v1.4.4",
        "repository": {"root_sha": "abc123", "sonic_sha": "def456"},
        "artifacts": [
            {
                "name": artifact_name,
                "path": artifact_name,
                "size_bytes": len(artifact_data),
                "sha256": artifact_sha,
            }
        ],
    }
    manifest_path = build_dir / "build-manifest.json"
    manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    (build_dir / "checksums.txt").write_text(
        f"{artifact_sha}  {artifact_name}\n{manifest_sha}  build-manifest.json\n",
        encoding="utf-8",
    )
    (build_dir / "build-manifest.json.sig").write_text("sig", encoding="utf-8")
    (build_dir / "checksums.txt.sig").write_text("sig", encoding="utf-8")


def test_release_readiness_is_reproducible_for_identical_artifacts(tmp_path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    build_dir = repo_root / "distribution" / "builds" / "fixture-build"
    build_dir.mkdir(parents=True)
    _write_fixture_build(build_dir)

    monkeypatch.setattr(
        SonicBuildService,
        "_verify_detached_signature",
        staticmethod(lambda _payload, _sig: {"present": True, "verified": True, "detail": "test"}),
    )
    service = SonicBuildService(repo_root=repo_root)

    first = service.get_release_readiness("fixture-build")
    second = service.get_release_readiness("fixture-build")

    assert first["release_ready"] == second["release_ready"]
    assert first["checksums"] == second["checksums"]
    assert first["signing"] == second["signing"]
    assert first["artifacts"] == second["artifacts"]
    assert first["issues"] == second["issues"]
