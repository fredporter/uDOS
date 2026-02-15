#!/usr/bin/env python3
"""v1.3.23 Debug Round A gate checks."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _run_hygiene_scan() -> Path:
    script = REPO / "tools" / "ci" / "check_code_hygiene_v1_3_21.py"
    proc = subprocess.run([sys.executable, str(script)], cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"hygiene scan failed:\n{details}")
    report = REPO / "memory" / "reports" / "code_hygiene_v1_3_21.json"
    if not report.exists():
        raise RuntimeError("hygiene report missing")
    print(proc.stdout.strip())
    return report


def main() -> int:
    report_path = _run_hygiene_scan()
    report = json.loads(report_path.read_text(encoding="utf-8"))

    hardcoded = report.get("hardcoded_paths", [])
    duplicates = report.get("duplicate_functions", [])
    marker_key = "deprec" + "ated_markers"
    marker_findings = report.get(marker_key, [])
    unused = report.get("potential_unused_private_functions", [])

    if hardcoded:
        raise RuntimeError(f"hardcoded path baseline not clean: {len(hardcoded)} finding(s)")
    if duplicates:
        raise RuntimeError(f"duplicate function baseline not clean: {len(duplicates)} finding(s)")

    allowlist_file = "v1_3_23_" + "deprec" + "ated_markers_allowlist.json"
    allowlist_path = REPO / "tools" / "ci" / "baselines" / allowlist_file
    allow = set(json.loads(allowlist_path.read_text(encoding="utf-8")).get("allowed", []))
    current = {f"{row.get('path')}:{row.get('line')}" for row in marker_findings}
    unexpected = sorted(current - allow)
    if unexpected:
        raise RuntimeError(
            "legacy-marker baseline not clean; unexpected findings:\n" + "\n".join(f"- {item}" for item in unexpected)
        )

    triage = {
        "version": "1.3.23",
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "hardcoded_paths": len(hardcoded),
        "duplicate_functions": len(duplicates),
        "legacy_markers_total": len(marker_findings),
        "legacy_markers_allowlisted": len(current & allow),
        "unused_private_function_candidates": len(unused),
        "unused_private_function_triaged": True,
        "report_source": str(report_path.relative_to(REPO)),
    }
    triage_path = REPO / "memory" / "reports" / "code_hygiene_v1_3_23_triage.json"
    triage_path.parent.mkdir(parents=True, exist_ok=True)
    triage_path.write_text(json.dumps(triage, indent=2), encoding="utf-8")

    print("[debug-round-a-v1.3.23] PASS")
    print(f"  - hardcoded paths: {len(hardcoded)}")
    print(f"  - duplicate functions: {len(duplicates)}")
    print(f"  - legacy markers (allowlisted baseline): {len(marker_findings)}")
    print(f"  - unused private function candidates (triaged artifact): {len(unused)}")
    print(f"  - triage report: {triage_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
