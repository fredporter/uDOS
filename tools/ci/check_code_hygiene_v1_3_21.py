#!/usr/bin/env python3
"""Debug-round code hygiene checks for v1.3.21+ stabilization.

Checks:
- hardcoded absolute paths in core/wizard/tools code
- deprecated/depreciated code markers
- duplicate Python function definitions per file
- potential unused top-level private Python functions (heuristic report)
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

REPO = Path(__file__).resolve().parents[2]
CODE_ROOTS = [REPO / "core", REPO / "wizard", REPO / "tools"]
TEXT_EXTS = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}

HARD_PATH_RE = re.compile(r"(/Users/|/home/|C:\\\\Users\\\\|C:/Users/)")
DEPRECATED_RE = re.compile(r"@deprecated|\bdepreciated\b|\bDEPRECATED\b", re.IGNORECASE)


@dataclass
class Finding:
    path: str
    line: int
    message: str


def _iter_files() -> List[Path]:
    out: List[Path] = []
    for root in CODE_ROOTS:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in TEXT_EXTS:
                continue
            if any(part in {"node_modules", "dist", "__pycache__", "venv", "coverage"} for part in path.parts):
                continue
            if "tests" in path.parts:
                continue
            out.append(path)
    return out


def _scan_text_findings(path: Path, hardcoded: List[Finding], deprecated: List[Finding]) -> None:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return
    if path.name == "check_code_hygiene_v1_3_21.py":
        return
    for idx, line in enumerate(lines, start=1):
        if HARD_PATH_RE.search(line):
            hardcoded.append(Finding(str(path.relative_to(REPO)), idx, "hardcoded absolute path"))
        if DEPRECATED_RE.search(line):
            deprecated.append(Finding(str(path.relative_to(REPO)), idx, "deprecated/depreciated marker"))


def _annotate_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)


def _scan_python_ast_with_parents(path: Path, duplicates: List[Finding], unused_candidates: List[Finding]) -> None:
    if path.suffix != ".py":
        return
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except Exception:
        return
    _annotate_parents(tree)

    func_lines: Dict[str, int] = {}
    names: List[str] = []
    referenced: Set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
            names.append(name)
            if name in func_lines:
                duplicates.append(
                    Finding(str(path.relative_to(REPO)), node.lineno, f"duplicate top-level function: {name}")
                )
            else:
                func_lines[name] = node.lineno
        elif isinstance(node, ast.Name):
            referenced.add(node.id)

    for name in names:
        if name.startswith("_") and name not in referenced:
            unused_candidates.append(
                Finding(str(path.relative_to(REPO)), func_lines[name], f"potentially unused private function: {name}")
            )


def main() -> int:
    hardcoded: List[Finding] = []
    deprecated: List[Finding] = []
    duplicates: List[Finding] = []
    unused_candidates: List[Finding] = []

    for path in _iter_files():
        _scan_text_findings(path, hardcoded, deprecated)
        _scan_python_ast_with_parents(path, duplicates, unused_candidates)

    report = {
        "hardcoded_paths": [f.__dict__ for f in hardcoded],
        "deprecated_markers": [f.__dict__ for f in deprecated],
        "duplicate_functions": [f.__dict__ for f in duplicates],
        "potential_unused_private_functions": [f.__dict__ for f in unused_candidates],
    }

    out_path = REPO / "memory" / "reports" / "code_hygiene_v1_3_21.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    fail_messages: List[str] = []
    if hardcoded:
        fail_messages.append(f"hardcoded absolute paths: {len(hardcoded)}")

    if fail_messages:
        print("[code-hygiene-v1.3.21] FAIL")
        for row in fail_messages:
            print(f"  - {row}")
        print(f"  - report: {out_path}")
        return 1

    print("[code-hygiene-v1.3.21] PASS")
    print(f"  - deprecated/depreciated markers (report-only): {len(deprecated)}")
    print(f"  - duplicate top-level python functions (report-only): {len(duplicates)}")
    print(f"  - potential unused private function candidates: {len(unused_candidates)}")
    print(f"  - report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
