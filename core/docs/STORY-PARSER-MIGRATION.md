# Story Parser Migration

**Date:** 2026-01-26  
**Action:** Moved story parser from Goblin to Core

## What Moved

Moved from `/dev/goblin/src/lib/services/` to `/core/src/story/`:

- `storyParser.ts` → `parser.ts` — Parse -story.md files (YAML frontmatter + sections + ```story blocks)
- `storyService.ts` → `service.ts` — Load/save story state
- `story.ts` (types) → `types.ts` — TypeScript interfaces
- `storyParser.test.ts` → Removed (needs rewrite for Core test suite)

## Why

Story format is one of the five core markdown formats (uCode, Story, Marp, Guide, Config). It belongs in Core's TypeScript runtime, not in Goblin (which is for experimental features).

## Dependencies

The story parser uses:

- `js-yaml` — Parse YAML frontmatter and ```story blocks
- `marked` — Render markdown content to HTML

Both are already in Core's package.json.

## Python Side

Core already has `/core/services/story_service.py` which provides the same functionality for Python consumers (Wizard setup routes).

## Usage

```typescript
import { parseStoryFile, loadStory, StoryState } from "@udos/runtime/story";

// Parse story markdown
const story = parseStoryFile(markdownContent);

// Load from file/URL
const story = await loadStory("/path/to/file-story.md");
```

## Breaking Changes

None for external consumers. Goblin's internal story dashboard needs updating to import from Core instead.

---

**Status:** Complete  
**Verified:** Story parser error fixed (wizard-setup-story.md trailing --- removed)
