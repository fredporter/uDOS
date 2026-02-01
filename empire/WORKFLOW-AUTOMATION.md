# BIZINTEL Workflow Automation

**AI-powered keyword generation and location resolution for uDOS workflows**

## Overview

BIZINTEL workflow automation provides two key capabilities:

1. **Keyword Generation**: AI-powered search keyword generation using Google Gemini
2. **Location Resolution**: Convert addresses to TILE codes and MeshCore grid positions

Both features integrate with uDOS workflows (TypeScript scripts in .md files) via variable export.

---

## 1. Keyword Generation

### Purpose
Generate intelligent search keywords for business discovery workflows using:
- Google Gemini AI (when available)
- Industry-specific templates (offline fallback)

### Command Syntax

```bash
CLOUD GENERATE KEYWORDS <industry> [--location <location>] [--type <business_type>] [--export]
```

**Arguments:**
- `<industry>` - Required. Industry category (e.g., "live music venues", "cafes", "gyms")
- `--location <location>` - Optional. Geographic context (e.g., "Sydney", "Brooklyn NYC")
- `--type <business_type>` - Optional. Business subcategory (e.g., "jazz club", "organic cafe")
- `--export` - Optional. Export as TypeScript variables for workflow automation

### Examples

**Basic keyword generation:**
```bash
uDOS> CLOUD GENERATE KEYWORDS "live music venues"
```

Output:
```
✅ Generated keywords for: live music venues

🔍 Primary Keywords (10):
   • live music venues
   • concert halls
   • music clubs
   • live performance spaces
   • acoustic venues
   ...

🏢 Industry Terms (5):
   • entertainment venues
   • nightlife
   • ticketing
   ...

Source: gemini-ai
```

**With location context:**
```bash
uDOS> CLOUD GENERATE KEYWORDS "cafes" --location "Sydney CBD"
```

**Export for workflow automation:**
```bash
uDOS> CLOUD GENERATE KEYWORDS "live music venues" --location "Sydney" --export
```

Output (uPY variable format):
```upy
# Keyword Set: live music venues
{$KEYWORDS.PRIMARY} = ["live music venues", "concert halls", ...]
{$KEYWORDS.LOCATION} = ["Sydney live music", "Sydney concert venues", ...]
{$KEYWORDS.INDUSTRY} = ["entertainment venues", "nightlife", ...]
{$KEYWORDS.COMPETITOR} = ["Opera House", "Metro Theatre", ...]
{$KEYWORDS.NICHE} = ["acoustic venues", "jazz clubs", ...]
```

### Keyword Categories

**Generated keyword sets include 5 categories:**

1. **Primary Keywords** (5-15 terms)
   - Core search terms for the industry
   - Example: "live music venues", "concert halls", "music clubs"

2. **Location Variants** (0-10 terms, if location provided)
   - Geographic + industry combinations
   - Example: "Sydney live music", "Sydney CBD concerts"

3. **Industry Terms** (5-10 terms)
   - Related business categories
   - Example: "entertainment venues", "nightlife", "event spaces"

4. **Competitor Keywords** (0-5 terms)
   - Known competitors or landmarks
   - Example: "Opera House", "Metro Theatre"

5. **Niche Keywords** (5-10 terms)
   - Specialized subcategories
   - Example: "acoustic venues", "jazz clubs", "indie music"

### Workflow Integration

**Example TypeScript workflow:**

```typescript
# memory/workflows/missions/find-music-venues-script.md

# Generate keywords with Gemini AI
(CLOUD GENERATE KEYWORDS|live music venues|--location|Sydney|--export)

# Keywords now available as variables:
# {$KEYWORDS.PRIMARY}, {$KEYWORDS.LOCATION}, etc.

# Use in search workflow
FOR {$keyword} IN {$KEYWORDS.PRIMARY}
  (CLOUD SEARCH|{$keyword})
  WAIT (2)
END FOR

# Save results
(CLOUD EXPORT|JSON|businesses)
```

### Offline Fallback

When Gemini API is unavailable (no API key or network error), the system uses **industry templates**:

**Supported industries:**
- Hospitality (restaurants, cafes, bars)
- Retail (shops, stores, boutiques)
- Services (medical, legal, consultants)
- Entertainment (venues, events, arts)

