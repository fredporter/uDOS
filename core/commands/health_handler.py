"""HEALTH command handler - offline/stdlib core health checks."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple

from core.commands.base import BaseCommandHandler
from core.services.mission_objective_registry import MissionObjectiveRegistry
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
        if params and params[0].lower() == "check":
            return self._handle_check(params[1:])

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

    def _handle_check(self, params: List[str]) -> Dict:
        target = params[0].lower() if params else ""
        fmt = "text"
        for idx, token in enumerate(params):
            lower = token.lower()
            if lower == "--format" and idx + 1 < len(params):
                fmt = params[idx + 1].strip().lower()
            elif lower.startswith("--format="):
                fmt = lower.split("=", 1)[1].strip()
        if target in {"release-gates", "release-gate", "gates"}:
            return self._check_release_gates(fmt)
        return {
            "status": "error",
            "message": "Syntax: HEALTH CHECK release-gates [--format json|text]",
        }

    def _check_release_gates(self, fmt: str = "text") -> Dict:
        payload = MissionObjectiveRegistry().snapshot()
        summary = payload.get("summary", {})
        status = "success"
        if (
            bool(summary.get("blocker_open"))
            or bool(summary.get("contract_drift"))
            or int(summary.get("fail", 0) or 0) > 0
            or int(summary.get("error", 0) or 0) > 0
        ):
            status = "warning"

        if fmt == "json":
            output = json.dumps(payload, indent=2)
        else:
            output_lines = [OutputToolkit.banner("HEALTH CHECK release-gates"), ""]
            output_lines.append(
                "Summary: total={total} pass={pass_} fail={fail} error={error} pending={pending} blocker_open={blocker}".format(
                    total=summary.get("total", 0),
                    pass_=summary.get("pass", 0),
                    fail=summary.get("fail", 0),
                    error=summary.get("error", 0),
                    pending=summary.get("pending", 0),
                    blocker=summary.get("blocker_open", False),
                )
            )
            drift = payload.get("contract_drift", {}).get("unknown_objective_ids", [])
            if drift:
                output_lines.append("Contract drift: unknown objective ids -> " + ", ".join(drift))
            output_lines.append("")
            output_lines.append("Objectives:")
            for row in payload.get("objectives", []):
                output_lines.append(
                    f"- {row.get('id')} [{row.get('severity')}] status={row.get('status')}"
                )
            output = "\n".join(output_lines)

        return {
            "status": status,
            "message": "Release-gate mission objective status",
            "output": output,
            "release_gates": payload,
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
