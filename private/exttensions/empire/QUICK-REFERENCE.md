# BIZINTEL Quick Reference - Workflow Automation

**Version:** v1.2.21+  
**Quick Start Guide**

---

## Setup (One-time)

Add API keys to `.env`:

```bash
# Keyword Generation (AI-powered)
GEMINI_API_KEY=your_gemini_api_key_here

# Location Resolution
GOOGLE_GEOCODING_API_KEY=your_geocoding_api_key_here
```

Get keys:
- **Gemini:** https://makersuite.google.com/app/apikey (1,500 free/day)
- **Geocoding:** https://console.cloud.google.com/apis/ (28,500 free/month)

---

## Quick Commands

### Generate Keywords

```bash
# Basic (human-readable output)
CLOUD GENERATE KEYWORDS "live music venues"

# With location context
CLOUD GENERATE KEYWORDS "live music venues" --location "Sydney"

# Export for workflows (uPY variables)
CLOUD GENERATE KEYWORDS "live music venues" --location "Sydney" --upy
```

**Output (--upy):**
```upy
{$KEYWORDS.PRIMARY} = ["live music venues", "concert halls", ...]
{$KEYWORDS.LOCATION} = ["Sydney live music", "Sydney venues", ...]
{$KEYWORDS.INDUSTRY} = ["entertainment", "nightlife", ...]
```

---

### Resolve Location

```bash
# Basic (human-readable output)
CLOUD RESOLVE LOCATION "Opera House, Sydney NSW"

# Specify layer (100-500)
CLOUD RESOLVE LOCATION "Opera House, Sydney" --layer 300

# Export for workflows (uPY variables)
CLOUD RESOLVE LOCATION "Opera House, Sydney" --upy
```

**Output (--upy):**
```upy
{$LOCATION.TILE} = "DN340"              # Grid position
{$LOCATION.TILE_FULL} = "DN340-300"     # With layer
{$LOCATION.MESHCORE_X} = 432            # MeshCore grid X
{$LOCATION.MESHCORE_Y} = 340            # MeshCore grid Y
{$LOCATION.LAT} = -33.856784            # Latitude
{$LOCATION.LON} = 151.215297            # Longitude
```

---

## Workflow Examples

### 1. Search with AI Keywords

```upy
# Generate keywords
(CLOUD GENERATE KEYWORDS|cafes|--location|Brooklyn|--upy)

# Search using keywords
FOR {$keyword} IN {$KEYWORDS.PRIMARY}
  (CLOUD SEARCH|{$keyword})
  WAIT (2)
END FOR
```

### 2. Map Business Locations

```upy
# Get business list
(CLOUD LIST|businesses|--format|ids) → {$business_ids}

# Resolve and map each location
FOR {$bid} IN {$business_ids}
  (CLOUD GET|{$bid}|--field|address) → {$address}
  (CLOUD RESOLVE LOCATION|{$address}|--upy)
  (CLOUD UPDATE|{$bid}|--tile|{$LOCATION.TILE})
  (MAP ADD|{$LOCATION.TILE}|business|{$bid})
END FOR
```

### 3. Full Discovery Pipeline

```upy
# 1. Generate keywords
(CLOUD GENERATE KEYWORDS|live music venues|--location|Sydney|--upy)

# 2. Search
FOR {$keyword} IN {$KEYWORDS.PRIMARY}
  (CLOUD SEARCH|{$keyword})
END FOR

# 3. Map locations
(CLOUD LIST|businesses|--format|ids) → {$business_ids}
FOR {$bid} IN {$business_ids}
  (CLOUD GET|{$bid}|--field|address) → {$address}
  (CLOUD RESOLVE LOCATION|{$address}|--upy)
  (CLOUD UPDATE|{$bid}|--tile|{$LOCATION.TILE})
END FOR

# 4. Export results
(CLOUD EXPORT|JSON|businesses)
```

---

## TILE Code System

**Format:** `AA000-300` (column + row + layer)

**Grid:**
- Columns: AA-RL (480 columns, A-R alphabet)
- Rows: 0-269 (270 rows)
- Total: 129,600 global cells

**Layers:**
```
100 = World    (~83km cells)   - Continents
200 = Region   (~2.78km cells) - Cities
300 = City     (~93m cells)    - Neighborhoods ← DEFAULT
400 = District (~3m cells)     - Buildings
500 = Block    (~10cm cells)   - Rooms
```

**Examples:**
```
AA000-100   = Northwest corner, world layer
DN340-300   = Sydney Opera House, city layer
JF057-200   = London, region layer
```

---

## Keyword Categories

Generated keywords include 5 categories:

1. **PRIMARY** (5-15 terms)
   - Core search terms
   - Example: "live music venues", "concert halls"

2. **LOCATION** (0-10 terms)
   - Geographic variants
   - Example: "Sydney live music", "Sydney concerts"

3. **INDUSTRY** (5-10 terms)
   - Related categories
   - Example: "entertainment venues", "nightlife"

4. **COMPETITOR** (0-5 terms)
   - Known competitors
   - Example: "Opera House", "Metro Theatre"

5. **NICHE** (5-10 terms)
   - Specialized subcategories
   - Example: "acoustic venues", "jazz clubs"

---

## Common Use Cases

### Business Discovery
```bash
CLOUD GENERATE KEYWORDS "gyms" --location "Manhattan" --upy
```

### Address Validation
```bash
CLOUD RESOLVE LOCATION "123 Main St, City, State" --upy
```

### Mapping
```bash
CLOUD RESOLVE LOCATION "Business Address" --layer 300 --upy
# Use {$LOCATION.TILE} in MAP ADD command
```

### Competitor Research
```bash
CLOUD GENERATE KEYWORDS "coffee shops" --type "specialty coffee" --upy
# Check {$KEYWORDS.COMPETITOR} for known brands
```

---

## Troubleshooting

**Keywords are generic:**
- Check if GEMINI_API_KEY is set in .env
- System uses offline templates if API unavailable
- Verify Gemini API key is active

**Location resolution fails:**
- Check if GOOGLE_GEOCODING_API_KEY is set
- Verify address includes city/state/country
- Try known landmark instead of street address
- Check API quota hasn't been exceeded

**TILE code seems wrong:**
- Verify layer is appropriate (300 for most use cases)
- Check lat/lon coordinates are correct
- TILE system uses grid approximation

**Rate limit errors:**
- Gemini: 1,500 requests/day (free tier)
- Geocoding: 28,500 requests/month (free tier)
- Add delays between requests in workflows

---

## Test Script

Run the test workflow:

```bash
./start_udos.sh memory/workflows/test-workflow-automation.upy
```

Tests:
- ✓ Keyword generation with AI
- ✓ Location resolution with TILE codes
- ✓ Combined workflow
- ✓ Offline fallback

---

## Full Documentation

- **Complete Guide:** `extensions/cloud/bizintel/WORKFLOW-AUTOMATION.md`
- **BIZINTEL README:** `extensions/cloud/bizintel/README.md`
- **Mapping System:** `wiki/Mapping-System.md`
- **uPY Syntax:** `wiki/Function-Programming-Guide.md`

---

**Questions?** Check the full documentation or run `CLOUD HELP`
