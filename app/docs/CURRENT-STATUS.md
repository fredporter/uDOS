# uMarkdown App - Current Status

**Date:** 2026-01-15  
**Version:** v1.0.0.0 (Alpha)  
**Status:** 🟡 In Development

---

## ✅ What's Complete

### Core Infrastructure

- ✅ Tauri + Svelte + Tailwind setup complete
- ✅ Basic app scaffold with components:
  - `BinderNav.svelte` — Sidebar navigation
  - `MarkdownEditor.svelte` — Text editor
  - `Preview.svelte` — Markdown preview
  - `SyncIndicator.svelte` — Sync status
- ✅ Typo cloned in `/library/ucode/typo` (v2.0.0)
- ✅ Version management system in place
- ✅ Development environment configured
- ✅ Build scripts operational (`npm run tauri:dev`)

### Dependencies

- ✅ Svelte 4.2.0
- ✅ Tailwind CSS 3.4.1
- ✅ Tauri 2.x
- ✅ TypeScript 5.6.2

---

## 🔧 Current Implementation State

### What Exists (Needs Review/Integration)

1. **App Structure:** Basic layout with header, binder sidebar, split editor/preview
2. **Styling:** Basic Tailwind config with brand colors, but NOT using Typo patterns yet
3. **Components:** Four components created but not following mdk- naming convention
4. **CSS:** Currently using basic styles.css (117 lines) with Vite defaults

### What's Missing (Priority Tasks)

#### High Priority

1. **Typo Integration**

   - [ ] Study Typo's actual implementation in `/library/ucode/typo/src`
   - [ ] Port Typo's editor component
   - [ ] Port Typo's preview rendering
   - [ ] Integrate Typo's bottom bar with font toggles

2. **Style System Overhaul**

   - [ ] Replace `src/styles.css` with proper `@layer` structure
   - [ ] Add `@tailwindcss/typography` plugin
   - [ ] Implement CSS variables for 3 font families
   - [ ] Create component classes (`.mdk-*`)
   - [ ] Establish prose rendering with separate heading/body/code fonts

3. **Font Management**
   - [ ] Create Preferences panel component
   - [ ] Implement font selection from macOS system fonts
   - [ ] Add 3 font toggle buttons to bottom bar
   - [ ] Wire up font persistence (localStorage or Tauri store)

#### Medium Priority

4. **File Operations**

   - [ ] Add file/folder open buttons to toolbar
   - [ ] Implement Mac Finder integration via Tauri
   - [ ] Add folder navigation (auto-open README.md or first .md)
   - [ ] Support multiple file types (.txt, .sh, .py)

5. **Component Refactoring**
   - [ ] Rename components to follow mdk- convention
   - [ ] Split UI into modular pieces (toolbar, bottom-bar, etc)
   - [ ] Extract reusable button/panel components

#### Lower Priority

6. **Polish & Features**
   - [ ] Keyboard shortcuts
   - [ ] Theme switching (if applicable)
   - [ ] Save/autosave functionality
   - [ ] Recent files list

---

## 🎯 Immediate Next Steps

### Step 1: Study Typo Implementation (30 min)

```bash
cd /Users/fredbook/Code/uDOS/library/ucode/typo
# Review these files:
# - src/routes/+page.svelte (main editor layout)
# - src/lib/components/* (editor, preview, controls)
# - src/app.css (styling approach)
```

**Goal:** Understand Typo's architecture before integrating

### Step 2: Install Tailwind Typography (5 min)

```bash
cd /Users/fredbook/Code/uDOS/app
npm install -D @tailwindcss/typography
```

Update `tailwind.config.js`:

```javascript
plugins: [
  require('@tailwindcss/typography'),
],
```

### Step 3: Overhaul styles.css (30 min)

Create new structure following STYLE-GUIDE.md:

- Add `@layer base/components/utilities`
- Add CSS variables for fonts
- Create `.mdk-*` component classes
- Add prose overrides for heading/body/code fonts

### Step 4: Create Preferences Component (1 hour)

Build `src/components/Preferences.svelte`:

