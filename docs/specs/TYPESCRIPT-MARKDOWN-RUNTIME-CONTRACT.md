# TypeScript Markdown Runtime Contract

Updated: 2026-03-03
Status: active runtime contract
Scope: markdown-first interactive runtime, state model, block model, and core boundary rules

## Purpose

This contract defines the active TypeScript markdown runtime surface for uDOS.

It exists to keep the runtime:
- markdown-first
- deterministic
- inspectable
- safe by default
- portable across UI surfaces

## Core Model

The runtime treats a markdown document as:
- narrative content
- structured runtime blocks
- explicit state
- deterministic rendering

Markdown remains the source of truth. Runtime behavior is derived from fenced blocks and current state.

## Required Capabilities

The active runtime contract supports:
- variable declaration and interpolation
- deterministic state mutation
- conditional rendering
- simple form inputs
- navigation choices
- render-only panels and maps
- explicit persistence of runtime state where enabled

The runtime does not require arbitrary code execution.

## Supported Block Families

Canonical block families:
- `state`
- `set`
- `form`
- `if`
- `else`
- `nav`
- `panel`
- `map`

Rules:
- block behavior must be deterministic
- `else` must directly follow `if`
- blocks describe behavior, not general programs

## State Contract

Variables:
- use `$name` syntax
- must be explicit and inspectable
- support basic scalar values in the core contract

State rules:
- state defaults load from document order
- runtime mutations are explicit
- render output depends only on the document, current state, and renderer settings

## Execution Contract

Document lifecycle:
1. parse markdown and runtime blocks
2. establish default state
3. apply persisted state where allowed
4. render markdown with current state
5. apply user actions through allowed block operations
6. re-render deterministically

No hidden side effects are allowed in the core runtime contract.

## Safety Rules

The runtime must be:
- deterministic
- offline-capable
- safe by default
- explicit about invalid blocks and expressions

Not allowed in the active contract:
- arbitrary JavaScript execution
- unrestricted filesystem access
- unrestricted network access
- hidden execution hooks

## Architecture Boundary

The TypeScript runtime is a lightweight execution partner.

It may own:
- parsing/render helpers
- stateful markdown interaction
- renderer adapters
- UI-facing runtime behavior

It must not:
- duplicate Python core ownership
- absorb Wizard orchestration responsibilities
- become a second command-routing authority

## v1.5 Usage

For v1.5, this contract matters where markdown-first interactive documents are used for:
- binder content
- forms and guided workflows
- panel or map rendering
- deterministic interactive views

The runtime must stay aligned with:
- core deterministic boundaries
- Obsidian-readable source documents
- workflow and schedule artifacts that remain human-readable

## Canonical Status

This file is the active short-form contract.

Historical detail and earlier mixed brief material were split out of the older oversized document:
- `docs/specs/typescript-markdown-runtime.md`

