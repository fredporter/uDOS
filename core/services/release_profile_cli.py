"""CLI helpers for certified release profile install flows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.services.release_profile_service import ReleaseProfileService


def _parse_profiles(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(prog="release-profile-cli")
    parser.add_argument("action", choices=["list", "summary", "install", "tier", "extensions", "packages", "resolved"])
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--profiles", default="")
    args = parser.parse_args()

    service = ReleaseProfileService(Path(args.repo_root).resolve())
    profiles = _parse_profiles(args.profiles)

    if args.action == "list":
        print(json.dumps(service.list_profiles(), indent=2))
        return 0
    if args.action == "summary":
        print(json.dumps(service.install_summary(profiles), indent=2))
        return 0
    if args.action == "install":
        print(json.dumps(service.install_profiles(profiles), indent=2))
        return 0
    if args.action == "tier":
        print(service.install_summary(profiles)["tinycore_tier"])
        return 0
    if args.action == "resolved":
        print(",".join(service.resolve_profile_ids(profiles)))
        return 0
    if args.action == "extensions":
        print(" ".join(service.extensions_for_profiles(profiles)))
        return 0
    if args.action == "packages":
        print(" ".join(service.package_groups_for_profiles(profiles)))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
