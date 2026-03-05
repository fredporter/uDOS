"""SONIC command handler - Sonic Screwdriver planning utilities."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, LogTags
from core.services.mode_policy import RuntimeMode, boundaries_enforced, resolve_runtime_mode
from core.services.sonic_device_service import get_sonic_device_service
from extensions.sonic_loader import load_sonic_plugin

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
        if action == "bootstrap":
            return self._bootstrap(params[1:])
        if action == "submission":
            return self._submission(params[1:])
        if action == "verify":
            return self._verify(params[1:])
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
        runtime = get_sonic_device_service(self._repo_root()).runtime_contract()
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
                "path": runtime["paths"]["legacy_db_path"],
                "exists": Path(runtime["paths"]["legacy_db_path"]).exists(),
                "seed_db_path": runtime["paths"]["seed_db_path"],
                "user_db_path": runtime["paths"]["user_db_path"],
                "seed_record_count": runtime["seed_catalog"]["record_count"],
                "user_record_count": runtime["user_catalog"]["record_count"],
                "current_machine_registered": runtime["user_catalog"]["current_machine_registered"],
            },
            "submissions": runtime["submissions"],
            "manifest": {
                "example": str(sonic_root / "config" / "sonic-manifest.json.example"),
                "default": str(sonic_root / "config" / "sonic-manifest.json"),
                "layout": str(sonic_root / "config" / "sonic-layout.json"),
            },
        }

    def _verify(self, params: List[str]) -> Dict:
        flags, _ = self._parse_flags(params)
        sonic_root = self._sonic_root()
        manifest_path = Path(flags.get("manifest") or "config/sonic-manifest.json")
        if not manifest_path.is_absolute():
            manifest_path = sonic_root / manifest_path
        build_dir = None
        if flags.get("build-dir"):
            build_dir = Path(str(flags.get("build-dir")))
            if not build_dir.is_absolute():
                build_dir = self._repo_root() / build_dir
        elif flags.get("build-id"):
            build_dir = self._repo_root() / "distribution" / "builds" / str(flags.get("build-id"))
        flash_pack = str(flags.get("flash-pack")).strip() if flags.get("flash-pack") else None

        try:
            from sonic.core.verify import verify_sonic_ready
        except ImportError:
            return {
                "status": "error",
                "message": "Sonic manifest verifier is unavailable",
                "suggestion": "Install the Sonic module and retry SONIC VERIFY.",
            }

        verification = verify_sonic_ready(
            sonic_root,
            manifest_path=manifest_path,
            build_dir=build_dir,
            flash_pack=flash_pack,
        )
        if not verification["ok"]:
            return {
                "status": "error",
                "message": "Sonic verification failed.",
                "manifest_path": str(manifest_path),
                "build_dir": str(build_dir) if build_dir else None,
                "verification": verification,
            }

        manifest_warnings = (verification.get("manifest") or {}).get("warnings", [])
        media_issues = verification.get("media_policy", {}).get("issues", [])
        release_issues = (verification.get("release_bundle") or {}).get("issues", [])
        status = "warning" if manifest_warnings or media_issues or release_issues else "ok"
        return {
            "status": status,
            "message": "Sonic verification complete.",
            "manifest_path": str(manifest_path),
            "build_dir": str(build_dir) if build_dir else None,
            "verification": verification,
        }

    def _sync(self, params: List[str]) -> Dict:
        flags, _ = self._parse_flags(params)
        sonic_root = self._sonic_root()
        sql_source = sonic_root / "datasets" / "sonic-devices.sql"
        force = bool(flags.get("force"))
        db_path = Path(get_sonic_device_service(self._repo_root()).paths.legacy_db_path)

        if not sql_source.exists():
            return {
                "status": "error",
                "message": f"Sonic dataset SQL missing: {sql_source}",
                "suggestion": "Initialize/update the sonic submodule, then run SONIC SYNC again.",
            }

        db_path.parent.mkdir(parents=True, exist_ok=True)
        if db_path.exists() and not force:
            return {
                "status": "ok",
                "message": "Device DB already exists. Use SONIC SYNC --force to rebuild.",
                "db_path": str(get_sonic_device_service(self._repo_root()).paths.legacy_db_path),
                "wizard_equivalent": "POST /api/sonic/sync/rebuild?force=false",
            }

        try:
            plugin = load_sonic_plugin(self._repo_root())
            sync_factory = plugin["sync"].DeviceDatabaseSync
            sync_service = sync_factory(repo_root=self._repo_root())
            result = sync_service.rebuild_database(force=force)
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to load Sonic sync service: {exc}",
                "suggestion": "Use Wizard endpoint POST /api/sonic/sync/rebuild as fallback.",
            }

        if result.get("status") == "error":
            return {
                "status": "error",
                "message": result.get("message", "Sonic DB sync failed."),
            }
        if result.get("status") == "skip":
            return {
                "status": "ok",
                "message": result.get("message", "Device DB already exists."),
                "result": result,
                "db_path": str(db_path),
                "wizard_equivalent": "POST /api/sonic/sync/rebuild?force=false",
            }

        return {
            "status": "ok",
            "message": "Sonic device DB sync delegated to canonical plugin sync service.",
            "result": result,
            "wizard_equivalent": "POST /api/sonic/sync/rebuild",
        }

    def _bootstrap(self, params: List[str]) -> Dict:
        flags, _ = self._parse_flags(params)
        overwrite = not bool(flags.get("no-overwrite"))
        try:
            plugin = load_sonic_plugin(self._repo_root())
            sync_service = plugin["sync"].get_sync_service()
            result = sync_service.bootstrap_current_machine(overwrite=overwrite)
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to bootstrap Sonic current-machine record: {exc}",
                "suggestion": "Use Wizard endpoint POST /api/sonic/bootstrap/current as fallback.",
            }
        if result.get("status") != "ok":
            return {"status": "error", "message": result.get("message", "Sonic bootstrap failed.")}
        return {
            "status": "ok",
            "message": "Current machine registered in Sonic user catalog.",
            "result": result,
            "wizard_equivalent": "POST /api/sonic/bootstrap/current",
        }

    def _plan(self, params: List[str]) -> Dict:
        mode = resolve_runtime_mode()
        if mode not in {RuntimeMode.WIZARD, RuntimeMode.DEV} and boundaries_enforced():
            return {
                "status": "warning",
                "message": "SONIC PLAN is restricted outside Wizard/Dev mode",
                "output": (
                    "Boundary enforcement is active: SONIC planning is restricted to Wizard/Dev modes.\n"
                    "Switch to Wizard mode or disable boundary enforcement explicitly for local testing."
                ),
                "policy_flag": "wizard_mode_required",
            }

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
            from sonic.core.manifest import validate_manifest_data
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

        verification = validate_manifest_data(manifest, manifest_path=resolved_out)
        logger.info(f"{LogTags.LOCAL} SONIC: plan written {resolved_out}")
        policy_flag = None
        policy_note = None
        if mode not in {RuntimeMode.WIZARD, RuntimeMode.DEV}:
            policy_flag = "wizard_mode_recommended"
            policy_note = (
                "[policy-flag] SONIC PLAN outside Wizard/Dev mode. "
                "Boundary enforcement is currently disabled by configuration."
            )
        return {
            "status": "warning" if verification["warnings"] else "ok",
            "manifest_path": str(resolved_out),
            "manifest": manifest,
            "verification": verification,
            "dry_run": bool(flags.get("dry-run")),
            **({"policy_flag": policy_flag} if policy_flag else {}),
            **({"policy_note": policy_note} if policy_note else {}),
        }

    def _submission(self, params: List[str]) -> Dict:
        if not params:
            return {
                "status": "error",
                "message": "Syntax: SONIC SUBMISSION <LIST|SUBMIT|APPROVE|REJECT> ...",
            }
        action = params[0].lower()
        flags, args = self._parse_flags(params[1:])
        service = get_sonic_device_service(self._repo_root())

        if action == "list":
            submission_status = args[0] if args else flags.get("status")
            records = service.list_submissions(status=submission_status)
            return {
                "status": "ok",
                "message": "Sonic submissions listed",
                "submission_count": len(records),
                "submissions": records,
            }

        if action == "submit":
            file_arg = flags.get("file") or (args[0] if args else None)
            if not file_arg:
                return {
                    "status": "error",
                    "message": "SONIC SUBMISSION SUBMIT requires --file <path>",
                }
            submission_path = Path(str(file_arg))
            if not submission_path.is_absolute():
                submission_path = self._repo_root() / submission_path
            if not submission_path.exists():
                return {
                    "status": "error",
                    "message": f"Submission file not found: {submission_path}",
                }
            try:
                payload = json.loads(submission_path.read_text(encoding="utf-8"))
                result = service.submit_device_submission(
                    payload, submitter=str(flags.get("submitter") or "local-user")
                )
            except ValueError as exc:
                return {"status": "error", "message": str(exc)}
            return result

        if action == "approve":
            if not args:
                return {
                    "status": "error",
                    "message": "SONIC SUBMISSION APPROVE requires <submission_id>",
                }
            return service.approve_submission(
                args[0], approved_by=str(flags.get("by") or "contributor")
            )

        if action == "reject":
            if not args:
                return {
                    "status": "error",
                    "message": "SONIC SUBMISSION REJECT requires <submission_id>",
                }
            reason = " ".join(args[1:]) if len(args) > 1 else str(flags.get("reason") or "")
            return service.reject_submission(
                args[0],
                rejected_by=str(flags.get("by") or "contributor"),
                reason=reason,
            )

        return {
            "status": "error",
            "message": f"Unknown SONIC SUBMISSION action '{params[0]}'.",
        }

    def _run(self, params: List[str]) -> Dict:
        mode = resolve_runtime_mode()
        if mode not in {RuntimeMode.WIZARD, RuntimeMode.DEV} and boundaries_enforced():
            return {
                "status": "warning",
                "message": "SONIC RUN is restricted outside Wizard/Dev mode",
                "output": (
                    "Boundary enforcement is active: SONIC run/build actions are restricted to Wizard/Dev modes.\n"
                    "Switch to Wizard mode or disable boundary enforcement explicitly for local testing."
                ),
                "policy_flag": "wizard_mode_required",
            }

        flags, _ = self._parse_flags(params)
        sonic_root = self._sonic_root()
        manifest = flags.get("manifest") or "config/sonic-manifest.json"
        manifest_path = Path(manifest)
        if not manifest_path.is_absolute():
            manifest_path = sonic_root / manifest_path

        try:
            from sonic.core.verify import verify_sonic_ready
        except ImportError:
            return {
                "status": "error",
                "message": "Sonic manifest verifier is unavailable",
                "suggestion": "Install the Sonic module and retry SONIC RUN.",
            }

        verification = verify_sonic_ready(
            sonic_root,
            manifest_path=manifest_path,
            flash_pack=(str(flags.get("flash-pack")).strip() if flags.get("flash-pack") else None),
        )
        manifest_verification = verification.get("manifest") or {"ok": False, "errors": ["manifest verification unavailable"]}
        if not manifest_verification["ok"]:
            return {
                "status": "error",
                "message": "SONIC RUN blocked: manifest failed verification.",
                "manifest_path": str(manifest_path),
                "verification": verification,
            }
        warnings = list(manifest_verification.get("warnings", []))
        warnings.extend(verification.get("media_policy", {}).get("issues", []))
        if warnings and not flags.get("no-validate-payloads"):
            return {
                "status": "warning",
                "message": "SONIC RUN blocked until verification warnings are reviewed.",
                "manifest_path": str(manifest_path),
                "verification": verification,
                "suggestion": (
                    "Fix the reported payload/layout warnings, or rerun with "
                    "--no-validate-payloads if you intentionally accept them."
                ),
            }

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

        logger.info(f"{LogTags.LOCAL} SONIC: executing {' '.join(cmd)}")
        rc = subprocess.call(cmd)
        policy_flag = None
        policy_note = None
        if mode not in {RuntimeMode.WIZARD, RuntimeMode.DEV}:
            policy_flag = "wizard_mode_recommended"
            policy_note = (
                "[policy-flag] SONIC RUN outside Wizard/Dev mode. "
                "Boundary enforcement is currently disabled by configuration."
            )
        return {
            "status": "ok" if rc == 0 else "error",
            "return_code": rc,
            "command": " ".join(cmd),
            "verification": verification,
            **({"policy_flag": policy_flag} if policy_flag else {}),
            **({"policy_note": policy_note} if policy_note else {}),
        }

    def _help(self) -> Dict:
        return {
            "status": "ok",
            "syntax": [
                "SONIC STATUS",
                "SONIC SYNC [--force]",
                "SONIC BOOTSTRAP [--no-overwrite]",
                "SONIC SUBMISSION LIST [pending|approved|rejected]",
                "SONIC SUBMISSION SUBMIT --file path/to/device.json",
                "SONIC SUBMISSION APPROVE <submission_id>",
                "SONIC SUBMISSION REJECT <submission_id> [reason]",
                "SONIC VERIFY [--manifest config/sonic-manifest.json] [--build-id <id>] [--flash-pack <pack>]",
                "SONIC PLAN [--usb-device /dev/sdb] [--layout-file config/sonic-layout.json]",
                "SONIC PLAN [--payloads-dir /path/to/payloads] [--format-mode full|skip]",
                "SONIC RUN [--manifest config/sonic-manifest.json] [--dry-run]",
                "SONIC RUN [--payloads-dir /path/to/payloads] [--no-validate-payloads] --confirm",
            ],
            "note": "SONIC VERIFY checks manifest structure, media-source policy, device DB readiness, and optional signed release bundles. SONIC RUN requires --confirm and Linux for destructive operations. SONIC SYNC mirrors Wizard /api/sonic/db/rebuild. SONIC BOOTSTRAP registers the current machine in the local user Sonic catalog. SONIC SUBMISSION manages the local submission queue and contributor approval flow.",
        }
