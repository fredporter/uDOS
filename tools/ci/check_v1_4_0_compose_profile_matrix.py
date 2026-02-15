#!/usr/bin/env python3
"""v1.4.0 docker-compose profile matrix validation gate."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO / "docker-compose.yml"
REPORT_PATH = REPO / "memory" / "reports" / "v1_4_0_compose_profile_matrix.json"


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
            services[current] = {"profiles": [], "build": None, "build_context": None}
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
                services[current]["build"] = tail
                services[current]["build_context"] = tail
            continue

        if in_profiles:
            if line.startswith("      - "):
                services[current]["profiles"].append(line.strip()[2:].strip())
                continue
            in_profiles = False

        if in_build:
            if line.startswith("      context:"):
                ctx = line.split(":", 1)[1].strip()
                services[current]["build_context"] = ctx
                continue
            if line.startswith("    ") and not line.startswith("      "):
                in_build = False

    return services


def _docker_compose_available() -> bool:
    if not shutil.which("docker"):
        return False
    probe = subprocess.run(["docker", "compose", "version"], cwd=str(REPO), capture_output=True, text=True)
    return probe.returncode == 0


def _validate_compose_profiles_with_docker() -> Dict[str, Any]:
    combos = {
        "default": [],
        "scheduler": ["--profile", "scheduler"],
        "homeassistant": ["--profile", "homeassistant"],
        "groovebox": ["--profile", "groovebox"],
        "all": ["--profile", "all"],
    }
    results: Dict[str, Any] = {}
    for name, extra in combos.items():
        cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), *extra, "config"]
        proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
        results[name] = {
            "ok": proc.returncode == 0,
            "stderr": (proc.stderr or "").strip()[:4000],
        }
    return results


def main() -> int:
    lines = COMPOSE_FILE.read_text(encoding="utf-8").splitlines()
    services = _parse_services(lines)

    required_services = {"wizard", "ollama", "mission-scheduler", "home-assistant", "groovebox"}
    missing_services = sorted(list(required_services - set(services.keys())))

    expected_profiles = {
        "mission-scheduler": {"scheduler", "all"},
        "home-assistant": {"homeassistant", "all"},
        "groovebox": {"groovebox", "all"},
    }

    profile_mismatches = []
    for service, expected in expected_profiles.items():
        got = set(services.get(service, {}).get("profiles", []))
        if got != expected:
            profile_mismatches.append(
                {"service": service, "expected": sorted(list(expected)), "actual": sorted(list(got))}
            )

    missing_build_contexts = []
    for service in ["wizard", "mission-scheduler", "home-assistant", "groovebox"]:
        ctx = services.get(service, {}).get("build_context")
        if not ctx:
            missing_build_contexts.append({"service": service, "reason": "missing build context"})
            continue
        resolved = (REPO / ctx).resolve() if ctx != "." else REPO
        if not resolved.exists():
            missing_build_contexts.append({"service": service, "reason": f"build context not found: {ctx}"})

    docker_results = None
    if _docker_compose_available():
        docker_results = _validate_compose_profiles_with_docker()

    docker_failures = []
    if docker_results:
        for name, row in docker_results.items():
            if not row.get("ok"):
                docker_failures.append({"profile": name, "stderr": row.get("stderr", "")})

    report = {
        "ok": not missing_services and not profile_mismatches and not missing_build_contexts and not docker_failures,
        "missing_services": missing_services,
        "profile_mismatches": profile_mismatches,
        "missing_build_contexts": missing_build_contexts,
        "docker_compose_validation": {
            "executed": docker_results is not None,
            "profiles": docker_results or {},
            "failures": docker_failures,
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"report: {REPORT_PATH.relative_to(REPO)}")

    if not report["ok"]:
        raise RuntimeError("compose profile matrix validation failed")

    print("[compose-profile-matrix-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
