# uMarkdown App - Visual Architecture

**Quick Reference for Understanding the App Structure**

---

## 🏗️ Component Hierarchy

```
uMarkdown App (mdk-app)
│
├─ Toolbar (mdk-toolbar)
│  ├─ File Operations Group
│  │  ├─ Open File 📄
│  │  ├─ Open Folder 📁
│  │  ├─ Save 💾
│  │  └─ Reveal in Finder 🔍
│  └─ ...other controls
│
├─ Main Layout (mdk-main)
│  │
│  ├─ Binder Sidebar (mdk-pane--binder)
│  │  └─ Navigation tree
│  │
│  ├─ Editor Pane (mdk-pane--editor)
│  │  └─ MarkdownEditor.svelte
│  │     └─ mdk-editor mdk-font-body
│  │
│  └─ Preview Pane (mdk-pane--preview)
│     └─ Preview.svelte
│        └─ mdk-preview mdk-font-body
│           ├─ h1-h6 (uses --mdk-font-heading)
│           ├─ p, li (uses --mdk-font-body)
│           └─ code, pre (uses --mdk-font-code)
│
└─ Bottom Bar (mdk-bottom-bar)
   ├─ Font Toggles Group
   │  ├─ Heading Font [is-active]
   │  ├─ Body Font [is-active]
   │  └─ Code Font [is-active]
   └─ Size Controls Group
      └─ prose-base ▼
```

---

## 🎨 Class Naming System

### mdk- Prefix (Markdown Kit)

All custom classes use `mdk-` prefix for:

- **Component containers:** `mdk-app`, `mdk-shell`, `mdk-toolbar`
- **Semantic regions:** `mdk-editor`, `mdk-preview`, `mdk-preferences`
- **Reusable UI:** `mdk-btn`, `mdk-panel`, `mdk-field`

### State Classes

- **is-\*** for state: `is-active`, `is-disabled`, `is-dragging`
- **has-\*** for features: `has-file`, `has-folder`, `has-split-view`

### Data Attributes

- **data-action=""** for JS hooks: `data-action="open-file"`
- **data-font-target=""** for font controls: `data-font-target="heading"`

---

## 🔤 Font System Flow

```
Preferences Panel
    ↓ (user selects fonts)
CSS Variables (--mdk-font-*)
    ├─ --mdk-font-heading
    ├─ --mdk-font-body
    └─ --mdk-font-code
    ↓ (applied via classes)
Component Classes
    ├─ .mdk-font-heading
    ├─ .mdk-font-body
    └─ .mdk-font-code
    ↓ (used in components)
Preview Rendering
    ├─ h1-h6 → heading font
    ├─ p, li → body font
    └─ code, pre → code font
```

### Toggle Flow

```
Bottom Bar Buttons
    [Heading] [Body] [Code]
       ↓        ↓      ↓
   is-active states
       ↓        ↓      ↓
Enable/disable font application
       ↓        ↓      ↓
   CSS var → component class → rendered element
```

---

## 📁 File Structure (Proposed)

```
app/
├── docs/
│   ├── STYLE-GUIDE.md           ← Class naming & patterns
│   ├── CURRENT-STATUS.md        ← Project status
│   ├── IMPLEMENTATION-ROADMAP.md ← Step-by-step plan
│   └── VISUAL-ARCHITECTURE.md   ← This file
│
├── src/
│   ├── App.svelte               ← Main app shell
│   ├── styles.css               ← Global styles (@layer structure)
│   │
│   ├── components/
│   │   ├── Toolbar.svelte       ← Top bar (file ops)
│   │   ├── BottomBar.svelte     ← Bottom bar (font toggles)
│   │   ├── Preferences.svelte   ← Settings panel
│   │   ├── BinderNav.svelte     ← Sidebar navigation
│   │   ├── MarkdownEditor.svelte ← Text editor
│   │   ├── Preview.svelte       ← Markdown preview
│   │   └── SyncIndicator.svelte ← Sync status
│   │
│   ├── lib/
│   │   ├── api.ts
│   │   └── fonts.ts             ← Font utilities (to create)
│   │
│   └── stores/
│       ├── syncStore.ts
│       └── fontStore.ts         ← Font state (to create)
│
├── src-tauri/
│   └── src/
│       └── main.rs              ← Tauri backend (file ops)
│
└── tailwind.config.js           ← Tailwind + Typography
```

