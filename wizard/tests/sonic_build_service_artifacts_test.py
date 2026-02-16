import json
import hashlib
from pathlib import Path

from wizard.services.sonic_build_service import SonicBuildService



def _write_manifest(build_dir: Path, artifacts):
    payload = {
        "schema": "udos.sonic-stick.build-manifest.v1",
        "build_id": build_dir.name,
        "created_at": "2026-02-15T00:00:00Z",
        "profile": "alpine-core+sonic",
        "version": "v1.3.17",
        "repository": {"root_sha": "abc", "sonic_sha": "def"},
        "artifacts": artifacts,
    }
    (build_dir / "build-manifest.json").write_text(json.dumps(payload), encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()



def test_get_build_artifacts_reads_manifest_and_file_presence(tmp_path):
    repo = tmp_path / "repo"
    build_dir = repo / "distribution" / "builds" / "b1"
    build_dir.mkdir(parents=True)

    present_file = build_dir / "sonic-stick.img"
    present_file.write_bytes(b"img")

    _write_manifest(
        build_dir,
        [
            {
                "name": "sonic-stick.img",
                "path": "sonic-stick.img",
                "size_bytes": 3,
                "sha256": "x",
            },
            {
                "name": "sonic-stick.iso",
                "path": "sonic-stick.iso",
                "size_bytes": 10,
                "sha256": "y",
            },
        ],
    )

    svc = SonicBuildService(repo_root=repo)
    result = svc.get_build_artifacts("b1")

    assert result["build_id"] == "b1"
    by_name = {a["name"]: a for a in result["artifacts"]}

    assert by_name["sonic-stick.img"]["exists"] is True
    assert by_name["sonic-stick.img"]["size_bytes"] == 3
    assert by_name["sonic-stick.iso"]["exists"] is False
    assert by_name["sonic-stick.iso"]["size_bytes"] == 10

    assert result["checksums"].endswith("/distribution/builds/b1/checksums.txt")
    assert result["manifest"].endswith("/distribution/builds/b1/build-manifest.json")



def test_get_build_artifacts_raises_when_build_missing(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    svc = SonicBuildService(repo_root=repo)

    try:
        svc.get_build_artifacts("nope")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as exc:
        assert "Build not found" in str(exc)


def test_release_readiness_reports_ready_when_checksums_and_signatures_match(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    build_dir = repo / "distribution" / "builds" / "b2"
    build_dir.mkdir(parents=True)

    img_data = b"img-bytes"
    iso_data = b"iso-bytes"
    manifest_data = b'{"hello":"world"}'
    img_sha = _sha256_bytes(img_data)
    iso_sha = _sha256_bytes(iso_data)

    (build_dir / "sonic-stick.img").write_bytes(img_data)
    (build_dir / "sonic-stick.iso").write_bytes(iso_data)
    (build_dir / "build-manifest.json").write_bytes(manifest_data)
    (build_dir / "checksums.txt").write_text(
        "\n".join(
            [
                f"{img_sha}  sonic-stick.img",
                f"{iso_sha}  sonic-stick.iso",
                f"{_sha256_bytes(manifest_data)}  build-manifest.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (build_dir / "build-manifest.json.sig").write_text("sig", encoding="utf-8")
    (build_dir / "checksums.txt.sig").write_text("sig", encoding="utf-8")

    # Overwrite manifest with correct artifact hashes expected by readiness.
    _write_manifest(
        build_dir,
        [
            {"name": "sonic-stick.img", "path": "sonic-stick.img", "size_bytes": len(img_data), "sha256": img_sha},
            {"name": "sonic-stick.iso", "path": "sonic-stick.iso", "size_bytes": len(iso_data), "sha256": iso_sha},
        ],
    )
    # Recompute manifest checksum after overwrite.
    manifest_sha = hashlib.sha256((build_dir / "build-manifest.json").read_bytes()).hexdigest()
    (build_dir / "checksums.txt").write_text(
        "\n".join(
            [
                f"{img_sha}  sonic-stick.img",
                f"{iso_sha}  sonic-stick.iso",
                f"{manifest_sha}  build-manifest.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    svc = SonicBuildService(repo_root=repo)
    monkeypatch.setattr(
        SonicBuildService,
        "_verify_detached_signature",
        staticmethod(lambda _payload, _sig: {"present": True, "verified": True, "detail": "test"}),
    )
    readiness = svc.get_release_readiness("b2")

    assert readiness["release_ready"] is True
    assert readiness["checksums"]["verified"] is True
    assert readiness["signing"]["ready"] is True
    assert readiness["issues"] == []


def test_release_readiness_reports_issues_for_missing_signatures(tmp_path):
    repo = tmp_path / "repo"
    build_dir = repo / "distribution" / "builds" / "b3"
    build_dir.mkdir(parents=True)

    img_data = b"img-bytes"
    img_sha = _sha256_bytes(img_data)
    (build_dir / "sonic-stick.img").write_bytes(img_data)
    _write_manifest(
        build_dir,
        [{"name": "sonic-stick.img", "path": "sonic-stick.img", "size_bytes": len(img_data), "sha256": img_sha}],
    )
    manifest_sha = hashlib.sha256((build_dir / "build-manifest.json").read_bytes()).hexdigest()
    (build_dir / "checksums.txt").write_text(
        "\n".join(
            [
                f"{img_sha}  sonic-stick.img",
                f"{manifest_sha}  build-manifest.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    svc = SonicBuildService(repo_root=repo)
    readiness = svc.get_release_readiness("b3")

    assert readiness["release_ready"] is False
    assert readiness["checksums"]["verified"] is True
    assert readiness["signing"]["ready"] is False
    assert "release signatures incomplete" in readiness["issues"]


def test_release_readiness_reports_unverified_signatures_when_pubkey_missing(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    build_dir = repo / "distribution" / "builds" / "b4"
    build_dir.mkdir(parents=True)

    img_data = b"img-bytes"
    img_sha = _sha256_bytes(img_data)
    (build_dir / "sonic-stick.img").write_bytes(img_data)
    _write_manifest(
        build_dir,
        [{"name": "sonic-stick.img", "path": "sonic-stick.img", "size_bytes": len(img_data), "sha256": img_sha}],
    )
    manifest_sha = hashlib.sha256((build_dir / "build-manifest.json").read_bytes()).hexdigest()
    (build_dir / "checksums.txt").write_text(
        "\n".join(
            [
                f"{img_sha}  sonic-stick.img",
                f"{manifest_sha}  build-manifest.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (build_dir / "build-manifest.json.sig").write_text("sig", encoding="utf-8")
    (build_dir / "checksums.txt.sig").write_text("sig", encoding="utf-8")

    monkeypatch.delenv("WIZARD_SONIC_SIGN_PUBKEY", raising=False)
    svc = SonicBuildService(repo_root=repo)
    readiness = svc.get_release_readiness("b4")

    assert readiness["release_ready"] is False
    assert readiness["signing"]["manifest_signature_present"] is True
    assert readiness["signing"]["checksums_signature_present"] is True
    assert readiness["signing"]["manifest_signature_verified"] is False
    assert readiness["signing"]["checksums_signature_verified"] is False
