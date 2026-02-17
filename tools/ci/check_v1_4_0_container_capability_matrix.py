#!/usr/bin/env python3
"""v1.4.0 container capability matrix validation gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[2]
MATRIX_PATH = REPO / "core" / "config" / "v1_4_0_container_capability_matrix.json"
COMPOSE_PATH = REPO / "docker-compose.yml"
REPORT_PATH = REPO / "memory" / "reports" / "v1_4_0_container_capability_matrix.json"


def _parse_services(lines: List[str]) -> Dict[str, Dict[str, Any]]:
    services: Dict[str, Dict[str, Any]] = {}
    in_services = False
    current = None
    in_profiles = False
    in_build = False

    for raw in lines:
        line = raw.rstrip("\n")

        if line.startswith("services:"):
            in_services = True
            continue
        if in_services and line and not line.startswith(" "):
            break
        if not in_services:
            continue

        if line.startswith("  ") and line.endswith(":") and not line.startswith("    "):
            current = line.strip()[:-1]
            services[current] = {"profiles": [], "build_context": None}
            in_profiles = False
            in_build = False
            continue

        if not current:
            continue

        if line.startswith("    profiles:"):
            in_profiles = True
            in_build = False
            continue

        if line.startswith("    build:"):
            in_build = True
            in_profiles = False
            tail = line.split(":", 1)[1].strip()
            if tail:
                services[current]["build_context"] = tail
            continue

        if in_profiles:
            if line.startswith("      - "):
                services[current]["profiles"].append(line.strip()[2:].strip())
                continue
            in_profiles = False

        if in_build:
            if line.startswith("      context:"):
                services[current]["build_context"] = line.split(":", 1)[1].strip()
                continue
            if line.startswith("    ") and not line.startswith("      "):
                in_build = False

    return services


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    lanes = matrix.get("lanes", [])
    if not isinstance(lanes, list) or not lanes:
        raise RuntimeError("container capability matrix has no lanes")

    compose = _parse_services(COMPOSE_PATH.read_text(encoding="utf-8").splitlines())

    missing_services: List[Dict[str, Any]] = []
    profile_mismatches: List[Dict[str, Any]] = []
    context_mismatches: List[Dict[str, Any]] = []
    missing_artifacts: List[Dict[str, Any]] = []
    missing_smoke_gates: List[Dict[str, Any]] = []

    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        lane_id = str(lane.get("id", "unknown"))
        service = str(lane.get("service", "")).strip()
        expected_profiles = sorted(str(x) for x in lane.get("profiles", []) if str(x).strip())
        expected_context = str(lane.get("build_context", "")).strip()
        smoke_gate = str(lane.get("smoke_gate", "")).strip()

        skip_compose = lane.get("skip_compose", False)

        if not skip_compose:
            svc = compose.get(service)
            if not svc:
                missing_services.append({"lane": lane_id, "service": service})
                continue

            actual_profiles = sorted(str(x) for x in svc.get("profiles", []) if str(x).strip())
            if actual_profiles != expected_profiles:
                profile_mismatches.append(
                    {
                        "lane": lane_id,
                        "service": service,
                        "expected": expected_profiles,
                        "actual": actual_profiles,
                    }
                )

            actual_context = str(svc.get("build_context") or "").strip()
            if expected_context and actual_context and actual_context != expected_context:
                context_mismatches.append(
                    {
                        "lane": lane_id,
                        "service": service,
                        "expected": expected_context,
                        "actual": actual_context,
                    }
                )

        for artifact in lane.get("required_artifacts", []):
            rel = str(artifact).strip()
            if rel and not (REPO / rel).exists():
                missing_artifacts.append({"lane": lane_id, "path": rel})

        if smoke_gate and not (REPO / smoke_gate).exists():
            missing_smoke_gates.append({"lane": lane_id, "path": smoke_gate})

    report = {
        "ok": not missing_services and not profile_mismatches and not context_mismatches and not missing_artifacts and not missing_smoke_gates,
        "matrix": str(MATRIX_PATH.relative_to(REPO)),
        "missing_services": missing_services,
        "profile_mismatches": profile_mismatches,
        "context_mismatches": context_mismatches,
        "missing_artifacts": missing_artifacts,
        "missing_smoke_gates": missing_smoke_gates,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"report: {REPORT_PATH.relative_to(REPO)}")

    if not report["ok"]:
        raise RuntimeError("container capability matrix validation failed")

    print("[container-capability-matrix-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
