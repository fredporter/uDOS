"""CLI for the canonical v1.5 uDOS launcher."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from wizard.services.udos_launcher_service import get_udos_launcher_service


def _add_release_audit_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target-version", default="v1.5")
    parser.add_argument("--no-dev-mode", action="store_true")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="udos")
    parser.add_argument("--json", action="store_true", dest="json_output")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status")

    start = sub.add_parser("start")
    start.add_argument("--no-repair", action="store_true")
    start.add_argument("--no-tui", action="store_true")

    sub.add_parser("repair")
    sub.add_parser("rebuild")

    update = sub.add_parser("update")
    update.add_argument("--remote", default="origin")
    update.add_argument("--branch", default="main")

    wizard = sub.add_parser("wizard")
    wizard.add_argument(
        "wizard_command",
        nargs="?",
        default="status",
        choices=("start", "stop", "restart", "status", "health", "logs"),
    )

    tui = sub.add_parser("tui")
    tui.add_argument("args", nargs=argparse.REMAINDER)

    ops = sub.add_parser("ops")
    ops.add_argument("args", nargs=argparse.REMAINDER)

    install = sub.add_parser("install")
    install.add_argument("--core", action="store_true")
    install.add_argument("--wizard", action="store_true")
    install.add_argument("--update", action="store_true")
    install.add_argument("--profile")
    install.add_argument("--tier")
    install.add_argument("--preflight-json", action="store_true")
    install.add_argument("args", nargs=argparse.REMAINDER)

    doctor = sub.add_parser("doctor")
    _add_release_audit_args(doctor)

    audit = sub.add_parser("audit")
    _add_release_audit_args(audit)

    release_check = sub.add_parser("release-check")
    _add_release_audit_args(release_check)
    return parser


def _run_release_audit(
    *,
    strict: bool,
    target_version: str,
    dev_mode: bool,
    json_output: bool,
) -> int:
    cmd = [
        sys.executable,
        "-m",
        "tools.ci.udos_release_audit",
        "--target-version",
        target_version,
    ]
    if strict:
        cmd.append("--strict")
    if json_output:
        cmd.append("--json")
    if dev_mode:
        cmd.append("--dev-mode")
    return subprocess.call(cmd, cwd=Path(__file__).resolve().parents[2])


def _emit(payload: dict[str, object], *, json_output: bool) -> int:
    if json_output:
        print(json.dumps(payload, indent=2))
        return int(payload.get("exit_code", 0))
    message = str(payload.get("message", "")).strip()
    if message:
        print(message)
    details = payload.get("details", {})
    if payload.get("action") == "wizard-logs" and isinstance(details, dict):
        tail = str(details.get("tail", "")).strip()
        if tail:
            print(tail)
    return int(payload.get("exit_code", 0))


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    command = args.command or "start"
    service = get_udos_launcher_service()

    if command == "tui":
        try:
            return service.launch_tui(list(args.args))
        except RuntimeError as exc:
            return _emit(
                {
                    "success": False,
                    "action": "tui",
                    "message": str(exc),
                    "details": {},
                    "exit_code": 1,
                },
                json_output=args.json_output,
            )
    if command == "install":
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "bin" / "install-udos.sh"
        install_args: list[str] = []
        if args.core:
            install_args.append("--core")
        if args.wizard:
            install_args.append("--wizard")
        if args.update:
            install_args.append("--update")
        if args.profile:
            install_args.extend(["--profile", args.profile])
        if args.tier:
            install_args.extend(["--tier", args.tier])
        if args.preflight_json:
            install_args.append("--preflight-json")
        install_args.extend(list(args.args))
        os.environ["UDOS_INSTALL_ENTRYPOINT"] = "udos"
        os.execv("/bin/bash", ["/bin/bash", str(script), *install_args])
        raise AssertionError("unreachable")
    if command in {"doctor", "audit", "release-check"}:
        strict = command == "release-check"
        return _run_release_audit(
            strict=strict,
            target_version=args.target_version,
            dev_mode=not args.no_dev_mode,
            json_output=args.json_output,
        )

    if command == "status":
        return _emit(service.status().to_dict(), json_output=args.json_output)
    if command == "start":
        no_repair = bool(getattr(args, "no_repair", False))
        no_tui = bool(getattr(args, "no_tui", False))
        result = service.start_runtime(auto_repair=not no_repair)
        if not result.success or no_tui or not sys.stdin.isatty() or not sys.stdout.isatty():
            return _emit(result.to_dict(), json_output=args.json_output)
        try:
            return service.launch_tui([])
        except RuntimeError as exc:
            return _emit(
                {
                    "success": False,
                    "action": "start",
                    "message": str(exc),
                    "details": {"runtime": result.to_dict()},
                    "exit_code": 1,
                },
                json_output=args.json_output,
            )
    if command == "repair":
        return _emit(service.repair_runtime().to_dict(), json_output=args.json_output)
    if command == "rebuild":
        return _emit(service.rebuild_runtime().to_dict(), json_output=args.json_output)
    if command == "update":
        return _emit(
            service.update_from_remote(remote=args.remote, branch=args.branch).to_dict(),
            json_output=args.json_output,
        )
    if command == "wizard":
        return _emit(
            service.wizard_command(args.wizard_command).to_dict(),
            json_output=args.json_output,
        )
    if command == "ops":
        return service.launch_ops(list(args.args))
    raise AssertionError(f"unsupported command: {command}")


if __name__ == "__main__":
    raise SystemExit(main())
