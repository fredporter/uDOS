# Packaging and Release Contract v1.5

Updated: 2026-03-03
Status: active packaging contract
Scope: release variants, profile packaging, artifact expectations, and release evidence

## Purpose

This contract defines the active packaging and release expectations for v1.5.

It replaces older milestone-sized packaging briefs with a shorter release-facing contract.

## Release Packaging Goals

uDOS packaging must support:
- certified profile releases
- clear variant boundaries
- reproducible release artifacts
- recoverable installs
- verifiable package metadata

## Active Packaging Lanes

The active release lanes are:
- `core`
- `home`
- `creator`
- `gaming`
- `dev`

Each supported lane must have:
- explicit install path
- verification path
- repair path
- release evidence

## Artifact Contract

Release artifacts must provide:
- version metadata
- profile or variant identity
- install instructions
- verification guidance
- checksums or equivalent integrity evidence

Where relevant, artifacts may include:
- package manifests
- signed bundles
- profile-specific assets
- offline seed content

## Runtime Boundary Rules

Packaging must preserve the core/Wizard split:
- core stays deterministic and offline-capable
- Wizard carries networked and web responsibilities
- extensions remain profile-gated and separately owned

Packaging must not blur those boundaries by bundling hidden alternate runtimes as the default path.

## Installer and Repair Expectations

For each supported release lane:
- install flow must be documented
- repair flow must be documented
- rollback or recovery behavior must be defined where applicable
- profile drift detection must be part of release hardening

## Release Evidence

Before v1.5 release, packaging must include:
- profile install evidence
- profile verification evidence
- shakedown/demo evidence for active specs
- documented known issues for deferred patch work

## Observability and Hardening

Packaging and release work must cover:
- health and verification checks
- logging expectations
- security review inputs
- backup or recovery expectations where relevant

## Sonic and Managed Lanes

Specialized release lanes such as Sonic or managed Wizard deployment may extend this contract, but must still align with:
- the canonical roadmap
- current decision docs
- current install and operator guides

Standalone distributions remain valid where explicitly defined by active specs.
For v1.5 this may include standalone Sonic and standalone `uHOME` artifacts, so
long as:

- variant identity is explicit
- install and verification paths remain documented
- optional Wizard control surfaces do not become hidden hard dependencies
- thin-GUI and Steam-console presentation assets remain profile-scoped rather
  than redefining runtime ownership

## Canonical Status

This file is the active short-form packaging contract for v1.5.

Historical detail and earlier oversized milestone material were archived under:
- `docs/.compost/historic/2026-03-04-retired-plan-and-spec-relics/PACKAGING-DISTRIBUTION-ARCHITECTURE-v1.4.6.md`
