# Extract uFont Manager from Goblin to Wizard

**Status:** 📋 Ready for Implementation  
**Priority:** HIGH (Next task after UI styling is validated)  
**Estimated Effort:** 2-3 hours  

---

## 🎯 Objective

Move font management functionality from Goblin dev server (`/dev/goblin/src/routes/font/`) to Wizard production server (`/public/wizard/`), creating enterprise-grade uFont Manager service.

---

## 📍 Source Files in Goblin

### 1. Font Manager UI
- **File:** `/dev/goblin/src/routes/font/+page.svelte`
- **Size:** 345 lines
- **Purpose:** Font collection browser + character grid display
- **Key Functions:**
  - Load font manifest from Wizard server
  - Parse font data (names, categories, characters)
  - Render character grid with search/filter
  - Export font selections

### 2. Pixel Editor UI
- **File:** `/dev/goblin/src/routes/pixel-editor/+page.svelte`
- **Size:** 789 lines
- **Purpose:** Character-by-character editor for custom fonts
- **Key Functions:**
  - Load fonts into editor
  - Pixel-by-pixel grid editing
  - Character creation/modification
  - Export edited fonts

### 3. Font Assets
- **Location:** `/dev/goblin/public/fonts/`
- **Contents:**
  - `NotoColorEmoji.ttf` (referenced by config panel)
  - `NotoEmoji-Regular.ttf` (referenced by config panel)
  - Other font files?

---

## 🏗️ Wizard Architecture (Target)

### New Service: uFont Manager
```
/public/wizard/services/ufont_manager.py (NEW)
  ├── FontCollection class
  ├── FontCharacter class
  ├── FontManifest class
  ├── Functions:
  │   ├── load_font_collection(collection_name)
  │   ├── get_characters(collection_name)
  │   ├── search_characters(query)
  │   ├── export_font(collection_name, format)
  │   └── get_font_metadata()
  └── Integration with static fonts directory

/public/wizard/routes/fonts.py (NEW)
  ├── @app.get("/api/v1/fonts/collections")
  ├── @app.get("/api/v1/fonts/characters/{collection}")
  ├── @app.get("/api/v1/fonts/search")
  ├── @app.get("/api/v1/fonts/{collection}/export")
  └── @app.post("/api/v1/fonts/{collection}/upload")

/public/wizard/static/fonts/
  ├── NotoColorEmoji.ttf (already symlinked)
  ├── NotoEmoji-Regular.ttf (already symlinked)
  └── [other fonts as they're added]
```

### New Frontend Components (Tauri App)
```
/app/src/routes/wizard/+page.svelte (NEW)
  ├── Font Manager tab
  ├── Character Grid component
  ├── Search/Filter UI
  └── Export controls

/app/src/lib/components/CharacterGrid.svelte (NEW)
  ├── Display font characters in grid
  ├── Highlight on hover
  ├── Copy-to-clipboard support
  └── Responsive layout

/app/src/lib/components/FontMetadata.svelte (NEW)
  ├── Display font name, license, family
  ├── Show character count, encoding
  └── Export options
```

---

## 📋 Implementation Phases

### Phase 1: Backend Service (2 hours)

**Create:** `public/wizard/services/ufont_manager.py` (~300 lines)

```python
# Font data structures
@dataclass
class FontCharacter:
    codepoint: int
    name: str
    category: str
    utf8: str
    bitmap: Optional[List[List[int]]] = None

@dataclass
class FontCollection:
    name: str
    family: str
    style: str
    characters: List[FontCharacter]
    metadata: Dict[str, Any]

# Main service class
class UFontManager:
    def __init__(self, fonts_path: Path = None):
        """Initialize font manager."""
        self.fonts_path = fonts_path or Path(__file__).parent.parent / "static" / "fonts"
        self.collections = self._load_collections()
    
    def _load_collections(self) -> Dict[str, FontCollection]:
        """Load all available font collections."""
        # Parse TTF/OTF files
        # Build character maps
        # Return {name: FontCollection}
    
    def get_characters(self, collection: str) -> List[FontCharacter]:
        """Get all characters in a font collection."""
        return self.collections[collection].characters
    
    def search_characters(self, query: str) -> List[FontCharacter]:
        """Search characters by name or category."""
        # Implement fuzzy search across all fonts
    
    def export_collection(self, name: str, format: str = "json") -> str:
        """Export font collection in requested format."""
        # Formats: json, csv, markdown, html
    
    @staticmethod
    def parse_ttf_file(path: Path) -> FontCollection:
        """Parse TTF file and extract character data."""
        # Use fontTools library
        # Extract glyph data, codepoints, names
        # Return FontCollection object
```

