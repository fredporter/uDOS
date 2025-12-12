# uDOS ID Format Standard (SCRAPE v2.0)

All internal IDs in uDOS must follow this canonical pattern:

```text
[a-z0-9-]+
```

Lowercase, alphanumeric, dashes only.

This ensures IDs are:

- URL-safe
- Filesystem-safe
- JSON/CSV friendly
- Cross-platform compatible
- Easy to copy, paste, grep and log

---

## 1. Business ID

### 1.1 Format

**Field:** `business_id` (Primary Key)

```text
biz-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Where `x` = lowercase hex character (`0–9`, `a–f`).

**Example:**

```text
biz-a13f9bca-2e7c-4e1e-a2a3-d9db8a3f90bf
```

### 1.2 Requirements

- Must always be generated **internally by uDOS**
- Must never be derived from external provider IDs
- Must be globally unique
- Must remain stable for the life of the business entity
- Used as the **root key** in the Business → People → Audience graph

### 1.3 Rationale for `biz-` prefix

- Fast visual identification of object type
- Easy filtering and indexing by prefix
- Avoids collisions with other ID spaces (people, roles, audiences)

---

## 2. Person ID

### 2.1 Format

**Field:** `person_id`

```text
prs-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Example:**

```text
prs-f1ac03df-baaa-4b4e-b63f-95b2316761ab
```

### 2.2 Requirements

- One `person_id` per unique individual
- Represents staff, owners, performers, public-facing influencers, etc.
- Must not be used for random, non-public fans/customers (privacy concerns)

---

## 3. Relationship IDs (Business ↔ Person)

If a join table requires its own primary key, use:

```text
rel-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Otherwise, a composite primary key of `(business_id, person_id)` may be used.

**Recommended format:**

- `business_person_role_id: rel-...`

Used in the `BusinessPersonRole` table to uniquely identify the relationship record itself.

---

## 4. Audience IDs (Optional)

Audience records can also have a dedicated ID if needed for auditing or versioning:

```text
aud-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Field:** `audience_id`

Used in the `BusinessAudience` table.

This is optional; a composite key of `(business_id, platform)` can also work where appropriate.

---

## 5. ID Generation Specification

### 5.1 General Rules

All IDs MUST:

- Be **lowercase**
- Include only these characters: `a–z`, `0–9`, `-`
- Start with a semantic prefix and a dash:
  - `biz-` for businesses
  - `prs-` for people
  - `rel-` for business–person relationships
  - `aud-` for audience records
- Never include:
  - Uppercase letters
  - Underscores (`_`)
  - Spaces
  - Other special characters
  - Leading or trailing dashes

### 5.2 Recommended Strategy

#### Option A — UUIDv4 Hex + Prefix (Preferred)

1. Generate a standard UUIDv4.
2. Use its lowercase hex form (`uuid4().hex`).
3. Format with dashes and prefix, e.g.:

```text
biz-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

This gives:
- Extremely low collision risk
- Familiar UUID structure
- Consistent length

#### Option B — Short IDs (NanoID-style)

If shorter IDs are needed in future:

```text
biz-8h2k3ldp9am0q1xr
```

Still must respect:

- Lowercase
- Alphanumeric + dashes only
- Prefix + dash convention

The primary recommendation for v2.0 is **UUIDv4 hex** with typed prefixes.

---

## 6. Entity Resolution and IDs

External provider IDs **must never** be used as primary keys.
Instead, they act as **anchors** that map onto internal uDOS IDs.

### 6.1 Business Matching Priority

When a new business-like record is discovered (from Google Places, LinkedIn, Facebook, Twitter/X, or a website), the system should:

1. Check for matching `google_place_id`
2. Else check `linkedin_company_id`
3. Else check `website_domain` (normalised)
4. Else check `facebook_page_id`
5. Else check `twitter_handle`
6. Else perform a fuzzy match on `(name + normalised address)`
7. If no confident match is found → **create a new `business_id` (biz-...)**

### 6.2 External IDs as Attributes

External IDs must be stored as attributes on the Business entity, for example:

- `google_place_id: string | null`
- `facebook_page_id: string | null`
- `linkedin_company_id: string | null`
- `twitter_handle: string | null`
- `website_domain: string | null`

All of these help **resolve and merge** records, but none of them replace `business_id` as the primary key.

---

## 7. Data Model Snippets (with uDOS IDs)

### 7.1 Business

```yaml
Business:
  business_id: biz-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  name: string
  raw_address: string
  lat: float
  lon: float
  website: string
  website_domain: string

  google_place_id: string | null
  facebook_page_id: string | null
  linkedin_company_id: string | null
  twitter_handle: string | null

  created_at: datetime
  updated_at: datetime
```

### 7.2 Person

```yaml
Person:
  person_id: prs-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  full_name: string
  primary_email: string | null
  linkedin_url: string | null
  twitter_handle: string | null
  instagram_url: string | null
  notes: string | null

  created_at: datetime
  updated_at: datetime
```

### 7.3 BusinessPersonRole

```yaml
BusinessPersonRole:
  business_person_role_id: rel-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

  business_id: biz-...
  person_id: prs-...

  role_type: string        # e.g. "Owner", "Staff", "Artist"
  role_title: string       # e.g. "Marketing Manager", "Talent Booker"
  tags: string             # e.g. "drag;promoter;dj"
  is_primary_contact: boolean
  source: string           # e.g. "linkedin", "website", "scrape", "manual"

  created_at: datetime
```

### 7.4 BusinessAudience

```yaml
BusinessAudience:
  audience_id: aud-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

  business_id: biz-...
  platform: string          # "facebook", "instagram", "twitter", etc.
  followers_count: int
  engagement_score: float | null
  last_synced_at: datetime
```

---

## 8. Dev Brief Insert (One Paragraph)

> **ID Standard (uDOS v2.0)**  
> All internal entities (businesses, people, relationships, audience metrics) must use a unified uDOS ID format. IDs must be lowercase, alphanumeric with dashes only, and prefixed by entity type. Examples include `biz-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` for businesses and `prs-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` for people. External provider IDs (Google/Facebook/LinkedIn/Twitter) may never substitute for internal IDs. Entity resolution must always map external identifiers onto internal `biz-*` / `prs-*` IDs, with `business_id` and `person_id` acting as the sole primary keys for their respective entities.
