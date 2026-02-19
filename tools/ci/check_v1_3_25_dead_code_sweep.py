#!/usr/bin/env python3
"""v1.3.25 dead-code sweep (python + ts) with duplicate-function guardrail."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set

REPO = Path(__file__).resolve().parents[2]
PY_ROOTS = [REPO / "core", REPO / "wizard", REPO / "tools"]
TS_ROOTS = [REPO / "core" / "src", REPO / "wizard" / "static"]
REPORT_PATH = REPO / "memory" / "reports" / "v1_3_25_dead_code_sweep.json"


@dataclass
class Finding:
    path: str
    line: int
    message: str


def _iter_py_files() -> List[Path]:
    out: List[Path] = []
    for root in PY_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(part in {"__pycache__", "venv", "dist", "node_modules", "tests"} for part in path.parts):
                continue
            out.append(path)
    return out


def _scan_python() -> Dict[str, List[Finding]]:
    duplicates: List[Finding] = []
    unused_private: List[Finding] = []

    for path in _iter_py_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        func_defs: Dict[str, int] = {}
        top_names: Set[str] = set()
        referenced: Set[str] = set()

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                name = node.name
                top_names.add(name)
                if name in func_defs:
                    duplicates.append(Finding(str(path.relative_to(REPO)), node.lineno, f"duplicate top-level function: {name}"))
                else:
                    func_defs[name] = node.lineno
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        top_names.add(target.id)

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                referenced.add(node.id)

        for name, line in func_defs.items():
            if name.startswith("_") and name not in referenced:
                unused_private.append(
                    Finding(str(path.relative_to(REPO)), line, f"potentially unused private function: {name}")
                )

    return {"duplicates": duplicates, "unused_private": unused_private}


def _iter_ts_files() -> List[Path]:
    out: List[Path] = []
    for root in TS_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".ts", ".tsx", ".js", ".mjs", ".cjs"}:
                continue
            if any(part in {"dist", "node_modules", "coverage", "tests"} for part in path.parts):
                continue
            out.append(path)
    return out


def _scan_ts_private_candidates() -> List[Finding]:
    decl_re = re.compile(r"^\s*(?:const|function)\s+(_[A-Za-z0-9_]+)\b")
    findings: List[Finding] = []

    for path in _iter_ts_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        joined = "\n".join(lines)
        for idx, line in enumerate(lines, start=1):
            match = decl_re.search(line)
            if not match:
                continue
            name = match.group(1)
            if joined.count(name) <= 1:
                findings.append(Finding(str(path.relative_to(REPO)), idx, f"potentially unused private symbol: {name}"))

    return findings


def main() -> int:
    py = _scan_python()
    ts_private = _scan_ts_private_candidates()

    report: Dict[str, Any] = {
        "duplicate_functions": [f.__dict__ for f in py["duplicates"]],
        "python_unused_private_candidates": [f.__dict__ for f in py["unused_private"]],
        "ts_unused_private_candidates": [f.__dict__ for f in ts_private],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"duplicate_functions={len(report['duplicate_functions'])}")
    print(f"python_unused_private_candidates={len(report['python_unused_private_candidates'])}")
    print(f"ts_unused_private_candidates={len(report['ts_unused_private_candidates'])}")
    print(f"report: {REPORT_PATH.relative_to(REPO)}")

    if report["duplicate_functions"]:
        raise RuntimeError("duplicate top-level Python functions detected")

    print("[dead-code-sweep-v1.3.25] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