**Tests:** `public/wizard/tests/test_ufont_manager.py` (~150 lines)
- Test font loading
- Test character parsing
- Test search functionality
- Test export formats

---

### Phase 2: REST API Routes (1 hour)

**Create:** `public/wizard/routes/fonts.py` (~200 lines)

```python
from fastapi import APIRouter, HTTPException, Query
from wizard.services.ufont_manager import UFontManager

router = APIRouter(prefix="/api/v1/fonts", tags=["fonts"])
font_manager = UFontManager()  # Lazy load on first request

@router.get("/collections")
async def list_collections():
    """List available font collections."""
    return {
        "collections": [
            {
                "name": name,
                "family": collection.family,
                "style": collection.style,
                "character_count": len(collection.characters),
            }
            for name, collection in font_manager.collections.items()
        ]
    }

@router.get("/characters/{collection}")
async def get_collection_characters(
    collection: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get characters from a font collection."""
    if collection not in font_manager.collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    chars = font_manager.get_characters(collection)
    return {
        "collection": collection,
        "total": len(chars),
        "items": [
            {
                "codepoint": c.codepoint,
                "name": c.name,
                "category": c.category,
                "utf8": c.utf8,
            }
            for c in chars[offset : offset + limit]
        ],
    }

@router.get("/search")
async def search_characters(q: str = Query(..., min_length=1)):
    """Search characters across all collections."""
    results = font_manager.search_characters(q)
    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "codepoint": c.codepoint,
                "name": c.name,
                "utf8": c.utf8,
                "collection": [
                    name for name, coll in font_manager.collections.items()
                    if c in coll.characters
                ],
            }
            for c in results[:50]  # Limit to 50 results
        ],
    }

@router.get("/{collection}/export")
async def export_collection(
    collection: str,
    format: str = Query("json", regex="^(json|csv|markdown|html)$"),
):
    """Export a font collection in specified format."""
    if collection not in font_manager.collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    data = font_manager.export_collection(collection, format)
    
    mime_types = {
        "json": "application/json",
        "csv": "text/csv",
        "markdown": "text/markdown",
        "html": "text/html",
    }
    
    return {
        "collection": collection,
        "format": format,
        "content": data,
        "mime_type": mime_types[format],
    }

@router.post("/{collection}/characters")
async def add_character(collection: str, character_data: dict):
    """Add or modify a character in a collection (admin only)."""
    # TODO: Add authentication check
    # TODO: Validate character data
    # TODO: Update font file
    pass

@router.delete("/{collection}/characters/{codepoint}")
async def delete_character(collection: str, codepoint: int):
    """Delete a character from a collection (admin only)."""
    # TODO: Add authentication check
    # TODO: Update font file
    pass
```

**Register in server.py:**
```python
from wizard.routes.fonts import router as fonts_router
app.include_router(fonts_router)
```

---

### Phase 3: Frontend Components (1 hour)

**Create:** `/app/src/routes/wizard/+page.svelte` (~300 lines, simplified)