**Fallback behavior:**
```python
# If Gemini fails, uses template-based generation
keyword_set = generator.generate_keywords(
    industry="live music venues",
    location_context="Sydney"
)
# Returns: KeywordSet with template-generated keywords
# Source: "offline-template"
```

---

## 2. Location Resolution

### Purpose
Convert addresses to:
- **TILE codes** - uDOS spatial grid system (AA000-RL269, layers 100-500)
- **MeshCore positions** - Grid coordinates for mesh networking
- **Coordinates** - Latitude/longitude

### Command Syntax

```bash
CLOUD RESOLVE LOCATION <address> [--layer <100-500>] [--export]
```

**Arguments:**
- `<address>` - Required. Full address or landmark (e.g., "123 George St, Sydney NSW")
- `--layer <100-500>` - Optional. TILE layer (default: 300 city layer)
- `--export` - Optional. Export as TypeScript variables for workflow automation

### Examples

**Basic location resolution:**
```bash
uDOS> CLOUD RESOLVE LOCATION "Opera House, Sydney NSW"
```

Output:
```
✅ Resolved location: Sydney Opera House, Sydney NSW 2000, Australia

📍 Coordinates: -33.856784, 151.215297
🗺️  TILE Code: DN340
🗺️  Full TILE: DN340-300
📐 Layer: 300 (cell size: 93m)

🔌 MeshCore Position:
   Grid X: 432
   Grid Y: 340
   Layer: 300

Confidence: high
```

**Specify layer:**
```bash
uDOS> CLOUD RESOLVE LOCATION "123 George St, Sydney" --layer 400
```

**Export for workflow automation:**
```bash
uDOS> CLOUD RESOLVE LOCATION "Opera House, Sydney" --export
```

Output (uPY variable format):
```upy
# Location: Sydney Opera House
{$LOCATION.ADDRESS} = "Sydney Opera House, Sydney NSW 2000, Australia"
{$LOCATION.LAT} = -33.856784
{$LOCATION.LON} = 151.215297
{$LOCATION.TILE} = "DN340"
{$LOCATION.TILE_FULL} = "DN340-300"
{$LOCATION.LAYER} = 300
{$LOCATION.MESHCORE_X} = 432
{$LOCATION.MESHCORE_Y} = 340
{$LOCATION.MESHCORE_LAYER} = 300
{$LOCATION.CELL_SIZE} = 93
```

### TILE Code System

**Grid Structure:**
- **Columns**: AA-RL (480 columns, 2-letter encoding using A-R alphabet)
- **Rows**: 0-269 (270 rows)
- **Total**: 480 × 270 = 129,600 global grid cells

**Layer System (5 layers):**
```
Layer 100: World layer    ~83km per cell    (global continents)
Layer 200: Region layer   ~2.78km per cell  (cities/towns)
Layer 300: City layer     ~93m per cell     (neighborhoods) ← DEFAULT
Layer 400: District layer ~3m per cell      (buildings)
Layer 500: Block layer    ~10cm per cell    (rooms/objects)
```

**TILE Code Format:**
```
AA000       - Grid position only (column AA, row 0)
AA000-100   - Full TILE with layer (world layer)
DN340-300   - Sydney Opera House (city layer)
JF057-200   - London (region layer)
```

**Column Encoding Algorithm:**
```
18-letter alphabet: A-R (18 letters, no S-Z)
2-letter combinations: AA, AB, AC, ..., RA, RB, ..., RR

Examples:
AA = 0   (A=0, A=0) → 0*18 + 0 = 0
AB = 1   (A=0, B=1) → 0*18 + 1 = 1
BA = 18  (B=1, A=0) → 1*18 + 0 = 18
DN = 63  (D=3, N=13) → 3*18 + 13 = 63
RL = 479 (R=17, L=11) → 17*18 + 11 = 479
```

### MeshCore Integration

**MeshCore Grid Positioning:**
```python
{
    'grid_x': 432,           # Grid column (0-479)
    'grid_y': 340,           # Grid row (0-269)
    'layer': 300,            # Layer (100-500)
    'cell_size_m': 93        # Cell size in meters
}
```

**Usage in mesh networking:**
- Device placement on spatial grid
- Signal propagation calculations
- Network topology visualization
- Coverage area analysis

