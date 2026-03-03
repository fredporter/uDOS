# Sonic Screwdriver v1.5 Contract

Status: Active
Updated: 2026-03-03

## Purpose

Define Sonic Screwdriver as the v1.5 standalone provisioning layer for
profile-aware installs, with explicit alignment to the canonical `uHOME`
runtime and Wizard-managed networking.

Key goals:

- provide a standalone, decoupleable provisioning utility
- materialize profile-aware install layouts and staged bundles
- preserve `uHOME Server` and `uHOME TV Node` rollout support for v1.5
- support thin-GUI and Steam-console presentation packaging for `uHOME`
- hand off managed networking and control-plane behavior to Wizard
- keep device database and launch-profile data deterministic

---

## Standalone Contract

Sonic Screwdriver should run in isolation from uDOS:
- Own repo + docs + datasets + release artifacts.
- Optional integration hooks for uDOS/Wizard/App.
- No dependency on uDOS internals for basic partition/build operations.

---

## v1.5 install lanes

Sonic provides two active install lanes for v1.5:

- standalone bundle install
- USB or image install

The standalone bundle install is the canonical `uHOME Server` lane for v1.5.
The USB or image lane remains valid for profile-aware node rollout, including
`uHOME TV Node`.

Both lanes may be used for:

- standalone Sonic distribution
- standalone `uHOME` distribution
- combined Sonic + `uHOME` distribution

## USB or image layout contract

The USB or image lane uses:

- `config/sonic-layout.json`
- `config/sonic-manifest.json.example`
- `core/sonic_cli.py`
- `scripts/partition-layout.sh`
- `scripts/apply-payloads-v2.sh`
- `scripts/sonic-stick.sh`

The default layout remains a profile-capable multi-partition GPT layout. Layout
values may be adjusted through `config/sonic-layout.json` and the Sonic CLI.

Rules:

- layouts remain profile-aware
- install manifests must be reviewable before execution
- run steps are destructive and must be treated as explicit execution
- layout-driven installs may bootstrap a node for later Wizard enrollment, but
  may not define a separate Sonic runtime protocol
- layouts may package thin GUI, Steam-console UX, or both for the target node

## Standalone bundle contract

The bundle lane is backed by:

- `sonic/core/uhome_bundle.py`
- `sonic/core/uhome_installer.py`
- `sonic/core/uhome_preflight.py`

Bundle responsibilities:

- preflight hardware validation
- artifact manifest verification
- staged install plan generation
- config and enable steps
- rollback token support where provided

Current canonical component family for `uHOME` bundle installs:

- `jellyfin`
- `comskip`
- `hdhomerun_config`
- `udos_uhome`

## Wizard networking alignment

Sonic provisions nodes. Wizard owns ongoing network-aware control.

For v1.5:

- Sonic may bootstrap a `uHOME` node for LAN use or later enrollment
- Wizard owns `/api/beacon/*` and `/api/ha/*`
- beacon configuration, tunnel state, and node control remain Wizard-managed
- baseline `uHOME` must still work LAN-local without beacon or VPN setup
- Sonic and `uHOME` may be shipped without the full `uDOS/core` runtime package
  set when used as standalone distributions

## Device and launch-profile data

Sonic device and launch-profile data remain valid v1.5 inputs for:

- hardware-aware install guidance
- profile selection
- launcher and UI bundle planning where those surfaces are active

These records must not redefine the `uHOME` runtime scope.

## Presentation packaging

Sonic may provision the following `uHOME` presentation combinations:

- thin GUI only
- Steam-console only
- thin GUI plus Steam-console

These remain presentation-layer choices over the same `uHOME` install and node
contracts.

## Non-goals

- no separate Sonic-owned runtime networking protocol
- no mandatory Windows gaming or dual-boot requirement for `uHOME`
- no cloud dependency in the core provisioning lane

## Related documents

- `sonic/docs/integration-spec.md`
- `docs/specs/UHOME-v1.5.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
- `wizard/docs/BEACON-IMPLEMENTATION.md`
