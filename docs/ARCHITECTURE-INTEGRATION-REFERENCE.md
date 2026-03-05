# Architecture Integration Reference

Updated: 2026-03-03
Status: active reference

## Scope

Detailed reference for:
- non-fork integration strategy
- repository structure
- `.vibe/config.toml` integration contract
- integration phases
- file ownership rules
- compatibility and validation expectations

## Non-Fork Strategy

uDOS integrates with Vibe through addon layers instead of modifying upstream runtime internals.

Key rules:
- keep uDOS code isolated
- treat Vibe as an external interface surface
- use `.vibe/config.toml` as the integration contract

## Repository Structure

The architecture separates:
- core
- Wizard
- TypeScript runtime or related lightweight partners
- Vibe-facing configuration and discovery surfaces

## Integration Contract

The main integration point is:
- `.vibe/config.toml`

It controls:
- tool discovery
- skill discovery
- optional MCP registration

## Integration Phases

The active architecture documents:
- direct command-routing history
- MCP-based current integration
- future distributed extensions where applicable

## File Ownership

Maintain strict ownership boundaries:
- uDOS-owned addon code is safe to evolve
- upstream runtime code is not the place for local repo-specific architecture drift

## Validation

Validate architecture changes with:
- tool discovery checks
- MCP startup checks
- command-surface checks
- compatibility tests after upgrades

## Canonical Front Door

Start with:
- [Architecture](ARCHITECTURE.md)