### Workflow Integration

**Example TypeScript workflow:**

```typescript
# memory/workflows/missions/map-sydney-venues-script.md

# Resolve business address
(CLOUD RESOLVE LOCATION|Opera House, Sydney NSW|--layer|300|--export)

# Location data now available:
# {$LOCATION.TILE}, {$LOCATION.MESHCORE_X}, etc.

# Store in business record
(CLOUD UPDATE|biz-OP3R4H0U53|--tile|{$LOCATION.TILE})
(CLOUD UPDATE|biz-OP3R4H0U53|--grid|{$LOCATION.MESHCORE_X},{$LOCATION.MESHCORE_Y})

# Add to map layer
(MAP ADD|{$LOCATION.TILE}|label|Sydney Opera House)
```

---

## 3. Combined Workflow Example

**Full business discovery workflow with keywords + locations:**

```upy
# memory/workflows/missions/discover-sydney-music-script.md

# PHASE 1: Generate search keywords
(PRINT|Generating keywords for Sydney live music venues...)
(CLOUD GENERATE KEYWORDS|live music venues|--location|Sydney|--export)

# PHASE 2: Search using keywords
(PRINT|Searching Google Business Profiles...)
FOR {$keyword} IN {$KEYWORDS.PRIMARY}
  (CLOUD SEARCH|{$keyword})
  WAIT (2)
END FOR

# PHASE 3: Resolve locations for discovered businesses
(CLOUD LIST|businesses|--format|ids) → {$business_ids}

FOR {$bid} IN {$business_ids}
  # Get business address
  (CLOUD GET|{$bid}|--field|address) → {$address}
  
  # Resolve to TILE code
  (CLOUD RESOLVE LOCATION|{$address}|--layer|300|--export)
  
  # Update business record
  (CLOUD UPDATE|{$bid}|--tile|{$LOCATION.TILE})
  (CLOUD UPDATE|{$bid}|--meshcore|{$LOCATION.MESHCORE_X},{$LOCATION.MESHCORE_Y})
  
  # Add to map
  (MAP ADD|{$LOCATION.TILE}|business|{$bid})
END FOR

# PHASE 4: Export results
(CLOUD EXPORT|JSON|businesses|memory/workflows/results/sydney-music-venues.json)
(PRINT|✅ Discovered and mapped {$business_ids.length} venues)
```

---

## 4. API Configuration

### Required API Keys

Add to `.env` file:

```bash
# Gemini AI (keyword generation)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Geocoding (location resolution)
GOOGLE_GEOCODING_API_KEY=your_geocoding_api_key_here
```

### Getting API Keys

**Gemini API:**
1. Visit https://makersuite.google.com/app/apikey
2. Create new API key
3. Add to `.env` as `GEMINI_API_KEY`

**Google Geocoding API:**
1. Visit https://console.cloud.google.com/apis/
2. Enable "Geocoding API"
3. Create credentials → API key
4. Add to `.env` as `GOOGLE_GEOCODING_API_KEY`

### Graceful Degradation

Both systems handle missing API keys:

**Keyword Generator:**
- Gemini unavailable → Uses industry templates (offline fallback)
- No performance impact, template-based keywords still useful

**Location Resolver:**
- Geocoding unavailable → Cannot resolve addresses
- Returns error message, workflow can handle failure

---

## 5. Development API

### Python API

```python
from extensions.cloud.bizintel import KeywordGenerator, LocationResolver

# Keyword generation
generator = KeywordGenerator()
keywords = generator.generate_keywords(
    industry="live music venues",
    location_context="Sydney",
    business_type="jazz club"
)

print(keywords.primary_keywords)
# ['live music venues', 'concert halls', 'music clubs', ...]

print(keywords.location_variants)
# ['Sydney live music', 'Sydney concert venues', ...]

# Export for TypeScript scripts
script_code = generator.export_for_script(keywords)
# Returns: "{$KEYWORDS.PRIMARY} = [...]\n..."

# Location resolution
resolver = LocationResolver()
location = resolver.resolve_address(
    "Opera House, Sydney NSW",
    preferred_layer=300
)

print(location.tile_code)        # "DN340"
print(location.tile_code_full)   # "DN340-300"
print(location.meshcore_position)
# {'grid_x': 432, 'grid_y': 340, 'layer': 300, 'cell_size_m': 93}

# Export for uPY
upy_code = resolver.format_for_upy(location)
# Returns: "{$LOCATION.TILE} = 'DN340'\n..."
```

