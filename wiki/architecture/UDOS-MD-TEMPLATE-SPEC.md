# uDOS.md Template Specification v1.0.0

**Date:** 2026-01-07  
**Author:** uDOS System  
**Status:** Draft

---

## Overview

The **uDOS.md** format extends standard Markdown with embedded code blocks that can be invoked via **shortcodes**. This enables rich, interactive documents that combine:

1. **Narrative content** (regular Markdown)
2. **Slideshow presentation** (via `---` separators)
3. **Executable code** (uPY functions, scripts, JSON data)
4. **Variable interpolation** (story/form $variables)

## Document Structure

```
┌──────────────────────────────────────────────────────────────────┐
│                     UDOS.MD FILE STRUCTURE                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. YAML FRONTMATTER                                             │
│     ---                                                           │
│     title: "Document Title"                                       │
│     template: "guide|story|form|dashboard"                       │
│     variables:                                                    │
│       $player_name: "Hero"                                       │
│       $location: "Sydney"                                         │
│     ---                                                           │
│                                                                   │
│  2. SHORTCODE SECTION (top of document)                          │
│     [SPLASH]                 → Calls [@SPLASH] code block below  │
│     [FORM:player_setup]      → Interactive form                  │
│                                                                   │
│  3. NARRATIVE CONTENT (body)                                     │
│     # Welcome to $location                                       │
│                                                                   │
│     Regular Markdown text with $variable interpolation.          │
│                                                                   │
│     ---                                                           │
│     ## Slide 2                                                   │
│     Next slide content...                                        │
│                                                                   │
│  4. CODE BLOCKS SECTION (bottom of document)                     │
│     ```upy @SPLASH                                               │
│     # Splash screen code                                         │
│     PRINT(':wave: Welcome, $player_name!')                       │
│     DELAY(2000)                                                  │
│     ```                                                           │
│                                                                   │
│     ```json @config                                              │
│     { "theme": "dark", "animation": true }                       │
│     ```                                                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 1. YAML Frontmatter

Standard YAML frontmatter with uDOS-specific fields:

```yaml
---
title: "City Guide: Sydney"
template: guide                    # guide|story|form|dashboard|presentation
version: "1.0.0"
author: "Fred Porter"
created: "2026-01-07"
updated: "2026-01-07"

# Template type
type: location_guide

# Variables available in document
variables:
  $city_name: "Sydney"
  $country: "Australia"
  $emergency: "000"
  $currency: "AUD"

# Shortcode definitions (optional - auto-detected from code blocks)
shortcodes:
  - SPLASH
  - WEATHER_CHECK
  - EMERGENCY_CARD

# Knowledge links
knowledge:
  guide_path: "/knowledge/places/cities/sydney.md"
  coordinate: "EARTH-OC-L100-AB34-CD15"
  tags: ["city", "oceania", "coastal"]
  
# Slideshow settings
slideshow:
  auto_advance: false
  transition: "fade"
  duration: 5000
