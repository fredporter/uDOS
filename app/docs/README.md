# uMarkdown App Documentation

**Navigation Guide for the uMarkdown Mac App Development**

---

## 📖 Documentation Index

| Document                                                     | Purpose                                  | When to Read            |
| ------------------------------------------------------------ | ---------------------------------------- | ----------------------- |
| **[STYLE-GUIDE.md](./STYLE-GUIDE.md)**                       | Complete class naming & CSS architecture | Reference while coding  |
| **[CURRENT-STATUS.md](./CURRENT-STATUS.md)**                 | Project status & known issues            | Starting a session      |
| **[IMPLEMENTATION-ROADMAP.md](./IMPLEMENTATION-ROADMAP.md)** | Step-by-step implementation plan         | Planning work           |
| **[VISUAL-ARCHITECTURE.md](./VISUAL-ARCHITECTURE.md)**       | Visual component hierarchy               | Understanding structure |

---

## 🎯 Quick Links by Task

### I want to understand the class naming system

→ **[STYLE-GUIDE.md](./STYLE-GUIDE.md)** Section 1, 5, 11

### I want to know what's already built

→ **[CURRENT-STATUS.md](./CURRENT-STATUS.md)** Section "What's Complete"

### I want to start coding

→ **[IMPLEMENTATION-ROADMAP.md](./IMPLEMENTATION-ROADMAP.md)** Phase 1

### I want to see the component hierarchy

→ **[VISUAL-ARCHITECTURE.md](./VISUAL-ARCHITECTURE.md)** Component Hierarchy diagram

### I want to understand the font system

→ **[STYLE-GUIDE.md](./STYLE-GUIDE.md)** Section 3, 4, 7  
→ **[VISUAL-ARCHITECTURE.md](./VISUAL-ARCHITECTURE.md)** Font System Flow

### I want to port Typo features

→ **[IMPLEMENTATION-ROADMAP.md](./IMPLEMENTATION-ROADMAP.md)** "Typo Patterns to Port"  
→ Source: `/library/ucode/typo/src/`

---

## 🏗️ Project Structure

```
uMarkdown App
├── Core: Typo (markdown editor)
├── Extensions: 3 font controls + file ops
└── Platform: Tauri + Svelte + Tailwind
```

**Key Difference from Typo:**

- Typo: 1 font toggle for entire document
- uMarkdown: 3 independent font controls (heading/body/code)

---

## 🎨 The mdk- System

**All custom classes use `mdk-` prefix** (Markdown Kit):

```css
/* Component containers */
.mdk-app
.mdk-shell
.mdk-toolbar

/* Semantic regions */
.mdk-editor
.mdk-preview
.mdk-preferences

/* Reusable UI */
.mdk-btn
.mdk-panel
.mdk-field;
```

**State classes:**

```css
.is-active    /* for toggles */
/* for toggles */
.is-disabled  /* for buttons */
.has-file; /* for app state */
```

**Data attributes for JS:**

```html
<button data-action="open-file">
  <button data-font-target="heading"></button>
</button>
```

---

## 📚 Required Reading

### Before Starting

1. [STYLE-GUIDE.md](./STYLE-GUIDE.md) — Skim sections 1-5
2. [CURRENT-STATUS.md](./CURRENT-STATUS.md) — Read "Immediate Next Steps"

### During Development

1. [IMPLEMENTATION-ROADMAP.md](./IMPLEMENTATION-ROADMAP.md) — Follow phase by phase
2. Reference [STYLE-GUIDE.md](./STYLE-GUIDE.md) section 11 (cheat sheet)

### For Architecture Questions

1. [VISUAL-ARCHITECTURE.md](./VISUAL-ARCHITECTURE.md) — Component hierarchy
2. Check Typo source: `/library/ucode/typo/src/`

---

## 🔧 Development Commands

```bash
# Start development server
cd /Users/fredbook/Code/uDOS/app
npm run tauri:dev

# Install new dependency
npm install -D @tailwindcss/typography

# Build for production
npm run tauri:build

# Check Typo reference
cd /Users/fredbook/Code/uDOS/library/ucode/typo
npm run dev  # Opens at localhost:5173
```

---

## 🎯 Implementation Phases