- Font selection dropdowns (heading, body, code)
- Query macOS system fonts via Tauri
- Persist to localStorage
- Apply fonts via CSS variable updates

### Step 5: Build Bottom Bar with Font Toggles (1 hour)

Create `src/components/BottomBar.svelte`:

- 3 toggle buttons (heading, body, code)
- Wire to CSS variables
- Show active state
- Include Typo's existing size toggles

---

## 📂 File Structure (Current)

```
/Users/fredbook/Code/uDOS/app/
├── docs/
│   ├── STYLE-GUIDE.md        ← JUST CREATED
│   └── CURRENT-STATUS.md     ← THIS FILE
├── src/
│   ├── App.svelte            ← Main app (needs refactor)
│   ├── styles.css            ← NEEDS OVERHAUL
│   ├── components/
│   │   ├── BinderNav.svelte
│   │   ├── MarkdownEditor.svelte
│   │   ├── Preview.svelte
│   │   └── SyncIndicator.svelte
│   ├── lib/
│   │   └── api.ts
│   └── stores/
├── tailwind.config.js        ← NEEDS @tailwindcss/typography
├── package.json
└── ...
```

---

## 🔗 Key References

### Internal Docs

- [STYLE-GUIDE.md](./STYLE-GUIDE.md) — Comprehensive class naming guide
- [/docs/roadmap.md](../../docs/roadmap.md) — Project roadmap
- [AGENTS.md](../../AGENTS.md) — Architecture & boundaries

### Typo Resources

- **Live Demo:** https://typo.robino.dev/
- **Source:** `/library/ucode/typo/` (cloned locally)
- **Repo:** https://github.com/rossrobino/typo

### External Docs

- **Svelte:** https://svelte.dev/docs/kit/introduction
- **Tailwind:** https://tailwindcss.com/docs/installation/using-vite
- **Tailwind Typography:** https://tailwindcss.com/docs/typography-plugin

---

## 🚨 Known Issues

1. **Dependency mismatch:** Typo uses Tailwind v4, we're on v3
   - **Action:** Keep v3 for stability, port patterns not version
2. **npm install errors:** Fixed with `--legacy-peer-deps`
   - **Status:** Resolved
3. **Tauri dev not starting:** Fixed after npm install
   - **Status:** Resolved

---

## 💡 Design Decisions

### Why mdk- prefix?

- **M**ark**d**own (internal name)
- **K**it (SvelteKit convention)
- Unique, semantic, won't conflict with Typo classes

### Why separate heading/body/code fonts?

- Professional editors (VS Code, iA Writer) allow this
- Common user request for accessibility
- Enables mixing serif headings with sans body

### Why keep Typo as-is?

- Proven UX (clean, minimal, fast)
- Active development
- SvelteKit + Tailwind aligned with our stack

---

## 🎓 Learning Resources

If you're new to the stack:

1. **Svelte Basics:** https://svelte.dev/tutorial/basics
2. **SvelteKit Routing:** https://kit.svelte.dev/docs/routing
3. **Tailwind @layer:** https://tailwindcss.com/docs/adding-custom-styles#using-css-and-layer
4. **Tauri Guides:** https://tauri.app/v2/guides/

---

## 📊 Progress Tracking

| Area               | Status         | Progress |
| ------------------ | -------------- | -------- |
| Infrastructure     | ✅ Complete    | 100%     |
| Typo Integration   | 🔴 Not Started | 0%       |
| Style System       | 🟡 Planning    | 10%      |
| Font Management    | 🔴 Not Started | 0%       |
| File Operations    | 🔴 Not Started | 0%       |
| Component Refactor | 🟡 Partial     | 25%      |

**Overall:** ~15% complete

---

## 🤝 Next Collaborator Handoff

When picking this up:

1. **Read:** STYLE-GUIDE.md (comprehensive patterns)
2. **Study:** Typo source in `/library/ucode/typo/src`
3. **Install:** `@tailwindcss/typography`
4. **Start:** Overhaul `styles.css` with proper layers
5. **Build:** Preferences component first (it's foundational)

---

_Updated: 2026-01-15 by GitHub Copilot_
