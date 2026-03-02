# uCODE Dispatch Contract

Updated: 2026-03-03
Status: active command-dispatch contract
Scope: input routing order, safety boundaries, fallback behavior, and dispatch debugging

## Purpose

This contract defines the active dispatch behavior for uCODE input handling.

## Dispatch Order

Input is resolved in this order:
1. uCODE command match
2. shell validation and execution, when allowed
3. OK fallback or Wizard-backed natural-language handling, when enabled

This order is deterministic and must remain visible in the implementation.

## Stage 1: uCODE Matching

The command surface is authoritative.

Rules:
- exact command matches win first
- aliases may be supported explicitly
- ambiguous shorthand must not silently guess
- typo correction must remain conservative if enabled

## Stage 2: Shell Path

Shell execution is a fallback, not the primary control surface.

Rules:
- validate syntax before execution
- reject dangerous patterns
- use bounded execution time
- keep shell execution within the permitted runtime boundary

## Stage 3: OK Fallback

If input is not resolved by command or shell paths, the runtime may hand off to the configured OK fallback path.

Rules:
- fallback must fail clearly when unavailable
- fallback must not bypass command or shell safety rules
- offline operation must remain understandable when fallback is disabled

## Safety Rules

Dispatch behavior must:
- preserve command priority
- avoid unsafe shell expansion
- expose failure reasons clearly
- support offline-capable operation where expected

## Debug and Observability

Dispatch debugging should allow operators and developers to see:
- which stage handled the input
- why earlier stages did not match
- whether a shell path was rejected for safety

## Performance Expectations

Dispatch should keep:
- command matching fast
- shell validation bounded
- fallback latency clearly separated from local dispatch costs

## Canonical Status

This file is the active short-form dispatch contract.

The older versioned spec path remains only as a redirect stub:
- `docs/specs/UCODE-COMMAND-DISPATCH-v1.4.4.md`