```svelte
<script>
  import { onMount } from 'svelte';
  import CharacterGrid from '$lib/components/CharacterGrid.svelte';
  import FontMetadata from '$lib/components/FontMetadata.svelte';

  let collections = [];
  let selectedCollection = null;
  let characters = [];
  let searchQuery = '';
  let loading = false;

  onMount(async () => {
    // Fetch available font collections
    const resp = await fetch('/api/v1/fonts/collections');
    const data = await resp.json();
    collections = data.collections;
    if (collections.length > 0) {
      selectedCollection = collections[0].name;
      loadCharacters(selectedCollection);
    }
  });

  async function loadCharacters(collectionName) {
    loading = true;
    const resp = await fetch(`/api/v1/fonts/characters/${collectionName}`);
    const data = await resp.json();
    characters = data.items;
    loading = false;
  }

  async function handleSearch() {
    if (!searchQuery.trim()) {
      loadCharacters(selectedCollection);
      return;
    }
    loading = true;
    const resp = await fetch(`/api/v1/fonts/search?q=${encodeURIComponent(searchQuery)}`);
    const data = await resp.json();
    characters = data.results;
    loading = false;
  }

  function handleExport() {
    window.open(`/api/v1/fonts/${selectedCollection}/export?format=json`);
  }
</script>

<div class="app">
  <div class="pane">
    <div class="card">
      <div class="card-header">
        <h2>Font Manager</h2>
      </div>
      <div class="card-body">
        <!-- Collection selector -->
        <div class="form-group">
          <label for="collection">Font Collection:</label>
          <select 
            id="collection" 
            bind:value={selectedCollection}
            on:change={() => loadCharacters(selectedCollection)}
            class="form-control"
          >
            {#each collections as coll}
              <option value={coll.name}>{coll.family} ({coll.character_count})</option>
            {/each}
          </select>
        </div>

        <!-- Search -->
        <div class="form-group">
          <input 
            type="text" 
            placeholder="Search characters..." 
            bind:value={searchQuery}
            on:keyup={handleSearch}
            class="form-control"
          />
        </div>

        <!-- Export -->
        <button class="btn btn-primary" on:click={handleExport}>
          Export Collection
        </button>
      </div>
    </div>

    <!-- Character Grid -->
    {#if loading}
      <p>Loading...</p>
    {:else}
      <CharacterGrid {characters} />
    {/if}
  </div>
</div>
```

**Create:** `/app/src/lib/components/CharacterGrid.svelte` (~150 lines)

```svelte
<script>
  import { tooltip } from '$lib/actions/tooltip.js';

  export let characters = [];

  function copyToClipboard(char) {
    navigator.clipboard.writeText(char.utf8);
  }
</script>

<div class="character-grid">
  {#each characters as char (char.codepoint)}
    <button
      class="grid-item"
      use:tooltip={`${char.name} (U+${char.codepoint.toString(16).toUpperCase()})`}
      on:click={() => copyToClipboard(char)}
    >
      <span class="emoji-mono">{char.utf8}</span>
      <p class="text-xs text-gray-400">{char.name}</p>
    </button>
  {/each}
</div>

<style>
  .character-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 1rem;
    padding: 1rem;
  }

  .grid-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    background: rgb(30 41 59);
    border: 1px solid rgb(51 65 85);
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .grid-item:hover {
    background: rgb(51 65 85);
    border-color: rgb(59 130 246);
  }

  .emoji-mono {
    font-size: 2rem;
    font-family: "Noto Emoji Regular";
  }
</style>
```

---

## 🔍 Key Design Decisions

### Why Extract to Wizard?
- Wizard is production-ready, always-on server
- Goblin is experimental dev environment
- Font management is stable, not experimental
- Wizard can expose as public API for client consumption

### Why ufont_manager.py (not Goblin's Svelte components)?
- Backend service is reusable (Tauri app, API clients, CLI tools)
- Can optimize TTF parsing once, use everywhere
- Easier to test and version independently
- Goblin's Svelte code is UI-specific (not portable)

### How to Handle Existing Goblin Functionality?
- Keep Goblin's font routes as wrappers around Wizard API
- Goblin calls Wizard: `GET http://localhost:8765/api/v1/fonts/...`
- This maintains dev environment isolation
- Goblin can still experiment with new font features locally

---

## 📚 Dependencies

