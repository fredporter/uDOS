#!/usr/bin/env python3
"""v1.4.0 release preflight automation gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO / "memory" / "reports" / "v1_4_0_release_preflight.json"

CHECKS: List[List[str]] = [
    [sys.executable, "tools/ci/check_v1_3_25_contract_freeze.py"],
    [sys.executable, "tools/ci/check_v1_3_26_final_stabilization.py"],
    [sys.executable, "tools/ci/check_v1_4_0_toybox_lifespan_readiness.py"],
    [sys.executable, "tools/ci/check_v1_4_0_sonic_docker_smoke.py"],
    [sys.executable, "tools/ci/check_v1_4_0_groovebox_docker_smoke.py"],
    [sys.executable, "tools/ci/check_v1_4_0_compose_profile_matrix.py"],
    [sys.executable, "tools/ci/check_v1_4_0_container_capability_matrix.py"],
]


def _run(cmd: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "ok": proc.returncode == 0,
        "stdout": (proc.stdout or "").strip()[-4000:],
        "stderr": (proc.stderr or "").strip()[-4000:],
    }


def main() -> int:
    results = [_run(cmd) for cmd in CHECKS]
    ok = all(row["ok"] for row in results)

    report = {
        "version": "1.4.0",
        "milestone": "v1.4.0",
        "status": "ok" if ok else "fail",
        "checks": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"report: {REPORT_PATH.relative_to(REPO)}")

    if not ok:
        raise RuntimeError("v1.4.0 release preflight failed")

    print("[release-preflight-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
