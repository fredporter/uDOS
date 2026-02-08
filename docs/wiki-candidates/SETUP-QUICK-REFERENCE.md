# Quick Reference - UDOS Setup System

## What Changed?

| Before | After |
|--------|-------|
| 15+ setup fields | 6 essential fields |
| TUI data not saved | Auto-saved to .env |
| Wizard config didn't sync back | Bidirectional sync |
| No identity encoding | UDOS Crypt system |
| Plain UUID profile IDs | Memorable color-animal-adjective |

## The 6 Essential Fields

1. **Username** - Text, required, no numbers
2. **Date of Birth** - YYYY-MM-DD format, required
3. **Role** - admin | user | ghost
4. **Password** - Optional (blank for ghost)
5. **Location** - City or grid code
6. **Timezone** - IANA format (e.g., America/Los_Angeles)
7. **OS Type** - alpine | ubuntu | mac | windows

## UDOS Crypt ID

Maps user's DOB to 3-part identifier:

```
DOB: 1975-11-15 + Location: New York
  ↓
Starsign: Scorpio → Color: blue
Generation: Gen X → Animal: wolf
Rising: day 319 % 12 = 6 → Adjective: nurturing
  ↓
UDOS Crypt ID: blue-wolf-nurturing
Profile ID: c1bc259dc971c012 (locked to location)
```

## Command Reference

### View Setup Profile
```bash
SETUP --profile
```

Shows:
- Current identity
- UDOS Crypt ID
- Generated Profile ID
- Age, role, timezone

### Run Setup Story
```bash
SETUP
```

Launches interactive setup with:
- Color-coded form fields
- System predictions (timezone, etc.)
- Tab/Enter to accept
- Validation feedback

### Manual Sync (if offline during setup)
```bash
CONFIG SYNC
```

Syncs local .env to Wizard keystore.

## .env Structure

**What's stored in .env (Local only):**
```
USER_NAME="ghost"
USER_DOB="1980-01-01"
USER_ROLE="user"
USER_PASSWORD=""
UDOS_LOCATION="New York"
UDOS_TIMEZONE="America/New_York"
OS_TYPE="mac"
WIZARD_KEY="uuid-here"
```

**NOT in .env (Goes to Wizard keystore):**
- API keys
- OAuth tokens
- Cloud credentials
- Webhooks
- Integration settings

## UDOS Crypt Tables (Quick Reference)

### Zodiac → Color (12)
```
Capricorn(Dec-Jan) → black
Aquarius → silver
Pisces → indigo
Aries → red
Taurus → green
Gemini → yellow
Cancer → pearl
Leo → gold
Virgo → cream
Libra → rose
Scorpio → blue ← Example (Nov)
Sagittarius → purple
```

### Generation → Animal (12)
```
1900-1945: Pre-Boomer → phoenix
1946-1964: Boomer → eagle
1965-1980: Gen X → wolf
1981-1996: Millennial → fox
1997-2012: Gen Z → owl
2013-2025: Gen Alpha → dolphin
2026-2041: Gen Beta → mongoose
2042-2057: Gen Gamma → raven
2058-2073: Future1 → leopard
2074-2089: Future2 → lynx
2090-2105: Future3 → badger
2106-2121: Future4 → hawk
```

### Rising/Decan → Adjective (12)
```
Day-of-year % 12:
0 → swift
1 → steady
2 → adaptive
3 → bold
4 → grounded
5 → flowing
6 → nurturing ← Example (day 319)
7 → creative
8 → analytical
9 → harmonious
10 → mysterious
11 → visionary
```

## Test Examples

All working ✓:

```
1975-11-15 (New York)     → blue-wolf-nurturing       (Gen X, Scorpio)
1990-01-01 (San Francisco) → black-fox-swift          (Millennial, Capricorn)
2005-07-23 (London)       → gold-owl-visionary        (Gen Z, Leo)
1945-06-21 (Tokyo)        → pearl-phoenix-bold        (Pre-Boomer, Cancer)
2020-03-15 (Sydney)       → indigo-dolphin-adaptive   (Gen Alpha, Pisces)
```

