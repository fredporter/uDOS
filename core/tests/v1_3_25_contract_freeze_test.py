import json
from pathlib import Path

from tools.ci.check_v1_3_25_contract_freeze import verify_manifest


def test_v1_3_25_contract_freeze_manifest_passes_against_repo_root():
    manifest = json.loads(
        Path("tools/ci/baselines/v1_3_25_contract_freeze_manifest.json").read_text(encoding="utf-8")
    )
    report = verify_manifest(manifest, repo_root=Path("."))
    assert report["ok"] is True
    assert report["missing"] == []
    assert report["drift"] == []


def test_v1_3_25_contract_freeze_reports_hash_drift(tmp_path):
    target = tmp_path / "contracts" / "alpha.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"v":1}\n', encoding="utf-8")

    manifest = {
        "contracts": [
            {
                "path": "contracts/alpha.json",
                "sha256": "0" * 64,
            }
        ]
    }

    report = verify_manifest(manifest, repo_root=tmp_path)
    assert report["ok"] is False
    assert report["missing"] == []
    assert len(report["drift"]) == 1
    assert report["drift"][0]["path"] == "contracts/alpha.json"


def test_v1_3_25_contract_freeze_reports_missing_files(tmp_path):
    manifest = {
        "contracts": [
            {
                "path": "contracts/missing.json",
                "sha256": "a" * 64,
            }
        ]
    }

    report = verify_manifest(manifest, repo_root=tmp_path)
    assert report["ok"] is False
    assert report["missing"] == ["contracts/missing.json"]
    assert report["drift"] == []