---
```

---

## 2. Shortcode Syntax

Shortcodes call named code blocks defined at the bottom of the document.

### Basic Shortcode

```markdown
[SPLASH]
```

Calls the `@SPLASH` code block.

### Shortcode with Type

```markdown
[FORM:player_setup]
```

Calls the `@player_setup` code block and renders it as a form.

### Shortcode with Parameters

```markdown
[WEATHER:$city_name:metric]
```

Passes `$city_name` and `"metric"` to the `@WEATHER` code block.

### Inline Shortcode

```markdown
The temperature is [TEMP:$city_name].
```

Returns value inline (no block rendering).

### Conditional Shortcode

```markdown
[IF:$has_emergency:EMERGENCY_CARD]
```

Only renders if `$has_emergency` is truthy.

---

## 3. Code Block Definitions

Code blocks at the bottom of the document define shortcode implementations.

### uPY Code Block

````markdown
```upy @SPLASH
# Splash screen animation
PRINT(':globe: Loading $city_name guide...')
DELAY(1500)
PRINT(':check: Ready!')
```
````

### JSON Data Block

````markdown
```json @config
{
  "display_mode": "slideshow",
  "theme": "city-guide",
  "fonts": {
    "heading": "system-ui",
    "body": "Georgia"
  }
}
```
````

### uPY Function Block

````markdown
```upy @WEATHER($location, $units)
# Fetch weather for location
$weather = API_GET('weather/$location?units=$units')
RETURN $weather.temp + '°' + $weather.unit
```
````

### Form Definition Block

````markdown
```json @player_setup
{
  "type": "form",
  "title": "Player Setup",
  "fields": [
    {
      "name": "$player_name",
      "type": "text",
      "label": "Your Name",
      "required": true
    },
    {
      "name": "$difficulty",
      "type": "choice",
      "label": "Difficulty",
      "options": ["Easy", "Normal", "Hard"],
      "default": "Normal"
    }
  ],
  "submit_action": "@START_GAME"
}
```
````

---

## 4. Variable Interpolation

### Document Variables

```markdown
Welcome to $city_name, $country!
```

Renders as: "Welcome to Sydney, Australia!"

### System Variables

```markdown
Current location: $TILE.CELL
User: $USER.NAME
```

### Computed Variables

In code blocks:

```upy
$distance = CALC_DISTANCE($TILE.CELL, 'AB34')
PRINT('Distance: $distance km')
```

---

## 5. Slideshow Mode

Use `---` to separate slides:

```markdown
---
# Welcome to Sydney

Your adventure begins here.

---

## Getting Around

Sydney has excellent public transport.

[TRANSPORT_MAP]

---

## Emergency Numbers

[EMERGENCY_CARD]

---
```

Each `---` creates a new slide in presentation mode.

---

## 6. Template Types

### Guide Template

For knowledge articles and location guides:

```yaml
template: guide
```

Features:
- Table of contents auto-generated from headings
- Knowledge cross-references
- Print-friendly layout

### Story Template

For interactive narratives:

```yaml
template: story
```

Features:
- Slideshow navigation
- Character dialogue
- Branching choices

### Form Template

For data collection:

```yaml
template: form
```

Features:
- Form fields rendered from JSON
- Validation
- Submit actions

### Dashboard Template

For real-time displays:

```yaml
template: dashboard
```

Features:
- Auto-refresh shortcodes
- Live data binding
- Widget layout

---

## 7. Integration with markdowndb

The uDOS.md format is designed to work with [markdowndb](https://github.com/flowershow/markdowndb) for:

### SQLite Indexing

```javascript
// Index all .md files with frontmatter extraction
npx mddb ./knowledge --output knowledge.db
```

### JSON Export

```javascript
// Export single file to JSON
npx mddb ./knowledge/places/cities/sydney.md
// Returns parsed frontmatter + content structure
```

### Computed Fields

```javascript
// Add computed fields during indexing
const addCoordinate = (fileInfo, ast) => {
  if (fileInfo.metadata.knowledge?.coordinate) {
    fileInfo.tile_cell = fileInfo.metadata.knowledge.coordinate;
  }
};

client.indexFolder('knowledge', { computedFields: [addCoordinate] });
```

### Query Examples

```sql
-- Find all city guides
SELECT * FROM files WHERE metadata->>'template' = 'guide' 
  AND metadata->>'type' = 'location_guide';

-- Find guides by coordinate region
SELECT * FROM files WHERE metadata->>'knowledge'->>'coordinate' LIKE 'EARTH-OC-%';
```

---

## 8. Example: City Guide Template

```markdown
---
title: "City Guide: Sydney"
template: guide
type: location_guide
variables:
  $city: "Sydney"
  $country: "Australia"
  $emergency: "000"
  $timezone: "Australia/Sydney"
