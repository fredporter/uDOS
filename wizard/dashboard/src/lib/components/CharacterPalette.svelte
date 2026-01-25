<script>
  /**
   * CharacterPalette - Character selection palette for Layer Editor
   * Browse and select ASCII, block graphics, and map symbols
   */

  import {
    ASCII_PRINTABLE,
    TELETEXT_BLOCK_GRAPHICS,
    MAP_SYMBOLS,
  } from "$lib/util/characterDatasets";

  let {
    selectedCode = $bindable(),
    onSelect,
    activeSet = "blocks",
  } = $props();

  let currentSet = $state("blocks");

  // Sync currentSet with activeSet prop
  $effect(() => {
    currentSet = activeSet;
  });

  // Character sets
  const characterSets = {
    ascii: ASCII_PRINTABLE,
    blocks: TELETEXT_BLOCK_GRAPHICS,
    maps: MAP_SYMBOLS,
  };

  const setNames = {
    ascii: "ASCII Printable",
    blocks: "Block Graphics",
    maps: "Map Symbols",
  };

  const currentCharSet = $derived(characterSets[currentSet]);
  const currentName = $derived(setNames[currentSet]);

  const handleSelect = (code) => {
    const char = String.fromCharCode(code);
    selectedCode = code;
    onSelect(char, code);
  };

  const switchSet = (set) => {
    currentSet = set;
  };

  // Group ASCII by category
  const asciiGroups = $derived.by(() => {
    if (currentSet !== "ascii") return [];

    return [
      {
        name: "Common",
        codes: [0x0020, 0x002e, 0x002c, 0x003a, 0x003b, 0x0021, 0x003f],
      },
      {
        name: "Numbers",
        codes: Array.from({ length: 10 }, (_, i) => 0x0030 + i),
      },
      {
        name: "Uppercase",
        codes: Array.from({ length: 26 }, (_, i) => 0x0041 + i),
      },
      {
        name: "Lowercase",
        codes: Array.from({ length: 26 }, (_, i) => 0x0061 + i),
      },
      {
        name: "Symbols",
        codes: [
          0x0023, 0x0024, 0x0025, 0x0026, 0x002a, 0x002b, 0x002d, 0x002f,
          0x003c, 0x003d, 0x003e, 0x0040, 0x005e, 0x007e,
        ],
      },
      {
        name: "Brackets",
        codes: [0x0028, 0x0029, 0x005b, 0x005d, 0x007b, 0x007d, 0x003c, 0x003e],
      },
    ];
  });
</script>

