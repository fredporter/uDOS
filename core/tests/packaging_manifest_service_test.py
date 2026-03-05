from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.services.packaging_manifest_service import load_packaging_manifest


def test_load_packaging_manifest_returns_defaults_when_file_missing(tmp_path: Path):
    manifest = load_packaging_manifest(tmp_path)
    assert manifest["schema"] == "udos.packaging.manifest.v2"
    assert manifest["global"]["offline_assets"]["root"] == "distribution/offline-assets"
    assert manifest["global"]["offline_assets"]["cache_namespace"] == "memory/wizard/offline-assets"
    assert manifest["platforms"]["linux"]["app_bundle"]["default_profile"] == "alpine-core+sonic"
    assert manifest["platforms"]["windows"]["shell_defaults"]["default_game_launcher_path"].endswith(
        "Playnite.FullscreenApp.exe"
    )
    assert manifest["platforms"]["linux"]["dependency_profiles"]["udos-ui-thin-gui"]["runtime_packages"] == [
        "cage",
        "wayland",
        "libxkbcommon",
        "mesa",
        "libinput",
        "seatd",
    ]
    assert manifest["platforms"]["windows"]["media_game_image_steps"]["boot_timeout_seconds"] == 5


def test_load_packaging_manifest_merges_repo_overrides(tmp_path: Path):
    manifest_path = tmp_path / "packaging.manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "platforms": {
                    "linux": {
                        "app_bundle": {
                            "default_profile": "custom-profile",
                            "builds_root": "custom/builds",
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    manifest = load_packaging_manifest(tmp_path)
    assert manifest["platforms"]["linux"]["app_bundle"]["default_profile"] == "custom-profile"
    sonic_stick = manifest["platforms"]["linux"]["app_bundle"]
    assert sonic_stick["default_profile"] == "custom-profile"
    assert sonic_stick["builds_root"] == "custom/builds"
    assert sonic_stick["build_script"] == "distribution/alpine-core/build-sonic-stick.sh"
    assert manifest["platforms"]["windows"]["shell_defaults"]["default_game_launcher_path"].endswith(
        "Playnite.FullscreenApp.exe"
    )


def test_load_packaging_manifest_rejects_non_v2_schema(tmp_path: Path):
    manifest_path = tmp_path / "packaging.manifest.json"
    manifest_path.write_text(
        json.dumps({"schema": "udos.packaging.manifest.v1"}),
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        load_packaging_manifest(tmp_path)
