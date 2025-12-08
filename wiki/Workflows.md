# Common Workflows in uDOS

**Practical guides for getting things done with uDOS**

This page documents real-world workflows using uDOS commands and features. Each workflow includes step-by-step instructions, examples, and tips.

---

## Table of Contents

1. [Knowledge Management](#knowledge-management)
2. [Writing and Publishing](#writing-and-publishing)
3. [Research and Note-Taking](#research-and-note-taking)
4. [Script Automation with uCODE](#script-automation-with-ucode)
5. [Theme Customization](#theme-customization)
6. [Web Extension Usage](#web-extension-usage)
7. [File Organization](#file-organization)
8. [Daily Productivity](#daily-productivity)

---

## Knowledge Management

### Building Your Personal Knowledge Base

**Goal**: Create an organized, searchable knowledge library in uDOS.

#### Step 1: Set Up Your Structure

```bash
# Navigate to knowledge directory
🔮 > CD knowledge

# Create your personal knowledge area
🔮 > MKDIR personal

# Create topic-based subdirectories
🔮 > MKDIR personal/projects
🔮 > MKDIR personal/learning
🔮 > MKDIR personal/ideas
🔮 > MKDIR personal/reference
```

#### Step 2: Create Your First Knowledge Entry

```bash
# Create a new topic file
🔮 > EDIT knowledge/personal/learning/python-notes.md
```

**Template to use**:
```markdown
# Python Notes

**Category**: Learning / Programming
**Started**: 2025-11-14
**Status**: Active

## Key Concepts

-

## Code Snippets

```python
# Example code here
```

## Resources

-

## Questions/TODO

-
```

#### Step 3: Link Related Knowledge

Create index files that link to related topics:

```bash
🔮 > EDIT knowledge/personal/index.md
```

```markdown
# My Knowledge Index

## By Category

### Programming
- [Python Notes](learning/python-notes.md)
- [Git Commands](reference/git-cheatsheet.md)

### Projects
- [Website Redesign](projects/website-redesign.md)

## Recently Updated
- 2025-11-14: Python Notes
```

#### Step 4: Search Your Knowledge

```bash
# Find all mentions of a topic
🔮 > FIND "python" knowledge/personal/

# List all markdown files
🔮 > LIST knowledge/personal/*.md

# View a specific file
🔮 > CAT knowledge/personal/learning/python-notes.md
```

#### Tips for Knowledge Management

- ✅ **Use consistent naming**: `topic-name.md` (lowercase, hyphens)
- ✅ **Add metadata**: Date, category, status at top of files
- ✅ **Link liberally**: Reference related topics
- ✅ **Review regularly**: Weekly review of recent notes
- ✅ **Keep it simple**: Don't over-organize, just start writing

---

## Writing and Publishing

### From Draft to Published Document

**Goal**: Write, edit, and publish a document using uDOS.

#### Workflow 1: Blog Post

```bash
# 1. Create draft
🔮 > EDIT sandbox/blog-draft.md

# 2. Write content (in editor)
#    - Write freely, don't edit yet
#    - Focus on getting ideas down

# 3. Review draft
🔮 > CAT sandbox/blog-draft.md

# 4. Edit for clarity
🔮 > EDIT sandbox/blog-draft.md
#    - Fix typos
#    - Improve structure
#    - Add examples

# 5. Move to final location
🔮 > COPY sandbox/blog-draft.md output/blog-post.md

# 6. Export/publish
#    - Copy content to blogging platform
#    - Or use as-is (Markdown is portable!)
```

#### Workflow 2: Technical Documentation

```bash
# 1. Create documentation structure
🔮 > MKDIR output/docs
🔮 > EDIT output/docs/index.md
🔮 > EDIT output/docs/installation.md
🔮 > EDIT output/docs/usage.md
🔮 > EDIT output/docs/troubleshooting.md

# 2. Write each section
#    Follow documentation template

# 3. Cross-link documents
#    Add "See also" sections with links

# 4. Generate table of contents (manual)
🔮 > EDIT output/docs/index.md
```

**Documentation Template**:
```markdown
# Feature Name

**Last Updated**: 2025-11-14
**Version**: 1.0

## Overview

Brief description of what this does.

## Installation

Step-by-step setup instructions.

## Usage

### Basic Usage

```bash
# Example command
```

### Advanced Options

## Troubleshooting

### Problem: Issue description
**Solution**: How to fix it

## See Also

- [Related Doc](related.md)
```

#### Writing Tips

- 📝 **Draft first, edit later** - Don't self-censor while writing
- 📝 **Use Markdown** - Future-proof, portable, version-controllable
- 📝 **One idea per file** - Easier to find and reuse
- 📝 **Name files descriptively** - `what-is-this-about.md`

---

## Research and Note-Taking

### Capturing and Organizing Research

**Goal**: Research a topic and build useful, organized notes.

#### Research Workflow

```bash
# 1. Create research folder
🔮 > MKDIR sandbox/research/topic-name

# 2. Start with questions
🔮 > EDIT sandbox/research/topic-name/questions.md
```

**Questions Template**:
```markdown
# Research Questions: [Topic Name]

## Main Question
What am I trying to learn/solve?

## Sub-Questions
1.
2.
3.

## Success Criteria
I'll know I'm done when I can:
-
-
```

```bash
# 3. Collect sources
🔮 > EDIT sandbox/research/topic-name/sources.md
```

**Sources Template**:
```markdown
# Sources: [Topic Name]

## Articles
- [Title](URL) - Key takeaway
-

## Books
- Title by Author - Notes

## Videos
- [Title](URL) - Summary
```

```bash
# 4. Take notes while researching
🔮 > EDIT sandbox/research/topic-name/notes.md
```

**Note-Taking Format**:
```markdown
# Notes: [Topic Name]

## Source: Article Title
**Date**: 2025-11-14
**URL**: https://...

### Key Points
- Point 1
- Point 2

### Quotes
> "Important quote here"

### My Thoughts
-

---

## Source: Another Article
...
```

```bash
# 5. Synthesize findings
🔮 > EDIT sandbox/research/topic-name/synthesis.md
```

**Synthesis Template**:
```markdown
# Synthesis: [Topic Name]

## What I Learned
Summary of key findings

## Answering My Questions
1. Question 1: Answer
2. Question 2: Answer

## Actionable Insights
What can I do with this knowledge?
-
-

## Further Research
What questions remain?
-
```

```bash
# 6. Archive useful research
🔮 > COPY sandbox/research/topic-name/synthesis.md knowledge/personal/reference/
```

#### Research Tips

- 🔍 **Start with questions** - Guides your research
- 🔍 **Take notes in your own words** - Aids understanding
- 🔍 **Synthesize, don't just collect** - Create new understanding
- 🔍 **Archive the best** - Move completed research to knowledge/

---

## Script Automation with uCODE

### Automating Repetitive Tasks

**Goal**: Use uCODE scripts to automate common workflows.

#### Example 1: Daily Standup Log

Create `scripts/daily-standup.uscript`:

```bash
# Daily Standup Log Generator
# Prompts for what you did, what you're doing, any blockers

ECHO "=== Daily Standup ==="
ECHO ""

# Get today's date
SET date = TODAY

# Create or append to standup file
SET filename = "sandbox/logs/standup-${date}.md"

ECHO "What did you accomplish yesterday?"
READ yesterday

ECHO "What will you work on today?"
READ today

ECHO "Any blockers?"
READ blockers

# Write to file
ECHO "# Standup ${date}" >> ${filename}
ECHO "" >> ${filename}
ECHO "## Yesterday" >> ${filename}
ECHO "${yesterday}" >> ${filename}
ECHO "" >> ${filename}
ECHO "## Today" >> ${filename}
ECHO "${today}" >> ${filename}
ECHO "" >> ${filename}
ECHO "## Blockers" >> ${filename}
ECHO "${blockers}" >> ${filename}
ECHO "" >> ${filename}

ECHO "Standup logged to ${filename}"
```

**Usage**:
```bash
🔮 > RUN scripts/daily-standup.uscript
```

#### Example 2: Backup Important Files

Create `scripts/backup.uscript`:

```bash
# Backup Script
# Copies important files to backup location

ECHO "Starting backup..."

SET backup_dir = "memory/backups"
SET date = TODAY

# Create dated backup folder
MKDIR ${backup_dir}/${date}

# Copy important directories
COPY knowledge/personal ${backup_dir}/${date}/personal
COPY sandbox/projects ${backup_dir}/${date}/projects
COPY sandbox/logs ${backup_dir}/${date}/logs

ECHO "Backup complete: ${backup_dir}/${date}"
LIST ${backup_dir}/${date}
```

#### Example 3: Weekly Review Template

Create `scripts/weekly-review.uscript`:

```bash
# Weekly Review Template Generator

SET week = CURRENT_WEEK
SET filename = "memory/reviews/week-${week}.md"

# Create template
ECHO "# Weekly Review - Week ${week}" > ${filename}
ECHO "" >> ${filename}
ECHO "## Accomplishments" >> ${filename}
ECHO "- " >> ${filename}
ECHO "" >> ${filename}
ECHO "## Challenges" >> ${filename}
ECHO "- " >> ${filename}
ECHO "" >> ${filename}
ECHO "## Lessons Learned" >> ${filename}
ECHO "- " >> ${filename}
ECHO "" >> ${filename}
ECHO "## Next Week Goals" >> ${filename}
ECHO "1. " >> ${filename}
ECHO "2. " >> ${filename}
ECHO "3. " >> ${filename}

# Open for editing
EDIT ${filename}
```

#### Automation Tips

- 🤖 **Automate the boring** - Repetitive tasks first
- 🤖 **Test scripts in sandbox/** - Don't risk real data
- 🤖 **Add error handling** - What if file doesn't exist?
- 🤖 **Comment your scripts** - Future you will thank you
- 🤖 **Start simple** - Don't over-engineer

**See also**: [uCODE Language](uCODE-Language.md) for complete scripting reference

---

## Theme Customization

### Personalizing Your uDOS Experience

**Goal**: Customize colors, fonts, and appearance.

#### Changing Themes

```bash
# List available themes
🔮 > THEME LIST

# Try a theme
🔮 > THEME matrix      # Green on black
🔮 > THEME amber       # Amber on black
🔮 > THEME classic     # Default

# See current theme
🔮 > STATUS
```

#### Custom Theme Creation

```bash
# 1. View existing theme
🔮 > CAT data/themes/matrix.theme

# 2. Create your own
🔮 > EDIT data/themes/custom.theme
```

**Theme File Format**:
```ini
[Colors]
foreground = #00ff00
background = #000000
prompt = #00ff00
highlight = #00ff00
error = #ff0000
warning = #ffff00
success = #00ff00

[Font]
family = monospace
size = 12

[Cursor]
style = block
blink = true
```

```bash
# 3. Load your theme
🔮 > THEME custom
```

#### Customization Tips

- 🎨 **High contrast** - Easier on the eyes
- 🎨 **Monospace fonts** - Better for code and tables
- 🎨 **Test in different lighting** - Day vs night
- 🎨 **Save favorite themes** - Keep backups

---

## Web Extension Usage

### Accessing Web Content from uDOS

**Goal**: Use the web extension to browse and capture web content.

#### Basic Web Browsing

```bash
# Open a website
🔮 > WEB https://example.com

# Search the web
🔮 > WEB SEARCH "uDOS documentation"

# Navigate
🔮 > WEB BACK
🔮 > WEB FORWARD
🔮 > WEB REFRESH
```

#### Capturing Web Content

```bash
# Save current page as text
🔮 > WEB SAVE output/saved-page.txt

# Extract article text (if extension supports)
🔮 > WEB EXTRACT output/article.md

# Take screenshot (if supported)
🔮 > WEB SCREENSHOT output/screenshot.png
```

#### Research Workflow with Web

```bash
# 1. Search for topic
🔮 > WEB SEARCH "python best practices"

# 2. Extract useful articles
🔮 > WEB EXTRACT sandbox/research/python-bp-1.md

# 3. Continue to next result
🔮 > WEB NEXT

# 4. Extract another
🔮 > WEB EXTRACT sandbox/research/python-bp-2.md

# 5. Synthesize findings
🔮 > EDIT sandbox/research/python-synthesis.md
```

#### Web Extension Tips

- 🌐 **Extract to Markdown** - Converts HTML to readable text
- 🌐 **Save source URLs** - Add as metadata to saved files
- 🌐 **Batch save tabs** - If extension supports it
- 🌐 **Privacy mode** - Use for sensitive research

**Note**: Web extension features depend on which extension is installed. See extension-specific documentation.

---

## File Organization

### Keeping Your Workspace Tidy

**Goal**: Maintain an organized file structure.

#### The uDOS Organization System

```
uDOS/
├── sandbox/          ← Active work, experiments
│   ├── drafts/
│   ├── projects/
│   └── research/
├── knowledge/        ← Permanent knowledge
│   └── personal/
├── memory/           ← Logs, history, state
│   ├── logs/
│   └── backups/
└── output/           ← Finished work
    └── published/
```

#### Weekly File Organization Routine

```bash
# 1. Review what's in sandbox
🔮 > LIST sandbox

# 2. Archive completed work
🔮 > COPY sandbox/project-done output/projects/project-name
🔮 > DELETE sandbox/project-done

# 3. Promote good notes to knowledge base
🔮 > COPY sandbox/research/useful-topic knowledge/personal/reference/

# 4. Clean up old drafts
🔮 > LIST sandbox/drafts
🔮 > DELETE sandbox/drafts/old-idea.md

# 5. Backup important files
🔮 > RUN scripts/backup.uscript
```

#### File Naming Conventions

**Good**:
- `project-name-v2.md` (lowercase, hyphens, version)
- `2025-11-14-meeting-notes.md` (date prefix)
- `python-best-practices.md` (descriptive, clear)

**Bad**:
- `Untitled.md` (not descriptive)
- `asdf.txt` (meaningless)
- `final FINAL v3 (1).md` (confusing)

#### Organization Tips

- 📁 **Weekly cleanup** - Don't let files pile up
- 📁 **Archive, don't delete** - Move old work to memory/archive/
- 📁 **Use dates in filenames** - `YYYY-MM-DD-description.md`
- 📁 **One topic per file** - Easier to find and manage

---

## Daily Productivity

### Morning Startup Routine

**Goal**: Start your day organized and focused.

#### Morning Script

Create `scripts/morning-routine.uscript`:

```bash
# Morning Startup Routine

CLEAR

ECHO "=== Good Morning! ==="
ECHO ""

# Show system status
STATUS

ECHO ""
ECHO "=== Today's Tasks ==="
# Show today's task file
CAT memory/tasks/today.md

ECHO ""
ECHO "=== Recent Notes ==="
# List recent files
LIST sandbox --sort date --limit 5

ECHO ""
ECHO "Ready to start the day!"
ECHO "Remember: One task at a time."
```

**Run it**:
```bash
🔮 > RUN scripts/morning-routine.uscript
```

#### Task Management Workflow

```bash
# 1. Create today's task file
🔮 > EDIT memory/tasks/today.md
```

**Task Template**:
```markdown
# Tasks - 2025-11-14

## High Priority
- [ ] Most important task
- [ ] Second priority

## Medium Priority
- [ ] Can wait if needed
- [ ] Not urgent

## Low Priority
- [ ] Nice to do
- [ ] If time permits

## Completed Today
- [x] Morning review
```

```bash
# 2. Throughout the day, update task file
🔮 > EDIT memory/tasks/today.md
#    Check off completed tasks

# 3. End of day review
🔮 > EDIT memory/tasks/today.md
#    Move incomplete tasks to tomorrow
```

#### Evening Shutdown Routine

Create `scripts/evening-routine.uscript`:

```bash
# Evening Shutdown Routine

ECHO "=== End of Day Review ==="
ECHO ""

ECHO "What did you accomplish today?"
CAT memory/tasks/today.md | grep "\[x\]"

ECHO ""
ECHO "Creating tomorrow's task file..."

# Copy incomplete tasks to tomorrow
# (Simplified - actual implementation would parse checkboxes)
SET tomorrow = TOMORROW
COPY memory/tasks/today.md memory/tasks/${tomorrow}.md

ECHO ""
ECHO "Backing up today's work..."
RUN scripts/backup.uscript

ECHO ""
ECHO "Good work today! See you tomorrow."
```

#### Productivity Tips

- ⚡ **Start with most important task** - Do it first
- ⚡ **Time-box tasks** - Use Pomodoro technique
- ⚡ **Review daily** - Morning plan, evening reflect
- ⚡ **Keep it simple** - Don't over-organize

---

## Mission Templates (v1.1.3+)

**Fast-track complex projects with pre-built mission templates**

Mission templates provide structured workflows for common projects, eliminating manual setup and ensuring consistent organization.

### What Are Mission Templates?

Templates are pre-configured mission structures with:
- **Moves**: Major project phases (e.g., Planning, Drafting, Revision)
- **Steps**: Specific tasks within each move
- **Variables**: Customizable parameters (title, author, goals, etc.)
- **Checkpoints**: Progress milestones

**Time Savings**: Create a 35-step novel writing mission in 30 seconds vs. 30 minutes of manual setup.

### Available Templates

#### List All Templates

```bash
# See all available templates
🔮 > MISSION TEMPLATES

# Filter by category
🔮 > MISSION TEMPLATES creative-writing
```

**Categories**:
- `creative-writing` - Novels, plays, screenplays, poetry
- `research-learning` - Research, skill development, learning paths
- `personal-development` - Habits, goals, journaling
- `knowledge-creation` - Documentation, tutorials, reference materials

#### Preview a Template

```bash
# See template details, variables, and structure
🔮 > MISSION TEMPLATE novel

📋 Template: Novel Writing Project
   Category: creative-writing
   Moves: 7
   Total Steps: 35

🔧 Variables:
   [✓] NOVEL_TITLE - Title of your novel
   [✓] AUTHOR_NAME - Author name
   [✓] GENRE - Novel genre (Fantasy, Sci-Fi, Mystery, etc.)
   [ ] TARGET_WORDS - Target word count (default: 80000)
   ...
```

### Using Templates

#### Quick Start: Novel Writing Project

```bash
# 1. Preview the template
🔮 > MISSION TEMPLATE novel

# 2. Create mission from template
🔮 > MISSION CREATE --template novel --id my-novel \
       --vars "NOVEL_TITLE=The Dragon's Oath,AUTHOR_NAME=Sarah Wordsmith,GENRE=Fantasy,TARGET_WORDS=120000"

# ✅ Mission created with 7 moves, 35 steps!

# 3. Start working
🔮 > MISSION START my-novel
🔮 > MISSION STATUS my-novel
```

#### Template Variables

**Required variables** (marked with ✓):
- Must be provided when creating mission
- Validation ensures all required variables are present

**Optional variables** (marked with space):
- Have sensible defaults
- Can override if needed

**Variable Types**:
- `string` - Text values (titles, names, descriptions)
- `number` - Numeric values (word counts, chapter numbers)
- `choice` - Select from predefined options (genres, difficulty levels)
- `boolean` - True/false flags
- `date` - Date values

#### Example: Create Novel with Custom Title

```bash
# Create mission with template variables and custom title
🔮 > MISSION CREATE --template novel --id epic-fantasy \
       --vars "NOVEL_TITLE=Crystal Throne,AUTHOR_NAME=Jane Writer,GENRE=Fantasy" \
       --title "My Epic Fantasy Novel Project" \
       --desc "A 100k-word epic fantasy about dragons and magic"

# The mission uses the template structure but with your custom title/description
```

### Template Structure

#### Novel Template Example

**7 Moves** (Major Phases):
1. **Planning & Outline** - Story structure, characters, world
2. **First Draft - Opening** - Write first 25% (approx. 20k words)
3. **First Draft - Rising Action** - Middle 50% (approx. 40k words)
4. **First Draft - Climax** - Final 25% (approx. 20k words)
5. **Revision - Structure** - Plot, pacing, character arcs
6. **Revision - Line Editing** - Sentence-level improvements
7. **Final Polish** - Proofreading, formatting, submission prep

**35 Steps** spread across moves:
- Each step is a specific, actionable task
- Checkpoints after major milestones
- Progress tracking built-in

**6 Variables**:
- NOVEL_TITLE, AUTHOR_NAME, GENRE (required)
- TARGET_WORDS, CHAPTER_COUNT, DAILY_WORD_GOAL (optional)

### Common Workflows

#### Workflow 1: Start a Novel

```bash
# List creative writing templates
🔮 > MISSION TEMPLATES creative-writing

# Preview the novel template
🔮 > MISSION TEMPLATE novel

# Create your novel mission
🔮 > MISSION CREATE --template novel --id my-scifi-novel \
       --vars "NOVEL_TITLE=Starship Nexus,AUTHOR_NAME=Alex Chen,GENRE=Sci-Fi,TARGET_WORDS=90000,DAILY_WORD_GOAL=1000"

# Start writing
🔮 > MISSION START my-scifi-novel

# Check your progress
🔮 > MISSION STATUS my-scifi-novel
```

#### Workflow 2: Write a Stage Play

```bash
# Preview the play template
🔮 > MISSION TEMPLATE play

# Create your play mission (3-act drama)
🔮 > MISSION CREATE --template play --id garden-play \
       --vars "PLAY_TITLE=Echoes in the Garden,PLAYWRIGHT=Jordan Lee,GENRE=Drama,ACT_COUNT=3,SCENE_COUNT=12"

# Start developing characters and scenes
🔮 > MISSION START garden-play
🔮 > MISSION STATUS garden-play
```

**Play Template Structure** (8 moves, 54 steps):
1. Foundation & Concept
2. Character Development
3. Structure & Outline
4. First Draft - Act 1
5. First Draft - Acts 2+
6. Revision - Structure & Story
7. Revision - Dialogue & Craft
8. Polish & Submission

**Variables**: PLAY_TITLE, PLAYWRIGHT, GENRE (Drama/Comedy/Tragedy/Farce/Melodrama/Absurdist/Musical Drama), ACT_COUNT, SCENE_COUNT, RUNTIME_TARGET, CHARACTER_COUNT

#### Workflow 3: Compose a Musical

```bash
# Preview the musical template
🔮 > MISSION TEMPLATE musical

# Create your musical mission (Broadway-style show)
🔮 > MISSION CREATE --template musical --id neon-dreams \
       --vars "MUSICAL_TITLE=Neon Dreams,COMPOSER=Alex Chen,LYRICIST=Jordan Lee,GENRE=Broadway,SONG_COUNT=16"

# Start with concept and characters
🔮 > MISSION START neon-dreams
```

**Musical Template Structure** (8 moves, 55 steps):
1. Concept & Story Development
2. Character & Song List Development
3. Book Writing (Scenes & Dialogue)
4. Lyric Writing - Act 1
5. Lyric Writing - Act 2+
6. Music Composition - Melodies & Structure
7. Orchestration & Arrangements
8. Revision & Production Preparation

**Variables**: MUSICAL_TITLE, COMPOSER, LYRICIST, BOOK_WRITER, GENRE (Broadway/Rock Musical/Jukebox Musical/Operetta/Folk/Jazz/Pop), SONG_COUNT, ACT_COUNT, RUNTIME_TARGET

#### Workflow 4: Write a Screenplay

```bash
# Preview the screenplay template
🔮 > MISSION TEMPLATE screenplay

# Create feature film screenplay
🔮 > MISSION CREATE --template screenplay --id last-signal \
       --vars "SCREENPLAY_TITLE=The Last Signal,SCREENWRITER=Taylor Brooks,GENRE=Sci-Fi,FORMAT=Feature Film,PAGE_TARGET=110"

# Or create TV pilot
🔮 > MISSION CREATE --template screenplay --id city-echoes \
       --vars "SCREENPLAY_TITLE=City of Echoes,SCREENWRITER=Morgan Lee,GENRE=Drama,FORMAT=TV Pilot,PAGE_TARGET=60"

# Start writing
🔮 > MISSION START last-signal
```

**Screenplay Template Structure** (8 moves, 52 steps):
1. Concept & Logline
2. Character Development
3. Story Structure & Beat Sheet
4. First Draft - Act 1
5. First Draft - Act 2 & 3
6. Revision - Story & Structure
7. Revision - Dialogue & Action
8. Polish & Submission

**Variables**: SCREENPLAY_TITLE, SCREENWRITER, GENRE (Action/Drama/Comedy/Thriller/Horror/Sci-Fi/Fantasy/Romance/Mystery/Adventure), FORMAT (Feature Film/TV Pilot/TV Episode/Short Film), PAGE_TARGET, ACT_COUNT

**Key Feature**: Proper screenplay formatting guidance (1 page = 1 minute screen time)

#### Workflow 5: Curate a Poetry Collection

```bash
# Preview the poetry template
🔮 > MISSION TEMPLATE poetry-collection

# Create free verse collection
🔮 > MISSION CREATE --template poetry-collection --id wire-whispers \
       --vars "COLLECTION_TITLE=Whispers in the Wire,POET=River Song,THEME=Technology and human connection,POEM_COUNT=42,STYLE=Free Verse"

# Or create formal poetry collection
🔮 > MISSION CREATE --template poetry-collection --id stone-seasons \
       --vars "COLLECTION_TITLE=Seasons of Stone,POET=Morgan Wilde,THEME=Geological time and memory,POEM_COUNT=50,STYLE=Formal"

# Begin drafting poems
🔮 > MISSION START wire-whispers
```

**Poetry Collection Template Structure** (7 moves, 45 steps):
1. Vision & Theme Development
2. Initial Draft - Poem Generation
3. Organization & Structure
4. Revision - Individual Poems
5. Revision - Collection Cohesion
6. Line-Level Polish
7. Publication Preparation

**Variables**: COLLECTION_TITLE, POET, THEME, POEM_COUNT, STYLE (Free Verse/Formal/Prose Poetry/Mixed/Experimental/Narrative), SECTION_COUNT, PAGE_TARGET

**Unique Focus**: Collection as unified artistic statement, not just gathered poems

#### Workflow 6: Conduct Academic Research

```bash
# Preview the research template
🔮 > MISSION TEMPLATE research-topic

# Create academic research project
🔮 > MISSION CREATE --template research-topic --id climate-study \
       --vars "TOPIC=Climate adaptation strategies in urban planning,RESEARCHER=Dr. Sarah Chen,DISCIPLINE=Social Sciences,SCOPE=Comprehensive,METHODOLOGY=Case Study,TIMELINE=16"

# Or create personal research project
🔮 > MISSION CREATE --template research-topic --id architecture-history \
       --vars "TOPIC=Victorian-era commercial buildings in downtown Brisbane,RESEARCHER=Alex Martinez,DISCIPLINE=Humanities,METHODOLOGY=Historical Analysis,OUTPUT_FORMAT=Article"

# Begin research planning
🔮 > MISSION START climate-study
```

**Research Topic Template Structure** (8 moves, 44 steps):
1. Research Question & Planning
2. Literature Review & Background Research
3. Data Collection & Primary Research
4. Data Analysis & Interpretation
5. Writing & Structuring Research Output
6. Citations & References
7. Revision & Polish
8. Submission & Dissemination

**Variables**: TOPIC, RESEARCHER, DISCIPLINE (10 choices), SCOPE (Exploratory/Moderate/Comprehensive/Thesis-Level), METHODOLOGY (8 choices including Literature Review/Experimental/Survey/Case Study), TIMELINE (weeks), OUTPUT_FORMAT (Research Paper/Report/Thesis/Article/etc.)

**Key Feature**: Rigorous academic methodology with proper citation management and data analysis guidance

#### Workflow 7: Explore a New Subject

```bash
# Preview the subject exploration template
🔮 > MISSION TEMPLATE explore-subject

# Learn data science for career transition
🔮 > MISSION CREATE --template explore-subject --id data-science \
       --vars "SUBJECT=Data Science and Machine Learning,LEARNER=Jamie Park,DEPTH=Intermediate (working knowledge),TIMEFRAME=16,LEARNING_STYLE=Project-Based (learn by building),GOAL=Career Development"

# Or explore philosophy for personal growth
🔮 > MISSION CREATE --template explore-subject --id philosophy \
       --vars "SUBJECT=Western Philosophy,LEARNER=Morgan Lee,DEPTH=Survey (broad overview),TIMEFRAME=12,LEARNING_STYLE=Theory-First (concepts then practice)"

# Start learning journey
🔮 > MISSION START data-science
```

**Explore Subject Template Structure** (5 moves, 26 steps):
1. Foundation & Orientation
2. Core Concepts & Fundamentals (3 concepts with practice)
3. Intermediate Topics & Applications
4. Advanced Topics & Specialization
5. Synthesis & Knowledge Consolidation

**Variables**: SUBJECT, LEARNER, DEPTH (Survey/Intermediate/Advanced/Mastery), TIMEFRAME (weeks), LEARNING_STYLE (Theory-First/Practice-First/Balanced/Project-Based), GOAL (Personal Growth/Career Development/Academic/Creative/Problem-Solving/Teaching)

**Key Feature**: Adaptable to any subject with customizable depth and learning approach

#### Workflow 8: Learn Programming

```bash
# Preview the coding template
🔮 > MISSION TEMPLATE learn-to-code

# Learn uCODE for workflow automation
🔮 > MISSION CREATE --template learn-to-code --id ucode-automation \
       --vars "LANGUAGE=uCODE (uDOS workflow scripting),LEARNER=Taylor Kim,SKILL_LEVEL=Complete Beginner,PROJECT_GOAL=Automate my daily task tracking and reporting,PRACTICE_HOURS=4"

# Or learn Python for data analysis
🔮 > MISSION CREATE --template learn-to-code --id python-data \
       --vars "LANGUAGE=Python,LEARNER=Jordan Martinez,SKILL_LEVEL=Some Coding Experience,PROJECT_GOAL=Build data dashboards for sales analysis,PRACTICE_HOURS=8,LEARNING_PATH=Fundamentals-First (theory then practice)"

# Start coding
🔮 > MISSION START ucode-automation
```

**Learn to Code Template Structure** (8 moves, 40 steps):
1. Setup & Hello World
2. Variables & Data Types
3. Control Flow - Decisions & Loops
4. Data Structures - Lists & Collections
5. Functions & Code Organization
6. Files & External Data
7. Advanced Concepts & Best Practices
8. Next Steps & Continued Learning

**Variables**: LANGUAGE (uCODE/Python/JavaScript/Java/C++/Ruby/Go/Rust/Other), LEARNER, SKILL_LEVEL (Complete Beginner/Some Experience/New to This Language/Intermediate), PROJECT_GOAL, PRACTICE_HOURS (weekly), LEARNING_PATH (Project-Based/Fundamentals-First/Tutorial-Driven/Problem-Solving)

**Key Feature**: Special focus on uCODE for uDOS users, with detailed language-specific guidance in step notes

#### Workflow 9: Master a Foreign Language

```bash
# Preview the language learning template
🔮 > MISSION TEMPLATE language-learning

# Learn Spanish for travel
🔮 > MISSION CREATE --template language-learning --id spanish-travel \
       --vars "LANGUAGE=Spanish,LEARNER=Alex Rivera,CURRENT_LEVEL=Complete Beginner,TARGET_LEVEL=Intermediate (B1),STUDY_HOURS=7,MOTIVATION=Travel,FOCUS_SKILLS=Speaking/Listening"

# Or learn Japanese for career
🔮 > MISSION CREATE --template language-learning --id japanese-business \
       --vars "LANGUAGE=Japanese,LEARNER=Sam Chen,CURRENT_LEVEL=Elementary (A1),TARGET_LEVEL=Upper-Intermediate (B2),STUDY_HOURS=10,MOTIVATION=Career/Business,FOCUS_SKILLS=Balanced (all skills)"

# Begin language study
🔮 > MISSION START spanish-travel
```

**Language Learning Template Structure** (6 moves, 31 steps):
1. Foundation & First Steps
2. Elementary Communication
3. Intermediate Conversations
4. Reading & Writing Development
5. Cultural Fluency & Advanced Skills
6. Maintenance & Continued Growth

**Variables**: LANGUAGE, LEARNER, CURRENT_LEVEL (Complete Beginner/A1/A2/B1/B2), TARGET_LEVEL (A1/A2/B1/B2/C1/C2 using CEFR scale), STUDY_HOURS (weekly), MOTIVATION (Personal Interest/Travel/Career/Family/Academic/Immigration), FOCUS_SKILLS (Balanced/Speaking-Listening/Reading-Writing/Conversational/Academic-Formal)

**Key Feature**: CEFR-aligned proficiency levels with cultural awareness and real-world communication focus

#### Workflow 10: Track and Build Habits

```bash
# Preview the habit tracking template
🔮 > MISSION TEMPLATE habit-tracking

# Build daily meditation habit
🔮 > MISSION CREATE --template habit-tracking --id meditation-90 \
       --vars "HABIT_NAME=Morning meditation,TRACKER=Alex Park,FREQUENCY=Daily,DURATION=90,TIME_COMMITMENT=10,MOTIVATION=Mental Wellbeing"

# Or establish fitness routine
🔮 > MISSION CREATE --template habit-tracking --id strength-training \
       --vars "HABIT_NAME=Strength training workout,TRACKER=Sam Rodriguez,FREQUENCY=3x per Week,DURATION=90,TIME_COMMITMENT=45,MOTIVATION=Health & Fitness"

# Start habit building
🔮 > MISSION START meditation-90
```

**Habit Tracking Template Structure** (6 moves, 26 steps):
1. Habit Design & Setup
2. Launch & First Week (Days 1-7)
3. Consistency Building (Days 8-30)
4. Habit Solidification (Days 31-60)
5. Habit Mastery (Days 61-90)
6. Long-Term Maintenance & Expansion

**Variables**: HABIT_NAME, TRACKER, FREQUENCY (Daily/Every Weekday/3x per Week/Weekly/Custom), DURATION (in days, default 90), TIME_COMMITMENT (minutes per instance), MOTIVATION (Health & Fitness/Personal Growth/Career/Relationships/Creativity/Mental Wellbeing/Productivity)

**Key Feature**: Progressive 90-day framework with trigger design, obstacle planning, and streak counting

#### Workflow 11: Achieve Major Goals

```bash
# Preview the goal achievement template
🔮 > MISSION TEMPLATE goal-achievement

# Train for half marathon
🔮 > MISSION CREATE --template goal-achievement --id half-marathon \
       --vars "GOAL=Complete a half marathon in under 2 hours,ACHIEVER=Jordan Lee,TIMEFRAME=6 Months,GOAL_TYPE=Health/Fitness,MEASUREMENT=Official race completion time and distance,DIFFICULTY=Challenging"

# Or launch side business
🔮 > MISSION CREATE --template goal-achievement --id course-business \
       --vars "GOAL=Launch online course business generating $5,000 monthly revenue,ACHIEVER=Taylor Martinez,TIMEFRAME=1 Year,GOAL_TYPE=Career/Professional,MEASUREMENT=Monthly recurring revenue of $5,000+,DIFFICULTY=Very Ambitious"

# Begin goal pursuit
🔮 > MISSION START half-marathon
```

**Goal Achievement Template Structure** (6 moves, 27 steps):
1. Goal Clarity & Vision
2. Milestone Planning & Roadmap
3. Launch & First Milestone
4. Middle Milestones & Momentum
5. Final Push & Goal Achievement
6. Reflection & Integration

**Variables**: GOAL (specific achievement), ACHIEVER, TIMEFRAME (30 Days/90 Days/6 Months/1 Year/Custom), GOAL_TYPE (Career/Financial/Health/Learning/Creative/Relationships/Personal Growth/Adventure), MEASUREMENT (success criteria), DIFFICULTY (Comfortable Stretch/Challenging/Very Ambitious/Moonshot)

**Key Feature**: Milestone-based progression with action planning, celebration points, and identity integration

#### Workflow 12: Develop Journaling Practice

```bash
# Preview the journaling template
🔮 > MISSION TEMPLATE journal-reflection

# Start gratitude journal
🔮 > MISSION CREATE --template journal-reflection --id morning-gratitude \
       --vars "JOURNAL_NAME=Morning Light Journal,JOURNALER=Casey Williams,FREQUENCY=Daily,JOURNAL_FOCUS=Gratitude & Positivity,DURATION=90,ENTRY_LENGTH=Short (0.5 page)"

# Or weekly personal growth journal
🔮 > MISSION CREATE --template journal-reflection --id growth-chronicle \
       --vars "JOURNAL_NAME=Evolution Journal,JOURNALER=Morgan Chen,FREQUENCY=Weekly,JOURNAL_FOCUS=Personal Growth,DURATION=365,ENTRY_LENGTH=Long (3-5 pages)"

# Begin journaling
🔮 > MISSION START morning-gratitude
```

**Journal & Reflection Template Structure** (6 moves, 25 steps):
1. Journal Foundation & Setup
2. Daily Practice Establishment (Days 1-14)
3. Depth & Discovery (Days 15-30)
4. Integration & Experimentation (Days 31-60)
5. Mastery & Long-term Vision (Days 61-90)
6. Lifelong Practice Design

**Variables**: JOURNAL_NAME, JOURNALER, FREQUENCY (Daily/3-5x per Week/Weekly/Monthly/Custom), JOURNAL_FOCUS (Personal Growth/Gratitude/Goal Tracking/Creative/Emotional Processing/Life Documentation/Problem Solving/General Reflection), DURATION (days), ENTRY_LENGTH (Short/Medium/Long/Stream of Consciousness)

**Key Feature**: Structured prompts, weekly/monthly reviews, and progressive depth from beginner to lifelong journaler

#### Workflow 13: Build Personal Knowledge Base

```bash
# Preview the knowledge expansion template
🔮 > MISSION TEMPLATE knowledge-expansion

# Master digital photography
🔮 > MISSION CREATE --template knowledge-expansion --id photo-mastery \
       --vars "TOPIC=Digital Photography,LEARNER=Riley Martinez,DEPTH_GOAL=Proficient (can teach others),TIMEFRAME=6 Months (Comprehensive),APPLICATION=Creative Work,LEARNING_STYLE=Balanced"

# Or understand climate science
🔮 > MISSION CREATE --template knowledge-expansion --id climate-knowledge \
       --vars "TOPIC=Climate Science,LEARNER=Alex Chen,DEPTH_GOAL=Working Knowledge (practical understanding),TIMEFRAME=3 Months (Deep Dive),APPLICATION=Pure Interest/Curiosity,LEARNING_STYLE=Reading-Heavy (books, articles, papers)"

# Start learning
🔮 > MISSION START photo-mastery
```

**Knowledge Expansion Template Structure** (5 moves, 28 steps):
1. Knowledge Mapping & Foundation
2. Core Concept Acquisition
3. Knowledge Expansion & Depth
4. Synthesis & Original Thinking
5. Maintenance & Continued Growth

**Variables**: TOPIC (subject to master), LEARNER, DEPTH_GOAL (Working Knowledge/Proficient/Expert/Authority), TIMEFRAME (1 Month/3 Months/6 Months/1 Year/Ongoing), APPLICATION (Career/Personal Project/Teaching/Creative/Problem Solving/Pure Interest/Writing), LEARNING_STYLE (Reading-Heavy/Practice-Focused/Social Learning/Balanced)

**Key Feature**: Systematic knowledge building from foundational mapping to original contributions, with knowledge management system setup

### Template Best Practices

#### Choosing the Right Template

**Creative Writing** (5 templates):
- **Novel Template**: Long-form fiction (50k+ words, 7 moves, 35 steps)
- **Play Template**: Stage drama/comedy (8 moves, 54 steps) - dialogue-driven theatrical work
- **Musical Template**: Musical theater (8 moves, 55 steps) - integrates book, music, lyrics
- **Screenplay Template**: Film/TV scripts (8 moves, 52 steps) - visual storytelling format
- **Poetry Collection Template**: Curated anthology (7 moves, 45 steps) - unified poetic vision

**Research & Learning** (4 templates):
- **Research Topic Template**: Academic/personal research (8 moves, 44 steps) - rigorous methodology with citations
- **Explore Subject Template**: Learn any subject (5 moves, 26 steps) - adaptable depth and learning style
- **Learn to Code Template**: Programming skills (8 moves, 40 steps) - includes uCODE focus for uDOS users
- **Language Learning Template**: Foreign language (6 moves, 31 steps) - CEFR-aligned with cultural awareness

**Personal Development & Knowledge** (4 templates):
- **Habit Tracking Template**: Build consistent habits (6 moves, 26 steps) - 90-day framework with trigger design
- **Goal Achievement Template**: Achieve major goals (6 moves, 27 steps) - milestone-based with action planning
- **Journal & Reflection Template**: Develop journaling practice (6 moves, 25 steps) - structured prompts and reviews
- **Knowledge Expansion Template**: Build knowledge base (5 moves, 28 steps) - systematic learning to expertise

#### Customizing Templates

**Do**:
- ✅ Use `--title` to override template title
- ✅ Use `--desc` to add custom description
- ✅ Adjust optional variables to your needs
- ✅ Review template preview before creating

**Don't**:
- ❌ Skip required variables (validation will fail)
- ❌ Use invalid choice values (e.g., "Fiction" when only "Fantasy" is allowed)
- ❌ Ignore the template structure - it's designed for success

#### Managing Template-Based Missions

```bash
# Template missions work like any other mission
🔮 > MISSION START my-novel
🔮 > MISSION PAUSE my-novel
🔮 > MISSION RESUME my-novel
🔮 > MISSION STATUS my-novel
🔮 > MISSION COMPLETE my-novel

# List all missions (including template-based)
🔮 > MISSION LIST

# Clone a template-based mission
🔮 > MISSION CLONE my-novel sequel-novel
```

### Creating Your Own Templates

See the **[Template Creation Guide](../sandbox/docs/template-creation-guide.md)** for:
- Template file structure
- Variable types and validation
- Move and step best practices
- Testing templates
- Contributing templates to uDOS

**Quick Template Anatomy**:
```json
{
  "id": "template-id",
  "name": "Template Name with {{VARIABLES}}",
  "category": "creative-writing",
  "variables": {
    "VARIABLE_NAME": {
      "type": "string|number|choice|boolean",
      "required": true,
      "description": "What this variable represents"
    }
  },
  "moves": [
    {
      "name": "Move Name",
      "steps": [
        {"description": "Step with {{VARIABLE}} substitution"}
      ]
    }
  ]
}
```

### Troubleshooting

#### Common Issues

**Problem**: "Template not found"
```bash
# Solution: List available templates
🔮 > MISSION TEMPLATES
```

**Problem**: "Variable validation failed"
```bash
# Solution: Preview template to see required variables
🔮 > MISSION TEMPLATE novel

# Then provide all required variables
🔮 > MISSION CREATE --template novel --id my-novel \
       --vars "NOVEL_TITLE=My Book,AUTHOR_NAME=Me,GENRE=Fantasy"
```

**Problem**: "Variable must be one of: Fantasy, Sci-Fi..."
```bash
# Solution: Use exact choice values from template
🔮 > MISSION TEMPLATE novel  # See valid choices
# Use "Sci-Fi" not "Science Fiction"
```

#### Getting Help

```bash
# See all mission commands including templates
🔮 > MISSION HELP

# Preview template for variable requirements
🔮 > MISSION TEMPLATE <template-id>

# Check template creation guide
🔮 > VIEW sandbox/docs/template-creation-guide.md
```

### Template Roadmap

**v1.1.3 Move 1** ✅ (Complete):
- Template engine
- Novel template
- Command interface

**v1.1.3 Move 2** ✅ (Complete):
- Play template (Drama/Comedy/Tragedy)
- Musical template (Broadway/Rock/Operetta)
- Screenplay template (Feature/TV/Short)
- Poetry collection template (Free Verse/Formal/Mixed)

**v1.1.3 Move 3** ✅ (Complete):
- Research topic template (Academic/Personal research)
- Explore subject template (Learning any subject)
- Learn to code template (Programming with uCODE focus)
- Language learning template (Foreign language study)

**v1.1.3 Move 4** ✅ (Complete):
- Habit tracking template (90-day habit building)
- Goal achievement template (Milestone-based goals)
- Journal & reflection template (Journaling practice)
- Knowledge expansion template (Personal knowledge base)

**Total Available Templates**: 13 templates
- 5 creative writing templates (novel, play, musical, screenplay, poetry)
- 4 research & learning templates (research, explore, code, language)
- 4 personal development & knowledge templates (habit, goal, journal, knowledge)

---

## Workflow Templates

### Quick Start Templates

#### New Project Template

```bash
# Create new project structure
🔮 > MKDIR sandbox/projects/project-name
🔮 > MKDIR sandbox/projects/project-name/docs
🔮 > MKDIR sandbox/projects/project-name/code
🔮 > MKDIR sandbox/projects/project-name/research

# Create README
🔮 > EDIT sandbox/projects/project-name/README.md
```

#### Research Project Template

```bash
# Research structure
🔮 > MKDIR sandbox/research/topic
🔮 > EDIT sandbox/research/topic/questions.md
🔮 > EDIT sandbox/research/topic/sources.md
🔮 > EDIT sandbox/research/topic/notes.md
```

#### Writing Project Template

```bash
# Writing structure
🔮 > MKDIR sandbox/writing/piece-name
🔮 > EDIT sandbox/writing/piece-name/outline.md
🔮 > EDIT sandbox/writing/piece-name/draft.md
🔮 > EDIT sandbox/writing/piece-name/final.md
```

---

## Related Documentation

- **[Command Reference](Command-Reference.md)** - All uDOS commands
- **[uCODE Language](uCODE-Language.md)** - Scripting reference
- **[Getting Started](Getting-Started.md)** - Beginner guide
- **[Knowledge System](Knowledge-System.md)** - Organizing knowledge

---

## Contributing Workflows

Have a workflow that works well for you? Share it!

1. Document your workflow with step-by-step instructions
2. Include examples and tips
3. Submit to the wiki or open a discussion
4. Help others be productive with uDOS

---

**Last Updated**: November 16, 2025
**Version**: v1.2.20 ✅ COMPLETE

**Remember**: Workflows evolve. Start with these, adapt them to your needs, and create your own. The best workflow is the one you'll actually use.

**v1.1.3 Achievement**: 13 mission templates across 4 categories, enabling structured approaches to creative writing, learning, personal development, and knowledge building.
