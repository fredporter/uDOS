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


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-08-seed-library-generation.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-08-runtime")
SEED_ROOT = REPO_ROOT / "core" / "framework" / "seed" / "bank"


def _count_files(path: Path, pattern: str) -> int:
    return len(list(path.glob(pattern)))


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    graphics_root = SEED_ROOT / "graphics"
    diagrams_root = graphics_root / "diagrams"
    templates_root = SEED_ROOT / "templates"

    payload = {
        "demo": "08-seed-library-generation",
        "runtime_root": str(runtime_root.resolve()),
        "seed_root": str(SEED_ROOT),
        "paths_exist": {
            "seed_root": SEED_ROOT.exists(),
            "graphics": graphics_root.exists(),
            "diagrams": diagrams_root.exists(),
            "templates": templates_root.exists(),
        },
        "counts": {
            "diagrams_ascii": _count_files(diagrams_root / "ascii", "*.txt"),
            "diagrams_blocks": _count_files(diagrams_root / "blocks", "*.txt"),
            "diagrams_plain": _count_files(diagrams_root / "plain", "*.txt"),
            "diagrams_flow": _count_files(diagrams_root / "flow", "*.txt"),
            "diagrams_sequence": _count_files(diagrams_root / "sequence", "*.txt"),
            "teletext_palettes": _count_files(diagrams_root / "teletext", "*.json"),
            "themes": _count_files(graphics_root / "themes", "*.json"),
            "templates": _count_files(templates_root, "*.json") + _count_files(templates_root, "*.md"),
        },
        "deterministic_index": {
            "diagram_catalog": str(diagrams_root / "catalog.json"),
            "theme_index": str(graphics_root / "themes" / "_index.json"),
            "theme_schema": str(graphics_root / "themes" / "_schema.json"),
        },
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
