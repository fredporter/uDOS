# uHOME v1.5 Canonical Spec

Status: Active
Updated: 2026-03-03
Release baseline: v1.5 rebaseline

## Purpose

This spec defines the canonical v1.5 `uHOME` runtime and install scope for the
certified `home` profile.

`uHOME` is the local household media and home-operations lane for uDOS. It is:

- local-first
- LAN-served
- Sonic-installed
- Wizard-compatible for managed scheduling and optional control-plane features
- aligned to the `core` vs `wizard` runtime boundary

This spec is the implementation-facing companion to
`docs/decisions/uHOME-spec.md`.

## Product scope

The canonical v1.5 `uHOME` shape has two roles:

- `uHOME Server`
- `uHOME TV Node`

The server is the primary deployment role. The TV node is a bounded companion
playback role for household viewing surfaces.

The canonical v1.5 scope does not treat the older hybrid-console,
dual-boot-gaming, or broad appliance exploration docs as baseline product
requirements.

## Role model

### uHOME Server

The `uHOME Server` owns:

- local media ingest
- tuner discovery compatibility
- DVR rule storage and scheduling control
- post-processing lane ownership
- library organization
- LAN playback serving for household clients
- primary install-time and upgrade-time state

Required capabilities:

- local storage for media and DVR workflows
- LAN availability for household playback
- Sonic install support
- deterministic local config and file-backed state where applicable
- at least one living-room presentation surface

Optional capabilities:

- direct-display kiosk UX
- thin-GUI session
- Steam-console launcher shell
- Home Assistant bridge
- playback handoff target behavior

### uHOME TV Node

The `uHOME TV Node` owns:

- LAN playback consumption
- direct-TV or living-room playback UX
- remote/controller-friendly operation where present
- optional playback handoff target behavior

Required capabilities:

- LAN playback target behavior
- Sonic deployment lane definition
- one direct-use living-room presentation surface

Optional capabilities:

- direct display
- kiosk session
- thin-GUI session
- Steam-console launcher shell
- household control integration through Wizard

The TV node is not required to own:

- recording
- tuner discovery
- heavy post-processing
- full library management

## Runtime ownership

### core

`core` owns:

- deterministic parsing
- command behavior
- offline-safe transforms
- local file-backed state contracts

### wizard

`wizard` owns:

- managed scheduling and orchestration
- home-node networking control
- beacon and tunnel management
- network-aware control-plane behavior
- Home Assistant bridge
- remote API surfaces

### sonic

`sonic` owns:

- install packaging
- preflight
- artifact verification
- staged install plans
- profile-aware deployment materialization

No layer may duplicate another layer's ownership.

## Presentation modes

`uHOME` v1.5 supports two first-class living-room presentation modes.

### Thin GUI

The thin-GUI mode follows the active Alpine thin-GUI runtime direction:

- Alpine Linux
- Wayland
- Cage
- Chromium
- a local static bundle or locally served UI path

This is the baseline kiosk-style GUI direction for direct-display `uHOME`
deployments.

### Steam console

The Steam-console mode is a living-room launcher presentation that may sit
alongside the thin-GUI surface for:

- controller-first navigation
- direct-TV playback entry
- launcher-style switching between playback surfaces

For v1.5, the Steam-console mode is a presentation shell, not a separate
runtime ownership stack. It must still align with the same `uHOME` node,
Wizard networking, and Sonic install contracts.

### Presentation rules

- a deployment may ship thin GUI only
- a deployment may ship Steam-console only
- a deployment may ship both modes side by side
- presentation choice must not redefine the install, DVR, or network contract

## Network and node model

`uHOME` v1.5 uses a server-and-node network model.

### Home node roles

- `uHOME Server`
  - authoritative home-node for ingest, library state, and LAN service
- `uHOME TV Node`
  - playback-focused node that consumes server-hosted media and control signals

### Wizard networking protocol alignment

Wizard is the network control plane for `uHOME` nodes. For v1.5 this means:

- node networking and control live in Wizard routes and services, not Sonic
- Sonic materializes install and bootstrap state for nodes, then hands off to
  Wizard-owned network control
- remote or managed node behavior must align with Wizard APIs rather than
  inventing a parallel Sonic-side network protocol

Current Wizard-owned network surfaces relevant to `uHOME`:

- `/api/ha/*` for optional Home Assistant control integration
- `/api/beacon/*` for beacon configuration, status, tunnel control, and local
  cache surfaces
