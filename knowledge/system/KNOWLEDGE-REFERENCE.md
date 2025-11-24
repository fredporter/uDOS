# uDOS Knowledge System Reference
# ================================
# Complete guide to navigating and using the knowledge bank

## Table of Contents

1. [System Overview](#system-overview)
2. [Knowledge Organization](#knowledge-organization)
3. [Using OK Assist](#using-ok-assist)
4. [Content Generation](#content-generation)
5. [Navigation & Search](#navigation-search)
6. [Cross-Referencing](#cross-referencing)
7. [Tagging System](#tagging-system)
8. [Workflows & Missions](#workflows-missions)
9. [Quality Standards](#quality-standards)
10. [Command Reference](#command-reference)

---

## System Overview

The uDOS Knowledge Bank is a comprehensive offline survival and self-sufficiency library with 1,000+ guides covering 8 core categories.

### Key Features

- **📚 1,000+ Comprehensive Guides** - Detailed survival instructions
- **🎨 500+ Technical Diagrams** - Visual learning aids (SVG format)
- **🤖 OK Assist Integration** - Content generation using advanced language models
- **🔗 Cross-Referenced Network** - Interconnected learning paths
- **🏷️ Smart Tagging** - Searchable by difficulty, environment, skill type
- **📱 Offline Access** - Complete local storage, no internet required
- **🎮 Interactive Learning** - STORY-based tutorials and missions

### Content Statistics (v1.4.0)

```
Total Guides:     161 / 1,000 (16.1%)
Total Diagrams:    80 /   500 (16.0%)
OK Assist Gen:     81 guides (50.3%)
Categories:         8 core areas
Average Length: 1,500 words/guide
```

---

## Knowledge Organization

### Category Structure

```
knowledge/
├── water/          (150 target) - Procurement, purification, storage
├── fire/           (100 target) - Starting, maintenance, safety
├── shelter/        (120 target) - Construction, weatherproofing
├── food/           (180 target) - Foraging, preservation, cooking
├── navigation/     (100 target) - Wayfinding, signaling, rescue
├── medical/        (150 target) - First aid, wilderness medicine
├── tools/          (100 target) - Use, maintenance, crafting
├── communication/  (100 target) - Coordination, security
└── reference/
    └── diagrams/   (500 target) - Technical SVG illustrations
```

### File Naming Convention

```
{category}/{topic_name}.md
{category}/{subcategory}/{topic_name}.md

Examples:
water/finding_water_sources.md
fire/friction/bow_drill_technique.md
shelter/emergency/debris_hut.md
```

### Guide Structure

Each guide contains:
1. **Metadata Header** - Category, difficulty, tags, creation date
2. **Quick Reference** - Key info at a glance
3. **Overview** - What, why, when to use
4. **Materials** - Essential, optional, alternatives
5. **Instructions** - Step-by-step with tips and warnings
6. **Safety** - Critical hazards and protocols
7. **Common Mistakes** - What to avoid and why
8. **Troubleshooting** - Problem-solution matrix
9. **Related Skills** - Prerequisites and next steps
10. **References** - Links to diagrams and resources

---

## Using OK Assist

### What is OK Assist?

OK Assist is uDOS's integrated content generation system powered by advanced language models. It creates comprehensive, accurate survival guides tailored to your needs.

### Capabilities

✅ **Generate Guides** - 800-1200 word comprehensive tutorials
✅ **Create Diagrams** - Technical SVG illustrations
✅ **Answer Questions** - Research and knowledge queries
✅ **Suggest Topics** - Related learning paths
✅ **Validate Content** - Quality and accuracy checks

### Basic Usage

```bash
# Ask OK Assistant a question
OK ASK "What are the best methods for water purification?"

# Generate a guide
GENERATE GUIDE water/water_purification_methods --mode ok-assist

# Create a diagram
GENERATE DIAGRAM water/filtration_system --style technical-kinetic

# Get suggestions
OK SUGGEST related-topics water/finding_sources
```

### Configuration

```bash
# Set API key (one-time setup)
CONFIG SET GEMINI_API_KEY your_key_here

# Check OK Assist status
OK STATUS

# View usage statistics
OK STATS
```

### Best Practices

- ✓ Use specific, clear prompts
- ✓ Review and refine generated content
- ✓ Validate technical accuracy
- ✓ Add local knowledge and experience
- ✓ Cross-reference with existing guides

---

## Content Generation

### Automated Generation

Use the generation tool for batch content creation:

```bash
# Generate category content
python3 dev/tools/generate_content_v1_4_0.py --category water --count 10

# Generate with OK Assist
python3 dev/tools/generate_content_v1_4_0.py --category fire --count 5 --guides-only

# Generate diagrams only
python3 dev/tools/generate_content_v1_4_0.py --category shelter --count 3 --diagrams-only

# Dry run (preview without creating)
python3 dev/tools/generate_content_v1_4_0.py --all --dry-run
```

### Workflow-Based Generation

Use uScript workflows for structured generation:

```bash
# Run automated workflow
RUN workflow/knowledge_generation.uscript

# Interactive tutorial mode
PLAY workflow/knowledge_learning.story

# Mission-based generation
MISSION START complete_knowledge_bank
```

### Manual Creation

1. Copy template: `memory/templates/guide_template.md`
2. Fill in required fields
3. Write content following structure
4. Add tags and cross-references
5. Validate formatting and links
6. Save to appropriate category

---

## Navigation & Search

### Browse by Category

```bash
# List category guides
LIST knowledge/water/

# View category index
READ knowledge/water/README.md

# Show category statistics
STATS knowledge/water/ --summary
```

### Search Operations

```bash
# Search by keyword
SEARCH "water purification" --category water

# Search by tags
SEARCH --tags level:beginner,skill:procurement

# Full-text search
SEARCH "emergency" --all

# Find related topics
RELATED water/finding_sources
```

### Filter by Difficulty

```bash
# Beginner guides
SEARCH --difficulty beginner --category all

# Advanced techniques
SEARCH --difficulty advanced --category tools
```

### Filter by Environment

```bash
# Desert survival
SEARCH --env desert

# Forest techniques
SEARCH --env forest --category shelter
```

---

## Cross-Referencing

### Link Syntax

```markdown
# Internal link (same category)
See [[water_purification]] for next steps.

# Cross-category link
Also review [[fire/bow_drill_technique]].

# Diagram reference
Refer to [[diagram:water_filtration]].

# With display text
Learn about [[water_purification|purification methods]].
```

### Relationship Types

**Prerequisites** (`🔑`)
Skills needed before attempting this guide

**Next Steps** (`➡️`)
Skills to learn after mastering this guide

**Related** (`🔗`)
Similar or complementary topics

**Alternatives** (`🔄`)
Different methods for same goal

**Complements** (`🤝`)
Topics that work well together

**Cross-Category** (`📚`)
Related topics from other categories

### Link Management

```bash
# Generate related links automatically
LINK GENERATE knowledge/water/finding_sources.md

# Validate all links
LINK VALIDATE knowledge/

# Show link network
LINK SHOW water/finding_sources

# Update broken links
LINK FIX knowledge/water/
```

---

## Tagging System

### Tag Categories

#### Difficulty Level
`level:beginner` `level:intermediate` `level:advanced` `level:expert`

#### Environment
`env:desert` `env:forest` `env:mountain` `env:coastal` `env:urban` `env:tropical` `env:arctic`

#### Skill Type
`skill:procurement` `skill:construction` `skill:crafting` `skill:medical` `skill:navigation`

#### Time Sensitivity
`time:emergency` `time:routine` `time:preparation` `time:long-term`

#### Resources
`res:minimal-tools` `res:specialized-tools` `res:no-tools` `res:natural-materials`

### Tag Usage

```bash
# Apply tags to guide
TAG knowledge/water/finding_sources.md --add level:beginner,env:forest

# Remove tags
TAG knowledge/water/finding_sources.md --remove obsolete-tag

# Suggest tags automatically
TAG SUGGEST knowledge/water/finding_sources.md

# Normalize tag format
TAG NORMALIZE knowledge/
```

### Tag Search

```bash
# Single tag
SEARCH --tags level:beginner

# Multiple tags (AND)
SEARCH --tags level:beginner,env:forest,skill:procurement

# Tag combination (OR)
SEARCH --tags "level:beginner|level:intermediate"
```

---

## Workflows & Missions

### Knowledge Generation Workflow

Automated content creation using uScript:

```bash
# Run full workflow
RUN workflow/knowledge_generation.uscript

# Run specific category
RUN workflow/knowledge_generation.uscript --category water

# Interactive mode
RUN workflow/knowledge_generation.uscript --interactive
```

### Learning Module (STORY)

Interactive tutorial for content generation:

```bash
# Start tutorial
PLAY workflow/knowledge_learning.story

# Continue from saved progress
PLAY workflow/knowledge_learning.story --continue

# Reset and restart
PLAY workflow/knowledge_learning.story --reset
```

### Complete Knowledge Bank Mission

Track progress toward 1,000-guide goal:

```bash
# Start mission
MISSION START complete_knowledge_bank

# Check progress
MISSION STATUS complete_knowledge_bank

# Update progress
MISSION UPDATE complete_knowledge_bank --progress 200

# View milestones
MISSION MILESTONES complete_knowledge_bank
```

---

## Quality Standards

### Content Requirements

✓ **Word Count**: 800-1200 words minimum
✓ **Structure**: All required sections present
✓ **Safety**: Critical warnings highlighted
✓ **Accuracy**: Technical correctness verified
✓ **Cross-References**: 3-5 related topics minimum
✓ **Tags**: 5-10 descriptive tags
✓ **Diagrams**: Visual aids where applicable

### Validation Commands

```bash
# Validate single guide
VALIDATE knowledge/water/finding_sources.md --metrics all

# Validate category
VALIDATE knowledge/water/ --metrics word-count,structure,links

# Full knowledge bank validation
VALIDATE knowledge/ --comprehensive

# Generate quality report
VALIDATE knowledge/ --report output/quality_report.md
```

### Quality Metrics

- **Completeness**: All template sections filled
- **Accuracy**: Technical information verified
- **Clarity**: Clear, actionable instructions
- **Safety**: Hazards properly identified
- **Linkage**: Interconnected with related topics
- **Tagging**: Properly categorized and searchable
- **Diagrams**: Visual support for complex topics

---

## Command Reference

### Content Generation

```bash
GENERATE GUIDE <category>/<topic> [--mode ok-assist|placeholder]
GENERATE DIAGRAM <topic> [--style technical-kinetic]
GENERATE INDEX <category>
GENERATE STATS <path> [--detailed]
```

### OK Assist

```bash
OK ASK "<question>"
OK SUGGEST <type> <topic>
OK STATUS
OK STATS
```

### Search & Navigation

```bash
SEARCH "<query>" [--category <cat>] [--tags <tags>]
LIST <path>
READ <file>
STATS <path> [--summary|--detailed]
RELATED <topic>
```

### Link Management

```bash
LINK GENERATE <file>
LINK VALIDATE <path>
LINK SHOW <topic>
LINK FIX <path>
```

### Tag Management

```bash
TAG <file> --add <tags>
TAG <file> --remove <tags>
TAG SUGGEST <file>
TAG NORMALIZE <path>
```

### Workflow & Mission

```bash
RUN <workflow.uscript> [options]
PLAY <learning.story> [--continue|--reset]
MISSION START <mission>
MISSION STATUS <mission>
MISSION UPDATE <mission> --progress <count>
```

### Validation

```bash
VALIDATE <path> --metrics <metrics>
VALIDATE <path> --report <output>
```

---

## Quick Start Guide

### For Learners

1. Browse categories: `LIST knowledge/`
2. Find beginner guides: `SEARCH --tags level:beginner`
3. Read a guide: `READ knowledge/water/finding_sources.md`
4. Start tutorial: `PLAY workflow/knowledge_learning.story`

### For Contributors

1. Start mission: `MISSION START complete_knowledge_bank`
2. Run workflow: `RUN workflow/knowledge_generation.uscript`
3. Or generate manually:
   - `GENERATE GUIDE water/new_topic --mode ok-assist`
4. Validate: `VALIDATE knowledge/water/new_topic.md --metrics all`
5. Update progress: `MISSION UPDATE complete_knowledge_bank --progress +1`

### For Developers

1. Review architecture: `READ knowledge/KNOWLEDGE-SYSTEM.md`
2. Understand templates: `READ memory/templates/guide_template.md`
3. Study linking system: `READ memory/templates/linking_tagging_system.json`
4. Check generation tool: `READ dev/tools/generate_content_v1_4_0.py`
5. Review OK Assist integration: `READ dev/tools/OK-ASSIST-INTEGRATION-GUIDE.md`

---

## Support & Resources

### Documentation

- **System Architecture**: `knowledge/KNOWLEDGE-SYSTEM.md`
- **OK Assist Guide**: `dev/tools/OK-ASSIST-INTEGRATION-GUIDE.md`
- **Template Reference**: `memory/templates/guide_template.md`
- **Linking System**: `memory/templates/linking_tagging_system.json`

### Workflows

- **Generation**: `memory/workflow/knowledge_generation.uscript`
- **Learning**: `memory/workflow/knowledge_learning.story`

### Missions

- **Complete Bank**: `memory/missions/complete_knowledge_bank.mission`

### Wiki

- **Knowledge Architecture**: `wiki/Knowledge-Architecture.md`
- **Command Reference**: `wiki/Command-Reference.md`
- **Quick Start**: `wiki/Quick-Start.md`

---

**Version**: 1.4.0
**Last Updated**: 2025-11-24
**Status**: Active Development
**Mode**: OK Assist Integration Enabled
