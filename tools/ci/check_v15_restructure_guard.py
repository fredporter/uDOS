#!/usr/bin/env python3
"""Guardrails for v1.5 restructure surface consistency."""

from __future__ import annotations

from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = ("core", "wizard", "bin")
SKIP_PARTS = {
    "node_modules",
    ".git",
    ".venv",
    "__pycache__",
    ".artifacts",
    "dist",
    "docs",
    "tests",
}


def should_scan(path: Path) -> bool:
    parts = set(path.parts)
    return not (parts & SKIP_PARTS)


FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "retired Sonic db route surface",
        re.compile(r"/api/sonic/db/"),
    ),
    (
        "retired Sonic integration alias route",
        re.compile(r"/api/library/integration/sonic(?:[^-\\w]|$)"),
    ),
    (
        "retired Sonic alias env toggle",
        re.compile(r"UDOS_SONIC_ENABLE_(?:LEGACY_ALIASES|LIBRARY_ALIAS)"),
    ),
    (
        "duplicate loopback constant (use core.services.loopback_host_utils)",
        re.compile(
            r'_LOOPBACK_HOSTS\s*=\s*frozenset\(\{"127\.0\.0\.1",\s*"::1",\s*"localhost"\}\)'
        ),
    ),
    (
        "retired MCP alias tool ucode_dispatch",
        re.compile(r"^def\s+ucode_dispatch\s*\(", re.MULTILINE),
    ),
)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if not should_scan(path):
                continue
            if path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".db"}:
                continue
            files.append(path)
    return files


def main() -> int:
    violations: list[str] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for label, pattern in FORBIDDEN_PATTERNS:
            if label == "retired MCP alias tool ucode_dispatch" and path.name != "mcp_server.py":
                continue
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{line_no}: {label}")

    if violations:
        print("v1.5 restructure guard failed:\n")
        for item in violations:
            print(f"- {item}")
        return 1

    gitignore_violations = _check_gitignore_contract()
    if gitignore_violations:
        print("v1.5 gitignore contract failed:\n")
        for item in gitignore_violations:
            print(f"- {item}")
        return 1

    print("v1.5 restructure guard passed.")
    return 0


def _check_gitignore_contract() -> list[str]:
    issues: list[str] = []
    root_gitignore = REPO_ROOT / ".gitignore"
    dev_gitignore = REPO_ROOT / "dev" / ".gitignore"

    if not root_gitignore.exists():
        return ["missing .gitignore"]
    if not dev_gitignore.exists():
        return ["missing dev/.gitignore"]

    root_text = root_gitignore.read_text(encoding="utf-8", errors="ignore")
    dev_text = dev_gitignore.read_text(encoding="utf-8", errors="ignore")

    required_root_entries = ("dev/files/", "dev/relecs/", "dev/dev-work/", "dev/testing/")
    required_dev_entries = ("files/", "relecs/", "dev-work/", "testing/")

    for entry in required_root_entries:
        if entry not in root_text:
            issues.append(f".gitignore missing required v1.5 @dev local-only entry: {entry}")
    for entry in required_dev_entries:
        if entry not in dev_text:
            issues.append(
                f"dev/.gitignore missing required v1.5 @dev local-only entry: {entry}"
            )

    return issues


if __name__ == "__main__":
    raise SystemExit(main())
