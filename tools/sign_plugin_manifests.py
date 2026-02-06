#!/usr/bin/env python3
"""Sign plugin manifests using Ed25519.

Generates a repo-wide signing key in memory/plugin_signing_keys.json if missing.
Canonicalization: JSON with sorted keys, UTF-8, no signature field.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Dict, Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def _canonical_payload(manifest: Dict[str, Any]) -> bytes:
    payload = {k: manifest[k] for k in manifest if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _load_or_create_keys(path: Path) -> Dict[str, str]:
    if path.exists():
        return json.loads(path.read_text())

    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    keys = {
        "algorithm": "ED25519",
        "private_key": _b64(private.private_bytes_raw()),
        "public_key": _b64(public.public_bytes_raw()),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(keys, indent=2))
    return keys


def _sign_manifest(manifest_path: Path, keys: Dict[str, str]) -> None:
    manifest = json.loads(manifest_path.read_text())
    private = Ed25519PrivateKey.from_private_bytes(base64.b64decode(keys["private_key"]))

    signature = private.sign(_canonical_payload(manifest))
    manifest["signature"] = {
        "algorithm": keys.get("algorithm", "ED25519"),
        "publicKey": keys["public_key"],
        "signature": _b64(signature),
    }

    manifest_path.write_text(json.dumps(manifest, indent=2))


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    keys_path = repo_root / "memory" / "plugin_signing_keys.json"
    keys = _load_or_create_keys(keys_path)

    library_dir = repo_root / "library"
    if not library_dir.exists():
        print("library directory not found")
        return 1

    manifests = list(library_dir.glob("*/manifest.json"))
    if not manifests:
        print("no manifests found")
        return 1

    for path in manifests:
        _sign_manifest(path, keys)

    print(f"signed {len(manifests)} manifest(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
