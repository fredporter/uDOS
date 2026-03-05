from __future__ import annotations

import argparse
from pathlib import Path
import sys

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from demo_runtime import write_report


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-06-ghost-to-wizard-onboarding.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-06-runtime")
MISSION_SCRIPT = Path("docs/examples/ghost-to-wizard-script.md")


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    levels = [
        "awakening_chamber",
        "command_vault",
        "tui_hall",
        "workflow_engine",
        "extension_forge",
        "research_tower",
        "surface",
    ]
    roles = ["ghost", "apprentice", "operator", "alchemist", "wizard"]

    payload = {
        "demo": "06-ghost-to-wizard-onboarding",
        "runtime_root": str(runtime_root.resolve()),
        "mission_script": str(MISSION_SCRIPT),
        "mission_script_exists": MISSION_SCRIPT.exists(),
        "level_sequence": levels,
        "role_progression": roles,
        "setup_contract": {
            "doctor": "udos doctor",
            "core_install": "udos install core",
            "workspace_init": "udos init my-first-binder",
            "workflow": "run mission hello_world",
            "extension": "udos install extension.image",
            "research": "research topic terminal interfaces",
            "publish": "publish",
        },
        "event_types": ["narration", "objective", "challenge", "reward", "unlock", "progress"],
        "final_state": {"role": "wizard", "progress_saved": True},
    }
    return write_report(output_path, payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--runtime-root", default=str(DEFAULT_RUNTIME))
    args = parser.parse_args()
    path = build_report(Path(args.output), Path(args.runtime_root))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
