#!/usr/bin/env python3
"""Sign delivery manifest with Ed25519."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    delivery_dir = repo_root / "memory" / "delivery"
    delivery_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = delivery_dir / "manifest.json"
    key_path = delivery_dir / "keys.json"

    if not manifest_path.exists():
        print("manifest.json not found")
        return 1

    if key_path.exists():
        keys = json.loads(key_path.read_text())
        private_key = Ed25519PrivateKey.from_private_bytes(base64.b64decode(keys["private_key"]))
    else:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        keys = {
            "private_key": _b64(private_key.private_bytes_raw()),
            "public_key": _b64(public_key.public_bytes_raw()),
        }
        key_path.write_text(json.dumps(keys, indent=2))

    manifest = json.loads(manifest_path.read_text())
    payload = json.dumps(
        {k: manifest[k] for k in manifest if k not in {"signature", "public_key", "signed_at"}},
        sort_keys=True,
    ).encode("utf-8")

    signature = private_key.sign(payload)
    manifest["signature"] = _b64(signature)
    manifest["public_key"] = keys["public_key"]
    manifest["signed_at"] = datetime.utcnow().isoformat() + "Z"

    manifest_path.write_text(json.dumps(manifest, indent=2))
    print("manifest signed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
