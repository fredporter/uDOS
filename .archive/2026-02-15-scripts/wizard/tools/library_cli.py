#!/usr/bin/env python3
"""
Wizard Library CLI

Manage /library repos, packages, inventory, and toolchain.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from wizard.tools.github_dev import PluginFactory
from wizard.services.library_manager_service import get_library_manager


def main() -> None:
    parser = argparse.ArgumentParser(description="uDOS Wizard library manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("inventory", help="Show dependency inventory")
    sub.add_parser("repos", help="List cloned repos")
    sub.add_parser("packages", help="List built packages")

    clone_p = sub.add_parser("clone", help="Clone a repo into library/containers")
    clone_p.add_argument("repo")
    clone_p.add_argument("--branch", default="main")

    update_p = sub.add_parser("update", help="Update a cloned repo")
    update_p.add_argument("name")

    build_p = sub.add_parser("build", help="Build a repo package")
    build_p.add_argument("name")
    build_p.add_argument("--format", default="tar.gz", choices=["tar.gz", "zip", "tcz"])

    build_apk_p = sub.add_parser("build-apk", help="Build an Alpine APK from repo")
    build_apk_p.add_argument("name")
    build_apk_p.add_argument("--arch", default="x86_64")

    toolchain_p = sub.add_parser("toolchain", help="Update Alpine toolchain packages")
    toolchain_p.add_argument("--packages", nargs="*", default=None)

    sub.add_parser("apk-index", help="Generate APKINDEX for distribution/plugins")

    keygen_p = sub.add_parser("apk-keygen", help="Generate abuild signing keys")
    keygen_p.add_argument("--install", action="store_true")
    keygen_p.add_argument("--name", default=os.environ.get("ABUILD_KEYNAME", "udos"))

    sub.add_parser("apk-status", help="Show APK toolchain/signing status")

    args = parser.parse_args()

    if args.cmd == "inventory":
        manager = get_library_manager()
        inventory = manager.get_dependency_inventory()
        for name, info in inventory.items():
            deps = info.get("deps", {})
            print(f"{name} ({info.get('source')}):")
            for key, vals in deps.items():
                if vals:
                    print(f"  {key}: {', '.join(vals) if isinstance(vals, list) else vals}")
        return

    if args.cmd == "repos":
        factory = PluginFactory()
        repos = factory.list_repos()
        print(f"Repos: {len(repos)}")
        for repo in repos:
            print(f"- {repo['name']} ({repo.get('license', 'unknown')})")
        return

    if args.cmd == "packages":
        factory = PluginFactory()
        packages = factory.list_packages()
        print(f"Packages: {len(packages)}")
        for pkg in packages:
            print(f"- {pkg['filename']} ({pkg.get('size_bytes', 0)} bytes)")
        return

    if args.cmd == "clone":
        factory = PluginFactory()
        cloned = factory.clone(args.repo, branch=args.branch)
        if not cloned:
            raise SystemExit("Clone failed")
        print(f"Cloned: {cloned.name} -> {cloned.path}")
        return

    if args.cmd == "update":
        factory = PluginFactory()
        ok = factory.update(args.name)
        if not ok:
            raise SystemExit("Update failed")
        print(f"Updated: {args.name}")
        return

    if args.cmd == "build":
        factory = PluginFactory()
        result = factory.build(args.name, format=args.format)
        if not result.success:
            raise SystemExit("Build failed")
        print(f"Built: {result.package_path}")
        return

    if args.cmd == "build-apk":
        from wizard.services.plugin_factory import APKBuilder
        from wizard.services.path_utils import get_repo_root

        repo_root = get_repo_root()
        container_path = repo_root / "library" / "containers" / args.name
        builder = APKBuilder()
        result = builder.build_apk(args.name, container_path=container_path, arch=args.arch)
        if not result.success:
            raise SystemExit(result.error or "APK build failed")
        print(f"Built APK: {result.package_path}")
        return

    if args.cmd == "toolchain":
        manager = get_library_manager()
        result = manager.update_alpine_toolchain(packages=args.packages)
        if not result.get("success"):
            raise SystemExit(result.get("message", "Toolchain update failed"))
        print(result.get("message"))
        return

    if args.cmd == "apk-index":
        from wizard.services.plugin_factory import APKBuilder

        builder = APKBuilder()
        ok, message = builder.generate_apkindex()
        if not ok:
            raise SystemExit(message)
        print(message)
        return

    if args.cmd == "apk-status":
        from wizard.services.plugin_factory import APKBuilder
        import shutil

        builder = APKBuilder()
        abuild_ok = shutil.which("abuild") is not None
        apk_ok = shutil.which("apk") is not None
        key_ok, key_msg = builder._check_abuild_key()
        print(f"abuild: {'ok' if abuild_ok else 'missing'}")
        print(f"apk: {'ok' if apk_ok else 'missing'}")
        print(f"signing: {'ok' if key_ok else 'missing'} ({key_msg})")
        return

    if args.cmd == "apk-keygen":
        from wizard.tools.apk_keygen import main as keygen_main

        keygen_main()
        return


if __name__ == "__main__":
    main()
