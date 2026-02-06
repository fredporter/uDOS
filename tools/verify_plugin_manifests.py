#!/usr/bin/env python3
"""Verify plugin manifest signatures (Ed25519).

Canonicalization: JSON with sorted keys, UTF-8, no signature field.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Dict, Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def _canonical_payload(manifest: Dict[str, Any]) -> bytes:
    payload = {k: manifest[k] for k in manifest if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _verify_manifest(path: Path) -> bool:
    manifest = json.loads(path.read_text())
    sig = manifest.get("signature")
    if not sig:
        print(f"FAIL {path}: missing signature")
        return False

    algorithm = sig.get("algorithm")
    if algorithm != "ED25519":
        print(f"FAIL {path}: unsupported algorithm {algorithm}")
        return False

    public_key_b64 = sig.get("publicKey")
    signature_b64 = sig.get("signature")
    if not public_key_b64 or not signature_b64:
        print(f"FAIL {path}: missing signature fields")
        return False

    try:
        public = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
        public.verify(base64.b64decode(signature_b64), _canonical_payload(manifest))
        print(f"OK   {path}")
        return True
    except Exception as exc:
        print(f"FAIL {path}: {exc}")
        return False


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    library_dir = repo_root / "library"

    manifests = list(library_dir.glob("*/manifest.json"))
    if not manifests:
        print("no manifests found")
        return 1

    ok = True
    for path in manifests:
        if not _verify_manifest(path):
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
