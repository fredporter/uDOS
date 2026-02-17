"""HEALTH command handler - offline/stdlib core health checks."""

from __future__ import annotations

import ast
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.commands.base import BaseCommandHandler
from core.services.mission_objective_registry import MissionObjectiveRegistry
from core.tui.output import OutputToolkit
from core.services.logging_api import get_repo_root
from core.services.maintenance_utils import (
    clean,
    get_compost_root,
    get_memory_root,
    tidy,
)


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
        if params and params[0].lower() in {"tidy", "clean"}:
            return self._handle_maintenance_action(params)
        if params and params[0].lower() == "check":
            return self._handle_check(params[1:])

        repo = get_repo_root()
        storage = self._storage_payload(repo)

        checks: List[Tuple[str, bool]] = []
        checks.append(("repo root present", repo.exists()))
        checks.append(("core config present", (repo / "core" / "config").exists()))
        checks.append(("memory root present", (repo / "memory").exists()))
        checks.append(("seed bank present", (repo / "core" / "framework" / "seed" / "bank").exists()))

        network_violations = self._scan_network_imports(repo)
        checks.append(("core command path has no banned network imports", len(network_violations) == 0))
        checks.append(("local storage reserve available", bool(storage.get("reserve_ok", False))))
        checks.append(("compost root writable", bool(storage.get("compost_access_ok", False))))

        passed = sum(1 for _, ok in checks if ok)
        failed = len(checks) - passed
        status = "success" if failed == 0 else "warning"

        output_lines = [OutputToolkit.banner("HEALTH"), ""]
        output_lines.append(OutputToolkit.checklist([(name, ok) for name, ok in checks]))
        output_lines.append("")
        output_lines.append(f"Summary: {passed}/{len(checks)} checks passed")
        output_lines.append("")
        output_lines.append("Storage:")
        output_lines.append(
            "  local free: {free} / {total} ({pct:.1f}% free)".format(
                free=self._format_bytes(int(storage.get("free_bytes", 0))),
                total=self._format_bytes(int(storage.get("total_bytes", 0))),
                pct=float(storage.get("free_percent", 0.0)),
            )
        )
        output_lines.append(
            "  reserve target: {reserve} -> {ok}".format(
                reserve=self._format_bytes(int(storage.get("reserve_bytes", 0))),
                ok="ok" if storage.get("reserve_ok", False) else "low",
            )
        )
        output_lines.append(
            "  compost total: {size} ({path})".format(
                size=self._format_bytes(int(storage.get("compost_total_bytes", 0))),
                path=storage.get("compost_path", ""),
            )
        )
        tier_sizes = storage.get("compost_tiers", {})
        for tier in ("archive", "trash", "backups"):
            output_lines.append(
                f"    - {tier}: {self._format_bytes(int(tier_sizes.get(tier, 0)))}"
            )

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
            "storage": storage,
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
        if target in {"storage", "local-storage", "disk"}:
            return self._check_storage(fmt)
        return {
            "status": "error",
            "message": "Syntax: HEALTH CHECK <release-gates|storage> [--format json|text]",
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

    def _check_storage(self, fmt: str = "text") -> Dict:
        payload = self._storage_payload(get_repo_root())
        status = "success" if payload.get("reserve_ok", False) else "warning"

        if fmt == "json":
            output = json.dumps(payload, indent=2)
        else:
            tiers = payload.get("compost_tiers", {})
            output_lines = [OutputToolkit.banner("HEALTH CHECK storage"), ""]
            output_lines.append(
                "Local disk: free={free} total={total} ({pct:.1f}% free)".format(
                    free=self._format_bytes(int(payload.get("free_bytes", 0))),
                    total=self._format_bytes(int(payload.get("total_bytes", 0))),
                    pct=float(payload.get("free_percent", 0.0)),
                )
            )
            output_lines.append(
                "Reserve: {reserve} status={status}".format(
                    reserve=self._format_bytes(int(payload.get("reserve_bytes", 0))),
                    status="ok" if payload.get("reserve_ok", False) else "low",
                )
            )
            output_lines.append(
                "Compost: {size} at {path}".format(
                    size=self._format_bytes(int(payload.get("compost_total_bytes", 0))),
                    path=payload.get("compost_path", ""),
                )
            )
            for tier in ("archive", "trash", "backups"):
                output_lines.append(
                    f"- {tier}: {self._format_bytes(int(tiers.get(tier, 0)))}"
                )
            output = "\n".join(output_lines)

        return {
            "status": status,
            "message": "Local storage health status",
            "output": output,
            "storage": payload,
        }

    def _handle_maintenance_action(self, params: List[str]) -> Dict:
        action = params[0].lower()
        scope, _remaining = self._parse_scope(params[1:])
        target_root, recursive = self._resolve_scope(scope)

        if action == "tidy":
            moved, archive_root = tidy(target_root, recursive=recursive)
            title = "HEALTH TIDY"
        else:
            allowlist = None
            repo_root = get_repo_root()
            memory_root = get_memory_root()
            if target_root == repo_root:
                allowlist = self._default_repo_allowlist()
            elif target_root == memory_root:
                allowlist = self._default_memory_allowlist()
            moved, archive_root = clean(
                target_root,
                allowed_entries=allowlist,
                recursive=recursive,
            )
            title = "HEALTH CLEAN"

        storage = self._storage_payload(get_repo_root())
        output = "\n".join(
            [
                OutputToolkit.banner(title),
                f"Scope: {scope}",
                f"Target: {target_root}",
                f"Moved: {moved}",
                f"Archive: {archive_root}",
                (
                    "Storage: free={free} compost={compost}".format(
                        free=self._format_bytes(int(storage.get("free_bytes", 0))),
                        compost=self._format_bytes(int(storage.get("compost_total_bytes", 0))),
                    )
                ),
            ]
        )
        return {
            "status": "success",
            "message": f"{action.upper()} complete",
            "output": output,
            "storage": storage,
            "moved": moved,
        }

    def _parse_scope(self, params: List[str]) -> Tuple[str, List[str]]:
        if not params:
            return "workspace", []
        scope = params[0].lower()
        if scope in {"current", "+subfolders", "workspace", "all"}:
            return scope, params[1:]
        return "workspace", params

    def _resolve_scope(self, scope: str) -> Tuple[Path, bool]:
        if scope == "current":
            return Path.cwd(), False
        if scope == "+subfolders":
            return Path.cwd(), True
        if scope == "all":
            return get_repo_root(), True
        return get_memory_root(), True

    def _default_repo_allowlist(self) -> List[str]:
        return [
            ".git",
            ".github",
            ".gitignore",
            ".compost",
            "README.md",
            "LICENSE",
            "core",
            "wizard",
            "memory",
            "bin",
            "docs",
            "scripts",
            "tests",
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-wizard.txt",
            "pyproject.toml",
            "version.json",
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            ".npm-cache",
            ".env",
            ".env.example",
            "venv",
        ]

    def _default_memory_allowlist(self) -> List[str]:
        return ["bindings", "flags", "rules", "scripts", "state", "temp", ".compost"]

    def _storage_payload(self, repo_root: Path) -> Dict[str, object]:
        try:
            usage = shutil.disk_usage(repo_root)
            total = int(usage.total)
            free = int(usage.free)
        except OSError:
            total = 0
            free = 0

        reserve_mb = self._safe_float(os.getenv("UDOS_COMPOST_RESERVE_MB"), default=512.0)
        reserve_bytes = int(max(0.0, reserve_mb) * 1024 * 1024)

        compost_root = get_compost_root()
        compost_access_ok = compost_root.exists() and os.access(compost_root, os.W_OK)
        tiers: Dict[str, int] = {}
        tier_names = ("archive", "trash", "backups")
        for tier in tier_names:
            tiers[tier] = 0

        for entry in compost_root.iterdir():
            if not entry.is_dir():
                continue
            for tier in tier_names:
                tier_path = entry / tier
                if tier_path.exists():
                    tiers[tier] += self._path_size_bytes(tier_path)
        for tier in tier_names:
            direct_tier = compost_root / tier
            if direct_tier.exists():
                tiers[tier] += self._path_size_bytes(direct_tier)

        compost_total = sum(tiers.values())

        free_percent = 0.0
        if total > 0:
            free_percent = (free / total) * 100.0

        return {
            "repo_root": str(repo_root),
            "total_bytes": total,
            "free_bytes": free,
            "free_percent": round(free_percent, 2),
            "reserve_bytes": reserve_bytes,
            "reserve_ok": free >= reserve_bytes,
            "compost_path": str(compost_root),
            "compost_access_ok": compost_access_ok,
            "compost_total_bytes": compost_total,
            "compost_tiers": tiers,
        }

    def _path_size_bytes(self, path: Path) -> int:
        try:
            if path.is_file():
                return path.stat().st_size
            if path.is_dir():
                total = 0
                for root, _dirs, files in os.walk(path):
                    root_path = Path(root)
                    for name in files:
                        try:
                            total += (root_path / name).stat().st_size
                        except OSError:
                            continue
                return total
        except OSError:
            return 0
        return 0

    def _safe_float(self, value: Optional[str], default: float) -> float:
        if value is None:
            return default
        try:
            return float(value.strip())
        except ValueError:
            return default

    def _format_bytes(self, size: int) -> str:
        value = float(max(0, size))
        units = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        while value >= 1024 and idx < len(units) - 1:
            value /= 1024
            idx += 1
        return f"{value:.1f}{units[idx]}"

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
