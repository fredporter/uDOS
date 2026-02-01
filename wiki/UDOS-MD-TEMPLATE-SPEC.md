# uDOS.md Template Specification (v1.0.0.51)

**Last Updated:** 2026-01-24
**Status:** Active Standard
**Author:** uDOS Engineering

The **uDOS.md** format extends standard Markdown with embedded code blocks that can be invoked via **shortcodes**. This enables rich, interactive documents that combine:

1. **Narrative content** (regular Markdown)
2. **Slideshow presentation** (via `---` separators)
3. **Executable code** (uPY functions, scripts, JSON data)
4. **Variable interpolation** (story/form $variables)

---

## Document Structure

````
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
````

---

## YAML Frontmatter

Standard YAML frontmatter with uDOS-specific fields:

```yaml
---
title: "City Guide: Sydney"
template: guide # guide|story|form|dashboard|presentation
version: "1.0.0"
author: "Fred Porter"
created: "2026-01-07"
updated: "2026-01-24"

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
  coordinate: "L300-OC-AB34-CD15"
  tags: ["city", "oceania", "coastal"]

# Slideshow settings
slideshow:
  auto_advance: false
  transition: "fade"
  duration: 5000
---
```

---

## Shortcode Syntax

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

## Code Block Definitions

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

## Variable Interpolation

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

## Slideshow Mode

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

## Template Types

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

## File Extensions

| Extension   | Purpose                           |
| ----------- | --------------------------------- |
| `.md`       | Standard Markdown (no shortcodes) |
| `.udos.md`  | uDOS.md with shortcodes           |
| `.md`       | TypeScript script (with -script/-template suffix) |
| `.guide.md` | Knowledge guide (auto-template)   |
| `.story.md` | Interactive story                 |
| `.form.md`  | Form template                     |

---

## Related Documentation

- [UDOS-MD-FORMAT.md](UDOS-MD-FORMAT.md) — Core document format
- [KNOWLEDGE-LINKING-SYSTEM.md](KNOWLEDGE-LINKING-SYSTEM.md) — Document relationships
- [LAYER-ARCHITECTURE.md](LAYER-ARCHITECTURE.md) — Spatial coordinate system
- [../../docs/development-streams.md](../../docs/development-streams.md) — Implementation roadmap

---

**Status:** Active Architecture Standard
**Repository:** https://github.com/fredporter/uDOS