---

## 🎯 Three Font Controls

### Visual Representation

````
╔════════════════════════════════════════════╗
║ PREVIEW PANE                               ║
╠════════════════════════════════════════════╣
║                                            ║
║  # Heading (uses --mdk-font-heading)       ║
║                                            ║
║  This is body text. It uses the body       ║
║  font set in preferences.                  ║
║  (uses --mdk-font-body)                    ║
║                                            ║
║  ```python                                 ║
║  def hello():                              ║
║      print("Code font")                    ║
║  ```                                       ║
║  (uses --mdk-font-code)                    ║
║                                            ║
╚════════════════════════════════════════════╝

Bottom Bar: [ H ] [ B ] [ C ] | prose-base ▼
            ━━━   ━━━   ━━━
            Heading Body Code
            (active = blue, inactive = gray)
````

---

## 🔄 Data Flow Diagram

```
User Action
    │
    ├─ Open File → Tauri API → Load content → Editor
    │
    ├─ Edit Text → Editor → Preview (live)
    │
    ├─ Change Font → Preferences → CSS vars → Rerender
    │
    ├─ Toggle Font → Bottom Bar → Enable/disable → Rerender
    │
    └─ Save File → Tauri API → Write to disk
```

---

## 🎨 Typo Integration Strategy

### What We Keep from Typo

1. ✅ Font size cycling (`prose-sm` → `prose-2xl`)
2. ✅ Font family options (sans, humanist, serif, mono, old-style)
3. ✅ View mode toggle (expand preview)
4. ✅ Text wrapping (balance for headings, pretty for body)
5. ✅ Syntax highlighting (Shiki variables)

### What We Add

1. ➕ **Three separate font controls** (not just one)
2. ➕ **Preferences panel** (persistent font selection)
3. ➕ **File operations** (open, save, Finder integration)
4. ➕ **Multi-file support** (.txt, .sh, .py, not just .md)
5. ➕ **Binder navigation** (Notion-style organization)

### What We Replace

1. 🔄 Single font toggle → Three toggles
2. 🔄 Default styles → mdk- prefixed classes
3. 🔄 Vercel-specific features → Tauri-native features

---

## 📊 Implementation Progress Matrix

| Component      | Exists | Needs mdk- | Needs Logic | Status |
| -------------- | ------ | ---------- | ----------- | ------ |
| App.svelte     | ✅     | 🔴         | 🟡          | 25%    |
| styles.css     | ✅     | 🔴         | 🔴          | 10%    |
| BinderNav      | ✅     | 🔴         | ✅          | 70%    |
| MarkdownEditor | ✅     | 🔴         | ✅          | 70%    |
| Preview        | ✅     | 🔴         | 🟡          | 60%    |
| Toolbar        | 🔴     | 🔴         | 🔴          | 0%     |
| BottomBar      | 🔴     | 🔴         | 🔴          | 0%     |
| Preferences    | 🔴     | 🔴         | 🔴          | 0%     |

**Legend:**

- ✅ Complete
- 🟡 Partial
- 🔴 Not Started

---

## 🚀 Quick Start Commands

```bash
# Terminal 1: Launch dev mode
cd /Users/fredbook/Code/uDOS/app
npm run tauri:dev

# Terminal 2: Watch Typo for reference
cd /Users/fredbook/Code/uDOS/library/ucode/typo
npm run dev
# Opens at http://localhost:5173

# Terminal 3: Monitor changes
cd /Users/fredbook/Code/uDOS
git status
```

---

## 📚 Key Reference Docs

1. **STYLE-GUIDE.md** — Complete class naming system
2. **CURRENT-STATUS.md** — What's done, what's missing
3. **IMPLEMENTATION-ROADMAP.md** — Step-by-step plan
4. **This file** — Visual overview

---

## 💡 Design Principles

### Keep It Simple

- One purpose per component
- Clear naming conventions
- Minimal prop drilling

### Typo First

- Use Typo's proven UX patterns
- Port, don't rewrite
- Extend thoughtfully

### Three Font Philosophy

- Heading: Bold, distinctive (serif or display sans)
- Body: Readable, comfortable (humanist sans or serif)
- Code: Monospace, clear (programmer fonts)

---

_This is a living document. Update as architecture evolves._