**New Python packages needed:**
- `fontTools` — Parse TTF/OTF files, extract glyph data
- `Pillow` — Font rendering to images (for pixel editor)
- `freetype-py` — Low-level font access (optional, if fontTools insufficient)

**Install:**
```bash
pip install fontTools Pillow
```

**No new JS/Svelte dependencies** — Uses existing Tailwind classes

---

## 🧪 Testing Strategy

### Unit Tests (test_ufont_manager.py)
- [ ] Load Noto fonts without errors
- [ ] Parse character data correctly
- [ ] Extract codepoints, names, categories
- [ ] Search finds characters by name
- [ ] Export generates valid JSON/CSV/Markdown

### Integration Tests (test_fonts_routes.py)
- [ ] GET `/api/v1/fonts/collections` returns list
- [ ] GET `/api/v1/fonts/characters/{collection}` returns paginated results
- [ ] GET `/api/v1/fonts/search?q=test` returns matches
- [ ] GET `/api/v1/fonts/{collection}/export?format=json` returns JSON

### Frontend Tests (CharacterGrid.svelte)
- [ ] Grid displays characters in columns
- [ ] Click copies character to clipboard
- [ ] Tooltip shows character name + codepoint
- [ ] Responsive on mobile (single column)

---

## 🚀 Rollout Plan

### Week 1: Backend
- [ ] Create `ufont_manager.py` service
- [ ] Write tests
- [ ] Create `fonts.py` routes
- [ ] Register routes in `wizard/server.py`
- [ ] Manual API testing with curl

### Week 2: Frontend (Optional)
- [ ] Create Svelte components
- [ ] Wire up to API endpoints
- [ ] Add export functionality
- [ ] User testing

### Week 3: Goblin Integration (Optional)
- [ ] Update Goblin routes to call Wizard API
- [ ] Maintain backward compatibility
- [ ] Deprecation timeline for old code

---

## 💾 Migration Path

**Phase 1 (Now):** Extract backend to Wizard
- Wizard has uFont Manager service
- Available via `/api/v1/fonts/*` endpoints
- Goblin can still use local Svelte components

**Phase 2 (Future):** Integrate frontend
- Tauri app has Font Manager tab
- Uses Wizard API (works offline if fonts cached)
- Replaces Goblin's experimental UI

**Phase 3 (Future):** Deprecate Goblin code
- Keep Goblin's code for reference
- Remove from active Goblin server
- Archive old Svelte components

---

## 📝 File Checklist

**Create:**
- [ ] `public/wizard/services/ufont_manager.py` (NEW)
- [ ] `public/wizard/routes/fonts.py` (NEW)
- [ ] `public/wizard/tests/test_ufont_manager.py` (NEW)
- [ ] `public/wizard/tests/test_fonts_routes.py` (NEW)
- [ ] `/app/src/routes/wizard/+page.svelte` (NEW)
- [ ] `/app/src/lib/components/CharacterGrid.svelte` (NEW)
- [ ] `/app/src/lib/components/FontMetadata.svelte` (NEW)

**Reference (Don't delete yet):**
- `/dev/goblin/src/routes/font/+page.svelte` (keep for reference)
- `/dev/goblin/src/routes/pixel-editor/+page.svelte` (keep for reference)

**Modify:**
- [ ] `public/wizard/server.py` (add fonts router)
- [ ] `/app/src/routes/+page.svelte` (add wizard link)

---

## 🎯 Success Criteria

- [ ] Wizard serves `/api/v1/fonts/collections`
- [ ] Can fetch character data for each collection
- [ ] Search works across all characters
- [ ] Can export in JSON/CSV/Markdown formats
- [ ] Frontend loads and displays character grid
- [ ] Characters copy to clipboard on click
- [ ] Works on mobile viewport
- [ ] No console errors or warnings
- [ ] Documented with inline comments
- [ ] Covered by tests (>80% coverage)

---

_Last Updated: 2026-01-18_  
_Next Phase: Extract uFont Manager from Goblin to Wizard_
