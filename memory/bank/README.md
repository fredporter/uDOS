# Memory Bank — `/memory/bank/`

**Purpose:** User-customizable data layer (not synced with git, but syncable P2P)

---

## 📁 Structure

```
memory/bank/
├── system/              # System scripts (TRACKED: templates only)
│   ├── startup-script.md
│   └── reboot-script.md
│
├── locations/           # Location and timezone data
│   ├── locations.json           # Full location database
│   ├── timezones.json           # Timezone mappings
│   ├── user-locations.json      # User-added locations
│   └── locations.db             # SQLite (when > 500KB)
│
├── knowledge/           # User knowledge additions
│   ├── personal/        # User notes, research
│   └── imported/        # Downloaded content
│
├── checklists/          # User checklists & templates
│   └── ...
│
└── binders/             # User binder projects
    └── ...
```

---

## 🔒 Git Status

| Path | Git Status | Sync Method | Notes |
|------|-----------|-------------|-------|
| `system/*.md` | ✅ **TRACKED** | Git | Framework templates only |
| `locations/` | ❌ Gitignored | P2P via MeshCore/QR/Audio | User location data |
| `knowledge/` | ❌ Gitignored | P2P via MeshCore/QR/Audio | User additions |
| `checklists/` | ❌ Gitignored | P2P via MeshCore/QR/Audio | User templates |
| `binders/` | ❌ Gitignored | P2P via MeshCore/QR/Audio | User projects |

---

## 📍 Location Data

### Layers

**Runtime (`locations.json`)**
- Full location database (currently ~60KB)
- All regions, connections, descriptions
- Loaded at startup
- User-editable

**Timezone Mappings (`timezones.json`)**
- Location ID → timezone mapping
- User-editable
- Used for time-based features

**User Additions (`user-locations.json`)**
- Custom locations added by user
- Separate file for easy management
- Merged with main locations at runtime

**SQLite Migration (`locations.db`)**
- When location data exceeds 500KB
- Tables: locations, timezones, connections, user_additions
- Better performance for large datasets
- Migration happens automatically

---

## 📚 Knowledge Bank

### Personal (`knowledge/personal/`)
- User notes and research
- Private observations
- Personal research projects

### Imported (`knowledge/imported/`)
- Content downloaded from other installations
- Shared knowledge via P2P
- Organized by source

---

## ✅ Checklists

Moved from `/knowledge/checklists/` (which should only contain static reference).

Store:
- User checklists
- Checklist templates
- Progress tracking

---

## 🔗 Binders

User binder projects:
- Documents
- Collections
- Custom organizations
- Compiled outputs

---

## 🔄 P2P Sync Protocol

Bank data can be synced across installations using:
- **MeshCore** (P2P mesh network)
- **QR Relay** (visual data transfer)
- **Audio Relay** (acoustic packets)
- **Bluetooth Private** (paired devices)
- **NFC** (physical contact)

**NOT synced via:**
- ❌ Git (user data, not tracked)
- ❌ Cloud (offline-first design)
- ❌ Bluetooth Public (signal only, no data)

---

## 📊 Data Size Guidelines

| Data Type | JSON Limit | Action at Threshold |
|-----------|-----------|---------------------|
| locations.json | 500KB | → locations.db |
| timezones.json | 100KB | → locations.db |
| user-locations.json | 200KB | → locations.db |

**Migration is automatic** when threshold reached.

---

## 🚀 Getting Started

### First Run (Automatic)
1. Framework seed data copied to bank
2. System scripts initialized
3. Empty user data directories created

### Adding Data

**Location:**
```bash
cp core/framework/templates/location-template.json \
   memory/bank/locations/my-place.json
```

**Knowledge:**
```bash
echo "# My Note" > memory/bank/knowledge/personal/note.md
```

**Checklist:**
```bash
echo "- [ ] Task 1" > memory/bank/checklists/todo.md
```

---

## 💾 Backup Strategy

Bank data should be backed up via:
1. **BACKUP command** (local snapshots)
2. **P2P sync** to other installations
3. **Encrypted export** for off-site storage

**NOT recommended:** Git commits of personal data

---

**Version:** 1.0.0
**Last Updated:** 2026-01-29
**Gitignored:** User data (except system/ templates)