### KeywordSet Dataclass

```python
@dataclass
class KeywordSet:
    primary_keywords: List[str]      # 5-15 core terms
    location_variants: List[str]     # 0-10 geo variants
    industry_terms: List[str]        # 5-10 related categories
    competitor_keywords: List[str]   # 0-5 competitors
    niche_keywords: List[str]        # 5-10 specialized terms
    context: Dict[str, Any]          # Metadata
```

### LocationData Dataclass

```python
@dataclass
class LocationData:
    address: str                     # Formatted address
    lat: float                       # Latitude
    lon: float                       # Longitude
    tile_code: str                   # Grid position (e.g., "DN340")
    tile_code_full: str              # With layer (e.g., "DN340-300")
    layer: int                       # 100-500
    meshcore_position: Dict[str, Any] # MeshCore grid data
    confidence: str                  # "high", "medium", "low"
```

---

## 6. Testing

### Test Keyword Generation

```bash
# With Gemini API
uDOS> CLOUD GENERATE KEYWORDS "live music venues" --location "Sydney"

# Without Gemini (offline fallback)
uDOS> CLOUD GENERATE KEYWORDS "cafes" --location "Brooklyn"

# Export for workflow
uDOS> CLOUD GENERATE KEYWORDS "gyms" --export
```

### Test Location Resolution

```bash
# Known landmark
uDOS> CLOUD RESOLVE LOCATION "Eiffel Tower, Paris"

# Street address
uDOS> CLOUD RESOLVE LOCATION "123 George St, Sydney NSW"

# Different layers
uDOS> CLOUD RESOLVE LOCATION "Opera House, Sydney" --layer 200
uDOS> CLOUD RESOLVE LOCATION "Opera House, Sydney" --layer 400

# Export for workflow
uDOS> CLOUD RESOLVE LOCATION "Opera House, Sydney" --export
```

### Test Workflow Integration

Create `memory/workflows/test-automation-script.md`:

```upy
# Test keyword generation
(CLOUD GENERATE KEYWORDS|cafes|--location|Sydney|--export)
(PRINT|Primary keywords: {$KEYWORDS.PRIMARY})

# Test location resolution
(CLOUD RESOLVE LOCATION|Opera House, Sydney|--export)
(PRINT|TILE code: {$LOCATION.TILE})
(PRINT|MeshCore position: {$LOCATION.MESHCORE_X},{$LOCATION.MESHCORE_Y})
```

Run: `./start_udos.sh memory/workflows/test-automation-script.md`

---

## 7. Troubleshooting

### Keyword Generation Issues

**Problem:** "Error generating keywords: 403 API key not valid"
**Solution:** Check `GEMINI_API_KEY` in `.env`, verify key is active at https://makersuite.google.com/

**Problem:** Keywords are generic/template-based
**Solution:** System is using offline fallback. Add Gemini API key for AI-powered keywords.

### Location Resolution Issues

**Problem:** "Error resolving location: Invalid API key"
**Solution:** Check `GOOGLE_GEOCODING_API_KEY` in `.env`, enable Geocoding API in Google Cloud Console

**Problem:** "Could not resolve address: ..."
**Solution:** 
- Check address format (include city/state/country)
- Try known landmark instead
- Verify geocoding API quota hasn't been exceeded

### TILE Code Issues

**Problem:** TILE code doesn't match expected location
**Solution:** 
- Verify layer is appropriate (100=world, 300=city, 500=block)
- Check lat/lon coordinates are correct
- TILE system uses grid approximation, not exact positioning

---

## 8. References

- **BIZINTEL System**: `extensions/cloud/bizintel/README.md`
- **uDOS Mapping**: `wiki/Mapping-System.md`
- **MeshCore Integration**: `extensions/play/meshcore_integration.py`
- **Workflow Syntax**: `wiki/Function-Programming-Guide.md`
- **TILE Code System**: uDOS v1.1.12+ grid architecture
