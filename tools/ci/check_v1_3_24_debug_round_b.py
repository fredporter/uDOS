#!/usr/bin/env python3
"""v1.3.24 Debug Round B hygiene gate and unused-function triage artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    script = REPO / "tools" / "ci" / "check_code_hygiene_v1_3_21.py"
    proc = subprocess.run([sys.executable, str(script)], cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"hygiene scan failed:\n{details}")
    print(proc.stdout.strip())

    report_path = REPO / "memory" / "reports" / "code_hygiene_v1_3_21.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    hardcoded = report.get("hardcoded_paths", [])
    duplicates = report.get("duplicate_functions", [])
    legacy_markers = report.get("deprecated_markers", [])
    unused = report.get("potential_unused_private_functions", [])

    if hardcoded:
        raise RuntimeError(f"hardcoded path findings remain: {len(hardcoded)}")
    if duplicates:
        raise RuntimeError(f"duplicate function findings remain: {len(duplicates)}")
    if legacy_markers:
        raise RuntimeError(f"legacy marker findings remain: {len(legacy_markers)}")

    triage_rows = []
    for row in unused:
        triage_rows.append(
            {
                "path": row.get("path"),
                "line": row.get("line"),
                "symbol": row.get("message"),
                "action": "annotate",
                "note": "Round B triage: retained intentionally or pending Round C consolidation.",
            }
        )

    triage = {
        "version": "1.3.24",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report": str(report_path.relative_to(REPO)),
        "summary": {
            "hardcoded_paths": len(hardcoded),
            "duplicate_functions": len(duplicates),
            "legacy_markers": len(legacy_markers),
            "unused_private_functions": len(unused),
            "unused_private_functions_annotated": len(triage_rows),
        },
        "entries": triage_rows,
    }
    out = REPO / "memory" / "reports" / "code_hygiene_v1_3_24_round_b_triage.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(triage, indent=2), encoding="utf-8")

    print("[debug-round-b-v1.3.24] PASS")
    print(f"  - hardcoded paths: {len(hardcoded)}")
    print(f"  - duplicate functions: {len(duplicates)}")
    print(f"  - legacy markers: {len(legacy_markers)}")
    print(f"  - unused private functions annotated: {len(triage_rows)}")
    print(f"  - triage report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

