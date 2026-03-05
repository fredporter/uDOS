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


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-05-grid-and-view-rendering.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-05-runtime")


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    view_matrix = [
        {"view": "text", "fixed_width": True, "fallback": "text"},
        {"view": "columns", "fixed_width": True, "fallback": "stacked"},
        {"view": "ascii", "fixed_width": True, "fallback": "ascii"},
        {"view": "teletext", "fixed_width": True, "fallback": "ascii"},
        {"view": "calendar", "fixed_width": True, "fallback": "list"},
        {"view": "task", "fixed_width": True, "fallback": "list"},
        {"view": "grid", "fixed_width": True, "fallback": "ascii"},
        {"view": "container", "fixed_width": True, "fallback": "stacked"},
    ]

    sample_events = [
        {"kind": "event", "event": "block", "view": "text", "title": "Status"},
        {"kind": "event", "event": "block", "view": "columns", "title": "Planner"},
        {"kind": "event", "event": "block", "view": "ascii", "title": "Diagram"},
        {"kind": "event", "event": "block", "view": "teletext", "title": "Map"},
        {"kind": "event", "event": "block", "view": "calendar", "title": "Schedule"},
        {"kind": "event", "event": "block", "view": "task", "title": "Mission Tasks"},
        {"kind": "event", "event": "block", "view": "grid", "title": "World Grid"},
        {"kind": "event", "event": "block", "view": "container", "title": "Workspace"},
    ]

    payload = {
        "demo": "05-grid-and-view-rendering",
        "runtime_root": str(runtime_root.resolve()),
        "character_model": {
            "ascii_safe_default": True,
            "block_graphics_optional": True,
            "teletext_fallback": "ascii",
        },
        "view_matrix": view_matrix,
        "sample_events": sample_events,
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
