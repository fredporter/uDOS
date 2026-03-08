# V1.5.1 TUI Closeout Checklist

Updated: 2026-03-07  
Status: active  
Scope: patch-stream completion checklist for the Bubble Tea `ucode` TUI

This checklist operationalizes
[v1-5-1-TUI-OPERATIONAL-CLOSEOUT.md](../decisions/v1-5-1-TUI-OPERATIONAL-CLOSEOUT.md).

## 1. Dispatch Integrity

- [x] plain core commands execute through the dispatcher instead of falling back
      to guidance text
- [x] `ucode.command` routes are handled uniformly across Go and Python layers
- [x] stale repo-root drift caused by persisted `UDOS_ROOT` mismatch is fixed in
      the local runtime baseline

## 2. Menu Truthfulness

- [x] invalid built-in binder shortcuts removed from the startup menu
- [x] placeholder editor/create labels replaced with truthful inspect/status
      labels where workflows are not yet implemented
- [ ] each built-in menu item is mapped to an explicit surface class:
      Inspect, Launch, Read, or Act
- [ ] unsupported aspirational actions are listed as deferred, not shipped as
      first-class menu actions

## 3. Result Visibility

- [x] runner detail view prefers meaningful result events over trailing progress
      packets
- [x] `PROGRESS` and `RULE` transport events no longer dominate the visible
      summary lane
- [x] structured results without `output` text render a fallback summary block

## 4. Workflow Completion Inventory

- [ ] mission/new binder flow implemented or explicitly deferred with replacement
      surface
- [ ] binder resume/open workflow implemented beyond raw listing or explicitly
      deferred with replacement surface
- [ ] script editor flow implemented or explicitly deferred with replacement
      surface
- [ ] setup/config edit flows inside Bubble Tea implemented or explicitly
      deferred with replacement surface
- [ ] server-control items categorized as inspect vs act and given safe runtime
      behavior

## 5. Documentation And Status

- [x] closeout decision recorded
- [x] public status page no longer implies the v1.5 TUI backlog is fully closed
- [x] known issues track the operational closeout gap as a v1.5.1 item
- [ ] final v1.5.1 closeout note written when remaining deferred workflow items
      are either implemented or formally accepted as deferred

## 6. Validation

- [x] Go TUI tests pass
- [x] protocol bridge tests pass
- [ ] startup menu contract test covers built-in menu route validity at the
      runtime level
- [ ] final launcher smoke check passes through the macOS shell launcher path