- shared Wizard service ownership for network-aware orchestration and API access

### Beacon and tunnel model

Beacon support is a valid v1.5 network extension for `uHOME`, especially for
home-node discovery, household edge nodes, and constrained local deployments.

Rules:

- beacons are Wizard-owned network surfaces
- Sonic may provision a node that participates in beacon-managed networking, but
  it must not own beacon runtime behavior
- beacon and tunnel state must remain optional for baseline LAN-local `uHOME`
- baseline `uHOME` operation must still work without beacon or VPN setup

## Install lanes

v1.5 recognizes two Sonic-aligned install lanes for `uHOME`.

### Lane 1: standalone bundle installer

This is the strongest current install contract and the canonical server-first
lane for v1.5.

Entry artifact:

- `uhome-bundle.json`

Authoritative implementation surfaces:

- `sonic/core/uhome_bundle.py`
- `sonic/core/uhome_installer.py`
- `sonic/core/uhome_preflight.py`

Current bundle component IDs:

- `jellyfin`
- `comskip`
- `hdhomerun_config`
- `udos_uhome`

Install phases:

- `preflight`
- `verify`
- `stage`
- `configure`
- `enable`
- `finalize`

Validation requirements:

- hardware profile preflight passes
- bundle manifest is present and readable
- checksums validate
- rollback token support remains available when supplied

Default role mapping:

- primary target: `uHOME Server`
- secondary use for `uHOME TV Node` allowed only when the staged component set
  is intentionally narrowed to playback-facing responsibilities

Standalone support rules:

- the bundle lane may be used for a standalone `uHOME` distribution
- standalone `uHOME` must be able to run without requiring the full
  `uDOS/core` runtime package set
- when run standalone, `uHOME` still uses the same file-backed state, install
  phases, and Wizard-owned optional network control contracts defined here

### Lane 2: Sonic USB/image lane

This lane exists for profile-aware image or USB deployment but is narrower than
the older Sonic hybrid-console briefs.

Starting contract surfaces:

- `sonic/config/sonic-layout.json`
- `sonic/config/sonic-manifest.json.example`
- `sonic/core/sonic_cli.py`

Rules:

- the USB/image lane must remain profile-aware rather than `uHOME`-exclusive
- a `uHOME` image profile must resolve to either `uHOME Server` or
  `uHOME TV Node`
- the lane should reuse the same component and config concepts as the bundle
  installer where practical
- the lane may materialize node bootstrap for Wizard-managed home-node or beacon
  enrollment, but it must hand off runtime networking ownership to Wizard
- the lane must not imply mandatory Windows gaming, dual-boot, or media-launcher
  behavior unless backed by active implementation and acceptance evidence

For v1.5, the USB/image lane is valid but bounded. It does not replace the
bundle installer as the main source of truth for `uHOME Server`.

Standalone USB or image variants may package:

- `uHOME` alone
- Sonic alone
- a combined Sonic + `uHOME` deployment image

These variants must stay compatible with the same role model and must not
introduce a second install or network protocol just because the full monorepo
runtime is absent.

## Runtime state surfaces

The following repo-backed surfaces are part of the current v1.5 `uHOME`
contract:

- DVR schedule store:
  - `memory/bank/uhome/dvr_schedule.json`
  - fallback: `~/.udos/uhome/dvr_schedule.json`
- playback handoff queue:
  - `memory/bank/uhome/playback_queue.json`
- Wizard config key:
  - `uhome_ad_processing_mode`

These surfaces are file-backed and local-first. Additional state may exist, but
it should not be treated as canonical without explicit spec promotion.

## Command and control surfaces

The currently evidenced remote-control surface is the optional Wizard-owned
Home Assistant bridge.

Routes:

- `GET /api/ha/status`
- `GET /api/ha/discover`
- `POST /api/ha/command`

Current `uhome.*` command families:

- `uhome.tuner.discover`
- `uhome.tuner.status`
- `uhome.dvr.list_rules`
- `uhome.dvr.schedule`
- `uhome.dvr.cancel`
- `uhome.ad_processing.get_mode`
- `uhome.ad_processing.set_mode`
- `uhome.playback.status`
- `uhome.playback.handoff`

Bridge policy:

- optional
- disabled by default unless enabled in Wizard config
- Wizard-owned
- not required for a valid baseline `uHOME` installation

If a first-class `ucode` surface is later promoted for `uHOME`, it must become
the preferred control boundary over ad hoc file mutation.

