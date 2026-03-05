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


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-07-layer-mapping-and-z-index.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-07-runtime")


def _lane_for_z(z_value: int) -> str:
    if z_value < 0:
        return "dungeon"
    if z_value >= 5:
        return "galaxy"
    return "foundation"


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    z_samples = [-4, -1, 0, 2, 6, 12]
    mapping = [{"z": z_value, "lane": _lane_for_z(z_value)} for z_value in z_samples]

    payload = {
        "demo": "07-layer-mapping-and-z-index",
        "runtime_root": str(runtime_root.resolve()),
        "z_policy": {
            "dungeon": "z < 0",
            "foundation": "0 <= z < 5",
            "galaxy": "z >= 5",
        },
        "sample_mapping": mapping,
        "theme_mapping": {
            "dungeon": ["dungeon", "fantasy", "role-play", "pirate"],
            "foundation": ["explorer", "adventure", "traveller"],
            "galaxy": ["galaxy", "foundation", "pilot", "scientist"],
        },
        "separation_rule": "Theme vocabulary remains independent from spatial renderer state",
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
