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

from demo_runtime import demo_runtime, write_report


DEFAULT_OUTPUT = Path(".artifacts/release-demos/demo-00-setup-and-status.json")
DEFAULT_RUNTIME = Path(".artifacts/release-demos/demo-00-runtime")


def build_report(output_path: Path = DEFAULT_OUTPUT, runtime_root: Path = DEFAULT_RUNTIME) -> Path:
    with demo_runtime(runtime_root, blocked_provider="mistral", primary_provider="openai") as client:
        logic = client.get("/api/ucode/logic/status").json()
        ops_config = client.get("/api/ops/config/status").json()
        ops_jobs = client.get("/api/ops/planning/jobs").json()
        releases = client.get("/api/ops/releases/overview").json()

    payload = {
        "demo": "00-setup-and-status",
        "runtime_root": str(runtime_root.resolve()),
        "logic_status": logic,
        "ops_config": ops_config,
        "ops_jobs": ops_jobs,
        "releases": releases,
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
