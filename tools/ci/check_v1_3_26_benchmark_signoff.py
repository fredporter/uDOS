#!/usr/bin/env python3
"""v1.3.26 benchmark sign-off against mission objective thresholds."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO / "memory" / "reports" / "v1_3_26_benchmark_signoff.json"
CHECKLIST_REPORT_PATH = REPO / "memory" / "reports" / "v1_3_25_release_checklist.json"


def main() -> int:
    cmd = [
        sys.executable,
        "tools/ci/check_v1_3_25_release_checklist.py",
        "--enforce",
        "--block-on-warn",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"benchmark sign-off failed:\n{details}")

    checklist_payload = None
    if CHECKLIST_REPORT_PATH.exists():
        try:
            checklist_payload = json.loads(CHECKLIST_REPORT_PATH.read_text(encoding="utf-8"))
        except Exception:
            checklist_payload = None

    payload = {
        "version": "1.3.26",
        "milestone": "v1.3.26",
        "status": "pass",
        "source_gate": "check_v1_3_25_release_checklist.py --enforce --block-on-warn",
        "release_checklist": checklist_payload,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"report: {REPORT_PATH.relative_to(REPO)}")
    print("[benchmark-signoff-v1.3.26] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
