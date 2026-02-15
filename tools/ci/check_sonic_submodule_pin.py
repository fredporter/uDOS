#!/usr/bin/env python3
"""Validate Sonic submodule points to the public repo and is pinned/clean."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


EXPECTED_URL_RE = re.compile(r"https://github\.com/fredporter/uDOS-sonic(?:\.git)?/?$")


def run(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "git command failed")
    return proc.stdout.strip()


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    gitmodules = repo / ".gitmodules"
    if not gitmodules.exists():
        print("[sonic-submodule] FAIL: .gitmodules missing")
        return 1

    names_raw = run(repo, "config", "-f", ".gitmodules", "--name-only", "--get-regexp", r"^submodule\..*\.url$")
    names = [n for n in names_raw.splitlines() if n.strip()]

    sonic_name = None
    sonic_url = ""
    for name_key in names:
        url = run(repo, "config", "-f", ".gitmodules", "--get", name_key)
        if EXPECTED_URL_RE.search(url):
            sonic_name = name_key[len("submodule.") : -len(".url")]
            sonic_url = url
            break

    if not sonic_name:
        print("[sonic-submodule] FAIL: no submodule URL points to https://github.com/fredporter/uDOS-sonic")
        return 1

    path_key = f"submodule.{sonic_name}.path"
    sonic_path = run(repo, "config", "-f", ".gitmodules", "--get", path_key)
    if not sonic_path:
        print(f"[sonic-submodule] FAIL: missing path for submodule '{sonic_name}'")
        return 1

    status_line = run(repo, "submodule", "status", "--", sonic_path)
    if not status_line:
        print(f"[sonic-submodule] FAIL: git submodule status returned empty for '{sonic_path}'")
        return 1

    state = status_line[0]
    if state == "-":
        print(f"[sonic-submodule] FAIL: submodule '{sonic_path}' is not initialized")
        return 1
    if state in {"+", "U"}:
        print(f"[sonic-submodule] FAIL: submodule '{sonic_path}' not pinned cleanly ({status_line})")
        return 1

    path = repo / sonic_path
    if not path.exists():
        print(f"[sonic-submodule] FAIL: submodule path missing on disk: {sonic_path}")
        return 1

    dirty = run(repo, "-C", sonic_path, "status", "--porcelain")
    if dirty:
        print(f"[sonic-submodule] FAIL: submodule '{sonic_path}' has local changes")
        return 1

    print(f"[sonic-submodule] PASS: {sonic_name} ({sonic_path}) -> {sonic_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
