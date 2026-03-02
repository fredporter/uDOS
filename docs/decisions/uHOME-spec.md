# uHOME Home Profile Decision

Status: active home profile lane  
Updated: 2026-03-03

## Purpose

uHOME defines the home-media and home-operations lane for uDOS:
- local broadcast/media ingestion
- DVR and post-processing workflows
- LAN-served playback and household access
- Sonic-installed packaging for home deployments

This is an active decision doc for the home profile direction, not a full implementation manual.

## Decision

uHOME remains:
- local-first
- LAN-oriented
- Sonic-installed
- compatible with Wizard-managed scheduling and job execution
- separate from cloud-dependent media stacks

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
- alignment with Wizard scheduling and job control

This lane should not block the general v1.5 release beyond the specific home-profile commitments tracked in the roadmap.

## Non-Negotiables

- local media remains the primary operational model
- household playback must work over LAN without requiring cloud mediation
- install and packaging rules must remain explicit and profile-aware
- home-profile workflows must align with the core vs Wizard boundary

## Related Documents

- `docs/roadmap.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
