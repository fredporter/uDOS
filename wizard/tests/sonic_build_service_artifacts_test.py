import json
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
