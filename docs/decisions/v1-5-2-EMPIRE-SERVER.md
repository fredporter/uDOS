V1.5.2 — Empire Extension + Server Migrations

## Goal

Move operational intelligence and provider-heavy workflows out of clients and into Empire/Wizard.

## Repository boundary

- Empire is an internal uDOS extension
- Wizard is internal to the uDOS platform/runtime surface
- client apps such as Android and macOS live in separate repositories
- this decision defines the uDOS-owned backend and extension requirements those client repos depend on
- Empire activation is explicit through Wizard Extensions and is disabled by default unless enabled

## Primary ownership

Empire becomes the owner of:
- Gmail receive/send workflows
- contact record processing
- company record processing
- HubSpot sync
- Google Contacts projection
- email classification and summarisation
- archive policy
- markdown email publishing
- bulk mail distribution
- uploaded email archive processing
- interaction logging
- binder-aware enrichment and task promotion

## Provider policy

### Live lanes for this stream
- Google
  - Wizard-managed OAuth
  - Gmail intake
  - Calendar intake
  - Places enhancement
- HubSpot
  - contact sync
  - company sync
  - webhook mapping support

### Explicit non-goals for current Android work
- iCloud provider support
- Outlook provider support

## Migration target architecture

### Client apps
separate-repo thin clients / local shells / editors / kiosk surfaces

### Wizard
network-aware orchestration, routes, queues, auth, job lifecycle, audit surface

### Empire
provider-specific business logic and data pipelines

### Empire activation model
- bundled with uDOS as a private internal extension
- activated explicitly through Wizard Extensions
- expected to soft-fail cleanly when not installed or not enabled

## Empire service domains

### 1. Contact engine
Handles:
- contact identity resolution
- dedupe/merge logic
- source precedence
- binder tags
- HubSpot contact mapping
- Google Contacts projection

### Canonical contact fields
Minimum required mapping for Contacts and Companies:
- name
- email
- address
- phone
- city
- postcode
- state
- country

### Communication-link mapping
- emails mapped by **email address**
- text / WhatsApp / phone interactions mapped by **phone number**

### Recommended internal normalized model

```yaml
contact_id: uuid
name: string
emails: [string]
phones: [string]
company_name: string|null
address_1: string|null
address_2: string|null
city: string|null
postcode: string|null
state: string|null
country: string|null
binder_tags: [string]
source_systems: [hubspot, gmail, android, import, manual]
email_summaries: []
message_summaries: []
linked_tasks: []
linked_binders: []
```

## 2. Email intake and archive engine

### Input sources
- live Gmail inbox data
- historical email threads
- uploaded email archives

### Classification lanes
Every message or thread should be classified into:
- important
- known contact
- human interaction
- notification
- promotion
- update/newsletter
- machine/system
- archive-only

### Priority rules
High-priority retention/logging should apply to:
- important emails
- emails from known contacts
- any human interaction
- any thread that creates or enriches a contact/company record

### Retention model
- full mail should **not** become the structured contact store
- parsed summary retained in contact/task layers
- original message retained only according to mailbox/archive/export policy
- notifications, promotions, and updates should be summarised/logged and archived

### Historical email rule
Any real human interaction in historical email and uploaded archives should be eligible to:
- create a contact/company
- enrich an existing contact/company
- generate a HubSpot activity/note
- generate a Google Contacts projection if in-scope

## 3. Email-to-task / binder promotion engine

### Required flows
- parse email
- extract sender/recipient/contact linkage
- generate summary
- attach summary to contact history
- optionally convert to `moves.json` task
- optionally attach to binder packet or project binder
- archive remote original per policy

## 4. Markdown email publishing engine

### Send lane
- Gmail API only in v1
- SMTP/provider adapters later

### Template source
Use the simple markdown email authoring spec from
[`fredporter/md-email-template`](https://github.com/fredporter/md-email-template)
as the canonical content contract for Empire-authored messages.

Integrate a cloned, pinned copy of
[`zestis/Markdown-Email-Templates`](https://github.com/zestis/Markdown-Email-Templates)
inside Empire as the preset/template library used for HTML email rendering.

Policy:
- the simple markdown spec defines the authoring shape
- Empire owns frontmatter validation, merge expansion, markdown normalization, and final render
- the cloned template library provides reusable layout/preset assets, not the canonical data model
- Android remains preview/approval/monitor only and must not own HTML render logic
- template library integration should be pinned and locally cloned so Empire releases are deterministic

### Empire publish inputs
- markdown source
- frontmatter
- template preset
- recipient list or segment
- binder context
- merge variables
- HubSpot/company/contact data

### Empire publish outputs
- HTML email
- plaintext alternative
- Gmail API draft/send payload
- send log
- HubSpot activity log
- binder log entry

### Recommended frontmatter shape

```yaml
---
type: email
subject: Launch update
preview: Big improvements this month
template: announcement
binder: @binders/sales
segment: binder_tagged_contacts
cta_text: View update
cta_href: https://example.com/update
---
```

### Render contract
- markdown body is the human-authored source of truth
- frontmatter selects the preset and supplies metadata
- Empire resolves merge variables from binder/contact/company context
- Empire renders both HTML and plaintext from the same source package
- Gmail payload generation happens after render, inside Empire

### Template presets for MVP
- `basic`
  - minimal single-column email mapped from the cloned library's simplest layout
- `announcement`
  - hero/update style layout for product, project, or binder announcements
- `digest`
  - summary layout for multi-item updates, reports, or periodic binder digests

### Integration rule
Empire should expose one stable internal template interface regardless of which cloned
library assets back each preset. That keeps v1.5.2 server behavior stable while allowing
template-library swaps or upgrades later without changing author-facing markdown.

## 5. Bulk email distribution

Empire should own:
- segment resolution
- merge fields
- queueing
- rate limiting
- send state
- bounce/error logging
- contact activity updates
- audit trail

Android should only own preview/approval/monitor surfaces.

## 6. Calendar support in Empire

Keep the scope narrow:
- next 90 days only
- availability computation
- important appointment packet generation
- optional linkage from appointments into `moves.json` and binder docs

## 7. Places enhancement policy

Allow Places API enhancement only for:
- legitimate incoming contacts
- current/new records
- cases where HubSpot enrichment is insufficient
- narrowly-scoped assistive enrichment

Do not use Places as a bulk lead-source or historical backfill source.

## 8. Wizard route impact

New/expanded Wizard surfaces should include:
- provider health/status
- sync queue and job history
- contact sync state
- mail queue state
- publish capability matrix
- activity logs and audit trails

## Acceptance criteria

### MVP
- Google + HubSpot auth stable
- HubSpot contact/company sync stable
- Gmail classify + summarize + archive pipeline works
- contact creation from human email works
- Google Contacts projection works

### Phase 2
- historical mail import works
- markdown email render/send via Gmail API works
- binder-aware task promotion works
- queue + audit surfaces work in Wizard

### Phase 3
- bulk distribution stable
- interaction loops update HubSpot and contact logs
- phone-number keyed message linking works for SMS/WhatsApp imports
