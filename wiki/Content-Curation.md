# Content Curation Guide

**Building and maintaining The People's Knowledge Commons**

This guide explains how to find, evaluate, collect, curate, and maintain high-quality knowledge for the uDOS knowledge library.

---

## Table of Contents

1. [Foraging: Finding Quality Content](#foraging-finding-quality-content)
2. [Research Protocols: Evaluating Sources](#research-protocols-evaluating-sources)
3. [Collection: Converting to Markdown](#collection-converting-to-markdown)
4. [Curation: Quality Standards](#curation-quality-standards)
5. [Archival: File Naming & Organization](#archival-file-naming--organization)
6. [Maintenance: Review & Updates](#maintenance-review--updates)
7. [Community Contribution](#community-contribution)

---

## Foraging: Finding Quality Content

### What to Look For

**High-value knowledge has these characteristics**:
- ✅ **Practical** - Can be applied immediately
- ✅ **Evidence-based** - Backed by research or proven experience
- ✅ **Timeless** - Remains relevant for years
- ✅ **Accessible** - Beginners can understand with effort
- ✅ **Complete** - Provides full context and steps
- ✅ **Accurate** - Factually correct and up-to-date

### Where to Search

#### Primary Sources (Best)
- **Academic research** - PubMed, Google Scholar, university publications
- **Official documentation** - Government agencies (CDC, USDA, etc.)
- **Professional organizations** - Red Cross, industry associations
- **Open textbooks** - OpenStax, MIT OpenCourseWare
- **Reputable non-profits** - Khan Academy, Wikipedia (with verification)

#### Secondary Sources (Use Critically)
- **Popular science books** - Check author credentials
- **Educational blogs** - Verify against primary sources
- **YouTube tutorials** - Quality varies, verify information
- **Forums and Q&A** - Good for practical tips, verify everything

#### Avoid
- ❌ Clickbait articles
- ❌ Unverified social media posts
- ❌ Paywalled or proprietary content
- ❌ Political or divisive content
- ❌ Corporate marketing disguised as information
- ❌ Pseudoscience and unfounded claims

### Research Strategy

1. **Start with broad overview** - Wikipedia is good for this
2. **Identify key concepts** - What are the fundamentals?
3. **Find primary sources** - Trace back to original research
4. **Cross-reference** - Verify information across multiple sources
5. **Check currency** - Is this information still current?

### Example: Foraging for CPR Knowledge

```
Goal: Create comprehensive CPR guide

Step 1: Overview
- Read Wikipedia article on CPR
- Identify key concepts: chest compressions, rescue breaths, AED

Step 2: Primary Sources
- American Red Cross official guidelines
- American Heart Association standards
- PubMed research on CPR effectiveness

Step 3: Cross-Reference
- Compare Red Cross vs AHA recommendations
- Check international standards (European Resuscitation Council)
- Verify compression depth, rate, technique

Step 4: Currency Check
- When were guidelines last updated? (Every 5 years typically)
- Are there new recommendations?

Step 5: Collect
- Save PDF guidelines
- Extract key information
- Note sources for citation
```

---

## Research Protocols: Evaluating Sources

### The CRAAP Test

Evaluate sources using these criteria:

#### Currency
- **When** was it published/updated?
- Is the information **still accurate**?
- Are there **newer guidelines** or research?

#### Relevance
- Does this **match my topic**?
- Is it the **right depth** (beginner vs advanced)?
- Will users **actually need** this information?

#### Authority
- **Who** wrote this?
- What are their **credentials**?
- Is the publisher **reputable**?
- Can I **verify** their expertise?

#### Accuracy
- Is information **supported by evidence**?
- Can I **verify** facts from other sources?
- Are there **citations** for claims?
- Is it **free from bias**?

#### Purpose
- Why does this exist?
- Is it **educational** or marketing?
- Are there **conflicts of interest**?
- Is it **objective** or opinionated?

### Red Flags

⚠️ **Be skeptical if**:
- No author or credentials listed
- Excessive use of superlatives ("amazing!", "best ever!")
- Miracle cures or too-good-to-be-true claims
- Heavy advertising or affiliate links
- Outdated information presented as current
- No citations or sources provided
- Sensationalist language or fear-mongering
- Promotes specific products or services

### Verification Checklist

Before accepting information:

- [ ] **Author verified** - Real person, relevant credentials
- [ ] **Publisher verified** - Reputable organization or institution
- [ ] **Date verified** - Recent or timeless information
- [ ] **Facts checked** - Cross-referenced with 2+ other sources
- [ ] **Bias assessed** - Conflicts of interest noted
- [ ] **Citations present** - Claims are sourced
- [ ] **Practical** - Can be applied in real world
- [ ] **Safe** - No dangerous or risky advice without warnings

---

## Collection: Converting to Markdown

### Extraction Methods

#### From Webpages

**Option 1: Manual extraction (best)**
```bash
# In uDOS (if web extension loaded)
🔮 > WEB https://example.com/article
🔮 > WEB EXTRACT output/article-draft.md
```

**Option 2: Copy and paste**
1. Select article text
2. Copy to clipboard
3. Paste into text editor
4. Clean up formatting

**Option 3: Command-line tools**
```bash
# Using pandoc (if installed)
pandoc -f html -t markdown input.html -o output.md

# Using wget + html2text
wget https://example.com/article -O temp.html
html2text temp.html > article.md
```

#### From PDFs

```bash
# Using pdftotext
pdftotext document.pdf output.txt

# Then manually convert to Markdown
```

#### From Videos

1. **Watch and take notes manually** (best for comprehension)
2. Use auto-generated captions (if available)
3. Summarize key points in your own words

### Markdown Conversion Standards

Convert content to clean Markdown:

```markdown
# Main Title

**Category**: Knowledge Category > Subcategory
**Source**: Original URL or citation
**Last Updated**: YYYY-MM-DD
**Author**: Original author (if known)

> Optional: Brief description or key takeaway

## Section Title

Content goes here with **bold** and *italic* emphasis.

### Subsection

- Bulleted lists
- For key points

1. Numbered lists
2. For sequential steps

### Code Examples (if relevant)

```language
code here
```

### Images/Diagrams

Since uDOS is text-first, convert visual information to:
- ASCII diagrams
- Detailed descriptions
- Structured tables
- Step-by-step text

### Links and References

- [Link Text](URL)
- [Related Document](../category/other-doc.md)
```

### Example Conversion

**Original HTML**:
```html
<h1>How to Make Fire</h1>
<p>Making fire requires three things: <b>fuel</b>, <b>heat</b>, and <b>oxygen</b>.</p>
<ol>
  <li>Gather dry tinder</li>
  <li>Create a spark</li>
  <li>Blow gently to add oxygen</li>
</ol>
```

**Converted Markdown**:
```markdown
# How to Make Fire

**Category**: Survival > Tools
**Source**: https://example.com/fire-making
**Last Updated**: 2025-11-14

Making fire requires three things: **fuel**, **heat**, and **oxygen**.

## Steps

1. **Gather dry tinder** - Small, easily ignitable material
2. **Create a spark** - Using friction, flint, or fire starter
3. **Blow gently** - Add oxygen to help flame catch
```

---

## Curation: Quality Standards

### Content Must Be

#### 1. Practical
- Can someone **actually use** this information?
- Are there **clear steps** or instructions?
- Is it **actionable** today?

**Good**: "To purify water, boil for 1 minute at sea level, 3 minutes above 5,000 feet."
**Bad**: "Water purification is important for health."

#### 2. Accurate
- **Fact-checked** against reliable sources
- **Up-to-date** with current best practices
- **Properly cited** when making claims

#### 3. Complete
- Provides **full context** needed to understand
- Doesn't require external knowledge not provided
- Includes **warnings** and **limitations**

#### 4. Accessible
- Written in **plain language**
- **Jargon explained** when necessary
- **Progressive disclosure** - simple first, complex later
- **Suitable for beginners** with clear path to advanced

#### 5. Well-Organized
- **Logical structure** (overview → details → examples)
- **Scannable** with headers and lists
- **Cross-referenced** to related topics
- **Navigable** with table of contents

### Writing Guidelines

#### Clarity Over Cleverness
```
❌ "Aqueous liberation techniques can facilitate beverage temperature modification."
✅ "Boiling water makes it safe to drink."
```

#### Action Over Theory
```
❌ "Understanding the principles of combustion is essential..."
✅ "To start a fire: 1. Gather tinder, 2. Create spark, 3. Add fuel."
```

#### Specific Over General
```
❌ "Compress the chest firmly."
✅ "Compress chest at least 2 inches deep (5 cm) for adults."
```

#### Show Over Tell
```
❌ "Many people use the Pomodoro technique."
✅ "Pomodoro technique: Work 25 minutes, break 5 minutes, repeat."
```

### Quality Checklist

Before publishing knowledge, verify:

- [ ] **Accurate** - Facts verified from reliable sources
- [ ] **Complete** - All necessary context provided
- [ ] **Clear** - Plain language, jargon explained
- [ ] **Practical** - Can be applied immediately
- [ ] **Safe** - Warnings included for risks
- [ ] **Organized** - Logical structure, scannable
- [ ] **Cited** - Sources linked or referenced
- [ ] **Current** - Information is up-to-date
- [ ] **Accessible** - Beginners can understand
- [ ] **Proofread** - No typos or grammatical errors

---

## Archival: File Naming & Organization

### File Naming Conventions

**Format**: `descriptive-name.md`

**Rules**:
- **Lowercase** only
- **Hyphens** for spaces (not underscores)
- **Descriptive** but concise (3-5 words ideal)
- **No dates** in filename (use frontmatter)
- **No version numbers** (use git for versioning)

**Good Examples**:
- `basic-cpr.md`
- `water-purification-methods.md`
- `pomodoro-technique.md`
- `square-foot-gardening.md`

**Bad Examples**:
- `Untitled.md` (not descriptive)
- `CPR_GUIDE_v2_FINAL.md` (uppercase, underscores, version)
- `2025-11-14-notes.md` (date in filename)
- `stuff.md` (meaningless)

### Directory Organization

Follow the established knowledge architecture:

```
knowledge/
├── [category]/
│   ├── README.md (explains category)
│   └── [subcategory]/
│       └── document-name.md
```

**Example**:
```
knowledge/
├── survival/
│   ├── README.md
│   ├── first-aid/
│   │   ├── basic-cpr.md
│   │   ├── choking-heimlich.md
│   │   └── wound-care.md
│   └── food-water/
│       ├── water-purification.md
│       └── emergency-food-storage.md
```

### Frontmatter Template

Every knowledge document should start with metadata:

```markdown
# Document Title

**Category**: Main Category > Subcategory
**Last Updated**: YYYY-MM-DD
**Author**: Original author (if applicable)
**Source**: URL or citation
**Status**: Draft | Review | Published

> Brief summary of what this document covers (1-2 sentences)

---

## Content begins here...
```

### When to Create New Documents vs Update Existing

**Create new document when**:
- Topic is **distinct** from existing content
- Document would be **too long** if combined (over 1000 lines)
- Information applies to **different audience** (beginner vs advanced)

**Update existing document when**:
- Information is **closely related**
- Document is **incomplete** without this addition
- Adding **recent updates** to existing topic

---

## Maintenance: Review & Updates

### Review Schedule

**Monthly**: Check recent additions
- Proofread for errors
- Verify links still work
- Ensure formatting is consistent

**Quarterly**: Review by category
- Check for outdated information
- Identify gaps in coverage
- Plan new content based on gaps

**Annually**: Major review
- Update all time-sensitive information
- Remove or archive obsolete content
- Reorganize if structure has issues
- Update references and citations

### Update Process

When updating existing documents:

1. **Note what changed**
   ```markdown
   **Last Updated**: 2025-11-14
   **Change Log**:
   - 2025-11-14: Updated CPR compression rate to match 2025 guidelines
   - 2025-06-01: Added section on AED usage
   ```

2. **Update Last Updated date**

3. **Test any instructions** if possible

4. **Commit with clear message**
   ```bash
   git commit -m "docs: Update CPR guidelines to 2025 standards"
   ```

### Identifying Outdated Content

**Signs content needs updating**:
- Medical/safety guidelines more than 5 years old
- Technology references more than 2 years old
- Broken links
- Comments from users noting inaccuracies
- Newer research contradicts existing information

### Archiving Obsolete Content

When information is no longer relevant:

```bash
# Don't delete - move to archive
mv knowledge/category/obsolete-doc.md knowledge/archive/

# Add archive notice
echo "# ARCHIVED - See [new-doc.md](../category/new-doc.md)" > knowledge/category/obsolete-doc.md
```

---

## Community Contribution

### How Anyone Can Contribute

#### 1. Submit New Content

**Via GitHub**:
1. Fork the repository
2. Add content following guidelines above
3. Submit pull request
4. Maintainers review and merge

**Via Discussion**:
1. Open GitHub discussion
2. Share your knowledge or found resource
3. Maintainers can help format and add

#### 2. Improve Existing Content

- Fix typos or errors
- Add missing information
- Update outdated content
- Improve clarity or examples
- Add cross-references

#### 3. Identify Gaps

Open issues for:
- Missing topics that should be covered
- Categories that need expansion
- Outdated information needing updates

### Contribution Guidelines

**Before contributing**:
- Read [Philosophy](Philosophy.md) - Understand what uDOS values
- Read [Knowledge System](Knowledge-System.md) - Organization system
- Check existing content - Avoid duplicates
- Verify information - Cite sources

**When writing**:
- Follow quality standards above
- Use templates provided
- Write for beginners first
- Include examples
- Cite sources

**Submitting**:
- Clear pull request description
- Explain what you added/changed and why
- Link to sources if applicable
- Be open to feedback

### Community Standards

**We welcome**:
- ✅ Practical, tested knowledge
- ✅ Clear, accessible writing
- ✅ Constructive feedback
- ✅ Diverse perspectives and experiences
- ✅ Regional variations and adaptations

**We don't accept**:
- ❌ Unverified or dangerous advice
- ❌ Political or divisive content
- ❌ Marketing or promotional content
- ❌ Plagiarized content
- ❌ Paywalled or proprietary information
- ❌ Content violating copyright

### Recognition

Contributors are credited in:
- **Git commit history** - Your name on every contribution
- **CREDITS.md** - List of all contributors
- **Document frontmatter** - "Contributed by" when appropriate

---

## Curation Workflow Summary

```
1. FORAGE
   ├─ Identify knowledge gap
   ├─ Search for quality sources
   └─ Evaluate with CRAAP test

2. RESEARCH
   ├─ Verify against multiple sources
   ├─ Check author credentials
   └─ Note sources for citation

3. COLLECT
   ├─ Extract content
   ├─ Convert to Markdown
   └─ Add metadata/frontmatter

4. CURATE
   ├─ Apply quality standards
   ├─ Edit for clarity
   ├─ Add examples and warnings
   └─ Cross-reference related topics

5. ORGANIZE
   ├─ Choose correct category
   ├─ Follow naming conventions
   └─ Update category README if needed

6. REVIEW
   ├─ Quality checklist
   ├─ Peer review (if available)
   └─ Test instructions (if applicable)

7. PUBLISH
   ├─ Commit to repository
   ├─ Update documentation index
   └─ Share with community

8. MAINTAIN
   ├─ Monthly: Check recent additions
   ├─ Quarterly: Review category
   └─ Annually: Major review and updates
```

---

## Tools and Resources

### Markdown Editors
- **nano** - Simple terminal editor (built-in)
- **vim** - Powerful terminal editor
- **VSCode** - Modern GUI editor
- **Typora** - WYSIWYG Markdown editor

### Conversion Tools
- **pandoc** - Universal document converter
- **html2text** - HTML to Markdown
- **pdftotext** - PDF to text

### Verification Tools
- **Google Scholar** - Academic research
- **Internet Archive** - Archived webpages
- **Snopes** - Fact-checking
- **MediaBias/FactCheck** - Source reliability

### Version Control
- **git** - Track changes over time
- **GitHub** - Collaboration platform
- **git diff** - See what changed

---

## Examples

### Example: Full Curation Process

**Goal**: Create guide on composting

**1. Forage** (30 min)
- Search: "composting basics" "how to compost" "composting science"
- Found: EPA guide, university extension articles, composting books
- Evaluated sources with CRAAP test

**2. Research** (1 hour)
- Cross-referenced 5 sources for accuracy
- Noted different methods (hot vs cold composting)
- Verified ratios (browns vs greens)
- Checked for regional variations

**3. Collect** (30 min)
- Extracted key information from each source
- Took notes in own words
- Saved source URLs for citation

**4. Curate** (2 hours)
- Organized into logical structure
- Wrote in clear, accessible language
- Added examples and measurements
- Included warnings (what not to compost)
- Created step-by-step instructions

**5. Organize** (10 min)
- Decided on: `knowledge/environment/gardening/composting-basics.md`
- Followed naming convention
- Added frontmatter with metadata

**6. Review** (30 min)
- Ran through quality checklist
- Proofread for errors
- Verified all facts double-checked
- Asked someone to review

**7. Publish** (10 min)
- Committed to git with clear message
- Updated environment/README.md
- Announced in discussion forum

**Total time**: ~5 hours for comprehensive guide

---

## Related Documentation

- **[Knowledge System](Knowledge-System.md)** - Organization system
- **[Philosophy](Philosophy.md)** - What uDOS values
- **[Contributing](Contributing.md)** - How to contribute code/docs
- **[Workflows](Workflows.md)** - Common uDOS workflows

---

**Last Updated**: November 14, 2025
**Version**: v1.0.15

**Remember**: Curation is an ongoing process. Start with quality over quantity. One excellent, well-researched document is worth more than ten mediocre ones. The knowledge commons grows stronger through careful, thoughtful contributions.

**Your knowledge could help someone. Please share it.**
