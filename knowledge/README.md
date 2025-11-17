# uDOS Knowledge Library

**Welcome to The People's Knowledge Commons**

A comprehensive collection of practical guides and information for self-sufficiency, survival, and sustainable living.

## Overview

This knowledge library is designed to be accessible both online and offline, with a focus on practical, actionable information. The structure uses a **flat folder layout** for easy navigation and fast searching with the GUIDE and DIAGRAM commands.

All measurements use **metric units** (ml, g, kg, cm, m, km) and content is relevant to **Australian conditions** while remaining generally applicable worldwide.

---

## 📚 Knowledge Structure (8 Categories)

### 1. [System](system/README.md) ⚙️
**uDOS technical documentation and configuration files.**

Contents: Commands reference, concepts, FAQ, datasets, themes, templates, JSON configs

**Key files**: `commands.json`, `uDOS-CONCEPTS.md`, `FAQ.md`

---

### 2. [Reference](reference/README.md) 📖
**Maps, resources, and tool references.**

Contents: Charts, tables, reference data, tool specifications

**Use for**: Quick lookups, specifications, reference tables

---

### 3. [Survival](survival/README.md) 🆘
**Essential skills and information for meeting basic needs and handling emergencies.**

Contents: 28 guides covering shelters, fire, navigation, first aid, emergency response

**Start here if**: You need practical emergency knowledge or basic survival skills

**Australian-specific**: Bushfire survival, snakebite treatment, water sources, bush navigation, bush tucker

---

### 4. [Medical](medical/README.md) 🏥
**First aid and medical treatment information.**

Contents: 4 guides covering CPR, wound care, emergency treatment

**Start here if**: You need first aid procedures or medical emergency guidance

**Note**: For emergencies call 000 (Australia). These guides supplement professional care.

---

### 5. [Food](food/README.md) 🍽️
**Foraging, preservation, recipes, and nutrition.**

Contents: 5 guides covering wild edibles, preservation methods, bushcraft recipes

**Start here if**: You want to learn foraging, food preservation, or wilderness cooking

**All recipes**: Metric measurements only (g, ml, kg)

---

### 6. [Water](water/README.md) 💧
**Purification, sources, and harvesting.**

Contents: 6 guides covering purification methods, rainwater harvesting, water sources

**Start here if**: You need to find, purify, or store water

**Australian context**: Seasonal water availability, climate-appropriate methods

---

### 7. [Making](making/README.md) 🔨
**Building, energy, and environment.**

Contents: 2 guides covering construction, solar power, composting

**Start here if**: You want to build shelters, generate power, or understand environmental systems

---

### 8. [Tech](tech/README.md) 💻
**Programming, productivity, and communication.**

Contents: 5 guides covering technical skills, workflows, digital tools

**Start here if**: You want to learn programming or improve digital productivity

---

## 🚀 Accessing Knowledge in uDOS

### Using the GUIDE Command

Step-through interactive tutorials with progress tracking:

```bash
# List available guides in a category
🔮 > GUIDE LIST survival

# Start a guide (resumes from last position)
🔮 > GUIDE START water-purification

# Navigate steps
🔮 > GUIDE NEXT    # Next step
🔮 > GUIDE PREV    # Previous step

# Track progress
🔮 > GUIDE COMPLETE 3    # Mark step 3 done
🔮 > GUIDE PROGRESS      # Show checklist
```

### Using the DIAGRAM Command

Browse ASCII art diagrams and technical drawings:

```bash
# List diagrams by type
🔮 > DIAGRAM LIST knot
🔮 > DIAGRAM LIST shelter

# Search for diagrams
🔮 > DIAGRAM SEARCH "water filter"

# Show a diagram
🔮 > DIAGRAM SHOW bowline-knot

# Export to file
🔮 > DIAGRAM EXPORT bowline-knot output/knots.txt
```

### Search Across Library

```bash
# Search for keywords
🔮 > FIND "bushfire" knowledge/
🔮 > FIND "first aid" knowledge/medical/

# Or use grep from terminal
grep -r "water purification" knowledge/
```

---

## 📝 Content Guidelines

### Measurements
- **Always use metric**: ml, g, kg, cm, m, km
- **Never use imperial**: oz, cups, inches, feet, miles

### Regional Context
- Content is relevant to **Australian conditions** (climate, seasons, wildlife)
- Guidance is **generally applicable** worldwide
- Avoid excessive location stamps (TZONE, Grid coordinates)
- Focus on techniques and principles, not specific locations

### Digital-First
- No CTAs to print documents
- Encourage searching and bookmarking within uDOS
- Use GUIDE and DIAGRAM commands for step-by-step access

