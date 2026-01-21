# uDOS Knowledge Bank

**The People's Knowledge Commons - v1.4.0 Comprehensive Survival Library**

A comprehensive offline collection of 166+ survival guides and technical diagrams for self-sufficiency, emergency preparedness, and sustainable living. Powered by OK Assist integration and Nano Banana diagram generation for continuous expansion.

**New in v1.1.7**: Full PNG→SVG diagram generation via `GENERATE SVG` command - create Technical-Kinetic diagrams for any survival topic.

---

## 📊 Current Status (v1.4.0 Phase 1)

```
Total Guides:     166 / 1,000 (16.6%)
Total Diagrams:    80 /   500 (16.0%)
OK Assist Gen:     86 guides (51.8%)
Categories:         8 core areas
Avg Length:     1,500 words/guide
Last Updated:  2025-11-24
```

**Week 2 Progress**: On track for 273 guides by Dec 1

---

## 🗂️ Knowledge Categories

### 1. 💧 [Water](water/README.md) - Procurement & Purification
**26 / 150 guides (17.3%)**

Finding, purifying, and storing water in all environments.

**Topics**: Water sources, purification methods, filtration systems, desalination, quality testing, storage, conservation

**Start with**: `finding_water_sources.md`, `water_purification_methods.md`

---

### 2. 🔥 [Fire](fire/README.md) - Starting & Maintenance
**20 / 100 guides (20.0%)**

Fire starting techniques, maintenance, and safety protocols.

**Topics**: Friction methods, bow drill, hand drill, flint & steel, char cloth, fire maintenance, safety zones, signal fires

**Start with**: `fire_starting_techniques.md`, `bow_drill_technique.md`

---

### 3. 🏠 [Shelter](shelter/README.md) - Construction & Protection
**20 / 120 guides (16.7%)**

Building shelters for protection from elements.

**Topics**: Site selection, emergency shelters, debris huts, lean-tos, weatherproofing, insulation, knot tying, camouflage

**Start with**: `shelter_site_selection.md`, `emergency_shelters.md`

---

### 4. 🍖 [Food](food/README.md) - Foraging & Preservation
**23 / 180 guides (12.8%)**

Finding, preparing, and preserving food.

**Topics**: Edible plants, foraging, preservation, smoking, drying, fishing, trapping, cooking methods, nutrition

**Start with**: `edible_plants.md`, `foraging_basics.md`

---

### 5. 🧭 [Navigation](navigation/README.md) - Wayfinding & Signaling
**20 / 100 guides (20.0%)**

Navigation techniques and emergency signaling.

**Topics**: Map reading, compass use, natural navigation, star/sun navigation, signaling, rescue signals, route planning

**Start with**: `map_reading.md`, `compass_use.md`

---

### 6. ⚕️ [Medical](medical/README.md) - First Aid & Wilderness Medicine
**27 / 150 guides (18.0%)**

Emergency medical care and wilderness medicine.

**Topics**: First aid, wound care, fractures, burns, hypothermia, heat exhaustion, snake bites, CPR, wilderness medicine

**Start with**: `first_aid_basics.md`, `wound_care.md`

---

### 7. 🔨 [Tools](tools/README.md) - Use & Maintenance
**15 / 100 guides (15.0%)**

Tool use, maintenance, and crafting.

**Topics**: Knife maintenance, axe safety, sharpening, makeshift tools, rope making, cordage, tool repairs

**Start with**: `knife_maintenance.md`, `tool_sharpening.md`

---

### 8. 📡 [Communication](communication/README.md) - Coordination & Security
**15 / 100 guides (15.0%)**

Communication systems and community coordination.

**Topics**: Radio basics, Morse code, hand signals, whistle codes, mirror signals, smoke signals, emergency communication

**Start with**: `radio_basics.md`, `morse_code.md`

---

## 📖 Additional Resources

### [System](system/README.md) ⚙️
uDOS technical documentation, commands, and configuration.

**Key Files**:
- `KNOWLEDGE-REFERENCE.md` - Complete system guide
- `commands.json` - Command specifications
- `OK.md` - OK Assistant documentation

### [Reference](reference/README.md) 📖
Maps, charts, diagrams, and quick-reference materials.

**Contents**: SVG diagrams, reference charts, technical specifications

### [Demos](demos/README.md) 🎮
Interactive demonstrations and example scripts.

**Contents**: Selector demos, UI examples, workflow samples

---

## 🎯 Quick Start

### For Learners
```bash
# Browse a category
LIST knowledge/water/

# Search for beginner guides
SEARCH --tags level:beginner

# Read a guide
READ knowledge/water/finding_water_sources.md

# Start interactive tutorial
PLAY workflow/knowledge_learning.story
```

