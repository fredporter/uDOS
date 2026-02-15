"""HEALTH command handler - offline/stdlib core health checks."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Tuple

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_api import get_repo_root


class HealthHandler(BaseCommandHandler):
    """Handler for HEALTH command - stdlib/offline checks only."""

    BANNED_IMPORT_ROOTS = {
        "requests",
        "urllib",
        "urllib3",
        "http",
        "socket",
        "websockets",
        "aiohttp",
        "ftplib",
        "smtplib",
        "imaplib",
        "poplib",
    }

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        repo = get_repo_root()

        checks: List[Tuple[str, bool]] = []
        checks.append(("repo root present", repo.exists()))
        checks.append(("core config present", (repo / "core" / "config").exists()))
        checks.append(("memory root present", (repo / "memory").exists()))
        checks.append(("seed bank present", (repo / "core" / "framework" / "seed" / "bank").exists()))

        network_violations = self._scan_network_imports(repo)
        checks.append(("core command path has no banned network imports", len(network_violations) == 0))

        passed = sum(1 for _, ok in checks if ok)
        failed = len(checks) - passed
        status = "success" if failed == 0 else "warning"

        output_lines = [OutputToolkit.banner("HEALTH"), ""]
        output_lines.append(OutputToolkit.checklist([(name, ok) for name, ok in checks]))
        output_lines.append("")
        output_lines.append(f"Summary: {passed}/{len(checks)} checks passed")

        if network_violations:
            output_lines.append("")
            output_lines.append("Network import findings:")
            for file_path, line_no, module in network_violations[:20]:
                output_lines.append(f"  - {file_path}:{line_no} -> {module}")
            if len(network_violations) > 20:
                output_lines.append(f"  ... and {len(network_violations) - 20} more")

        return {
            "status": status,
            "message": "Core health checks complete",
            "output": "\n".join(output_lines),
            "checks_passed": passed,
            "checks_total": len(checks),
            "network_violations": len(network_violations),
        }

    def _scan_network_imports(self, repo_root: Path) -> List[Tuple[str, int, str]]:
        target_dirs = [
            repo_root / "core" / "commands",
            repo_root / "core" / "tui",
            repo_root / "core" / "services",
        ]
        violations: List[Tuple[str, int, str]] = []

        for root in target_dirs:
            if not root.exists():
                continue
            for py_file in root.rglob("*.py"):
                try:
                    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
                except Exception:
                    continue

                rel = str(py_file.relative_to(repo_root))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            mod = alias.name
                            if mod.split(".", 1)[0] in self.BANNED_IMPORT_ROOTS:
                                violations.append((rel, node.lineno, mod))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            mod = node.module
                            if mod.split(".", 1)[0] in self.BANNED_IMPORT_ROOTS:
                                violations.append((rel, node.lineno, mod))

        return violations