---

## 📂 Directory Structure

```
knowledge/
├── system/          # uDOS technical docs, commands, configs (23 files)
├── reference/       # Maps, charts, reference data (1 file)
├── survival/        # Emergency skills, first response (28 files)
├── medical/         # First aid, medical treatment (4 files)
├── food/            # Foraging, recipes, preservation (5 files)
├── water/           # Purification, sources, harvesting (6 files)
├── making/          # Building, energy, environment (2 files)
├── tech/            # Programming, productivity, communication (5 files)
├── personal/        # User notes (preserved)
├── well-being/      # Health, mindfulness (preserved)
├── community/       # Collaboration, mutual aid (preserved)
└── skills/          # Art, writing, music (preserved)
```

**Total**: 74+ guides organized in 8 flat categories

---
```

### Add Your Own Knowledge

Each category has a README explaining:
- What belongs in that category
- Content guidelines (what to include/exclude)
- Example documents
- How to contribute

**See**: [Knowledge Architecture](../wiki/Knowledge-Architecture.md) for complete organization system

---

## 🎯 Content Philosophy

### ✅ What We Include

- **Practical**, actionable knowledge
- **Evidence-based** information
- **Timeless** principles that remain relevant
- **Accessible** to beginners
- **Well-organized** for easy discovery
- **Metric measurements** only (ml, g, kg, cm, m, km)
- **Australian conditions** considered but broadly applicable

### ❌ What We Exclude

- Political ideology or partisanship
- Corporate marketing or sponsored content
- Pseudoscience and unfounded claims
- Divisive or exclusionary content
- Temporary trends without lasting value
- Proprietary or paywalled information
- Imperial measurements (oz, cups, inches, feet)
- Excessive location stamps or grid coordinates
- CTAs to print documents

---

## 🤝 Contributing

### Adding New Knowledge

1. **Choose the right category** - survival, medical, food, water, making, tech, reference
2. **Follow content guidelines** - Use metric, keep general, Australian-relevant
3. **Use Markdown format** - Plain text, future-proof, works with GUIDE command
4. **Include sources** - Cite where information came from
5. **Test for clarity** - Can someone without expertise follow it?
6. **Keep it flat** - No subdirectories within main categories

### Adding Diagrams

1. **Use ASCII art** - Works in any terminal
2. **Wrap in code blocks** - ````ascii ... ````
3. **Add context** - Paragraph before diagram explaining what it shows
4. **Test rendering** - Use `DIAGRAM SHOW` to verify

### Updating Guides

When editing existing guides:
- Remove excessive TZONE/location stamps
- Convert measurements to metric
- Remove print CTAs
- Keep content general with Australian context
- Test with `GUIDE START` command

---

## 📚 Related Documentation

- **[KNOWLEDGE-SYSTEM.md](KNOWLEDGE-SYSTEM.md)** - Technical overview
- **[Knowledge Architecture Wiki](../wiki/Knowledge-Architecture.md)** - Organization system
- **[GUIDE Command](system/commands.json)** - Interactive guide viewer
- **[DIAGRAM Command](system/commands.json)** - ASCII art browser
- **[Content Curation](../wiki/Content-Curation.md)** - Quality guidelines

---

**Last Updated**: v1.0.21 (November 2024)
**Structure**: 8 flat categories, 74+ guides
**Focus**: Practical, metric, Australian-relevant, digitally accessible

### Suggesting Improvements

- Open an issue on GitHub
- Discuss in community forums
- Submit a pull request

**See**: [Content Curation](../wiki/Content-Curation.md) *(coming soon)* for detailed guidelines

---

## 🌍 The Vision

**A knowledge commons for The People's Operating System.**

Imagine a world where essential knowledge is:
- **Free** and accessible to all
- **Well-organized** and easy to find
- **Practical** and immediately useful
- **Community-curated** for quality
- **Future-proof** in simple text format
- **Offline-first** (no internet required)

This is that world. Welcome to the knowledge commons.

---

## 📚 Related Documentation

- **[Knowledge Architecture](../wiki/Knowledge-Architecture.md)** - Complete organization system
- **[Philosophy](../wiki/Philosophy.md)** - Why uDOS exists
- **[Content Curation](../wiki/Content-Curation.md)** - How to curate knowledge *(coming soon)*
- **[Getting Started](../wiki/Getting-Started.md)** - New user guide

---

**Last Updated**: November 14, 2025
**Structure**: v1.0.15 - Human-Centric Documentation & Philosophy

**Remember**: Knowledge shared is knowledge multiplied. Contribute what you know. Learn what others share.
