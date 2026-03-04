"""CLI wrapper for managing the local Wizard daemon lifecycle."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.services.background_service_manager import get_wizard_process_manager


def _tail(path: Path, lines: int = 120) -> str:
    if not path.exists():
        return f"log file not found: {path}"
    rows = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(rows[-max(1, lines):])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wizardd", add_help=True)
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=("start", "stop", "restart", "status", "health", "logs"),
    )
    parser.add_argument("--base-url", dest="base_url", default=None)
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--require-scheduler", action="store_true", default=False)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    manager = get_wizard_process_manager()

    match args.command:
        case "start":
            status = manager.ensure_running(
                base_url=args.base_url,
                wait_seconds=25,
                auto_repair=args.repair,
                require_scheduler=args.require_scheduler,
            )
            if status.connected:
                print(f"wizardd running ({status.base_url}) pid={status.pid or 'unknown'}")
                return 0
            print(f"wizardd unavailable: {status.message}")
            return 1
        case "stop":
            status = manager.stop(base_url=args.base_url, timeout_seconds=8)
            if status.connected or status.running:
                print("wizardd stop incomplete")
                return 1
            print("wizardd stopped")
            return 0
        case "restart":
            _ = manager.stop(base_url=args.base_url, timeout_seconds=8)
            status = manager.ensure_running(
                base_url=args.base_url,
                wait_seconds=25,
                auto_repair=args.repair,
                require_scheduler=args.require_scheduler,
            )
            if status.connected:
                print(f"wizardd running ({status.base_url}) pid={status.pid or 'unknown'}")
                return 0
            print(f"wizardd unavailable: {status.message}")
            return 1
        case "status":
            status = manager.status(base_url=args.base_url)
            if status.connected:
                print(f"running (pid {status.pid or 'unknown'})")
                return 0
            if status.running:
                print(f"starting/unhealthy (pid {status.pid or 'unknown'})")
                return 1
            print("stopped")
            return 0
        case "health":
            status = manager.status(base_url=args.base_url)
            scheduler_ok = (
                not args.require_scheduler or bool((status.scheduler or {}).get("healthy"))
            )
            if status.connected and scheduler_ok:
                print(f"healthy ({status.base_url}/health)")
                return 0
            print(f"unreachable ({status.base_url}/health)")
            return 1
        case "logs":
            print(_tail(manager.log_file))
            return 0
        case _:
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