### Phase 1: Style System (2-3 hours)

- [ ] Install Tailwind Typography
- [ ] Overhaul styles.css with @layer structure
- [ ] Add CSS variables for fonts

### Phase 2: Components (3-4 hours)

- [ ] Create BottomBar.svelte
- [ ] Create Toolbar.svelte
- [ ] Create Preferences.svelte

### Phase 3: Integration (2 hours)

- [ ] Refactor App.svelte
- [ ] Test all features
- [ ] Polish UI

**Total estimated time:** 7-9 hours

---

## 🚨 Common Pitfalls

### 1. Forgetting mdk- prefix

❌ `<div class="preview">`  
✅ `<div class="mdk-preview">`

### 2. Hardcoding fonts instead of using variables

❌ `font-family: 'Inter', sans-serif;`  
✅ `font-family: var(--mdk-font-body);`

### 3. Not using Tailwind @layer

❌ Writing CSS outside @layer  
✅ Using `@layer components { ... }`

### 4. Missing is-active states

❌ `<button class="mdk-toggle">`  
✅ `<button class="mdk-toggle is-active">`

---

## 📊 Progress Tracking

| Area                | Status      | Document to Check         |
| ------------------- | ----------- | ------------------------- |
| Architecture        | ✅ Complete | VISUAL-ARCHITECTURE.md    |
| Style Guide         | ✅ Complete | STYLE-GUIDE.md            |
| Status Assessment   | ✅ Complete | CURRENT-STATUS.md         |
| Implementation Plan | ✅ Complete | IMPLEMENTATION-ROADMAP.md |
| Code Implementation | 🟡 15%      | CURRENT-STATUS.md         |

---

## 🔗 External Resources

### Core Technologies

- **Svelte:** https://svelte.dev/docs/kit/introduction
- **Tailwind:** https://tailwindcss.com/docs
- **Tailwind Typography:** https://tailwindcss.com/docs/typography-plugin
- **Tauri:** https://tauri.app/v2/guides/

### Reference Implementation

- **Typo Live Demo:** https://typo.robino.dev/
- **Typo Source (cloned):** `/library/ucode/typo/`
- **Typo GitHub:** https://github.com/rossrobino/typo

### Project Documentation

- **Main Roadmap:** `/docs/roadmap.md`
- **AGENTS.md:** `/AGENTS.md` (architecture boundaries)
- **App README:** `../README.md`

---

## 💡 Tips for Success

1. **Follow the roadmap sequentially** — Don't skip Phase 1
2. **Reference Typo constantly** — It's the proven UX baseline
3. **Keep STYLE-GUIDE.md open** — Use the cheat sheet (section 11)
4. **Test font switching early** — It's the core feature
5. **Commit after each phase** — Makes rollback easier

---

## 🎓 Learning Path

### New to Svelte?

1. Read: https://svelte.dev/tutorial/basics
2. Focus on: components, stores, reactivity
3. Skip: SvelteKit routing (we're using Tauri)

### New to Tailwind @layer?

1. Read: https://tailwindcss.com/docs/adding-custom-styles
2. Understand: `@layer base` vs `@layer components`
3. Use: `@apply` for reusable classes

### New to Tauri?

1. Read: https://tauri.app/v2/guides/
2. Focus on: File system API, Window management
3. Bonus: IPC (inter-process communication)

---

## 📝 Notes & Updates

### 2026-01-15

- Created complete documentation set
- Analyzed Typo source in `/library/ucode/typo/`
- Established mdk- naming convention
- Defined 3-phase implementation plan

---

## 🤝 Contributing

When adding new features:

1. Update [STYLE-GUIDE.md](./STYLE-GUIDE.md) if new classes are needed
2. Update [VISUAL-ARCHITECTURE.md](./VISUAL-ARCHITECTURE.md) if structure changes
3. Mark tasks complete in [IMPLEMENTATION-ROADMAP.md](./IMPLEMENTATION-ROADMAP.md)
4. Update progress in [CURRENT-STATUS.md](./CURRENT-STATUS.md)

---

_Start here: [IMPLEMENTATION-ROADMAP.md](./IMPLEMENTATION-ROADMAP.md) Phase 1_
