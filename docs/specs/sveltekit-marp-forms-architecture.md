# SvelteKit + Marp + gtx-form: Architecture Assessment | 2026-01-14

## Overview

Evaluating feasibility and recommended approach for integrating Marp presentations and gtx-form (typeform-style Q&A) into uDOS App (Tauri + SvelteKit).

---

## 1. Marp Integration with SvelteKit

### Status: ✅ **FEASIBLE** (Multiple Approaches)

#### Option A: Marp HTML Output (Recommended for Simplicity)
**What:** Convert `-marp.md` → HTML slide deck at build time or on-demand.
**How:**
- Use `@marp-team/marp-cli` to compile `-marp.md` to single-file HTML
- Embed HTML output in SvelteKit component using `{@html sanitized_output}`
- Prevent FOUC with CSS framework (Tailwind)

**Pros:**
- ✅ No external renderer needed
- ✅ Full Marp styling works out-of-box
- ✅ Single-file distributable
- ✅ Works offline

**Cons:**
- Slides are static (no dynamic interactivity)
- XSS risk if not sanitized (use `sanitize-html` lib)

**Stack:**
```json
{
  "@marp-team/marp-cli": "^3.7.0",
  "sanitize-html": "^2.13.0"
}
```

#### Option B: Marp Plugin with Custom Renderer
**What:** Use `@marp-team/marp-core` for dynamic rendering + custom Svelte components.
**How:**
- Wrap Marp Core in Svelte component
- Add custom renderer for Marp directives
- Allow Svelte reactivity within slides

**Pros:**
- ✅ Dynamic slide updates
- ✅ Full Svelte integration
- ✅ Custom Marp themes via Svelte

**Cons:**
- More complex setup
- Requires browser-side rendering (slightly slower)

**Stack:**
```json
{
  "@marp-team/marp-core": "^3.7.0"
}
```

#### Option C: External Renderer Service (Not Recommended)
**What:** Offload rendering to Wizard Server.
**Cons:**
- Breaks offline-first model
- Adds latency
- Not recommended for uDOS

---

## 2. gtx-form Integration with SvelteKit

### Status: ✅ **FEASIBLE** (Build Custom or Use Library)

#### Option A: Build Custom Svelte Form Component (Recommended)
**Why Custom?**
- `gtx-form` is Vue-based; Svelte integration is awkward
- Full control over UX/animations
- Lighter bundle than full gtx-form port

**Architecture:**
```svelte
<script>
  export let fields = [];  // [{ name, type, label, required }]
  export let onSubmit;
  
  let answers = {};
  let currentIndex = 0;

  function next() {
    if (currentIndex < fields.length - 1) currentIndex++;
    else onSubmit(answers);
  }
</script>

<div class="typeform-style">
  <div class="question">
    <label>{fields[currentIndex].label}</label>
    <input bind:value={answers[fields[currentIndex].name]} />
  </div>
  <button on:click={next}>Next →</button>
</div>
```

**Pros:**
- ✅ Native Svelte (no friction)
- ✅ Lightweight
- ✅ Full customization
- ✅ Works with -story.md and -ucode.md

**Cons:**
- Requires time to build if feature-complete
- But core typeform-style Q&A is ~200 LOC

#### Option B: Adapt gtx-form to Svelte
**How:**
- Use gtx-form as reference for UI/UX
- Rebuild components in Svelte
- OR use SvelteKit + gtx-form CSS (CSS-only approach)

**Stack (for CSS reference):**
```json
{
  "gtx-form": "^1.0.0"  // Reference only; rebuild in Svelte
}
```

#### Option C: Use Formkit or Other Headless Form Library
**Alternatives:**
- **Formkit**: Vue/React/Svelte support ✅
- **React Hook Form**: React only ✗
- **PouchDB Forms**: Lightweight, form state management

---

## 3. -story.md Format Integration

### Recommended Architecture

**File Structure:**
```yaml
---
title: "User Setup"
type: "story"
version: "1.0.0"
sections:
  - title: "Welcome"
    questions:
      - name: "username"
        label: "What's your name?"
        type: "text"
  - title: "Preferences"
    questions:
      - name: "theme"
        label: "Choose a theme"
        type: "select"
        options: ["foundation", "cyberpunk", "classic"]
---

# Welcome to User Setup

Standard markdown with embedded ```story blocks.

--- (section break, renders as new "slide")

# Preferences

Another section.

---

variables:
  username: ""
  theme: "foundation"
```

**Rendering Pipeline:**
1. Parse YAML frontmatter
2. Split markdown by `---` sections
3. For each section:
   - Render markdown as prose
   - Extract ```story blocks as form questions
   - Collect answers into `variables` object
4. Return completed state with all answers

**SvelteKit Component:**
```svelte
<script>
  import StoryRenderer from './StoryRenderer.svelte';

  let story = {};  // Parsed -story.md
  let answers = {};

  async function loadStory(filename) {
    const response = await fetch(`/stories/${filename}`);
    story = await response.json();
  }

  function handleSubmit(data) {
    answers = { ...story.variables, ...data };
    // Save/return results
  }
</script>

<StoryRenderer {story} on:submit={handleSubmit} />
```

