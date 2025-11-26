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

**Last Updated**: November 14, 2025
**Version**: v1.0.0

**Remember**: Workflows evolve. Start with these, adapt them to your needs, and create your own. The best workflow is the one you'll actually use.
