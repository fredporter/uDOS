"""CLI entrypoint for packaging adapter executors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.services.packaging_adapters import linux, macos, windows


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(prog="packaging-adapter")
    parser.add_argument("platform", choices=["linux", "windows", "macos"])
    parser.add_argument("action")
    parser.add_argument("--repo-root", default=str(_repo_root()))
    parser.add_argument("--tier")
    parser.add_argument("--profile")
    parser.add_argument("--build-id")
    parser.add_argument("--source-image")
    parser.add_argument("--output-dir")
    parser.add_argument("--sign-key")
    parser.add_argument("--mode")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    match (args.platform, args.action):
        case ("linux", "sonic-default-profile"):
            print(linux.sonic_default_profile(repo_root))
        case ("linux", "build-sonic-stick"):
            payload = linux.build_sonic_stick(
                repo_root,
                profile=args.profile,
                build_id=args.build_id,
                source_image=args.source_image,
                output_dir=args.output_dir,
                sign_key=args.sign_key,
            )
            _print_json(payload)
        case ("windows", "entertainment-config"):
            _print_json(windows.entertainment_config(repo_root))
        case ("windows", "shell-path"):
            mode = args.mode or "kodi"
            print(windows.shell_path(repo_root, mode))
        case ("macos", "config"):
            _print_json(macos.config(repo_root))
        case _:
            raise SystemExit(f"Unsupported action: {args.platform} {args.action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
