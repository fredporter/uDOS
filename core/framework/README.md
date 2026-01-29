# Core Framework — `/core/framework/`

**Purpose:** Distribution templates, schemas, and seed data for uDOS installations

---

## 📁 Structure

```
core/framework/
├── schemas/           # JSON validation schemas
│   ├── location.schema.json
│   └── version.schema.json
├── templates/         # Default templates for customization
│   └── location-template.json
└── seed/              # Minimal seed data for new installations
    ├── locations-seed.json     (< 10KB)
    └── timezones-seed.json     (< 5KB)
```

---

## 📖 What Goes Where

### Schemas (`schemas/`)
- **Purpose:** Validation schemas for JSON data
- **Format:** `.schema.json`
- **Usage:** Validate incoming data against these schemas
- **Distribution:** Always included in public repo

### Templates (`templates/`)
- **Purpose:** Example files for customization
- **Format:** `-template.json` or `-template.md`
- **Usage:** Copy to `/memory/` and customize
- **Distribution:** Always included, for reference

### Seed Data (`seed/`)
- **Purpose:** Minimal data for framework initialization
- **Format:** `-seed.json` (< 10KB each)
- **Usage:** Automatically loaded on first run
- **Distribution:** Part of public repo distribution
- **Note:** Full data lives in `/memory/bank/` after installation

---

## 🔄 Initialization Flow

1. **Installation:** Framework files (this directory) are part of public distribution
2. **First Run:** Seed data is loaded from `seed/` directory
3. **User Customization:** User adds custom entries to `/memory/bank/`
4. **Runtime:** Core uses framework + bank data combined

---

## 🔗 Related Directories

| Directory | Purpose | Git Status |
|-----------|---------|------------|
| `/core/framework/` | Schemas, templates, seed | ✅ Tracked |
| `/knowledge/` | Static reference library | ✅ Tracked |
| `/memory/bank/` | User data (full locations, etc.) | ❌ Gitignored |

---

## 🚀 Using Templates

1. Copy template to `/memory/bank/`:
   ```bash
   cp core/framework/templates/location-template.json \
      memory/bank/locations/my-location.json
   ```

2. Customize for your needs:
   ```json
   {
     "id": "L300-XX00",
     "name": "My Custom Location",
     ...
   }
   ```

3. Your location is instantly available in the system

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-29
