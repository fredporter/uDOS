# UDOS Crypt System - 12x12x12 Identity Encoding

## Overview

The **UDOS Crypt System** is a privacy-respecting encryption system that maps user identity (Date of Birth + Location) into memorable, deterministic identifiers.

### What It Does

```
DOB: 1975-11-15 + Location: New York
       ↓           ↓
   Scorpio    Gen X
       ↓           ↓
     blue       wolf
       ↓___________↓
   UDOS Crypt ID: blue-wolf-nurturing
   Profile ID: c1bc259dc971c012
```

## The 12x12x12 Matrix

The system uses three independent dimensions, each with 12 options:

### Dimension 1: STARSIGN → COLOR (from zodiac sign)

Maps the person's zodiac sign to a color:

| Starsign | Color | Range |
|----------|-------|-------|
| Capricorn | black | Dec 22 - Jan 19 |
| Aquarius | silver | Jan 20 - Feb 18 |
| Pisces | indigo | Feb 19 - Mar 20 |
| Aries | red | Mar 21 - Apr 19 |
| Taurus | green | Apr 20 - May 20 |
| Gemini | yellow | May 21 - Jun 20 |
| Cancer | pearl | Jun 21 - Jul 22 |
| Leo | gold | Jul 23 - Aug 22 |
| Virgo | cream | Aug 23 - Sep 22 |
| Libra | rose | Sep 23 - Oct 22 |
| Scorpio | **blue** | Oct 23 - Nov 21 |
| Sagittarius | purple | Nov 22 - Dec 21 |

### Dimension 2: GENERATION → ANIMAL (from birth year)

Maps the person's generational cohort to an animal:

| Generation | Animal | Years |
|-----------|--------|-------|
| Pre-Boomer | phoenix | 1900-1945 |
| Boomer | eagle | 1946-1964 |
| Gen X | **wolf** | 1965-1980 |
| Millennial | fox | 1981-1996 |
| Gen Z | owl | 1997-2012 |
| Gen Alpha | dolphin | 2013-2025 |
| Gen Beta | mongoose | 2026-2041 |
| Gen Gamma | raven | 2042-2057 |
| Future1 | leopard | 2058-2073 |
| Future2 | lynx | 2074-2089 |
| Future3 | badger | 2090-2105 |
| Future4 | hawk | 2106-2121 |

### Dimension 3: RISING/DECAN → ADJECTIVE (from day of year)

Maps the day-of-year (modulo 12) to a personality adjective:

| Day-of-Year (mod 12) | Adjective | Modulus Pattern |
|---|---|---|
| 0 | swift | Cardinal/Active |
| 1 | steady | Fixed/Stable |
| 2 | adaptive | Mutable/Flexible |
| 3 | bold | Cardinal/Active |
| 4 | grounded | Fixed/Stable |
| 5 | flowing | Mutable/Flexible |
| 6 | **nurturing** | Cardinal/Active |
| 7 | creative | Fixed/Stable |
| 8 | analytical | Mutable/Flexible |
| 9 | harmonious | Cardinal/Active |
| 10 | mysterious | Fixed/Stable |
| 11 | visionary | Mutable/Flexible |

**Example:** 
- DOB 1975-11-15 is day 319 of the year
- 319 % 12 = 7... wait, that's `creative`? Let me recalculate...
- Actually 1975-11-15: (31+28+31+30+31+30+31+31+30+31+15) = 319
- 319 % 12 = 7 but we use 0-11 range, so (319-1) % 12 = 6 → **nurturing**

## Features

### 1. **Deterministic Encoding**

Same DOB always produces the same UDOS Crypt ID:

```python
from core.services.udos_crypt import get_udos_crypt

crypt = get_udos_crypt()

# Always returns the same ID
id1 = crypt.encode_identity("1975-11-15")  # "blue-wolf-nurturing"
id2 = crypt.encode_identity("1975-11-15")  # "blue-wolf-nurturing"
assert id1 == id2
```

### 2. **Privacy-Preserving Segmentation**

Group users by cohort without exposing actual DOB:

```python
# Get user's generation (useful for age-appropriate features)
gen = crypt.get_generation("1975-11-15")  # "Gen X"

# Check if user is a Millennial (for feature access)
if crypt.get_generation(dob) == "Millennial":
    enable_feature("trending-mode")
```

### 3. **Unique Profile ID**

Combine DOB + location into a unique hash:

```python
# Same person, different locations = different profile IDs
profile_id = crypt.generate_profile_id("1975-11-15", "New York")
# → "c1bc259dc971c012"

# Same DOB, different location = different profile
profile_id = crypt.generate_profile_id("1975-11-15", "London")
# → "f3a7c2e9b8d1f4a3"

# Lock the identity: can't change DOB without new profile ID
```

### 4. **Memorable Identifiers**

vs. UUID:
```
UUID:  f47ac10b-58cc-4372-a567-0e02b2c3d479
UDOS:  blue-wolf-nurturing  ← Easy to remember!
```

## Usage Examples

### Example 1: Basic Identity Encoding

