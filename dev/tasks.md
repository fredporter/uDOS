# tasks.md — Dev Mode Extension Active Tasks

Last Updated: 2026-03-03
Project: uDOS v1.5 Dev Mode Extension

---

## Active Tasks

### High Priority

- [ ] Release blocker audit: finish remaining v1.5 blocker matrix across `core`, `home`, `creator`, `gaming`, and `dev`
  - Status: In Progress
  - Owner: uDOS
  - Due: 2026-03-05
  - Notes: Certified profiles, Sonic verification, operator-first routing, and Library workflow improvements are in place; creator/gameplay closure still needs explicit blocker tracking.

- [ ] Dev extension consolidation: route remaining dev GitHub/library workflows through the Dev Mode extension service
  - Status: In Progress
  - Owner: uDOS
  - Due: 2026-03-06
  - Notes: Active Dev Mode runtime no longer depends on Goblin. Remaining work is to consolidate direct library/clone/build surfaces under the permission-gated Dev service.

- [ ] Creator profile completion plan: define Songscribe/Groovebox GA tasks and acceptance tests
  - Status: In Progress
  - Owner: uDOS
  - Due: 2026-03-07
  - Notes: Initial blocker matrix started at `docs/decisions/v1-5-creator-blocker-matrix.md`. Need the concrete transcription, score export, sound-library, and queue/health milestones that still block creator profile signoff.

### Medium Priority

- [ ] Gameplay release lane: map integrated educational missions to concrete v1.5 deliverables
  - Status: Not Started
  - Owner: uDOS
  - Due: 2026-03-08
  - Notes: Existing gameplay hooks need mission/progression packaging and profile verification to become a real v1.5 lane.

- [ ] Library operator hardening: add dependency remediation, launch health polling, and provenance/operator guidance across repo installs
  - Status: In Progress
  - Owner: uDOS
  - Due: 2026-03-04
  - Notes: Clone + launch + Thin GUI flow and per-row dependency install actions are live; next step is health/status drilldown and rollback handling.

- [ ] Documentation rebaseline: remove remaining stale GA and Goblin/server references from non-active docs
  - Status: In Progress
  - Owner: uDOS
  - Due: 2026-03-06
  - Notes: Active Dev Mode runtime/docs are aligned; broad legacy docs and utilities still contain historical language.

### Low Priority / Backlog

- [ ] Extension support levels: define support matrix for `empire`, `groovebox`, and `dev-mode`
  - Status: Not Started
  - Owner: uDOS
  - Due: 2026-03-10
  - Notes: Support matrix should land beside certified profile documentation and extension verification flows.

- [ ] Thin GUI polish: improve small-window container launcher UX and recovery messaging
  - Status: Not Started
  - Owner: uDOS
  - Due: 2026-03-10
  - Notes: Thin GUI scaffold exists; next round should improve degraded-state handling and container startup guidance.

---

## Blocked Tasks

- [ ] Overall v1.5 release signoff
  - Blocker: Creator and gameplay profile completion criteria are not yet closed
  - Resolution: Finish profile-specific blocker matrices and acceptance evidence, then run release-readiness verification across all certified profiles

---

## Notes

- `/dev` is the Dev Mode extension framework and governance root only. Runtime logic stays in `wizard/`.
- Standard runtime is operator-first. Dev tooling is implicit only through the active Dev extension lane and remains permission-gated.
- Local-only working paths under `/dev` are separate from the versioned template scaffold.

---

End of File
