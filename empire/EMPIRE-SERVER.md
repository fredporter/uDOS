# Empire Server (Private - CRM & Business Intelligence)

**Version:** v1.0.0.1
**Location:** `/empire/` (Private submodule, at root level)
**Port:** 5175 (Dev UI), 5176 (API - planned)
**Database:** `memory/bank/user/contacts.db`
**Status:** ✅ UI Shell + Scripts ready, HubSpot sync integrated

---

## What Empire Provides

**CRM & Contact Management:**
- Local SQLite contacts database (`memory/bank/user/contacts.db`)
- Business and person entity tracking (biz-*, prs-* IDs)
- Entity resolution and deduplication
- Contact extraction from Gmail
- Google Business Profile integration
- Website parsing for staff directories
- Social media enrichment (Twitter, Instagram)
- Email enrichment (Clearbit, Hunter.io, PeopleDataLabs)

**HubSpot Integration:**
- Bidirectional sync between Empire contacts.db and HubSpot CRM
- Contact import/export
- Enrichment and deduplication
- Moved from Wizard (Empire owns CRM data)

**UI & Automation:**
- Svelte + Tailwind dashboard (port 5175)
- Scripts read from `memory/inbox/` and write to `memory/sandbox/processed/`
- Aligned with Wizard global styles

---

## Quick Start

**Install dependencies:**
```bash
cd empire
npm install
```

**Run UI dev server:**
```bash
npm run dev  # Opens on http://localhost:5175
```

**Configure HubSpot:**
```bash
export HUBSPOT_API_KEY=your_api_key_here
```

**Run sync example:**
```python
from dev.empire.empire import Empire

empire = Empire()
stats = await empire.sync_hubspot()  # {imported: N, exported: M}
```

---

## Architecture

**Data Model:**
- businesses (biz-* IDs)
- people (prs-* IDs)
- business_person_roles (rel-* IDs)
- audience metrics (aud-* IDs)
- messages (msg-* IDs)
- social_profiles
- roles (structured job roles)
- enrichment_cache (7-day TTL)

**Core Modules:**
- `marketing_db.py` — SQLite wrapper
- `entity_resolver.py` — Deduplication logic
- `contact_extractor.py` — Gmail parsing
- `google_business_client.py` — Places API
- `hubspot_handler.py` — HubSpot sync
- `website_parser.py` — Team page scraping
- `social_clients.py` — Twitter/Instagram APIs
- `enrichment_client.py` — Email enrichment
- `keyword_generator.py` — AI keyword generation
- `id_generator.py` — uDOS ID standard

---

## HubSpot Sync

**Sync directions:**
```python
# Both ways (default)
await empire.sync_hubspot()

# Import only
await empire.sync_hubspot(direction="import")

# Export only
await empire.sync_hubspot(direction="export")
```

**API key required:**
- Set `HUBSPOT_API_KEY` in environment
- Get key from: https://app.hubspot.com/settings/api-keys

---

## Scripts

**Location:** `empire/scripts/`
**Input:** `memory/inbox/`
**Output:** `memory/sandbox/processed/`

**Example:**
```bash
python -m dev.empire.scripts.process_inbox --pattern "*.csv" --output-subdir processed
```

**Path guard:**
```python
from dev.empire.scripts.path_guard import resolve_inbox_path

safe_path = resolve_inbox_path("output.csv")  # Ensures memory/inbox/*
```

---

## UI Shell

**Tech stack:**
- Svelte 4
- Tailwind CSS (matches Wizard brand palette)
- Vite build system

**Development:**
```bash
cd empire
npm run dev     # Dev server (port 5175)
npm run build   # Production build
npm run preview # Preview build
```

**Structure:**
```
empire/
├── src/
│   ├── App.svelte       # Main app component
│   ├── main.js          # Entry point
│   └── app.css          # Tailwind + global styles
├── index.html
├── package.json
├── tailwind.config.js   # Brand colors matching Wizard
├── vite.config.js
└── svelte.config.js
```

---

## Documentation

- [QUICK-REFERENCE.md](QUICK-REFERENCE.md) — Command quick reference
- [WORKFLOW-AUTOMATION.md](WORKFLOW-AUTOMATION.md) — AI keywords + location resolution
- [scripts/README.md](scripts/README.md) — Script guidelines

---

## Related Systems

- **Wizard Server** (production services): `/wizard/`
- **Goblin Dev Server** (experimental): `/dev/goblin/`
- **Core TUI**: `/core/`

---

_Last Updated: 2026-01-22_
_Empire v1.0.0.1 (Private CRM)_
_HubSpot sync: Integrated_
