"""SONIC command handler - Sonic Screwdriver planning utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Any

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, LogTags

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
        if action == "sync":
            return self._sync(params[1:])
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
            "wizard_api": {
                "status": "/api/platform/sonic/status",
                "device_db": "/api/sonic/db/status",
                "sync": "/api/sonic/sync",
            },
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

    def _sync(self, params: List[str]) -> Dict:
        flags, _ = self._parse_flags(params)
        sonic_root = self._sonic_root()
        sql_source = sonic_root / "datasets" / "sonic-devices.sql"
        db_path = self._repo_root() / "memory" / "sonic" / "sonic-devices.db"

        if not sql_source.exists():
            return {
                "status": "error",
                "message": f"Sonic dataset SQL missing: {sql_source}",
                "suggestion": "Initialize/update the sonic submodule, then run SONIC SYNC again.",
            }

        db_path.parent.mkdir(parents=True, exist_ok=True)
        force = bool(flags.get("force"))
        command = ["sqlite3", str(db_path)]
        if db_path.exists() and not force:
            return {
                "status": "ok",
                "message": "Device DB already exists. Use SONIC SYNC --force to rebuild.",
                "db_path": str(db_path),
                "wizard_equivalent": "POST /api/sonic/db/rebuild?force=false",
            }

        if db_path.exists():
            try:
                db_path.unlink()
            except OSError as exc:
                return {
                    "status": "error",
                    "message": f"Failed to replace existing DB: {exc}",
                    "db_path": str(db_path),
                }

        import subprocess

        try:
            with sql_source.open("r", encoding="utf-8") as sql_fh:
                proc = subprocess.run(
                    command,
                    stdin=sql_fh,
                    capture_output=True,
                    text=True,
                    check=False,
                )
        except FileNotFoundError:
            return {
                "status": "error",
                "message": "sqlite3 is not installed; cannot sync Sonic device DB locally.",
                "suggestion": "Install sqlite3 or use Wizard endpoint POST /api/sonic/db/rebuild.",
            }

        if proc.returncode != 0:
            return {
                "status": "error",
                "message": "Sonic DB sync failed.",
                "stderr": (proc.stderr or "").strip(),
                "command": " ".join(command),
            }

        return {
            "status": "ok",
            "message": "Sonic device DB synced from dataset SQL.",
            "db_path": str(db_path),
            "wizard_equivalent": "POST /api/sonic/db/rebuild",
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

        try:
            from sonic.core.plan import write_plan
        except ImportError:
            return {
                "status": "error",
                "message": "Sonic extension not available",
                "suggestion": "Install sonic extension or check SONIC_ROOT path",
            }

        try:
            manifest = write_plan(
                repo_root=sonic_root,
                usb_device=flags.get("usb-device") or "/dev/sdb",
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
                "SONIC SYNC [--force]",
                "SONIC PLAN [--usb-device /dev/sdb] [--layout-file config/sonic-layout.json]",
                "SONIC PLAN [--payloads-dir /path/to/payloads] [--format-mode full|skip]",
                "SONIC RUN [--manifest config/sonic-manifest.json] [--dry-run]",
                "SONIC RUN [--payloads-dir /path/to/payloads] [--no-validate-payloads] --confirm",
            ],
            "note": "SONIC RUN requires --confirm and Linux for destructive operations. SONIC SYNC mirrors Wizard /api/sonic/db/rebuild.",
        }
