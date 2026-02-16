# Sonic Standalone Release and Install Guide

This guide defines the public release/install flow for Sonic Screwdriver as a standalone utility.

## Release Artifacts

Each release build should publish:

- `sonic-stick-<version>-<build-id>.img`
- `sonic-stick-<version>-<build-id>.iso`
- `build-manifest.json`
- `checksums.txt`
- `build-manifest.json.sig` (detached signature)
- `checksums.txt.sig` (detached signature)

## Build a Release Bundle

From the repo root:

```bash
bash distribution/alpine-core/build-sonic-stick.sh \
  --profile alpine-core+sonic \
  --build-id "$(date -u +%Y%m%dT%H%M%SZ)" \
  --sign-key /path/to/sonic-private.pem
```

Environment variables:

- `WIZARD_SONIC_SIGN_KEY` may be used instead of `--sign-key`.
- `SOURCE_DATE_EPOCH` can be set for deterministic image content generation.

## Verify Checksums and Signatures

1. Validate hashes:

```bash
cd distribution/builds/<build-id>
sha256sum -c checksums.txt
```

2. Verify signatures:

```bash
openssl dgst -sha256 -verify /path/to/sonic-public.pem \
  -signature build-manifest.json.sig build-manifest.json

openssl dgst -sha256 -verify /path/to/sonic-public.pem \
  -signature checksums.txt.sig checksums.txt
```

Wizard runtime can also validate readiness with:

`GET /api/platform/sonic/builds/<build-id>/release-readiness`

`WIZARD_SONIC_SIGN_PUBKEY` must point to the public key for signature verification.

## Install/Run (Linux)

1. Generate manifest:

```bash
python3 core/sonic_cli.py plan --usb-device /dev/sdX --layout-file sonic/config/sonic-layout.json
```

2. Execute installer:

```bash
bash sonic/scripts/sonic-stick.sh --manifest sonic/config/sonic-manifest.json
```

3. Optional dry run:

```bash
python3 core/sonic_cli.py plan --usb-device /dev/sdX --dry-run
bash sonic/scripts/sonic-stick.sh --manifest sonic/config/sonic-manifest.json --dry-run
```

## Public Distribution Notes

- Publish release checksums and detached signatures alongside artifacts.
- Include minimum hardware and OS support notes in release notes.
- Keep release notes aligned with `docs/roadmap.md` Sonic completion state.
