# Obsidian Companion Integration Contract

Status: active
Updated: 2026-02-16

## Scope

This contract defines how uDOS Wizard will integrate with the external Obsidian Companion app hosted in the private pre-release repository `fredporter/oc-app`.

The uDOS monorepo does not host or build the app directly.

## Boundaries

- `oc-app` owns app UX, release cadence, and app-specific TODOs.
- uDOS owns Wizard-side web view/rendering interfaces.
- Integration is API and artifact based, not source-tree based.

## Interfaces

1. Wizard Web View Host Contract
- Endpoint: `GET /api/publish/providers/oc_app/contract`
- Host contract version: `1.0.0`
- Render contract version: `1.0.0`
- Required route surface:
  - `GET /api/publish/providers/oc_app/contract`
  - `POST /api/publish/providers/oc_app/render`
- Host metadata includes:
  - route prefix
  - supported embed modes (`iframe`, `webview`)
  - compatibility window

2. Rendering API Contract
- Endpoint: `POST /api/publish/providers/oc_app/render`
- Input:
  - `contract_version` (required, currently `1.0.0`)
  - `content`, `content_type`, `entrypoint`
  - `render_options` (non-secret render metadata only)
  - `assets[]` (`path`, `media_type`, optional `content_sha256`)
  - `session` boundary payload (see below)
- Output:
  - deterministic HTML payload for the given content
  - `assets_manifest` with content-addressed `asset_id` values
  - cache metadata (`html_etag`, cache-control directives)
  - explicit `render_contract_version`

3. Asset Handoff and Cache Contract
- Asset IDs are generated as:
  - `sha256(path + content_sha256 + media_type)`
- Cache policy:
  - HTML response: `private, max-age=60`
  - assets: `public, max-age=31536000, immutable`
- Manifest includes stable fields:
  - `asset_id`, `path`, `media_type`, `content_sha256`, `cache_control`

4. Auth and Session Boundary Contract
- Session payload required on render:
  - `session_id`
  - `principal_id`
  - `token_lease_id`
  - `scopes[]`
- Required scope: `oc_app:render`
- Forbidden in payload:
  - `api_key`, `access_token`, `refresh_token`, `authorization`, `secret`, `password`
- Rule:
  - Wizard validates session lease identifiers and scopes.
  - Raw provider tokens/secrets must never be carried in app render payloads.

## Compatibility Rules

- Backward compatibility is guaranteed for one minor contract version.
- Breaking changes require:
  - new contract version
  - migration notes
  - compatibility test updates in uDOS

## Compatibility Tests in uDOS

- Route-level compatibility tests:
  - `wizard/tests/publish_routes_test.py`
  - validates contract endpoint shape and render endpoint behavior
  - validates auth/session boundary failures (missing scope, secret fields)
- Service-level compatibility tests:
  - `wizard/tests/publish_service_test.py`
  - validates contract payload and render output shape