knowledge:
  guide_path: "/knowledge/places/cities/sydney.md"
  coordinate: "EARTH-OC-L100-AB34-CD15"
  tags: ["city", "oceania", "coastal", "subtropical"]
---

[SPLASH]

# Welcome to $city

[WEATHER:$city:metric]

$city is a vibrant coastal city in $country, known for its 
iconic harbour, beaches, and cultural diversity.

---

## Quick Reference

[QUICKREF_CARD]

| Info | Value |
|------|-------|
| Emergency | $emergency |
| Timezone | $timezone |
| Currency | AUD |

---

## Getting Around

Sydney has an integrated transport system called Opal.

[TRANSPORT_INFO]

---

## Emergency Information

[IF:$show_emergency:EMERGENCY_CARD]

---

<!-- CODE BLOCKS SECTION -->

```upy @SPLASH
# Welcome animation
PRINT(':wave: Welcome to the $city Guide!')
PRINT(':globe: Coordinate: EARTH-OC-L100-AB34-CD15')
DELAY(2000)
```

```upy @WEATHER($location, $units)
# This would call weather API in production
RETURN ':sunny: 24°C in $location'
```

```json @QUICKREF_CARD
{
  "type": "card",
  "style": "info",
  "content": {
    "title": "Quick Facts",
    "items": [
      { "icon": ":phone:", "label": "Emergency", "value": "$emergency" },
      { "icon": ":clock:", "label": "Timezone", "value": "$timezone" },
      { "icon": ":money:", "label": "Currency", "value": "AUD ($)" }
    ]
  }
}
```

```upy @TRANSPORT_INFO
# Transport summary
PRINT(':train: Train: Sydney Trains (suburban)')
PRINT(':bus: Bus: 300+ routes')
PRINT(':ship: Ferry: 30+ routes across harbour')
PRINT(':metro: Metro: Northwest to CBD')
```

```json @EMERGENCY_CARD
{
  "type": "card",
  "style": "emergency",
  "content": {
    "title": "Emergency Numbers",
    "items": [
      { "label": "All Emergencies", "value": "000", "primary": true },
      { "label": "Police Non-Emergency", "value": "131 444" },
      { "label": "Health Advice", "value": "1800 022 222" }
    ]
  }
}
```
```

---

## 9. Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    UDOS.MD PROCESSING                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. PARSE                                                        │
│     └─ Extract YAML frontmatter                                 │
│     └─ Identify shortcodes in content                           │
│     └─ Extract code blocks with @names                          │
│                                                                  │
│  2. INDEX (markdowndb)                                          │
│     └─ Store frontmatter in SQLite                              │
│     └─ Compute derived fields (coordinates, tags)               │
│     └─ Build search index                                       │
│                                                                  │
│  3. RENDER                                                       │
│     └─ Interpolate $variables                                   │
│     └─ Execute shortcode code blocks                            │
│     └─ Apply template styling                                   │
│                                                                  │
│  4. DISPLAY                                                      │
│     └─ TUI: ANSI-formatted output                               │
│     └─ Tauri: HTML/Svelte rendering                             │
│     └─ Slideshow: Slide-by-slide navigation                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. File Extensions

| Extension | Purpose |
|-----------|---------|
| `.md` | Standard Markdown (no shortcodes) |
| `.udos.md` | uDOS.md with shortcodes |
| `.upy` | Pure uPY script (no Markdown) |
| `.guide.md` | Knowledge guide (auto-template) |
| `.story.md` | Interactive story |
| `.form.md` | Form template |

---

## Related

- [uPY Language Reference](../wiki/uPY-Language-Reference.md)
- [Geography Knowledge Spec](../../knowledge/GEOGRAPHY-KNOWLEDGE-SPEC.md)
- [markdowndb](../../library/markdowndb/README.md)
- [Typo Editor](../../library/typo/README.md)

---

*Version: 1.0.0 | Last Updated: 2026-01-07*
