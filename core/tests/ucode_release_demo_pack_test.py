import json
from pathlib import Path


PACK_ROOT = Path(__file__).resolve().parents[2] / "docs" / "examples" / "ucode_v1_5_release_pack"
DEMO_FILES = [
    "README.md",
    "CERTIFICATION.md",
    "certification.json",
    "00-setup-and-status.md",
    "01-local-assist-and-knowledge.md",
    "02-workflow-and-task-planning.md",
    "03-managed-scheduler-and-budget.md",
    "04-self-hosted-dev-mode.md",
]
REQUIRED_SECTIONS = [
    "## Goal",
    "## Target Profiles",
    "## Transcript",
    "## Expected Output",
    "## Validation",
]


def test_release_demo_pack_files_exist():
    for name in DEMO_FILES:
        assert (PACK_ROOT / name).exists(), name


def test_release_demo_scripts_include_required_sections():
    for name in DEMO_FILES:
        if name in {"README.md", "CERTIFICATION.md", "certification.json"}:
            continue
        text = (PACK_ROOT / name).read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            assert section in text, f"{name} missing {section}"


def test_release_demo_pack_readme_lists_all_demos():
    text = (PACK_ROOT / "README.md").read_text(encoding="utf-8")
    for name in DEMO_FILES[3:]:
        assert name in text, name


def test_release_demo_pack_certification_covers_all_demos_and_profiles():
    payload = json.loads((PACK_ROOT / "certification.json").read_text(encoding="utf-8"))

    assert payload["status"] == "certified"
    assert len(payload["demos"]) == 5
    assert set(payload["profile_coverage"]) == {"core", "home", "creator", "gaming", "dev"}
    assert all(item["status"] == "certified" for item in payload["demos"])
