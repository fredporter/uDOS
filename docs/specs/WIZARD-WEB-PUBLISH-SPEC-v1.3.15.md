# Wizard Web Publish Spec v1.3.15 (Draft)

Status: draft (to be developed)  
Target: v1.3.15

## Purpose

Refactor the monorepo concept into a clear Wizard Web publish architecture so publish behavior is deterministic, modular, and aligned with the uDOS platform contract.

This spec defines how publish logic is split across:

- core runtime (`core/`)
- Wizard server (`wizard/`)
- optional submodules (`dev/`, `sonic/`, `groovebox/`, future modules)
- external companion app integration contract (`oc-app`)

## Product Boundaries (Normative)

- `uCLI` remains the only terminal entry point.
- `Wizard GUI` remains the only GUI host for uDOS features.
- Publish orchestration happens in Wizard (`wizard/`) only.
- Optional module publish capabilities are loaded by capability discovery, not by hard dependency.
- No backward-compatibility shims are required for pre-v1.3 legacy publish paths.

## Monorepo Refactor Model

### 1) Publish Core (always present)

Owned by `wizard/` + `core/`:

- publish job orchestration
- render contract enforcement
- manifest generation (content, assets, checksums, provenance)
- publish queue state and audit trail
- role/capability checks for publish actions

### 2) Publish Providers (module adapters)

Owned by optional modules or wizard adapters:

- `wizard` provider: local Wizard-hosted publish lane
- `oc-app` provider: external companion app artifact handoff
- `sonic` provider: optional artifact exposure, no required coupling
- `groovebox` provider: optional media publish artifacts via Wizard
- `dev` provider: test/sandbox publish only when `/dev` is installed and active

Providers must register capabilities and declare readiness checks before publish routes are exposed.

### 3) Contract-first Routing

Wizard publish routes are defined by contract + capability matrix:

- route exists only when capability exists
- unavailable providers return explicit capability errors
- no hidden route aliases

## Wizard Publish Surface (v1.3.15 target)

Proposed canonical API surface:

- `GET /api/publish/capabilities`
- `GET /api/publish/jobs`
- `POST /api/publish/jobs`
- `GET /api/publish/jobs/{job_id}`
- `POST /api/publish/jobs/{job_id}/cancel`
- `GET /api/publish/manifests/{manifest_id}`
- `POST /api/publish/providers/{provider}/sync`

Proposed dashboard surface:

- `#/publish` (queue + manifests + provider status)
- `#/publish/providers` (provider health and capability matrix)

## Data Contract

Every publish job must produce:

- `publish_job_id`
- `contract_version`
- `provider`
- `source_workspace`
- `artifact_manifest`
- `checksum_set`
- `created_at`, `completed_at`
- `status` (`queued|running|failed|completed|cancelled`)
- `error_detail` (if failed)

## Security and Policy

- publish operations require Wizard auth and policy checks.
- module-scoped publish operations require module capability + activation checks.
- `/dev` publish/testing actions are admin-only and disabled when `/dev` is absent.
- no direct publish execution from standalone TUIs or legacy command aliases.

## Migration from v1.3.x

For v1.3.15:

1. move any remaining publish logic from ad-hoc route handlers into publish services
2. add provider registry + capability resolver
3. harden route exposure by capability matrix
4. add contract tests for each provider lane
5. archive legacy publish navigation paths in Wizard GUI

## Test Requirements

Required for release gate:

- capability matrix tests (provider on/off)
- publish job lifecycle tests
- manifest integrity tests
- auth/policy tests
- dashboard route tests for publish views

## Out of Scope (v1.3.15)

- multi-tenant distributed publish clusters
- external billing/commerce workflows
- non-Wizard GUI publish frontends

## Related Contracts

- `docs/specs/PLATFORM-CONTRACT-v1.3.md`
- `docs/decisions/SUBMODULE-STRATEGY.md`
- `docs/specs/OBSIDIAN-COMPANION-INTEGRATION-CONTRACT.md`
