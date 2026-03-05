from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SIGNOFF_JSON = REPO_ROOT / "docs" / "specs" / "V1-5-STABLE-SIGNOFF.json"
PROFILE_STATE = REPO_ROOT / "memory" / "ucode" / "release-profiles.json"


def test_stable_signoff_covers_all_certified_profiles():
    payload = json.loads(SIGNOFF_JSON.read_text(encoding="utf-8"))

    assert payload["release_version"] == "v1.5.0"
    assert payload["release_channel"] == "stable"
    assert set(payload["profiles"]) == {"core", "home", "creator", "gaming", "dev"}
    assert all(item["verify_healthy"] is True for item in payload["profiles"].values())


def test_stable_signoff_matches_current_release_profile_state():
    payload = json.loads(SIGNOFF_JSON.read_text(encoding="utf-8"))
    state = json.loads(PROFILE_STATE.read_text(encoding="utf-8"))

    installed = set(state["installed"])
    enabled = set(state["enabled"])
    assert installed == {"core", "home", "creator", "gaming", "dev"}
    assert enabled == {"core", "home", "creator", "gaming", "dev"}

    for profile_id, profile in payload["profiles"].items():
        assert profile["installed"] is True
        assert profile["enabled"] is True
        assert profile_id in installed
        assert profile_id in enabled