## Boundary Rules (Critical!)

| Layer | Contains | Does NOT Contain |
|-------|----------|------------------|
| **.env** | Username, DOB, Role, Location, Timezone, OS, Wizard Key | API keys, OAuth tokens, secrets |
| **Wizard Keystore** | Extended integrations, secrets | User identity (stored separately) |

## Files to Know

| File | Purpose | Size |
|------|---------|------|
| `core/services/udos_crypt.py` | UDOS Crypt encoding | 350 lines |
| `core/services/config_sync_manager.py` | .env ↔ Wizard sync | 450 lines |
| `core/tui/advanced_form_handler.py` | Enhanced form fields | 500+ lines |
| `core/tui/setup-story.md` | Setup questions | 80 lines |
| `docs/UDOS-CRYPT-SYSTEM.md` | Complete reference | 400 lines |

## Testing

```bash
python3 test_udos_crypt_standalone.py
```

Output:
```
✓ UDOS Crypt encoding (5 test cases)
✓ Identity enrichment
✓ Profile ID generation
✓ DOB validation (valid/invalid)
✓ Reference tables display
```

## Security Notes

✓ DOB is **local-only** (never transmitted initially)
✓ UDOS Crypt is **visible** (not cryptographic)
✓ Profile ID **ties to device location** (portable between devices)
✓ Wizard Key **gates access to keystore** (auto-generated)
✓ Password **protects Core locally only** (optional for ghost mode)

## Future Enhancements

- [ ] AES-256 encryption for DOB storage
- [ ] Extended decan system (36 adjectives instead of 12)
- [ ] Custom crypt tables per installation
- [ ] Profile migration tool for existing users
- [ ] Crypt registry & cohort analytics

## Key Insights

1. **Deterministic** - Same DOB always produces same crypt ID
2. **Memorable** - Color-animal-adjective vs UUID
3. **Privacy-Preserving** - Groups users by cohort without exposing DOB
4. **Device-Locked** - Profile ID unique per location
5. **Reversible** - Can verify DOB matches crypt ID
6. **Extensible** - Custom tables possible per installation

## Common Tasks

### Generate UDOS Crypt for DOB
```python
from core.services.udos_crypt import get_udos_crypt

crypt = get_udos_crypt()
crypt_id = crypt.encode_identity("1975-11-15")
# Returns: "blue-wolf-nurturing"
```

### Validate DOB
```python
is_valid, msg = crypt.validate_dob("1975-11-15")
# Returns: (True, "✅ Valid: Scorpio Gen X")
```

### Get Full Components
```python
components = crypt.get_crypt_components("1975-11-15")
# Returns: {
#   'starsign': 'Scorpio',
#   'color': 'blue',
#   'generation': 'Gen X',
#   'animal': 'wolf',
#   'adjective': 'nurturing',
#   'crypt_id': 'blue-wolf-nurturing'
# }
```

### Generate Profile ID
```python
profile_id = crypt.generate_profile_id("1975-11-15", "New York")
# Returns: "c1bc259dc971c012"
```

### Enrich Identity
```python
from core.services.identity_encryption import IdentityEncryption

identity = {
    'user_username': 'ghost',
    'user_dob': '1975-11-15',
    'user_location': 'New York',
}

enc = IdentityEncryption()
enriched = enc.enrich_identity(identity, location='New York')
# Adds: _starsign, _color, _generation, _animal,
#       _adjective, _crypt_id, _profile_id
```

---

**Quick Ref Version:** 1.0
**Last Updated:** 2026-01-30
**Related:** [UDOS-CRYPT-SYSTEM.md](docs/UDOS-CRYPT-SYSTEM.md), [TUI-SETUP-INTEGRATION.md](docs/TUI-SETUP-INTEGRATION.md)
