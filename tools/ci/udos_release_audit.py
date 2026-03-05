#!/usr/bin/env python3
"""Automated pre-release audit for uDOS v1.5+."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_PATH = REPO_ROOT / "memory" / "reports" / "udos_pre_release_audit.json"
DEFAULT_DEV_REPORT_PATH = REPO_ROOT / "dev" / "ops" / "reports" / "udos_pre_release_audit.json"

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".artifacts",
    ".compost",
}
TEXT_EXTS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".json",
    ".jsonl",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".ts",
    ".tsx",
    ".js",
    ".mjs",
    ".cjs",
    ".go",
    ".java",
    ".xml",
    ".sql",
    ".dockerfile",
    "",
}
HARD_PATH_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"/home/"),
    re.compile(r"/tmp/"),
    re.compile(r"/usr/local/"),
    re.compile(r"/opt/"),
    re.compile(r"~/uDOS"),
)


@dataclass
class CheckResult:
    section: int
    name: str
    status: str
    details: str
    findings: list[str]


def _iter_text_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            out.append(root)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() in TEXT_EXTS:
                out.append(path)
    return out


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _find_matches(path: Path, patterns: tuple[re.Pattern[str], ...]) -> list[str]:
    findings: list[str] = []
    text = _read_text(path)
    for idx, line in enumerate(text.splitlines(), start=1):
        if any(p.search(line) for p in patterns):
            findings.append(f"{path.relative_to(REPO_ROOT)}:{idx}")
    return findings


def _status_from_counts(fails: int, warns: int) -> str:
    if fails > 0:
        return "fail"
    if warns > 0:
        return "warn"
    return "pass"


def _has_any(globs: list[str]) -> bool:
    return any(REPO_ROOT.glob(pattern) for pattern in globs)


def check_1_repository_structure() -> CheckResult:
    required = [
        "bin",
        "core",
        "system",
        "runtime",
        "extensions",
        "library",
        "containers",
        "data",
        "missions",
        "tui",
        "api",
        "workspace",
        "binder",
        "docs",
        "help",
        "tests",
        "demos",
        "dev",
    ]
    missing = [name for name in required if not (REPO_ROOT / name).exists()]

    findings: list[str] = []
    if missing:
        findings.extend([f"missing required root path: {name}/" for name in missing])

    root_dev_docs = list(REPO_ROOT.glob("DEV*.md")) + list(REPO_ROOT.glob("*DEV*.md"))
    for path in root_dev_docs:
        findings.append(f"dev doc at repository root: {path.name}")

    goblin = REPO_ROOT / "dev" / "goblin"
    if not goblin.exists():
        findings.append("dev/goblin scaffold missing")

    gitignore = REPO_ROOT / ".gitignore"
    if gitignore.exists():
        content = _read_text(gitignore)
        for required_entry in ("containers/", "dev/", "workspace/"):
            if required_entry not in content:
                findings.append(f".gitignore may miss release artifact ignore entry: {required_entry}")
    else:
        findings.append(".gitignore missing")

    binaries: list[str] = []
    git_ls = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if git_ls.returncode == 0:
        for rel in git_ls.stdout.splitlines():
            if Path(rel).suffix.lower() in {".pyc", ".pyo", ".o", ".so", ".dll", ".exe"}:
                binaries.append(rel)
    findings.extend([f"compiled binary committed: {item}" for item in binaries[:20]])

    status = "pass" if not findings else ("fail" if missing or binaries else "warn")
    return CheckResult(1, "Repository Structure Validation", status, "Validate v1.5 root surface contract.", findings[:80])


def check_2_hardcoded_paths_env() -> CheckResult:
    scan_roots = [
        REPO_ROOT / "core",
        REPO_ROOT / "wizard",
        REPO_ROOT / "bin",
        REPO_ROOT / "tools",
        REPO_ROOT / "scripts",
        REPO_ROOT / "containers",
        REPO_ROOT / "extensions",
        REPO_ROOT / "tui",
    ]
    findings: list[str] = []
    for path in _iter_text_files(scan_roots):
        if "tests" in path.parts:
            continue
        findings.extend(_find_matches(path, HARD_PATH_PATTERNS))
        if len(findings) >= 120:
            break

    required_env = [
        "UDOS_ROOT",
        "UDOS_DATA",
        "UDOS_EXT",
        "UDOS_LIB",
        "UDOS_RUNTIME",
        "UDOS_WORKSPACE",
        "UDOS_BINDER",
    ]
    repo_text = "\n".join(_read_text(p) for p in _iter_text_files([REPO_ROOT / "core", REPO_ROOT / "wizard", REPO_ROOT / "bin", REPO_ROOT / "docs"]))
    missing_env = [token for token in required_env if token not in repo_text]
    findings.extend([f"required env variable appears undocumented/unused: {name}" for name in missing_env])

    containers_text = "\n".join(_read_text(p) for p in _iter_text_files([REPO_ROOT / "containers"]))
    if "UDOS_ROOT" not in containers_text:
        findings.append("containers do not appear to reference UDOS_ROOT mount variable")

    script_text = "\n".join(_read_text(p) for p in _iter_text_files([REPO_ROOT / "bin", REPO_ROOT / "scripts"]))
    if "git rev-parse --show-toplevel" not in script_text and "UDOS_ROOT" not in script_text:
        findings.append("scripts do not appear to detect repository root dynamically")

    status = "pass" if not findings else ("fail" if any("/Users/" in f or "/home/" in f for f in findings) else "warn")
    return CheckResult(2, "Hardcoded Path & Environment Validation", status, "Detect non-portable filesystem paths and env contract gaps.", findings[:120])


def check_3_feature_completion() -> CheckResult:
    matrix: dict[str, dict[str, list[str]]] = {
        "ucode engine": {
            "implementation": ["core/**/ucode*.py", "core/tui/ucode.py"],
            "demo": ["demos/**/*ucode*", "docs/examples/**/*ucode*"],
            "help": ["help/**/*ucode*", "docs/howto/**/*UCODE*"],
            "test": ["tests/**/*ucode*", "core/tests/**/*ucode*"],
        },
        "tui runtime": {
            "implementation": ["core/tui/**/*.py", "tui/**/*"],
            "demo": ["demos/**/*tui*", "docs/examples/**/*tui*"],
            "help": ["help/**/*tui*", "docs/howto/**/*TUI*"],
            "test": ["tests/**/*tui*", "core/tests/**/*tui*"],
        },
        "missions": {
            "implementation": ["missions/**/*", "core/**/*mission*"],
            "demo": ["demos/**/*mission*", "docs/examples/**/*mission*"],
            "help": ["help/**/*mission*", "docs/howto/**/*MISSION*"],
            "test": ["tests/**/*mission*", "core/tests/**/*mission*"],
        },
        "extensions": {
            "implementation": ["extensions/**/*", "wizard/services/*extension*"],
            "demo": ["demos/**/*extension*", "docs/examples/**/*extension*"],
            "help": ["help/**/*extension*", "docs/howto/**/*EXTENSION*"],
            "test": ["tests/**/*extension*", "wizard/tests/**/*extension*"],
        },
        "research mode": {
            "implementation": ["core/binder/**/*", "core/services/**/*research*"],
            "demo": ["demos/**/*research*", "docs/examples/**/*research*"],
            "help": ["help/**/*research*", "docs/howto/**/*RESEARCH*", "docs/howto/**/*BINDER*"],
            "test": ["tests/**/*research*", "core/tests/**/*binder*"],
        },
        "container runtime": {
            "implementation": ["containers/**/*", "core/services/*container*"],
            "demo": ["demos/**/*container*", "docs/examples/**/*container*"],
            "help": ["help/**/*container*", "docs/howto/**/*CONTAINER*"],
            "test": ["tests/**/*container*", "core/tests/**/*container*"],
        },
    }
    findings: list[str] = []
    for feature, components in matrix.items():
        for component, patterns in components.items():
            if not _has_any(patterns):
                findings.append(f"{feature}: missing {component}")

    command_docs = REPO_ROOT / "docs" / "howto" / "commands"
    if not command_docs.exists():
        findings.append("command registry docs missing at docs/howto/commands/")

    status = "pass" if not findings else "fail"
    return CheckResult(3, "Feature Completion Audit", status, "Validate implementation/demo/help/test coverage per major feature.", findings[:120])


def check_4_demo_coverage() -> CheckResult:
    required_demos = [
        "ghost_intro",
        "wizard_unlock",
        "sonic_demo",
        "extensions_demo",
        "research_demo",
        "tui_navigation",
    ]
    findings: list[str] = []
    for name in required_demos:
        if not (REPO_ROOT / "demos" / name).exists():
            findings.append(f"missing demo: demos/{name}/")
    if not (REPO_ROOT / "demos").exists():
        findings.append("demos/ directory missing")
    status = "pass" if not findings else "fail"
    return CheckResult(4, "Demo Script Coverage", status, "Verify demo surface exists for all major capabilities.", findings)


def check_5_help_docs() -> CheckResult:
    required = ["commands", "extensions", "workflows", "missions", "gameplay"]
    findings: list[str] = []
    for folder in required:
        if not (REPO_ROOT / "help" / folder).exists():
            findings.append(f"missing help directory: help/{folder}/")
    status = "pass" if not findings else "fail"
    return CheckResult(5, "Help Documentation Coverage", status, "Verify command/extension/workflow help hierarchy.", findings)


def check_6_test_coverage() -> CheckResult:
    required = ["unit", "integration", "runtime", "demo"]
    findings: list[str] = []
    for folder in required:
        if not (REPO_ROOT / "tests" / folder).exists():
            findings.append(f"missing tests/{folder}/")

    test_text = "\n".join(_read_text(p) for p in _iter_text_files([REPO_ROOT / "tests", REPO_ROOT / "core" / "tests", REPO_ROOT / "wizard" / "tests"]))
    for token in ("JSONL", "extension", "container", "ucode", "runtime boot"):
        if token.lower() not in test_text.lower():
            findings.append(f"test evidence missing keyword: {token}")

    status = "pass" if not findings else "warn"
    return CheckResult(6, "Test Coverage", status, "Check expected test taxonomy and runtime contract evidence.", findings[:80])


def _run_optional_tool(cmd: list[str]) -> tuple[str, int, str]:
    name = cmd[0]
    if shutil.which(name) is None:
        return (name, 127, "not installed")
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    out = (proc.stdout + "\n" + proc.stderr).strip()
    return (name, proc.returncode, out[:600])


def check_7_duplicate_code() -> CheckResult:
    findings: list[str] = []
    tool_cmds = [
        ["jscpd", "--silent", "--min-lines", "20", "--min-tokens", "100", "."],
        ["pmd", "--help"],
        ["golangci-lint", "run", "--out-format", "line-number"],
        ["flake8", "core", "wizard", "tools"],
    ]
    for cmd in tool_cmds:
        name, code, output = _run_optional_tool(cmd)
        if code == 127:
            findings.append(f"{name}: not installed")
        elif code != 0:
            findings.append(f"{name}: returned {code}")
            if output:
                findings.append(f"{name}: {output.splitlines()[0]}")

    dead_code_script = REPO_ROOT / "tools" / "ci" / "check_v1_3_25_dead_code_sweep.py"
    if dead_code_script.exists():
        proc = subprocess.run(
            [sys.executable, str(dead_code_script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            findings.append("dead-code-sweep: duplicate function guard failed")
    else:
        findings.append("dead-code-sweep script missing")

    status = _status_from_counts(
        fails=sum(1 for f in findings if "returned" in f or "failed" in f),
        warns=sum(1 for f in findings if "not installed" in f),
    )
    return CheckResult(7, "Duplicate Code Detection", status, "Run configured duplicate/lint analyzers where available.", findings[:120])


def check_8_deprecated_code() -> CheckResult:
    markers = ("TODO", "DEPRECATED", "OLD", "LEGACY", "REMOVE", "TEMP")
    findings: list[str] = []
    for path in _iter_text_files([REPO_ROOT / "core", REPO_ROOT / "wizard", REPO_ROOT / "extensions", REPO_ROOT / "containers", REPO_ROOT / "tui"]):
        text = _read_text(path)
        for idx, line in enumerate(text.splitlines(), start=1):
            if any(marker in line for marker in markers):
                findings.append(f"{path.relative_to(REPO_ROOT)}:{idx}")
                if len(findings) >= 120:
                    break
        if len(findings) >= 120:
            break
    status = "pass" if not findings else "warn"
    return CheckResult(8, "Deprecated Code Audit", status, "Scan runtime surface for legacy/deprecation markers.", findings)


def check_9_extension_contract() -> CheckResult:
    findings: list[str] = []
    ext_root = REPO_ROOT / "extensions"
    if not ext_root.exists():
        return CheckResult(9, "Extension Compatibility Check", "fail", "extensions/ is required.", ["extensions/ missing"])

    for ext_dir in sorted([p for p in ext_root.iterdir() if p.is_dir()]):
        manifest = ext_dir / "extension.json"
        if not manifest.exists():
            findings.append(f"{ext_dir.relative_to(REPO_ROOT)} missing extension.json")
            continue
        for required in ("commands", "ucode", "help", "tests"):
            if not (ext_dir / required).exists():
                findings.append(f"{ext_dir.relative_to(REPO_ROOT)} missing {required}/")
        try:
            payload = json.loads(_read_text(manifest))
            if any(str(v).startswith("/") for v in payload.values() if isinstance(v, str)):
                findings.append(f"{manifest.relative_to(REPO_ROOT)} contains absolute path values")
        except Exception as exc:
            findings.append(f"{manifest.relative_to(REPO_ROOT)} invalid json: {exc}")

    status = "pass" if not findings else "warn"
    return CheckResult(9, "Extension Compatibility Check", status, "Validate extension contract layout and metadata.", findings[:120])


def check_10_container_runtime() -> CheckResult:
    findings: list[str] = []
    container_root = REPO_ROOT / "containers"
    if not container_root.exists():
        return CheckResult(10, "Container Runtime Validation", "fail", "containers/ is required.", ["containers/ missing"])

    container_files = _iter_text_files([container_root, REPO_ROOT / "docker-compose.yml", REPO_ROOT / "Dockerfile"])
    joined = "\n".join(_read_text(p) for p in container_files)
    if "UDOS_ROOT" not in joined:
        findings.append("container definitions do not reference UDOS_ROOT")
    for path in container_files:
        findings.extend(_find_matches(path, HARD_PATH_PATTERNS))
        if len(findings) >= 80:
            break

    if shutil.which("docker") is None:
        findings.append("docker not installed; build validation skipped")
    else:
        proc = subprocess.run(
            ["docker", "compose", "config"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            findings.append("docker compose config failed")

    status = _status_from_counts(
        fails=sum(1 for f in findings if "failed" in f or "/Users/" in f or "/home/" in f),
        warns=sum(1 for f in findings if "skipped" in f),
    )
    return CheckResult(10, "Container Runtime Validation", status, "Validate container portability and compose integrity.", findings[:120])


def check_11_tui_contract() -> CheckResult:
    findings: list[str] = []
    tui_files = _iter_text_files([REPO_ROOT / "core" / "tui", REPO_ROOT / "tui"])
    joined = "\n".join(_read_text(p) for p in tui_files)
    for token in ("block", "column", "ascii", "teletext", "progress", "event"):
        if token not in joined:
            findings.append(f"missing TUI output token evidence: {token}")

    tests_joined = "\n".join(_read_text(p) for p in _iter_text_files([REPO_ROOT / "tests", REPO_ROOT / "core" / "tests"]))
    if "jsonl" not in tests_joined.lower():
        findings.append("JSONL protocol test evidence missing")

    status = "pass" if not findings else "warn"
    return CheckResult(11, "TUI Contract Validation", status, "Check TUI output contract tokens and JSONL evidence.", findings[:80])


def check_12_ucode_engine() -> CheckResult:
    findings: list[str] = []
    core_ucode = REPO_ROOT / "core" / "tui" / "ucode.py"
    if not core_ucode.exists():
        findings.append("core/tui/ucode.py missing")
    tests = list((REPO_ROOT / "core" / "tests").glob("*ucode*")) + list((REPO_ROOT / "tests").glob("*ucode*"))
    if not tests:
        findings.append("ucode tests missing")
    text = _read_text(core_ucode) if core_ucode.exists() else ""
    for token in ("if ", "for ", "while ", "error", "debug"):
        if token not in text:
            findings.append(f"ucode engine capability evidence missing token: {token.strip()}")
    status = "pass" if not findings else "warn"
    return CheckResult(12, "ucode Engine Validation", status, "Validate parser/runtime capability surface evidence.", findings[:80])


def check_13_gameplay_progression() -> CheckResult:
    findings: list[str] = []
    expected = [
        REPO_ROOT / "docs" / "examples" / "ghost-to-wizard-script.md",
        REPO_ROOT / "docs" / "examples" / "ucode_v1_5_release_pack" / "06-ghost-to-wizard-onboarding.md",
    ]
    for item in expected:
        if not item.exists():
            findings.append(f"missing gameplay progression artifact: {item.relative_to(REPO_ROOT)}")
    if not (REPO_ROOT / "missions").exists():
        findings.append("missions/ missing")
    status = "pass" if not findings else "warn"
    return CheckResult(13, "Gameplay Progression Validation", status, "Check Ghost to Wizard artifact and mission state surface.", findings)


def check_14_research_engine() -> CheckResult:
    findings: list[str] = []
    if not (REPO_ROOT / "core" / "binder").exists():
        findings.append("core/binder/ missing")
    required_tests = [
        REPO_ROOT / "core" / "tests" / "binder_research_import_test.py",
    ]
    for path in required_tests:
        if not path.exists():
            findings.append(f"missing research test: {path.relative_to(REPO_ROOT)}")
    binder_docs = list((REPO_ROOT / "docs" / "howto").glob("*BINDER*"))
    if not binder_docs:
        findings.append("binder/research docs missing in docs/howto")
    status = "pass" if not findings else "warn"
    return CheckResult(14, "Research Engine Validation", status, "Validate binder/research ingestion and docs evidence.", findings)


def check_15_markdown_workflows() -> CheckResult:
    findings: list[str] = []
    required_files = ("project.json", "agents.md", "tasks.json", "completed.json")
    for filename in required_files:
        candidates = [
            REPO_ROOT / filename,
            REPO_ROOT / "dev" / "ops" / filename,
            REPO_ROOT / "dev" / "ops" / filename.upper(),
            REPO_ROOT / "dev" / filename,
        ]
        if not any(path.exists() for path in candidates):
            findings.append(f"missing workflow file: {filename}")
    status = "pass" if not findings else "warn"
    return CheckResult(15, "Markdown Workflow Validation", status, "Check md/json workflow state files for dev operations.", findings)


def check_16_api_model_runtime() -> CheckResult:
    findings: list[str] = []
    service_files = _iter_text_files([REPO_ROOT / "core" / "services", REPO_ROOT / "wizard" / "services"])
    joined = "\n".join(_read_text(p) for p in service_files)
    for token in ("fallback", "budget", "api key", "model", "gpt4all"):
        if token not in joined.lower():
            findings.append(f"runtime/model keyword evidence missing: {token}")
    status = "pass" if not findings else "warn"
    return CheckResult(16, "API & Model Runtime Validation", status, "Check orchestration, fallback, and key-management evidence.", findings[:80])


def check_17_installation() -> CheckResult:
    findings: list[str] = []
    installer = REPO_ROOT / "bin" / "install-udos.sh"
    if not installer.exists():
        findings.append("bin/install-udos.sh missing")
    if installer.exists():
        proc = subprocess.run(
            ["/bin/bash", str(installer), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode not in {0, 1, 2}:
            findings.append("install script --help failed unexpectedly")
    install_doc = REPO_ROOT / "docs" / "INSTALLATION.md"
    if install_doc.exists():
        text = _read_text(install_doc).lower()
        for token in ("linux", "mac", "offline", "container", "update"):
            if token not in text:
                findings.append(f"installation docs missing scenario keyword: {token}")
    else:
        findings.append("docs/INSTALLATION.md missing")
    status = "pass" if not findings else "warn"
    return CheckResult(17, "Installation Validation", status, "Verify install surface and scenario coverage evidence.", findings)


def check_18_performance_stability() -> CheckResult:
    findings: list[str] = []
    expected = [
        REPO_ROOT / "tools" / "bench" / "long_run_soak_v1_3_25.py",
        REPO_ROOT / "tools" / "bench" / "benchmark_v1_3_21_runtime.py",
    ]
    for path in expected:
        if not path.exists():
            findings.append(f"missing benchmark/stability artifact: {path.relative_to(REPO_ROOT)}")
    status = "pass" if not findings else "warn"
    return CheckResult(18, "Performance & Stability", status, "Check stress/performance tooling artifacts.", findings)


def check_19_release_packaging() -> CheckResult:
    findings: list[str] = []
    if not (REPO_ROOT / "version.json").exists():
        findings.append("version.json missing")
    if not (REPO_ROOT / "CHANGELOG.md").exists():
        findings.append("CHANGELOG.md missing")
    migration_docs = list((REPO_ROOT / "docs" / "howto").glob("*MIGRATION*"))
    if not migration_docs:
        findings.append("migration notes missing in docs/howto")
    if not (REPO_ROOT / "packaging.manifest.json").exists():
        findings.append("packaging.manifest.json missing")
    status = "pass" if not findings else "warn"
    return CheckResult(19, "Release Packaging", status, "Verify release metadata/changelog/migration assets.", findings)


def check_20_wizard_certification() -> CheckResult:
    findings: list[str] = []
    cert = REPO_ROOT / "docs" / "examples" / "ucode_v1_5_release_pack" / "certification.json"
    if not cert.exists():
        findings.append("wizard certification artifact missing: docs/examples/ucode_v1_5_release_pack/certification.json")
    else:
        try:
            payload = json.loads(_read_text(cert))
            if "wizard" not in json.dumps(payload).lower() and "ghost" not in json.dumps(payload).lower():
                findings.append("certification.json does not include Ghost/Wizard journey evidence")
        except Exception as exc:
            findings.append(f"certification.json invalid: {exc}")
    status = "pass" if not findings else "warn"
    return CheckResult(20, "Final Wizard Certification", status, "Validate end-to-end Ghost to Wizard certification artifact.", findings)


def evaluate_checklist() -> list[CheckResult]:
    return [
        check_1_repository_structure(),
        check_2_hardcoded_paths_env(),
        check_3_feature_completion(),
        check_4_demo_coverage(),
        check_5_help_docs(),
        check_6_test_coverage(),
        check_7_duplicate_code(),
        check_8_deprecated_code(),
        check_9_extension_contract(),
        check_10_container_runtime(),
        check_11_tui_contract(),
        check_12_ucode_engine(),
        check_13_gameplay_progression(),
        check_14_research_engine(),
        check_15_markdown_workflows(),
        check_16_api_model_runtime(),
        check_17_installation(),
        check_18_performance_stability(),
        check_19_release_packaging(),
        check_20_wizard_certification(),
    ]


def _score(results: list[CheckResult]) -> tuple[float, dict[str, int]]:
    totals = {"pass": 0, "warn": 0, "fail": 0}
    sum_score = 0.0
    for item in results:
        totals[item.status] += 1
        if item.status == "pass":
            sum_score += 1.0
        elif item.status == "warn":
            sum_score += 0.5
    score = round((sum_score / max(len(results), 1)) * 100.0, 2)
    return score, totals


def _gate_status(score: float, totals: dict[str, int]) -> str:
    if totals["fail"] > 0:
        return "BLOCKED"
    if score < 90.0:
        return "AT_RISK"
    return "READY"


def _make_report(*, target_version: str, results: list[CheckResult]) -> dict[str, Any]:
    score, totals = _score(results)
    return {
        "schema": "udos.release.audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_version": target_version,
        "repo_root": str(REPO_ROOT),
        "release_readiness_score": score,
        "release_gate_status": _gate_status(score, totals),
        "summary": totals,
        "checks": [asdict(item) for item in results],
    }


def _write_dev_mode_projection(target_version: str, report: dict[str, Any]) -> Path:
    slug = target_version.lower().replace(" ", "-").replace(".", "_")
    plan_path = REPO_ROOT / "dev" / "ops" / "release" / slug / "future_release_plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    backlog = [
        {
            "section": item["section"],
            "name": item["name"],
            "status": item["status"],
            "next_action": item["findings"][0] if item["findings"] else "No action required",
        }
        for item in report["checks"]
        if item["status"] in {"warn", "fail"}
    ]
    payload = {
        "target_version": target_version,
        "generated_at": report["generated_at"],
        "score": report["release_readiness_score"],
        "gate": report["release_gate_status"],
        "backlog": backlog,
    }
    plan_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return plan_path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="uDOS automated pre-release audit")
    parser.add_argument("--target-version", default="v1.5")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any warning/failure exists.")
    parser.add_argument("--dev-mode", action="store_true", help="Write Dev Mode forward-planning artifact.")
    parser.add_argument("--report-path", default=None, help="Override audit report output path.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    os.environ.setdefault("UDOS_ROOT", str(REPO_ROOT))

    results = evaluate_checklist()
    report = _make_report(target_version=args.target_version, results=results)
    report_path = Path(args.report_path) if args.report_path else (DEFAULT_DEV_REPORT_PATH if args.dev_mode else DEFAULT_REPORT_PATH)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    dev_mode_plan = None
    if args.dev_mode:
        dev_mode_plan = _write_dev_mode_projection(args.target_version, report)

    if args.json_output:
        payload = {
            **report,
            "report_path": str(report_path),
            "dev_mode_plan_path": str(dev_mode_plan) if dev_mode_plan else None,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"uDOS pre-release audit for {args.target_version}")
        print(f"score={report['release_readiness_score']} gate={report['release_gate_status']}")
        print(f"pass={report['summary']['pass']} warn={report['summary']['warn']} fail={report['summary']['fail']}")
        print(f"report: {report_path.relative_to(REPO_ROOT)}")
        if dev_mode_plan is not None:
            print(f"dev-mode-plan: {dev_mode_plan.relative_to(REPO_ROOT)}")
        for item in report["checks"]:
            print(f"[{item['status'].upper()}] {item['section']:02d} {item['name']}")
            if item["findings"]:
                print(f"  - {item['findings'][0]}")

    fail_count = report["summary"]["fail"]
    warn_count = report["summary"]["warn"]
    if args.strict:
        return 1 if (fail_count > 0 or warn_count > 0) else 0
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