<div class="character-palette">
  <div class="palette-header">
    <h3>Character Palette</h3>
    <div class="set-tabs">
      <button
        class="tab"
        class:active={currentSet === "blocks"}
        onclick={() => switchSet("blocks")}
      >
        Blocks
      </button>
      <button
        class="tab"
        class:active={currentSet === "maps"}
        onclick={() => switchSet("maps")}
      >
        Maps
      </button>
      <button
        class="tab"
        class:active={currentSet === "ascii"}
        onclick={() => switchSet("ascii")}
      >
        ASCII
      </button>
    </div>
  </div>

  <div class="palette-body">
    <div class="set-info">
      <span class="set-name">{currentName}</span>
      <span class="set-count">{currentCharSet.codes.length} characters</span>
    </div>

    {#if currentSet === "ascii"}
      <!-- ASCII grouped by category -->
      {#each asciiGroups as group}
        <div class="char-group">
          <div class="group-label">{group.name}</div>
          <div class="char-grid">
            {#each group.codes as code}
              <button
                class="char-btn"
                class:selected={code === selectedCode}
                onclick={() => handleSelect(code)}
                title="U+{code.toString(16).toUpperCase().padStart(4, '0')}"
              >
                {String.fromCharCode(code)}
              </button>
            {/each}
          </div>
        </div>
      {/each}
    {:else}
      <!-- Block graphics or map symbols - single grid -->
      <div class="char-grid">
        {#each currentCharSet.codes as code}
          {@const char = String.fromCharCode(code)}
          {@const mapping =
            currentCharSet.asciiMapping?.[code] ||
            `U+${code.toString(16).toUpperCase()}`}
          <button
            class="char-btn"
            class:selected={code === selectedCode}
            onclick={() => handleSelect(code)}
            title={mapping}
          >
            {char}
          </button>
        {/each}
      </div>
    {/if}

    <!-- Selected character preview -->
    <div class="selection-preview">
      <div class="preview-label">Selected:</div>
      <div class="preview-char">{String.fromCharCode(selectedCode)}</div>
      <div class="preview-info">
        <div>Char: '{String.fromCharCode(selectedCode)}'</div>
        <div>
          Code: {selectedCode} (0x{selectedCode.toString(16).toUpperCase()})
        </div>
        {#if currentCharSet.asciiMapping?.[selectedCode]}
          <div>Mapping: {currentCharSet.asciiMapping[selectedCode]}</div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .character-palette {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--panel-bg, #1f2937);
  }

  .palette-header {
    padding: 12px;
    border-bottom: 1px solid var(--border-color, #374151);
  }

  .palette-header h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary, #f9fafb);
  }

  .set-tabs {
    display: flex;
    gap: 4px;
  }

  .tab {
    flex: 1;
    padding: 6px 8px;
    font-size: 12px;
    background-color: var(--tab-bg, #374151);
    border: 1px solid var(--border-color, #4b5563);
    border-radius: 3px;
    color: var(--text-secondary, #9ca3af);
    cursor: pointer;
    transition: all 0.2s;
  }

  .tab:hover {
    background-color: var(--tab-hover, #4b5563);
    color: var(--text-primary, #f9fafb);
  }

  .tab.active {
    background-color: var(--tab-active, #3b82f6);
    border-color: var(--tab-active-border, #2563eb);
    color: #ffffff;
  }

  .palette-body {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
  }

  .set-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color, #374151);
  }

  .set-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary, #f9fafb);
  }

  .set-count {
    font-size: 11px;
    color: var(--text-secondary, #9ca3af);
  }

  .char-group {
    margin-bottom: 16px;
  }

  .group-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary, #9ca3af);
    text-transform: uppercase;
    margin-bottom: 6px;
  }

  .char-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(32px, 1fr));
    gap: 4px;
    margin-bottom: 8px;
  }

  .char-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    background-color: var(--btn-bg, #374151);
    border: 1px solid var(--border-color, #4b5563);
    border-radius: 3px;
    color: var(--text-primary, #f9fafb);
    font-family: var(--font-mono-variant, "Monaco", monospace);
    font-size: 18px;
    line-height: 1;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .char-btn:hover {
    background-color: var(--btn-hover, #4b5563);
    transform: scale(1.1);
    z-index: 1;
  }

  .char-btn:active {
    transform: scale(0.95);
  }

  .char-btn.selected {
    background-color: var(--btn-selected, #3b82f6);
    border-color: var(--btn-selected-border, #2563eb);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  }

  .selection-preview {
    margin-top: 16px;
    padding: 12px;
    background-color: var(--preview-bg, #111827);
    border: 1px solid var(--border-color, #374151);
    border-radius: 4px;
  }

  .preview-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary, #9ca3af);
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .preview-char {
    font-family: var(--font-mono-variant, "Monaco", monospace);
    font-size: 48px;
    line-height: 1;
    color: var(--text-primary, #f9fafb);
    text-align: center;
    margin-bottom: 8px;
  }

  .preview-info {
    font-size: 11px;
    color: var(--text-secondary, #9ca3af);
    line-height: 1.4;
  }

  .preview-info div {
    margin-bottom: 2px;
  }

  /* Dark mode */
  :global(.dark) .character-palette {
    --panel-bg: #0f172a;
    --border-color: #1e293b;
    --tab-bg: #1e293b;
    --tab-hover: #334155;
    --tab-active: #3b82f6;
    --tab-active-border: #2563eb;
    --btn-bg: #1e293b;
    --btn-hover: #334155;
    --btn-selected: #3b82f6;
    --btn-selected-border: #2563eb;
    --preview-bg: #020617;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
  }
</style>
