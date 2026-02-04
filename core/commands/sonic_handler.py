"""SONIC command handler - Sonic Screwdriver planning utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Any

from core.commands.base import BaseCommandHandler
from core.services.logging_service import get_logger, LogTags

logger = get_logger("command-sonic")


class SonicHandler(BaseCommandHandler):
    """Handler for SONIC command - USB builder planning + status."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not self._sonic_root().exists():
            return {
                "status": "error",
                "message": "Sonic extension not installed.",
                "suggestion": "Install the sonic submodule or extension package, then retry.",
            }
        if not params:
            return self._help()

        action = params[0].lower()
        if action in {"help", "list"}:
            return self._help()
        if action == "status":
            return self._status()
        if action == "plan":
            return self._plan(params[1:])
        if action == "run":
            return self._run(params[1:])

        return {
            "status": "error",
            "message": f"Unknown SONIC action '{params[0]}'. Use SONIC HELP.",
        }

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _sonic_root(self) -> Path:
        return self._repo_root() / "sonic"

    def _parse_flags(self, params: List[str]) -> Tuple[Dict[str, Any], List[str]]:
        flags: Dict[str, Any] = {}
        args: List[str] = []
        it = iter(params)
        for token in it:
            if not token.startswith("--"):
                args.append(token)
                continue
            key = token[2:]
            if key in {
                "dry-run",
                "v2",
                "skip-payloads",
                "payloads-only",
                "no-validate-payloads",
                "confirm",
            }:
                flags[key] = True
                continue
            try:
                flags[key] = next(it)
            except StopIteration:
                flags[key] = None
        return flags, args

    def _status(self) -> Dict:
        sonic_root = self._sonic_root()
        dataset_root = sonic_root / "datasets"
        db_path = self._repo_root() / "memory" / "sonic" / "sonic-devices.db"
        return {
            "status": "ok",
            "sonic_root": str(sonic_root),
            "datasets": {
                "table": str(dataset_root / "sonic-devices.table.md"),
                "schema": str(dataset_root / "sonic-devices.schema.json"),
                "sql": str(dataset_root / "sonic-devices.sql"),
                "available": (dataset_root / "sonic-devices.table.md").exists(),
            },
            "device_db": {
                "path": str(db_path),
                "exists": db_path.exists(),
            },
        }

    def _plan(self, params: List[str]) -> Dict:
        flags, _ = self._parse_flags(params)
        sonic_root = self._sonic_root()
        out_path = flags.get("out") or "config/sonic-manifest.json"
        layout_file = flags.get("layout-file") or "config/sonic-layout.json"
        payloads_dir = flags.get("payloads-dir")

        def _resolve(path_value: str) -> Path:
            candidate = Path(path_value)
            if candidate.is_absolute():
                return candidate
            return sonic_root / candidate

        resolved_out = _resolve(out_path)
        resolved_layout = _resolve(layout_file)
        resolved_payloads = _resolve(payloads_dir) if payloads_dir else None

        from sonic.core.plan import write_plan

        try:
            manifest = write_plan(
                repo_root=sonic_root,
                usb_device=flags.get("usb-device") or "/dev/sdb",
                ventoy_version=flags.get("ventoy-version") or "1.1.10",
                dry_run=bool(flags.get("dry-run")),
                layout_path=resolved_layout,
                format_mode=flags.get("format-mode"),
                payload_dir=resolved_payloads,
                out_path=resolved_out,
            )
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}

        logger.info(f"{LogTags.LOCAL} SONIC: plan written {resolved_out}")
        return {
            "status": "ok",
            "manifest_path": str(resolved_out),
            "manifest": manifest,
            "dry_run": bool(flags.get("dry-run")),
        }

    def _run(self, params: List[str]) -> Dict:
        flags, _ = self._parse_flags(params)
        sonic_root = self._sonic_root()
        manifest = flags.get("manifest") or "config/sonic-manifest.json"
        manifest_path = Path(manifest)
        if not manifest_path.is_absolute():
            manifest_path = sonic_root / manifest_path

        cmd = ["python3", str(sonic_root / "core" / "sonic_cli.py"), "run", "--manifest", str(manifest_path)]
        if flags.get("dry-run"):
            cmd.append("--dry-run")
        if flags.get("v2"):
            cmd.append("--v2")
        if flags.get("skip-payloads"):
            cmd.append("--skip-payloads")
        if flags.get("payloads-only"):
            cmd.append("--payloads-only")
        if flags.get("payloads-dir"):
            cmd.extend(["--payloads-dir", str(flags.get("payloads-dir"))])
        if flags.get("no-validate-payloads"):
            cmd.append("--no-validate-payloads")

        if not flags.get("confirm"):
            return {
                "status": "preview",
                "message": "Add --confirm to execute the Sonic build command.",
                "command": " ".join(cmd),
            }

        import subprocess

        logger.info(f"{LogTags.LOCAL} SONIC: executing {' '.join(cmd)}")
        rc = subprocess.call(cmd)
        return {
            "status": "ok" if rc == 0 else "error",
            "return_code": rc,
            "command": " ".join(cmd),
        }

    def _help(self) -> Dict:
        return {
            "status": "ok",
            "syntax": [
                "SONIC STATUS",
                "SONIC PLAN [--usb-device /dev/sdb] [--layout-file config/sonic-layout.json]",
                "SONIC PLAN [--payloads-dir /path/to/payloads] [--format-mode full|skip]",
                "SONIC RUN [--manifest config/sonic-manifest.json] [--dry-run] [--v2]",
                "SONIC RUN [--payloads-dir /path/to/payloads] [--no-validate-payloads] --confirm",
            ],
            "note": "SONIC RUN requires --confirm and Linux for destructive operations.",
        }
