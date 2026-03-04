# Sonic Standalone Release and Install Guide

This guide is the canonical v1.5 release/install path for Sonic as a standalone utility.

For v1.5, this standalone lane may be used to ship:

- Sonic by itself
- `uHOME` by itself through Sonic-provisioned bundles or images
- a combined Sonic + `uHOME` deployment image

## v1.5 Runtime Contract

Sonic now ships with an open-box split:

- seeded global catalog: `memory/sonic/seed/sonic-devices.seed.db`
- local user overlay: `memory/sonic/user/sonic-devices.user.db`
- compatibility mirror: `memory/sonic/sonic-devices.db`

The distributed seed remains read-only for users. Local device records and current-machine bootstrap state live in the user overlay. Device entries may point to Obsidian-style Markdown templates for settings, installers, containers, and drivers.

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

## Seeded Catalog And Bootstrap Evidence

Release proof for v1.5 should show:

1. seed catalog rebuild succeeds from `sonic/datasets/sonic-devices.sql`
2. current-machine bootstrap succeeds through `SONIC BOOTSTRAP` or `POST /api/sonic/bootstrap/current`
3. merged device reads show both seed and user records
4. device template refs resolve to the seeded Markdown template set

## Open-Box Restore Evidence

Standalone Sonic release evidence is not complete until reinstall proof exists:

1. back up `memory/`
2. remove or replace runtime code
3. reinstall Sonic/uDOS runtime
4. restore `memory/`
5. confirm the local Sonic user overlay still merges with the rebuilt seed catalog

This is the same v1.5 `DESTROY`/`RESTORE` rule used across the main runtime.

## Public Distribution Notes

- Publish release checksums and detached signatures alongside artifacts.
- Include minimum hardware and OS support notes in release notes.
- Keep release notes aligned with `docs/STATUS.md` and local `@dev` release evidence.
- When targeting `uHOME`, document whether the image exposes thin GUI,
  Steam-console UX, or both.
