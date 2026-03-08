# v1.5 Stable Signoff

Updated: 2026-03-05
Status: Completed
Scope: final profile evidence and freeze inputs for the v1.5 stable release

## Purpose

This document records the final-lane evidence for the v1.5 release.

It follows the certified profile registry in
`distribution/profiles/certified-profiles.json` and the active install state in
`memory/ucode/release-profiles.json`.

## Current Install-State Truth

All certified profiles are currently installed and enabled:

- `core`
- `home`
- `creator`
- `gaming`
- `dev`

Install-state was persisted through the canonical profile CLI:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m core.services.release_profile_cli install \
  --repo-root . \
  --profiles creator,gaming,dev
```

## Profile Matrix

| Profile | Install state | Verify | Repair evidence | Rollback or recovery evidence | Demo coverage |
| --- | --- | --- | --- | --- | --- |
| `core` | installed and enabled in `memory/ucode/release-profiles.json` | `UCODE PROFILE VERIFY core` and `ReleaseProfileService.verify_profile("core")` return healthy | `UCODE REPAIR STATUS` and `core/tests/ucode_min_spec_command_test.py::test_ucode_repair_status` | rollback not applicable for mandatory base profile; recovery is reinstall plus re-verify, and mandatory-disable guard is covered by `test_set_enabled_rejects_disabling_mandatory_profile` | `00` `01` `02` |
| `home` | installed and enabled | `UCODE PROFILE VERIFY home` returns healthy | `UCODE REPAIR STATUS` covers shared runtime repair contract before profile verify | rollback and install behavior now live in the external `uHOME-server` repo; this repo only verifies Wizard-facing uHOME control surfaces | `00` `01` `03` |
| `creator` | installed and enabled | `UCODE PROFILE VERIFY creator` returns healthy | `UCODE REPAIR STATUS` plus profile verify | recovery path is profile-gated disable and re-enable through `UCODE PROFILE DISABLE|ENABLE creator`; the optional-profile recovery contract is covered by `core/tests/release_profile_service_test.py::test_set_enabled_can_disable_and_reenable_optional_profile` | `00` `02` `03` |
| `gaming` | installed and enabled | `UCODE PROFILE VERIFY gaming` returns healthy | `UCODE REPAIR STATUS` plus profile verify | recovery path is profile-gated disable and re-enable through `UCODE PROFILE DISABLE|ENABLE gaming`; the shared optional-profile recovery contract is covered by `test_set_enabled_can_disable_and_reenable_optional_profile` | `00` |
| `dev` | installed and enabled | `UCODE PROFILE VERIFY dev` returns healthy | `UCODE REPAIR STATUS` plus profile verify | recovery path is profile-gated disable and re-enable through `UCODE PROFILE DISABLE|ENABLE dev`; surface coverage exists in `core/tests/ucode_min_spec_command_test.py::test_ucode_profile_enable_disable_surface` | `00` `01` `02` `03` `04` |

## Release Inputs Now Closed

- demo pack certification
- install-state persistence for every certified profile
- profile verification for every certified profile
- shared repair contract evidence
- profile recovery evidence for optional profiles
- home-lane rollback-token evidence
- version truth alignment to `v1.5.0` stable at release cut
- decision implementation audit coverage in `docs/specs/V1-5-DECISION-IMPLEMENTATION-AUDIT.md`
- full docs inclusion audit coverage in `docs/specs/V1-5-DOCS-IMPLEMENTATION-AUDIT.md`

## Remaining Stable Freeze Work

- none

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m core.services.release_profile_cli list --repo-root .
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/release_profile_service_test.py \
  core/tests/ucode_min_spec_command_test.py \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py \
  wizard/tests/home_assistant_routes_test.py
```