## Wizard network control surfaces

The active v1.5 network-control contract for `uHOME` is Wizard-owned.

### Beacon routes

Current beacon control surfaces:

- `POST /api/beacon/configure`
- `GET /api/beacon/status`
- `GET /api/beacon/devices`
- `POST /api/beacon/tunnel/enable`
- `GET /api/beacon/tunnel/{id}/config`
- `GET /api/beacon/tunnel/{id}/status`
- `POST /api/beacon/tunnel/{id}/disable`
- `POST /api/beacon/tunnel/{id}/heartbeat`
- `POST /api/beacon/tunnel/{id}/stats`

These routes are part of the Wizard-managed networking lane and may be used to
support `uHOME` home-node and edge-node deployments.

### Home-node expectations

For v1.5, a `uHOME` home node may be:

- a server node on the main household LAN
- a TV node on the same LAN
- a Wizard-managed beacon-connected node when that networking extension is
  explicitly configured

The spec does not require mesh, VPN, or beacon deployment for baseline home
profile acceptance.

## Standalone distribution model

`uHOME` and Sonic may each ship as standalone distributions for v1.5.

### Standalone `uHOME`

A standalone `uHOME` distribution may include:

- `uHOME Server`
- `uHOME TV Node`
- thin-GUI presentation
- Steam-console presentation
- optional Wizard-connected control features

It must not require the full `uDOS/core` package set to boot or operate its
baseline home-media functions.

### Standalone Sonic

A standalone Sonic distribution may include:

- USB or image planning
- install execution
- profile selection
- node bootstrap for `uHOME`

It must not require `uDOS/core` to perform its provisioning role.

### Combined Sonic + uHOME

A combined distribution is valid when Sonic is used to ship a ready-to-run
`uHOME` image or staged bundle. In that model:

- Sonic owns provisioning and install
- `uHOME` owns the home-media runtime
- Wizard remains the owner of optional network-aware control surfaces

## Capability matrix

| Capability | uHOME Server | uHOME TV Node |
| --- | --- | --- |
| Local media ingest | Required | No |
| DVR rules and scheduling control | Required | No |
| Post-processing ownership | Required | No |
| LAN playback | Required | Required |
| Thin-GUI presentation | Supported | Supported |
| Steam-console presentation | Supported | Supported |
| Wizard network control | Optional | Optional |
| Beacon or tunnel integration | Optional | Optional |
| Direct-TV UX | Optional | Optional |
| Home Assistant bridge | Optional | Optional |
| Sonic bundle install | Required | Supported |
| Sonic USB/image install | Supported | Required |

## Acceptance criteria

### uHOME Server

- bundle manifest and checksum contract is documented and current
- install plan phases match the tested Sonic surfaces
- hardware preflight thresholds are documented
- DVR and post-processing responsibilities are explicit
- LAN-serving role is explicit

### uHOME TV Node

- playback role is explicit and bounded
- Sonic deployment lane is defined
- direct-display UX is optional rather than assumed
- server-only responsibilities are excluded

### Shared

- no cloud dependency is required for baseline operation
- Home Assistant remains optional
- Wizard networking alignment is explicit for home-node and beacon-managed
  deployments
- thin GUI and Steam-console presentation may coexist in one deployment
- standalone `uHOME` and standalone Sonic are valid release shapes
- runtime ownership remains aligned across `core`, `wizard`, and `sonic`
- older hybrid-console material is not treated as canonical v1.5 scope

## Deferred and historical lanes

The following remain deferred, historical, or non-canonical for v1.5:

- SteamOS and Windows hybrid-console baseline
- mandatory dual-boot gaming and media crossover
- LibreELEC-only productization
- Raspberry Pi exploratory deployment variants
- launcher-specific promises not backed by active code and tests

Older Sonic roadmap briefs may remain as historical references, but they do not
override this spec.

## Verification surfaces

The current repo-backed validation points for this spec are:

- `core/tests/sonic_uhome_bundle_test.py`
- `wizard/tests/home_assistant_routes_test.py`
- `sonic/core/uhome_bundle.py`
- `sonic/core/uhome_installer.py`
- `sonic/core/uhome_preflight.py`
- `wizard/services/uhome_command_handlers.py`
- `wizard/services/home_assistant_service.py`

## Related documents

- `docs/decisions/uHOME-spec.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
- `docs/decisions/MCP-API.md`
- `docs/STATUS.md`
- `sonic/docs/integration-spec.md`
