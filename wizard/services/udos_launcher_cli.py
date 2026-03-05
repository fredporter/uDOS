"""CLI for the canonical v1.5 uDOS launcher."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from wizard.services.udos_launcher_service import get_udos_launcher_service


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
    install.add_argument("args", nargs=argparse.REMAINDER)
    return parser


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

    if command == "tui":
        os.execv(
            sys.executable,
            [sys.executable, "-m", "core.tui.ucode_entry", *list(args.args)],
        )
        raise AssertionError("unreachable")
    if command == "install":
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "bin" / "install-udos.sh"
        os.execv("/bin/bash", ["/bin/bash", str(script), *list(args.args)])
        raise AssertionError("unreachable")

    service = get_udos_launcher_service()

    if command == "status":
        return _emit(service.status().to_dict(), json_output=args.json_output)
    if command == "start":
        result = service.start_runtime(auto_repair=not args.no_repair)
        if not result.success or args.no_tui or not sys.stdin.isatty() or not sys.stdout.isatty():
            return _emit(result.to_dict(), json_output=args.json_output)
        return service.launch_tui([])
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
