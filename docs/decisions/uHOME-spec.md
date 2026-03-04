# uHOME Home Profile Decision

Status: active home profile lane  
Updated: 2026-03-03

## Purpose

uHOME defines the home-media and home-operations lane for uDOS:
- local broadcast/media ingestion
- DVR and post-processing workflows
- LAN-served playback and household access
- Sonic-installed packaging for home deployments

This is an active decision doc for the home profile direction, not a full
implementation manual. The canonical implementation-facing contract lives in
`docs/specs/UHOME-v1.5.md`.

## Decision

uHOME remains:
- local-first
- LAN-oriented
- Sonic-installed
- compatible with Wizard-managed scheduling and job execution
- separate from cloud-dependent media stacks

For v1.5, the canonical `uHOME` product shape is:

- `uHOME Server` as the primary certified home-profile deployment role
- `uHOME TV Node` as a bounded companion playback/appliance role

The `uHOME` user-facing runtime may be presented through:

- an Alpine thin-GUI kiosk surface
- a Steam-console-style living-room launcher surface

These are presentation modes for the same home-profile lane rather than
separate architecture stacks.

The home profile should favor readable configuration, deterministic local processing, and open-box media workflow definitions where practical.

## Core Architecture

### Source and playback model

- broadcast or local media sources feed a home node
- the home node records, processes, and stores media locally
- playback is served across the LAN to household devices

### Processing model

uHOME supports:
- scheduled recording
- rule-based capture
- post-processing jobs
- library organization
- metadata enrichment where allowed by policy

### Runtime ownership

- `core` owns deterministic local parsing, command behavior, and offline-safe transforms
- `wizard` owns managed jobs, schedule orchestration, remote/control-plane surfaces, and any network-aware services
- Sonic owns install and packaging behavior for supported home profile deployments

## v1.5 Release Direction

For v1.5, uHOME work is focused on:
- packaging and profile clarity
- DVR and post-processing lane definition
- Sonic-installed home profile behavior
- thin-GUI and Steam-console presentation alignment for living-room use
- alignment with Wizard scheduling and job control
- standalone home deployment viability where `uHOME` or Sonic ship without the
  full monorepo runtime

The older hybrid-console and broad appliance exploration docs are not the
canonical v1.5 source of truth unless a shipped surface is explicitly promoted
into the active spec.

This lane should not block the general v1.5 release beyond the specific home-profile commitments tracked in the roadmap.

## Non-Negotiables

- local media remains the primary operational model
- household playback must work over LAN without requiring cloud mediation
- install and packaging rules must remain explicit and profile-aware
- home-profile workflows must align with the core vs Wizard boundary

## Related Documents

- `docs/specs/UHOME-v1.5.md`
- `docs/STATUS.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
