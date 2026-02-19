#!/usr/bin/env python3
"""v1.3.25 runtime hardcoded-local-path guardrail."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[2]
RUNTIME_ROOTS = [
    REPO / "core" / "commands",
    REPO / "core" / "services",
    REPO / "core" / "input",
    REPO / "core" / "tui",
    REPO / "wizard" / "routes",
    REPO / "wizard" / "services",
]
TEXT_EXTS = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}
HARD_PATH_RE = re.compile(r"(/Users/|/home/|C:\\\\Users\\\\|C:/Users/)")
REPORT_PATH = REPO / "memory" / "reports" / "v1_3_25_runtime_hardcoded_paths.json"


def scan_runtime_hardcoded_paths() -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []

    for root in RUNTIME_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_EXTS:
                continue
            if any(part in {"__pycache__", "venv", "dist", "node_modules", "tests"} for part in path.parts):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue
            for idx, line in enumerate(lines, start=1):
                if HARD_PATH_RE.search(line):
                    findings.append(
                        {
                            "path": str(path.relative_to(REPO)),
                            "line": idx,
                            "message": "hardcoded absolute machine path",
                        }
                    )

    return {
        "ok": len(findings) == 0,
        "findings": findings,
        "roots": [str(root.relative_to(REPO)) for root in RUNTIME_ROOTS if root.exists()],
    }


def main() -> int:
    report = scan_runtime_hardcoded_paths()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"report: {REPORT_PATH.relative_to(REPO)}")

    if not report["ok"]:
        raise RuntimeError("runtime contains hardcoded local machine paths")

    print("[runtime-hardcoded-paths-v1.3.25] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