### For Contributors
```bash
# Start the mission
MISSION START complete_knowledge_bank

# Generate content
RUN workflow/knowledge_generation.uscript

# Or create manually
GENERATE GUIDE water/new_topic --mode ok-assist

# Check progress
MISSION STATUS complete_knowledge_bank
```

---

## 🏷️ Tag System

**Difficulty Levels**
- `level:beginner` - Basic skills, minimal tools
- `level:intermediate` - Some experience needed
- `level:advanced` - Specialized knowledge required
- `level:expert` - Mastery of related skills

**Environments**
- `env:desert`, `env:forest`, `env:mountain`, `env:coastal`
- `env:urban`, `env:tropical`, `env:arctic`

**Skill Types**
- `skill:procurement`, `skill:construction`, `skill:crafting`
- `skill:medical`, `skill:navigation`, `skill:preservation`

**Time Sensitivity**
- `time:emergency` - Critical/life-threatening
- `time:routine` - Regular practice
- `time:preparation` - Advance planning
- `time:long-term` - Sustained operations

---

## 🔗 Cross-Referencing

Guides use `[[topic]]` syntax for linking:

```markdown
See [[water_purification]] for next steps.
Also review [[fire/bow_drill_technique]].
Refer to [[diagram:water_filtration]].
```

This creates an interconnected knowledge network for comprehensive learning.

---

## 📏 Content Standards

All guides meet these quality standards:

✓ **800-1200 words minimum** (avg 1,500 words)
✓ **Complete structure** (overview, materials, steps, safety)
✓ **Safety warnings** highlighted
✓ **Cross-references** to 3-5 related topics
✓ **Proper tagging** (5-10 tags)
✓ **Visual aids** where applicable
✓ **OK Assist reviewed** for accuracy

---

## 🌍 Metric Units & Australian Context

- **All measurements**: Metric (ml, g, kg, cm, m, km)
- **Primary context**: Australian conditions
- **Universal application**: Techniques work globally with local adaptation

**Australian-specific content**: Bushfire survival, snakebite treatment, water sources, bush navigation, native plants

---

## 🚀 v1.4.0 Features

**Offline Knowledge Library** (60 tests)
- Full-text search across all guides
- Version control and change tracking
- Category filtering and organization

**Knowledge Validation** (53 tests)
- Content quality scoring
- Freshness checking
- Contradiction detection

**OK Assist Integration** (New)
- Automated guide generation
- Quality content at scale
- Interactive learning workflows

**SVG/Citation Pipeline** (59 tests)
- Technical diagram generation
- APA/MLA/Chicago/IEEE citations
- 500+ diagram target

---

## 📚 Learning Paths

### Beginner Path (4-6 weeks)
1. Water basics (5 guides)
2. Fire fundamentals (5 guides)
3. Basic shelter (5 guides)
4. Food identification (5 guides)

### Intermediate Path (2-3 months)
1. Advanced water (10 guides)
2. Navigation skills (10 guides)
3. First aid (10 guides)
4. Tool crafting (10 guides)

### Advanced Path (6+ months)
1. All categories comprehensive
2. Cross-category integration
3. Community coordination
4. Long-term sustainability

---

## 🤝 Contributing

See `system/KNOWLEDGE-REFERENCE.md` for:
- Content generation workflows
- Quality standards
- Template usage
- Cross-referencing guidelines
- OK Assist integration

**Quick Commands**:
```bash
GENERATE GUIDE category/topic --mode ok-assist
TAG file.md --add tags
LINK file.md --to related_topics
VALIDATE knowledge/ --metrics all
```

---

## 📂 File Structure

```
knowledge/
├── README.md (this file)
├── water/ (26 guides)
├── fire/ (20 guides)
├── shelter/ (20 guides)
├── food/ (23 guides)
├── navigation/ (20 guides)
├── medical/ (27 guides)
├── tools/ (15 guides)
├── communication/ (15 guides)
├── system/ (documentation)
├── reference/ (charts, diagrams)
└── demos/ (examples)
```

Each category has:
- `README.md` - Category overview and guide index
- `*.md` - Individual guides with OK Assist generation
- Cross-references to related topics

---

## 🔍 Search Tips

```bash
# By keyword
SEARCH "water purification"

# By tag
SEARCH --tags level:beginner,env:desert

# By category
SEARCH --category water

# Full-text
SEARCH "emergency" --all
```

---

## 📞 Support

- **System Reference**: `system/KNOWLEDGE-REFERENCE.md`
- **OK Assist Guide**: `../dev/tools/OK-ASSIST-INTEGRATION-GUIDE.md`
- **Mission Tracking**: `../memory/missions/complete_knowledge_bank.mission`
- **Workflows**: `../memory/workflow/`

---

**Version**: v1.4.0 Phase 1
**License**: Public Domain (Tier 4)
**Maintainer**: uDOS Knowledge Team
**Last Updated**: 2025-11-24

*Building a comprehensive knowledge commons for human resilience and self-sufficiency.*

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
