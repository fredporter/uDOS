# uDOS Cloud Sync Brief
### *Login with Personal Gmail for Memory/Shared Synchronisation (15 MB Allowance)*

## 1. Overview

This brief outlines an approach for enabling **“Login with Gmail (personal)”** in uDOS to provide **secure cloud-based synchronisation** of selected memory tiers and shared assets. The solution uses Google's authentication and a lightweight cloud storage allocation (≈ **15 MB** per user) to keep key uDOS files synced across devices while the system remains fundamentally **offline-first**.

---

## 2. Why Gmail Login?

Most users already have a personal Gmail account. Leveraging this provides:

- **Zero onboarding friction**
  Users sign in with an identity they already trust.

- **Secure authentication**
  Google OAuth ensures industry-standard login security without uDOS handling passwords.

- **Small but powerful sync space**
  15 MB is enough for synchronising:
  - Memory metadata
  - Shared community structures
  - `.uPY` scripts
  - Knowledge index files
  - Small text-based notes, mission logs, configs
  - Survival guides in markdown
  - Sync manifests and permissions

uDOS remains offline-first; Gmail sync is a **supplement**, not a dependency.

uDOS simple email service using Gmail send and receive personal gmail in uDOS (convert .eml to uDOS flavoured .md) and/or tasks.json

Email is not stored on gmail, uDOS downlopds and deleted from cloud - replacing emails with md docs and udos diagrams stored in the Google drive cloud, for access by web applications/api.

---

## 3. How Gmail Sync Works

### a) Authentication
Users authenticate via:

- `LOGIN GMAIL`
- Browser-based OAuth consent screen
- uDOS receives:
  - an access token
  - a refresh token
  - user profile (email, name, ID)

Tokens are stored securely in .env

### b) Storage Backend
Using the user’s **personal Google Drive**:

- uDOS creates a folder:

/uDOS-sync/

- Allocates **≈15 MB** for synchronised assets
(lightweight due to text-first architecture).

### c) Sync Targets
uDOS syncs a curated set of files:

- `MEMORY/docs/` – user docs
- `MEMORY/shared/` – Community, Team &Shared/Public content
- `MEMORY/ucode/` - `.uPY` scripts
- Config and context files
- Knowledge index and metadata
- Mission state (lightweight logs, not maps)

Large/complex data (maps, diagrams, binaries, PDFs) remain **local-only**.

### d) Sync Mode
- **Manual:** `SYNC NOW`
- **On-exit:** optional
- **Conflict-safe:** last-write-wins with local commit history
- **Offline-proof:** no sync required for full usage

uDOS behaves normally without connectivity or login.

---

## 4. How This Fits uDOS Philosophy

### Offline-first
Nothing breaks if:
- user is offline
- token expires
- Google rejects the request
- storage is full

uDOS simply caches and syncs later.

### Security-first
- Tokens stored encrypted
- Scoped OAuth permissions (Drive App Folder only)
- No access to user’s personal Drive files outside the uDOS folder
- Tier 1 remains strictly offline-only
- Tier 2/3 sharing rules still apply

### Retro/Minimalist footprint
Sync is tiny:
- Markdown
- `.uPY` scripts
- JSON metadata
These are extremely small and efficient to store.

---

## 5. Developer Integration

### a) Hooks in the API Server
- `POST /api/sync`
- `POST /api/login/gmail`
- `POST /api/logout`

### b) VS Code Extension Support
The extension can provide:
- “Login with Gmail” button
- Sync status indicator
- Conflict viewer
- Quick upload of `.uPY` scripts or memory notes

### c) Webhook Compatibility
Although Gmail isn’t event-driven like Slack/Notion/GitHub, uDOS may periodically check for updates using a sync manifest.

---

## 6. User Experience Flow

1. User types:

LOGIN GMAIL

2. Web browser opens for Google OAuth.
3. On success, uDOS shows:

Gmail linked. Sync folder: /uDOS-sync/
Available cloud space: ~15 MB

4. User runs:

SYNC NOW

5. Cloud sync completes; conflict resolution runs if needed.

The experience is simple, low-friction, and tightly scoped.

---

## 7. Summary

Adding **Gmail (personal) login** for uDOS cloud sync provides:

- Secure and effortless authentication
- Lightweight cloud-based memory synchronisation
- Support for shared `.uPY` code, knowledge indexes, logs, and team/community tiers
- Extended integration with the API server and VS Code extension
- A compact 15 MB sync system aligned with uDOS’s offline-first, minimal, and privacy-focused design

This enables users to carry essential uDOS knowledge across devices without compromising its core philosophy.
