# uDOS v1.5 Creator Profile Blocker Matrix

Last updated: 2026-03-03
Status: Active

## Purpose

This document starts the creator-profile acceptance pass for v1.5.

It tracks the concrete blockers that still prevent the `creator` certified profile from release signoff and defines the evidence required to clear each blocker.

## Current Summary

Current creator-profile state on March 3, 2026:
- Groovebox browser/runtime surface exists
- Songscribe parsing and route surfaces exist
- Creator profile is registered in the certified profile manifest
- Transcription runtime is still scaffolded
- Score export and sound-library operational contracts are not yet closed

The creator profile is not release-ready yet.

## Blocker Matrix

| Blocker | Area | Current State | Acceptance Evidence | Status |
|---|---|---|---|---|
| `transcription-ga` | Songscribe transcription pipeline | [`wizard/services/transcription_service.py`](/Users/fredbook/Code/uDOS/wizard/services/transcription_service.py) still returns scaffold messages for transcription, stem separation, stems export, and score export | End-to-end test from source audio to text-based score output with queue/health reporting | Blocked |
| `score-export` | Songscribe score output | Parser exists, but export contract is not verified as a creator-profile release lane | Acceptance tests for score export formats and `MUSIC`/Wizard route parity | Blocked |
| `library-health` | Sound library management | Library/inventory surfaces exist, but creator-specific sound-library lifecycle, metadata, and recovery rules are not certified | Asset ingest/index/update/restart verification and operator recovery flow | Blocked |
| `creator-install-e2e` | Certified profile install | Profile manifest exists, but creator profile has not been proven through full install/verify/use flow | `UCODE PROFILE INSTALL creator` + extension verify + music runtime verification | Blocked |
| `creator-queue-health` | Long-running jobs | Queue/progress/health surfaces for creator jobs are not yet closed | Job schema, queue visibility, failure recovery, and operator status checks | Blocked |

## Acceptance Pass Checklist

### Phase 1: Runtime Contract Audit

- [x] Confirm creator profile exists in certified profile manifest
- [x] Confirm Groovebox extension is assigned to creator profile
- [x] Confirm Songscribe parsing/runtime surfaces exist
- [ ] Replace scaffold transcription responses with production job execution
- [ ] Define canonical creator job/result schema

### Phase 2: End-to-End Tests

- [ ] Audio input reaches transcription queue successfully
- [ ] Transcription job produces text-based score output
- [ ] Score export can be retrieved from Wizard and `MUSIC`
- [ ] Groovebox can consume or pair with creator-profile outputs where required
- [ ] Sound-library asset ingest/index survives restart

### Phase 3: Release Verification

- [ ] `UCODE PROFILE VERIFY creator` passes without missing components
- [ ] `UCODE EXTENSION VERIFY groovebox` passes in creator installs
- [ ] Creator runbook includes install, operations, and recovery guidance
- [ ] Release evidence captured in devlog and roadmap

## Immediate Next Tasks

1. Replace the transcription scaffold in [`wizard/services/transcription_service.py`](/Users/fredbook/Code/uDOS/wizard/services/transcription_service.py) with a real job-backed implementation or a more explicit blocked contract.
2. Define the score export contract and add direct acceptance tests for creator profile verification.
3. Add creator-specific sound-library health checks and operational evidence.