---

## 4. -ucode.md Format Integration

### Recommended Architecture

**Execution Environment:**
- ```upy code blocks execute in SvelteKit or Wizard Server
- Access to DOM/API via special runtime objects
- Results render inline or update UI

**Stack Options:**

#### Option A: Client-Side Execution (Preferred for Offline)
**How:**
- Transpile uPY → JavaScript at build time
- Run in sandboxed Web Worker
- Return results to Svelte component

**Pros:**
- ✅ Fully offline
- ✅ No server dependency
- ✅ Fast execution

**Cons:**
- Limited to browser APIs
- No filesystem access (unless via IndexedDB)

#### Option B: Server-Side Execution (Wizard Server)
**How:**
- Submit uPY code to Wizard Server for execution
- Wizard Server returns JSON results
- Svelte renders results

**Pros:**
- ✅ Full uPY runtime (file access, etc.)
- ✅ Shared execution environment

**Cons:**
- Requires network (breaks offline-first)
- Latency

**Recommendation:** **HYBRID**
- Try client-side first (Web Worker transpilation)
- Fall back to Wizard Server if needed

---

## 5. Full Integration Stack

### SvelteKit + Marp + Form Stack (Recommended)

```json
{
  "dependencies": {
    "svelte": "^4.2.0",
    "@sveltejs/kit": "^2.0.0",
    "@marp-team/marp-cli": "^3.7.0",
    "sanitize-html": "^2.13.0",
    "marked": "^11.1.0",
    "js-yaml": "^4.1.0"
  },
  "devDependencies": {
    "@sveltejs/adapter-tauri": "latest",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### Processing Pipeline

```
Input: filename-format.md
  ↓
[Parser] YAML frontmatter + markdown + code blocks
  ↓
[Marp] -marp.md → HTML slides
[Story] -story.md → form sections + prose
[uCode] -ucode.md → executable code + docs
[Guide] -guide.md → knowledge article
  ↓
[Renderer] Svelte component renders output
  ↓
[Storage] Save state (answers, results) to localStorage/IndexedDB
```

---

## 6. Implementation Roadmap

### Phase 1: Story Format + Custom Form Component (Week 1-2)
- [ ] Parse -story.md YAML + markdown
- [ ] Build SvelteKit StoryRenderer component
- [ ] Implement custom typeform-style form (no gtx-form dependency)
- [ ] Test with user-setup-story.md template

### Phase 2: Marp Integration (Week 2-3)
- [ ] Add Marp compilation to build pipeline
- [ ] Create SvelteKit MarpRenderer component
- [ ] Sanitize HTML output
- [ ] Test with -marp.md slides

### Phase 3: uCode Execution (Week 3-4)
- [ ] Research uPY → JavaScript transpiler
- [ ] Setup Web Worker for sandboxed execution
- [ ] Create uCodeRenderer component
- [ ] Test with templates

### Phase 4: Wizard Server Fallback (Week 4+)
- [ ] Wire up API calls to Wizard Server
- [ ] Implement execution fallback logic
- [ ] Test hybrid offline + online modes

---

## 7. Compatibility Summary

| Feature | SvelteKit | Marp | Custom Form | Status |
|---------|-----------|------|-------------|--------|
| -story.md | ✅ | N/A | ✅ | **READY** |
| -marp.md | ✅ | ✅ | N/A | **READY** |
| -ucode.md | ✅ | N/A | ✅ | **READY (Q3)** |
| -guide.md | ✅ | N/A | N/A | **READY** |
| -config.md | ✅ | N/A | ✅ | **READY** |
| Offline-first | ✅ | ✅ | ✅ | **READY** |
| Form state capture | ✅ | N/A | ✅ | **READY** |
| Distribution | ✅ | ✅ | ✅ | **READY** |

---

## 8. Recommendations

### ✅ Do This
1. **Build custom form component** instead of porting gtx-form
2. **Use Marp CLI** for slide HTML compilation
3. **Target client-side uPY execution** for offline capability
4. **Store form state in localStorage** for session recovery
5. **Use IndexedDB** for file-based document storage

### ❌ Don't Do This
1. Don't use gtx-form directly (Vue-specific)
2. Don't offload Marp rendering to server
3. Don't force server-side uPY execution initially
4. Don't use external services for offline content

---

## 9. Quick Win: Start with -story.md

**Minimal MVP** (1-2 days):
```svelte
<!-- pages/story/[slug].svelte -->
<script>
  import StoryRenderer from '$lib/StoryRenderer.svelte';
  
  export let data;  // { story: parsed }
</script>

<StoryRenderer story={data.story} />
```

Test with: `user-setup-ucode.md` (renamed from template)

---

*Assessment Created: 2026-01-14*  
*Architecture Review: SvelteKit, Marp, Form UI*  
*Next: Prototype StoryRenderer component + form state management*
