# Empire Markdown Email Publish Spec v1.5.2

Status: active implementation spec  
Decision basis: `docs/decisions/v1-5-2-EMPIRE-SERVER.md`

## Repository boundary

- Empire is an internal extension under the uDOS repository
- thin clients that consume Empire publish/preview/send capabilities may live in separate repositories
- this spec defines the uDOS-side contract those external clients and internal shells rely on
- Empire is Wizard-activated and disabled by default unless explicitly enabled

## Goal

Define the server-side contract for authoring, rendering, previewing, drafting, and sending
markdown email from Empire using:
- [`fredporter/md-email-template`](https://github.com/fredporter/md-email-template) as the canonical authoring spec
- [`zestis/Markdown-Email-Templates`](https://github.com/zestis/Markdown-Email-Templates) as the cloned, pinned preset/layout library

This spec exists so the Empire extension can implement a stable email pipeline inside uDOS
without redefining author-facing markdown later.

## Ownership boundary

### Empire owns
- markdown document ingestion
- frontmatter parsing and validation
- merge-variable resolution
- markdown normalization
- preset selection
- HTML render
- plaintext render
- Gmail draft/send payload construction
- send logging
- binder and activity audit entries

### Android / thin clients own
- compose/edit surface
- preview request surface
- approval actions
- monitoring of queue/job/send state

Thin clients must not own HTML rendering rules or provider payload construction.

## Activation contract

- Empire is a bundled private extension inside uDOS
- Empire must be activated explicitly through Wizard Extensions
- publish/preview/send surfaces must report a clear disabled state when the extension is not enabled
- callers must receive structured soft-fail responses instead of transport-level crashes when Empire is unavailable

## Source-of-truth model

### Canonical authoring input
The markdown source file is the source of truth. It contains:
- YAML frontmatter
- markdown body

The markdown/frontmatter contract follows the simple shape from `md-email-template`, with
Empire-specific fields added only where needed for binder and contact workflows.

### Cloned template library role
The cloned `Markdown-Email-Templates` library is an implementation dependency used to back
Empire presets. It does not define the public authoring API.

Empire must expose one stable preset interface even if the underlying cloned assets change.

## Canonical frontmatter

Required:

```yaml
---
type: email
subject: Launch update
template: announcement
---
```

Recommended:

```yaml
---
type: email
subject: Launch update
preview: Big improvements this month
template: announcement
binder: @binders/sales
segment: binder_tagged_contacts
from_profile: primary
reply_to: ops@example.com
cta_text: View update
cta_href: https://example.com/update
tags:
  - binder/sales
  - send/announcement
---
```

### Frontmatter fields

| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `type` | yes | string | must equal `email` |
| `subject` | yes | string | final mail subject after merge |
| `template` | yes | string | one of the supported preset ids |
| `preview` | no | string | preview/preheader text |
| `binder` | no | string | binder reference for audit and merge context |
| `segment` | no | string | recipient segment key |
| `from_profile` | no | string | sending identity/profile selector |
| `reply_to` | no | string | reply-to override |
| `cta_text` | no | string | top-level CTA label |
| `cta_href` | no | string | top-level CTA target |
| `tags` | no | array | audit and reporting tags |

### Validation rules
- reject documents missing `type`, `subject`, or `template`
- reject any `type` other than `email`
- reject unsupported template ids
- reject `cta_text` without `cta_href`
- reject `cta_href` without `cta_text`
- reject send requests with neither explicit recipients nor a resolvable segment

## Preset contract

Empire v1.5.2 must expose these preset ids:
- `basic`
- `announcement`
- `digest`

### `basic`
- single-column
- minimal header/footer
- suitable for direct notes, replies, and simple outbound mail

### `announcement`
- hero/title led
- supports preview text and primary CTA
- suitable for launches, updates, and binder/project notices

### `digest`
- multi-section summary layout
- suitable for recurring updates, weekly summaries, and binder reports

### Preset mapping rule
Each preset maps to one or more cloned-library templates internally, but that mapping is not
part of the public API. Empire may change the backing assets if the preset id and render
contract remain stable.

## Extension asset contract

Empire should vendor or pin the cloned template library under a deterministic path inside the
uDOS Empire extension, such as:

```text
extensions/empire/vendor/markdown_email_templates/
```

Requirements:
- the clone is pinned to a known commit or release snapshot
- local modifications are tracked in Empire docs or patch notes
- runtime rendering does not fetch remote templates
- releases remain reproducible offline

## Render pipeline

### Stage 1: ingest
Input:
- markdown file contents or compose payload
- optional explicit recipient list
- optional binder/contact/company context overrides

Output:
- parsed frontmatter
- markdown body
- normalized request envelope

### Stage 2: validate
Validate:
- required frontmatter
- supported preset id
- sender profile availability
- recipient/segment presence
- merge variable references

Failure result:
- structured validation error
- no provider action

### Stage 3: resolve context
Resolve:
- binder metadata
- segment members
- contact/company merge fields
- sender profile
- default footer/legal content if configured

Output:
- render context package

### Stage 4: normalize markdown
Normalize:
- heading spacing
- list formatting
- link expansion
- CTA blocks
- line breaks for plaintext parity

Empire may normalize markdown for rendering consistency, but it must not silently mutate the
stored authored source.

### Stage 5: render
Produce:
- rendered HTML using selected preset and cloned template assets
- plaintext alternative derived from the same source package

### Stage 6: package
Produce provider-ready structures:
- Gmail draft payload
- Gmail send payload
- audit metadata package

### Stage 7: persist and log
Record:
- render metadata
- template preset used
- recipient resolution summary
- draft/send result
- binder log entry
- contact/company activity linkage

## Internal request contract

Example normalized publish request:

```yaml
message_id: msg_01
mode: draft
source:
  kind: markdown
  path: memory/bank/outbox/launch-update.md
frontmatter:
  type: email
  subject: Launch update
  template: announcement
  binder: "@binders/sales"
context:
  binder_id: binder_sales
  segment_id: binder_tagged_contacts
  sender_profile: primary
recipients:
  mode: segment
  count_estimate: 120
render:
  preset: announcement
  html_template_id: announcement-v1
provider:
  kind: gmail
```

## API surface

Empire should expose four logical operations:
- `preview`
- `draft`
- `send`
- `validate`

### `preview`
Returns:
- normalized frontmatter
- resolved preset id
- rendered HTML
- rendered plaintext
- validation warnings

No provider-side draft/send is created.

### `draft`
Creates:
- provider draft payload
- persisted draft record
- audit trail

### `send`
Creates:
- send job or immediate send request
- provider payload
- send record
- activity log entries

### `validate`
Returns:
- errors
- warnings
- resolved dependencies

No render or provider action is required beyond lightweight checks.

## Gmail contract

### v1.5.2 send lane
- Gmail API only
- OAuth/session management is external to this spec

Empire must provide Gmail-ready payloads containing:
- `to`
- optional `cc`
- optional `bcc`
- `subject`
- MIME structure with HTML and plaintext alternatives
- sender identity/profile metadata
- optional reply-to

### Draft-first policy
For risky or bulk flows, Empire should support draft-first operation even when the caller
eventually intends to send.

## Merge variable contract

Supported merge sources:
- binder
- contact
- company
- sender profile
- runtime publish request

Example variables:
- `{{ contact.first_name }}`
- `{{ company.name }}`
- `{{ binder.name }}`
- `{{ sender.signature_name }}`

Rules:
- unresolved variables must produce a validation warning or hard error based on mode
- bulk sends should fail closed on required variables
- preview may show unresolved markers with warnings

## Queue and job model

Single-recipient and multi-recipient sends should use the same logical model:
- request accepted
- validation complete
- render complete
- draft created or send queued
- provider accepted
- provider failed
- audit persisted

Bulk sends additionally require:
- batch sizing
- rate limiting
- retry policy
- bounce/error capture

## Audit contract

Every draft/send must write an audit record with at least:
- message id
- authored source reference
- preset id
- sender profile
- recipient mode
- resolved recipient count
- binder reference if present
- render timestamp
- provider action result

Where applicable, Empire should also write:
- binder log entries
- contact activity entries
- HubSpot notes/activities

## Error model

Minimum error classes:
- `validation_error`
- `template_error`
- `merge_error`
- `provider_error`
- `queue_error`
- `audit_error`

Errors returned to thin clients must be structured and operator-readable.

## Recommended filesystem contract

Suggested authored source locations:

```text
memory/bank/outbox/
memory/bank/templates/email/
memory/bank/binders/<binder>/outbox/
```

Suggested generated artifact locations:

```text
var/empire/email/previews/
var/empire/email/renders/
var/empire/email/logs/
```

The exact runtime paths may differ across Empire modules, but authored markdown and generated
render artifacts should remain clearly separated within the uDOS extension boundary.

## Test requirements

Minimum test coverage for Empire implementation:
- frontmatter validation for required and invalid fields
- preset resolution for `basic`, `announcement`, `digest`
- markdown-to-HTML render for each preset
- markdown-to-plaintext render parity
- merge variable resolution success/failure
- Gmail payload generation
- audit record creation
- draft-first flow
- bulk-segment recipient resolution

## MVP acceptance

v1.5.2 email publishing is considered ready when:
- a markdown email can be validated from authored source
- preview returns HTML and plaintext from the same input
- draft creation works through Gmail payload packaging
- send works for at least one authenticated sender profile
- `basic`, `announcement`, and `digest` all render through the cloned template library
- binder-aware audit logging is present
- bulk mail is queue-backed rather than client-driven

## Explicit non-goals for v1.5.2

- Android-side render ownership
- direct SMTP support
- user-editable HTML templates in thin clients
- remote runtime fetching of template assets
- provider-agnostic abstraction beyond Gmail draft/send readiness
