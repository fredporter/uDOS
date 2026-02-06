#!/usr/bin/env python3
"""
Wizard Secret Store CLI

Manage secrets.tomb safely (admin token, provider keys).
Defaults to storing generated keys/tokens in memory/bank/private (local-only).
"""

from __future__ import annotations

import argparse
import os
import secrets
from pathlib import Path

from wizard.services.secret_store import get_secret_store, SecretEntry, SecretStoreError


def _ensure_private_dir(repo_root: Path) -> Path:
    private_dir = repo_root / "memory" / "private"
    private_dir.mkdir(parents=True, exist_ok=True)
    return private_dir


def _read_key_file(key_path: Path) -> str:
    if not key_path.exists():
        return ""
    return key_path.read_text().strip()


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def init_key(repo_root: Path, key_path: Path) -> str:
    key = secrets.token_urlsafe(48)
    _write_file(key_path, key)
    return key


def unlock_store(key_material: str | None) -> None:
    store = get_secret_store()
    store.unlock(key_material=key_material)


def set_admin_token(
    repo_root: Path,
    key_id: str,
    output_path: Path,
    init_if_missing: bool,
) -> dict:
    private_dir = _ensure_private_dir(repo_root)
    key_path = private_dir / "wizard_secret_store.key"

    key_material = os.environ.get("WIZARD_KEY") or os.environ.get("WIZARD_KEY_PEER")
    if not key_material:
        key_material = _read_key_file(key_path)

    if not key_material:
        if not init_if_missing:
            raise RuntimeError("No WIZARD_KEY available and init disabled")
        key_material = init_key(repo_root, key_path)

    unlock_store(key_material)

    token = secrets.token_urlsafe(48)
    store = get_secret_store()
    entry = SecretEntry(
        key_id=key_id,
        provider="wizard-admin",
        value=token,
    )
    store.set(entry)

    _write_file(output_path, token)

    return {
        "key_id": key_id,
        "token_path": str(output_path),
        "key_path": str(key_path),
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description="Wizard secret store utility")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init_parser = sub.add_parser("init-key", help="Generate a new secret store key")
    init_parser.add_argument(
        "--path",
        default=str(repo_root / "memory" / "private" / "wizard_secret_store.key"),
    )

    admin_parser = sub.add_parser("set-admin-token", help="Generate and store admin token")
    admin_parser.add_argument("--key-id", default="wizard-admin-token")
    admin_parser.add_argument(
        "--output",
        default=str(repo_root / "memory" / "private" / "wizard_admin_token.txt"),
    )
    admin_parser.add_argument(
        "--init-if-missing",
        action="store_true",
        default=True,
        help="Create a new secret store key if none exists",
    )

    args = parser.parse_args()

    if args.cmd == "init-key":
        key_path = Path(args.path)
        key = init_key(repo_root, key_path)
        print(f"✅ Secret store key created at: {key_path}")
        print("ℹ️  Export WIZARD_KEY to use this key.")
        return

    if args.cmd == "set-admin-token":
        output_path = Path(args.output)
        result = set_admin_token(
            repo_root,
            key_id=args.key_id,
            output_path=output_path,
            init_if_missing=args.init_if_missing,
        )
        print("✅ Admin token stored in secret store")
        print(f"   key_id: {result['key_id']}")
        print(f"   token_path: {result['token_path']}")
        print(f"   key_path: {result['key_path']}")
        return


if __name__ == "__main__":
    main()
