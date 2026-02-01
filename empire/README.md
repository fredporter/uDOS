# Empire Private Server - Business Intelligence & CRM

**Version:** v1.0.0.1
**Location:** `/empire/` (Private)
**Database:** `memory/bank/user/contacts.db`
**Status:** ✅ Production (v1.0.0.1)

---

## UI Shell (Tailwind + Svelte)

A minimal Svelte + Tailwind shell now lives in `empire/` (root level, private submodule) aligned with the Wizard dashboard styles (same Tailwind config and app.css).

- Install: `cd empire && npm install`
- Run dev server: `npm run dev` (default port 5175)
- Build: `npm run build`

Use this shell as the starting point for Empire dashboards; add Svelte components under `src/`.

## Scripts

All runnable scripts now live under `empire/scripts/` and are constrained to `memory/inbox/` via `path_guard.resolve_inbox_path()`.

- Example: `python -m dev.empire.scripts.process_inbox --pattern "*.csv"`
- Output: defaults to `memory/inbox/processed/`

## HubSpot Integration

HubSpot CRM synchronization is now owned by Empire (moved from Wizard, since it only syncs Empire's contacts.db).

**Setup:**
```bash
export HUBSPOT_API_KEY=your_hubspot_api_key
```

**Usage:**
```python
from dev.empire.empire import Empire

empire = Empire()

# Bidirectional sync
stats = await empire.sync_hubspot()  # {imported: N, exported: M}

# One-way import
stats = await empire.sync_hubspot(direction="import")

# One-way export
stats = await empire.sync_hubspot(direction="export")
```

---

## Overview

**Empire Private Server** is a unified private CRM and business intelligence system that consolidates:

- 📧 **Gmail Contact Extraction** - Parse email signatures and domains
- 🔍 **Google Places API** - Search and import business data
- 🌐 **Website Parsing** - Extract staff directories from team pages (robots.txt compliant)
- 📱 **Social Media Enrichment** - Twitter/X, Instagram public data via official APIs
- 💼 **Email Enrichment** - Clearbit, Hunter.io, PeopleDataLabs integrations
- 🏢 **Business Tracking** - Internal biz-\* ID system
- 👤 **Contact Management** - Person records with prs-\* IDs
- 🔗 **Relationship Mapping** - Business ↔ Person connections with roles
- 📨 **Message Archiving** - Thread compression and pruning
- 📤 **Export System** - CSV/JSON exports

All entity IDs follow the **uDOS ID Standard** (`dev/roadmap/udos_id_standard.md`):

- `biz-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (Business)
- `prs-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (Person)
- `rel-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (Relationship)
- `msg-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (Message)
- `aud-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (Audience)

---

## Legal & Compliance

**✅ BIZINTEL uses only legal, publicly accessible data sources:**

1. **Website Parsing** - Respects `robots.txt`, rate limits per domain
2. **Social Media** - Official APIs only (Twitter API v2, Instagram Graph API)
3. **Email Enrichment** - Authorized API access (Clearbit, Hunter.io, PDL)
4. **Google Places** - Public business data via official Places API
5. **No Scraping** - No automated page scraping, no unauthorized access
6. **User Consent** - LinkedIn imports require user authentication (1st degree connections only)

**Compliance Guarantees:**

- No bypassing technical restrictions
- No violation of platform Terms of Service
- No collection of private/non-public data
- Proper attribution and rate limiting
- Caching to minimize API load

---

## Architecture

### Core Modules

**Original BIZINTEL (v1.2.21):**

1. **`id_generator.py`** (120 lines)
   - `generate_business_id()` → biz-\*
   - `generate_person_id()` → prs-\*
   - `generate_relationship_id()` → rel-\*
   - `generate_audience_id()` → aud-\*
   - `generate_message_id()` → msg-\*

2. **`marketing_db.py`** (838 lines - extended)
   - SQLite wrapper for 8 tables (added: roles, social_profiles, enrichment_cache)
   - CRUD operations for all entities
   - Indexed searches (google_place_id, email, domain)
   - Foreign key relationships
   - Enrichment cache with TTL

3. **`entity_resolver.py`** (396 lines)
   - Priority matching (google_place_id → linkedin → domain → fuzzy)
   - `match_business()` - Find existing by anchors
   - `resolve_or_create_business()` - Match or generate new ID
   - `merge_businesses()` - Manual deduplication

4. **`contact_extractor.py`** (310 lines)
   - `extract_from_email()` - Parse Gmail messages
   - Signature parsing (company, title, phone)
   - Domain detection for businesses
   - System email filtering (noreply@, notifications)

5. **`message_pruner.py`** (272 lines)
   - `prune_thread()` - Keep 4 most recent per thread
   - Thread compression to `[Name:] content` format
   - Remove quoted text and signatures
   - Archive to `.archive/messages/*.jsonl`

6. **`google_business_client.py`** (308 lines)
   - Google Places API integration
   - `search_businesses()` - Text search with location bias
   - `get_business_details()` - Full place data
   - Maps to biz-\* IDs with google_place_id anchor

**🆕 Data Source Extensions (v1.2.21+):**

7. **`website_parser.py`** (575 lines)
   - **Robots.txt compliant** website scraping
   - Extracts: Staff directories, team pages, contact emails
   - Pattern detection: /team, /about-us, /crew, /staff, /artists
   - Role categorization: Owner, Manager, Director, Artist, Promoter
   - Rate limiting per domain (1 second minimum delay)
   - Email classification: booking@, press@, management@, info@
   - LinkedIn URL extraction from team pages

8. **`social_clients.py`** (450 lines)
   - **Twitter/X API v2** - Public profiles, followers, influence metrics
   - **Instagram Graph API** - Business account data (via Facebook)
   - Social profile enrichment from website HTML
   - Influence metrics calculation (followers, engagement)
   - Rate limiting per API requirements
   - Official APIs only - no scraping

9. **`enrichment_client.py`** (680 lines)
   - **Clearbit** - Person + company enrichment from email/domain
   - **Hunter.io** - Email finder and verification for domains
   - **PeopleDataLabs** - Person and company data enrichment
   - Fallback chain with cache-first strategy
   - Staff discovery for domains (Hunter.io domain-search)
   - Email verification and validation

---

## Data Sources & Enrichment Chain

### The BIZINTEL Enrichment Pipeline

**Starting Point:** Google Place ID (most reliable business anchor)

```
Google Place → Website → Staff → Social → Enrichment → Workflow Automation
```

1. **Google Places API**
   - Business name, address, phone, website
   - Google Place ID (strongest anchor)
   - Category, hours, reviews
   - ⚡ 28,500 free requests/month

2. **Website Parsing** (robots.txt compliant)
   - Team pages (/team, /about, /crew, /artists)
   - Staff names, job titles, departments
   - Contact emails (booking@, press@, management@)
   - LinkedIn profile URLs
   - Social media links
   - ⚡ Rate limited to 1 request/second per domain

3. **LinkedIn URLs → Profiles** (extracted from website)
   - Stored for manual linking
   - Future: OAuth for user-consented 1st degree connections
   - ⚡ No automated scraping

4. **Social Media Enrichment**
   - **Twitter/X:** Followers, bio, location, verified status
   - **Instagram:** Business account insights (followers, engagement)
   - ⚡ API rate limits apply (Twitter: 500 requests/15min)

5. **Email Enrichment** (Clearbit/Hunter.io/PDL cascade)
   - Person data: Job title, seniority, department, LinkedIn
   - Company data: Industry, employee count, description
   - Staff finder: Discover email addresses for domain
   - Email verification: Validate deliverability
   - ⚡ Cached for 7 days to minimize API costs

6. **🆕 Workflow Automation** (v1.2.21+)
   - **Keyword Generation:** AI-powered search terms via Gemini API
   - **Location Resolution:** Address → TILE codes + MeshCore positions
   - **uPY Integration:** Export data for .upy workflow scripts
   - ⚡ Gemini: 1,500 requests/day free tier, Geocoding: 28,500/month

---

## Database Schema

**File:** `memory/bank/user/contacts.db`

### Tables

**1. businesses**

```sql
business_id TEXT PRIMARY KEY          -- biz-uuid
name TEXT NOT NULL
raw_address TEXT
lat REAL, lon REAL
website TEXT, website_domain TEXT

google_place_id TEXT UNIQUE           -- External anchor
facebook_page_id TEXT
linkedin_company_id TEXT
twitter_handle TEXT, instagram_handle TEXT

phone TEXT, email TEXT
description TEXT, category TEXT
created_at TEXT, updated_at TEXT
source TEXT, notes TEXT
```

**2. people**

```sql
person_id TEXT PRIMARY KEY            -- prs-uuid
full_name TEXT NOT NULL
primary_email TEXT UNIQUE             -- Primary anchor

phone TEXT
linkedin_url TEXT, twitter_handle TEXT
instagram_url TEXT, facebook_url TEXT

job_title TEXT, company_name TEXT
created_at TEXT, updated_at TEXT
source TEXT, notes TEXT
```

**3. business_person_roles**

```sql
business_person_role_id TEXT PRIMARY KEY  -- rel-uuid
business_id TEXT → businesses
person_id TEXT → people

role_type TEXT                        -- Owner, Staff, Artist
role_title TEXT                       -- Marketing Manager
tags TEXT                             -- drag;promoter;dj
is_primary_contact INTEGER
created_at TEXT, source TEXT
```

**4. audience**

```sql
audience_id TEXT PRIMARY KEY          -- aud-uuid
business_id TEXT → businesses
platform TEXT                         -- facebook, instagram, twitter

followers_count INTEGER
engagement_score REAL
last_synced_at TEXT
created_at TEXT, notes TEXT
```

**5. messages**

```sql
message_id TEXT PRIMARY KEY           -- msg-uuid
gmail_message_id TEXT UNIQUE
thread_id TEXT

sender_email TEXT, sender_name TEXT
subject TEXT, snippet TEXT
compressed_content TEXT               -- [Name:] format

business_id TEXT → businesses
person_id TEXT → people

sent_at TEXT, created_at TEXT
is_archived INTEGER DEFAULT 0
```

**🆕 6. social_profiles**

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
business_id TEXT → businesses
person_id TEXT → people
platform TEXT                         -- twitter, instagram, facebook

username TEXT
profile_url TEXT
display_name TEXT, bio TEXT
followers_count INTEGER
following_count INTEGER
verified INTEGER
platform_user_id TEXT

created_at TEXT, updated_at TEXT
```

**🆕 7. roles** (structured job roles)

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
person_id TEXT → people
business_id TEXT → businesses

role_category TEXT                    -- Owner, Manager, Artist, etc.
role_title TEXT                       -- Marketing Director
department TEXT                       -- Marketing, Operations
seniority TEXT                        -- entry, junior, senior, director

source TEXT                           -- website_parse, manual, api
created_at TEXT
```

**🆕 8. enrichment_cache** (API response caching)

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
lookup_key TEXT UNIQUE                -- email or domain
lookup_type TEXT                      -- person or company

provider TEXT                         -- clearbit, hunter, pdl
response_data TEXT                    -- JSON response

cached_at TEXT
expires_at TEXT                       -- TTL = 7 days default
hit_count INTEGER                     -- Cache hit tracking
```

---

## Commands

### CLOUD EMAIL

```bash
CLOUD EMAIL SYNC
```

Extract contacts from Gmail messages (requires Gmail service integration).

**Process:**

1. Fetch recent Gmail messages
2. Filter system emails (noreply@, notifications)
3. Parse signatures (company, title, phone)
4. Detect business from email domain
5. Generate biz-_/prs-_ IDs
6. Link message to entities
7. Auto-prune old messages

**Status:** Framework complete, awaiting Gmail service integration

---

### CLOUD CONTACTS

```bash
CLOUD CONTACTS LIST                    # All people
CLOUD CONTACTS LIST --business <biz_id> # People for specific business
```

List contacts with their business relationships.

**Example Output:**

```
📇 Contacts (12)

John Smith
  📧 john@acmecorp.com
  💼 Marketing Manager
  🏢 Acme Corp

Jane Doe
  📧 jane@techstart.io
  💼 CEO
```

---

### CLOUD BUSINESS

```bash
CLOUD BUSINESS SEARCH <query> [--location TILE]  # Google Places search
CLOUD BUSINESS LIST                              # All local businesses
```

Search Google Places API and import businesses.

**Example:**

```bash
CLOUD BUSINESS SEARCH "coffee shops" --location AA340
```

**Output:**

```
🔍 Found 5 business(es)

1. Blue Bottle Coffee
   📍 123 Main St, Sydney NSW
   📞 +61 2 9876 5432
   🌐 bluebottlecoffee.com
   ⭐ 4.5 (230 reviews)
   ➕ Added to database: biz-a13f9bca-...
```

**Note:** Requires `GOOGLE_PLACES_API_KEY` in `.env`

---

### CLOUD LINK

```bash
CLOUD LINK MSG <msg_id> TO <biz_id|prs_id>
```

Manually link message to business or person.

**Example:**

```bash
CLOUD LINK MSG msg-abc123... TO biz-def456...
# ✅ Linked message msg-abc123... to business biz-def456...
```

---

### CLOUD PRUNE

```bash
CLOUD PRUNE
```

Archive old messages, keep 4 most recent per thread.

**Process:**

1. Scan all threads
2. Keep 4 most recent messages
3. Archive older messages to `.archive/messages/<thread_id>.jsonl`
4. Compress active messages to `[Name:] content` format
5. Remove quoted text and signatures

**Output:**

```
🗑️ Message Pruning Complete

Threads processed: 42
Messages kept: 168
Messages archived: 215
Messages compressed: 168

Archive: 215 messages in 42 threads (2.3 MB)
```

---

### CLOUD EXPORT

```bash
CLOUD EXPORT CSV|JSON <businesses|people|contacts>
```

Export data to `memory/bank/user/exports/`.

**Examples:**

```bash
CLOUD EXPORT CSV businesses
# ✅ Exported 150 records to: memory/bank/user/exports/businesses.csv

CLOUD EXPORT JSON people
# ✅ Exported 320 records to: memory/bank/user/exports/people.json

CLOUD EXPORT CSV contacts  # People + business relationships
# ✅ Exported 320 records to: memory/bank/user/exports/contacts.csv
```

---

### CLOUD STATS

```bash
CLOUD STATS
```

Show database statistics.

**Output:**

```
📊 BIZINTEL Statistics

Businesses: 150
People: 320
Relationships: 485
Messages (active): 168
Messages (archived): 215

Archive: 42 threads, 2.3 MB

Database: memory/bank/user/contacts.db
```

---

### 🆕 CLOUD WEBSITE PARSE

```bash
CLOUD WEBSITE PARSE <url> [business_id]
```

Extract staff directories and contact information from business websites.

**Legal Compliance:**

- Respects `robots.txt`
- Rate limited (1 second/request minimum)
- Only extracts publicly visible data
- No bypass of technical restrictions

**Extracted Data:**

- Staff names, job titles, departments
- Contact emails (booking@, press@, management@)
- LinkedIn profile URLs
- Phone numbers
- Team page bios

**Example:**

```bash
CLOUD WEBSITE PARSE https://example.com biz-abc123...
```

**Output:**

```
✅ Parsed website: https://example.com
   Found 12 staff members
   Found 5 contact emails
   Found 3 team pages

   ✓ John Smith - Marketing Director
   ✓ Jane Doe - CEO
   ✓ Bob Johnson - Operations Manager
   📧 booking: booking@example.com
   📧 press: media@example.com
```

---

### 🆕 CLOUD SOCIAL ENRICH

```bash
CLOUD SOCIAL ENRICH twitter <handle>
CLOUD SOCIAL ENRICH instagram <account_id>
```

Enrich social media profiles using official APIs.

**Twitter/X:**

- Public profile data (bio, location, verified)
- Follower/following counts
- Profile image URL
- Website links
- Influence metrics

**Instagram:**

- Business account data only (via Facebook Graph API)
- Follower counts, media count
- Bio and website
- Profile picture

**Example:**

```bash
CLOUD SOCIAL ENRICH twitter elonmusk
```

**Output:**

```
✅ Twitter profile: @elonmusk
   Name: Elon Musk
   Bio: Tesla, SpaceX, Twitter
   Followers: 169,421,380
   Following: 523
   Verified: True
   URL: https://twitter.com/elonmusk
```

---

### 🆕 CLOUD ENRICH

```bash
CLOUD ENRICH EMAIL <email>         # Person enrichment
CLOUD ENRICH DOMAIN <domain>       # Company enrichment
CLOUD ENRICH STAFF <domain>        # Find staff emails
```

Enrich data using Clearbit/Hunter.io/PeopleDataLabs APIs with cache-first strategy.

**EMAIL Enrichment:**

- Name, job title, seniority, department
- Company name and domain
- LinkedIn, Twitter profiles
- Phone number, location
- Verified status

**DOMAIN Enrichment:**

- Company name, legal name
- Industry, category
- Employee count, founded year
- Location, address, phone
- Social media handles

**STAFF Discovery:**

- Find email addresses for a domain
- Hunter.io domain-search API
- Job titles, departments
- Email verification status

**Example:**

```bash
CLOUD ENRICH EMAIL contact@acmecorp.com
```

**Output:**

```
✅ Enriched person: contact@acmecorp.com
   Name: John Smith
   Title: Marketing Director
   Company: Acme Corporation
   LinkedIn: https://linkedin.com/in/johnsmith
   Twitter: @johnsmith
   Verified: True
```

**Cache Benefits:**

- 7-day TTL reduces API costs
- Cache hit tracking
- Automatic expiration cleanup
- Per-lookup caching (email or domain)

---

## Configuration (Updated)

### API Keys

Add to `.env`:

```bash
# Google Places API (required for BUSINESS SEARCH)
GOOGLE_PLACES_API_KEY=AIza...

# Workflow Automation (v1.2.21+)
GEMINI_API_KEY=AIza...                               # Keyword generation with AI
GOOGLE_GEOCODING_API_KEY=AIza...                     # Location → TILE codes

# Social Media APIs
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAMlxswEA...  # Twitter API v2
FACEBOOK_ACCESS_TOKEN=EAABsbCS...                    # Instagram Graph API

# Email Enrichment APIs (choose one or more)
CLEARBIT_API_KEY=sk_...                              # Clearbit Enrichment
HUNTER_API_KEY=...                                   # Hunter.io Email Finder
PEOPLE_DATA_LABS_API_KEY=...                         # PeopleDataLabs
```

**Get API Keys:**

| Service             | Free Tier             | Link                                                              |
| ------------------- | --------------------- | ----------------------------------------------------------------- |
| Google Places API   | 28,500 requests/month | [console.cloud.google.com](https://console.cloud.google.com/)     |
| 🆕 Gemini API       | 1,500 requests/day    | [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| 🆕 Google Geocoding | 28,500 requests/month | [console.cloud.google.com](https://console.cloud.google.com/)     |
| Twitter API v2      | 500 requests/15min    | [developer.twitter.com](https://developer.twitter.com/)           |
| Instagram Graph     | Via Facebook App      | [developers.facebook.com](https://developers.facebook.com/)       |
| Clearbit            | 50 requests/month     | [clearbit.com](https://clearbit.com/)                             |
| Hunter.io           | 25 searches/month     | [hunter.io](https://hunter.io/)                                   |
| PeopleDataLabs      | 1,000 requests/month  | [peopledatalabs.com](https://peopledatalabs.com/)                 |

**Note:** All API keys are optional except for the specific features you want to use.

---

## Entity Resolution

Priority matching cascade (from strongest to weakest anchor):

1. **google_place_id** - Strongest, unique per place
2. **linkedin_company_id** - LinkedIn company page
3. **website_domain** - Normalized domain (e.g., `acmecorp.com`)
4. **facebook_page_id** - Facebook business page
5. **twitter_handle** - Twitter/X handle
6. **Fuzzy match** - Name + address similarity (85% threshold)

If no match → **Generate new `biz-*` ID**

### Example Workflow

```python
from extensions.cloud.bizintel import EntityResolver, MarketingDB

db = MarketingDB()
resolver = EntityResolver(db)

# Try to match existing business
business_id = resolver.match_business(
    google_place_id="ChIJ...",
    name="Acme Corp",
    website_domain="acmecorp.com"
)

if not business_id:
    # Create new business
    business_id = resolver.resolve_or_create_business(
        name="Acme Corp",
        google_place_id="ChIJ...",
        website="https://acmecorp.com",
        raw_address="123 Main St, Sydney NSW",
        lat=-33.87,
        lon=151.21,
        source="google_places_api"
    )

print(f"Business ID: {business_id}")
# Business ID: biz-a13f9bca-2e7c-4e1e-a2a3-d9db8a3f90bf
```

---

## Message Pruning

### Thread Compression

**Before:**

```
From: john@acmecorp.com
Subject: Re: Project Update

Hey team,

Great work on the sprint! Here are the tasks for next week:

1. Complete API integration
2. Fix login bug
3. Update documentation

Thanks,
John

---
Sent from my iPhone

> On Dec 10, 2025, at 3:45 PM, Jane Doe <jane@techstart.io> wrote:
>
> Thanks for the update! Looking forward to seeing the progress.
```

**After (Compressed):**

```
[John:] Great work on the sprint! Here are the tasks for next week: 1. Complete API integration 2. Fix login bug 3. Update documentation Thanks, John
```

**Storage Savings:** ~70% reduction in message size

---

## Development

### File Structure

```
extensions/cloud/bizintel/
├── __init__.py              # Module exports (extended)
├── id_generator.py          # UUID generation (120 lines)
├── marketing_db.py          # SQLite wrapper (838 lines - extended with 3 new tables)
├── entity_resolver.py       # Matching engine (396 lines)
├── contact_extractor.py     # Email parsing (310 lines)
├── message_pruner.py        # Thread compression (272 lines)
├── google_business_client.py # Places API (308 lines)
├── website_parser.py        # 🆕 Website scraping (575 lines)
├── social_clients.py        # 🆕 Social media APIs (450 lines)
├── enrichment_client.py     # 🆕 Email enrichment (680 lines)
└── README.md                # This file

core/commands/
└── cloud_handler.py         # Command interface (835 lines - extended with 3 new commands)
```

**Total:** ~4,784 lines across 10 files

**Line Breakdown:**

- Core BIZINTEL (v1.2.21): 2,632 lines
- Data Source Extensions: +2,152 lines
  - website_parser.py: 575 lines
  - social_clients.py: 450 lines
  - enrichment_client.py: 680 lines
  - marketing_db.py extensions: +200 lines
  - cloud_handler.py extensions: +247 lines

---

## Testing

### Manual Testing

```bash
# 1. Initialize database
python -c "from extensions.cloud.bizintel import MarketingDB; db = MarketingDB(); print('✅ Database created')"

# 2. Generate test IDs
python -c "from extensions.cloud.bizintel import generate_business_id, generate_person_id; print(f'Business: {generate_business_id()}'); print(f'Person: {generate_person_id()}')"

# 3. Test business search (requires API key)
# In uDOS:
CLOUD BUSINESS SEARCH "coffee" --location AA340

# 4. Test stats
CLOUD STATS
```

---

## Future Enhancements

### Phase 2 (v1.2.22+)

- **Gmail Integration** - Full email sync with contact extraction
- **LinkedIn API** - Company and people scraping (requires partnership)
- **Facebook Graph API** - Business page data and audience metrics

### Phase 3 (v1.3.0+)

- **Webhook Integration** - Real-time updates from external systems
- **Advanced Analytics** - Business insights, relationship graphs
- **CRM Features** - Task tracking, follow-ups, email templates
- **Mobile Sync** - Cross-device contact synchronization

---

## Troubleshooting

### Database Locked

```
sqlite3.OperationalError: database is locked
```

**Solution:** Close other connections to `contacts.db`

```python
from extensions.cloud.bizintel import MarketingDB
db = MarketingDB()
# ... use database
db.close()  # Always close when done
```

---

### Google Places API Errors

**Error:** `No Places API key found`

**Solution:** Add key to `.env`:

```bash
GOOGLE_PLACES_API_KEY=AIza...
```

**Error:** `403 Forbidden`

**Solution:** Enable "Places API (New)" in Google Cloud Console

---

## Related Documentation

- **🆕 Workflow Automation:** `extensions/cloud/bizintel/WORKFLOW-AUTOMATION.md`
- **uDOS ID Standard:** `dev/roadmap/udos_id_standard.md`
- **Gmail Sync Guide:** `wiki/Google-Cloud-Sync.md`
- **ROADMAP:** `dev/roadmap/ROADMAP.md` (v1.2.21 tasks)
- **Extension System:** `extensions/README.md`
- **Mapping System:** `wiki/Mapping-System.md` (TILE codes)
- **MeshCore Integration:** `extensions/play/meshcore_integration.py`

---

**Last Updated:** December 10, 2025
**Status:** v1.2.21+ Data Source Extensions Complete
**Total Lines:** 4,784 lines across 10 files

**Implementation:**

- ✅ Core BIZINTEL (v1.2.21): 2,632 lines
- ✅ Website Parser: 575 lines
- ✅ Social Media APIs: 450 lines
- ✅ Email Enrichment: 680 lines
- ✅ Database Extensions: 3 new tables (roles, social_profiles, enrichment_cache)
- ✅ Command Extensions: 3 new commands (WEBSITE PARSE, SOCIAL ENRICH, ENRICH)
- ⏳ LinkedIn User Import: Pending OAuth implementation

**Next Phase:** LinkedIn OAuth integration for user-consented 1st degree connection imports
