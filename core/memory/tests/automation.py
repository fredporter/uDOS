"""Automation entry point for memory/tests/phase1 TypeScript coverage."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parents[2]
    cmd = [
        "npm",
        "test",
        "--",
        "memory/tests/phase1/interpolation.test.ts",
        "memory/tests/phase1/sql-executor.test.ts",
        "memory/tests/phase1/sql-runner-chain.test.ts",
    ]

    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)

    summary_path = repo_root / "memory" / "logs" / "memory-tests-automation.json"
    summary = {
        "timestamp": datetime.now().isoformat(),
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