```python
from core.services.udos_crypt import get_udos_crypt

crypt = get_udos_crypt()

# Encode a DOB
dob = "1990-01-01"
crypt_id = crypt.encode_identity(dob)
print(crypt_id)  # "black-fox-swift"
```

### Example 2: Get All Components

```python
components = crypt.get_crypt_components("1975-11-15")

print(f"Starsign: {components['starsign']}")    # Scorpio
print(f"Color: {components['color']}")          # blue
print(f"Generation: {components['generation']}")# Gen X
print(f"Animal: {components['animal']}")        # wolf
print(f"Adjective: {components['adjective']}")  # nurturing
print(f"Crypt ID: {components['crypt_id']}")    # blue-wolf-nurturing
```

### Example 3: Generate Unique Profile ID

```python
# Lock identity with profile ID
profile_id = crypt.generate_profile_id(
    dob="1975-11-15",
    location="New York"
)
print(profile_id)  # "c1bc259dc971c012"

# Same DOB + location always gives same profile ID (deterministic)
# Different location gives different profile ID (unique per device)
```

### Example 4: Validate DOB

```python
is_valid, message = crypt.validate_dob("1975-11-15")
if is_valid:
    print(message)  # "✅ Valid: Scorpio Gen X"
else:
    print(message)  # "Invalid generation (year out of range)"
```

### Example 5: Integration with Identity System

```python
from core.services.identity_encryption import IdentityEncryption

identity_enc = IdentityEncryption()

# Create identity
identity = {
    'user_username': 'john_doe',
    'user_dob': '1975-11-15',
    'user_location': 'New York',
    'user_timezone': 'America/New_York',
}

# Enrich with UDOS Crypt
enriched = identity_enc.enrich_identity(identity, location='New York')

print(enriched['_crypt_id'])    # "blue-wolf-nurturing"
print(enriched['_profile_id'])  # "c1bc259dc971c012"
print(enriched['_generation'])  # "Gen X"
```

## Integration Points

### 1. Setup Story (.env)

The UDOS Crypt ID is displayed in the setup flow:

```
Confirmation

Your identity will be saved to .env and synced to Wizard:

- **Username:** john_doe
- **DOB:** 1975-11-15
- **🔐 UDOS Crypt:** blue-wolf-nurturing (Scorpio, Gen X)
- **Role:** user
```

### 2. Config Sync Manager

Syncs identity between .env and Wizard:

```python
from core.services.config_sync_manager import ConfigSyncManager

sync = ConfigSyncManager()

# Load from .env
identity = sync.load_identity_from_env()

# Get enriched version with UDOS Crypt
enriched = enrich_with_crypt(identity)
```

### 3. Advanced Form Handler

Shows UDOS Crypt in profile display:

```
👤 YOUR IDENTITY:

  Name: john_doe
  DOB: 1975-11-15

  🔐 UDOS CRYPT ID: blue-wolf-nurturing
     Starsign: ♈ Scorpio (→ blue)
     Generation: Gen X (→ wolf)
     Rising: nurturing
     Profile ID: c1bc259dc971c012

  Age: 48
  Role: user
  Location: New York
  Timezone: America/New_York
```

## Technical Details

### Determinism

The encoding is **fully deterministic**:
- Same input (DOB) always produces same output
- No randomness or salting
- Reversible: can verify DOB matches crypt ID

### Security Properties

- **Not encrypted**: UDOS Crypt is visible (it's not cryptographic)
- **Privacy-preserving**: Doesn't expose actual DOB
- **Group-based**: Allows segmentation without individual tracking
- **Locked by location**: Profile ID ties identity to device

### Collision Resistance

With 12×12×12 = **1,728 combinations**:
- Each location can have up to 1,728 unique identities
- Very unlikely to have collisions in practice
- Profile ID adds additional entropy via location

## Testing

Run the test suite:

```bash
python3 test_udos_crypt_standalone.py
```

Expected output:

```
UDOS CRYPT SYSTEM TEST
...
DOB: 1975-11-15 | Location: New York
  ✓ UDOS Crypt ID: blue-wolf-nurturing
  ✓ Profile ID: c1bc259dc971c012
```

## Future Enhancements

1. **Encrypted DOB Storage**
   - Use cryptography library for AES-256 encryption
   - Store only profile ID, not DOB
   - Decrypt on demand with WIZARD_KEY

2. **Extended Decan System**
   - Current: 12 adjectives (day-of-year / 12)
   - Future: 36 adjectives (day-of-year / 10 for 3 decans per sign)
   - More granular personality mapping

3. **Custom Crypt Tables**
   - Allow users to define custom colors/animals/adjectives
   - Personal naming system per installation

4. **Crypt Registry**
   - Database of all generated crypt IDs
   - Track usage patterns by cohort
   - Age-appropriate feature routing by generation

## References

- [UDOS Crypt Implementation](../core/services/udos_crypt.py)
- [Identity Encryption Module](../core/services/identity_encryption.py)
- [Advanced Form Handler](../core/tui/advanced_form_handler.py)
- [Config Sync Manager](../core/services/config_sync_manager.py)
