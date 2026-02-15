# Wizard API Contracts

This directory is the canonical home for Wizard service contracts.

## Structure

- `schemas/` — JSON schema or OpenAPI fragments
- `services/` — service-level descriptions and request/response examples
- `tools/` — MCP tool mapping notes

## Initial contracts (Phase 1/2)

- `wizard.health` — health and service status
- `wizard.config` — config get/set
- `wizard.providers` — list providers, capabilities
- `ucode.dispatch` — direct command execution (restricted in early phases)
- `sonic` — Sonic Screwdriver lifecycle + device DB + build endpoints
