<script>
  import { onMount } from 'svelte';

  const GRID_SIZE = 24;
  const CELL_SIZE = 20;

  // uDOS 32-Color Palette v2.0.0
  // Indices 0-15: Core palette (emoji/ANSI safe)
  // Indices 16-31: Extended palette
  const COLORS = {
    // Terrain Colors (0-7)
    FOREST: '#2d5016',
    GRASS: '#4c9a2a',
    DEEP_WATER: '#1b4965',
    WATER: '#3377dd',
    EARTH: '#6b4423',
    SAND: '#e0b984',
    MOUNTAIN: '#4f646f',
    SNOW: '#f2f6f9',

    // Marker / Signal Colors (8-15)
    DANGER: '#dc2626',
    ALERT: '#ff7a1a',
    WAYPOINT: '#ffd23f',
    SAFE: '#00e89a',
    OBJECTIVE: '#00bfe6',
    PURPLE: '#6f2ed6',
    PINK: '#ff006e',
    MAGENTA: '#e91fa0',

    // Greyscale Ramp (16-23)
    BLACK: '#000000',
    DARK_GREY: '#1a1a1a',
    CHARCOAL: '#333333',
    MEDIUM_GREY: '#666666',
    STEEL_GREY: '#999999',
    LIGHT_GREY: '#cccccc',
    OFF_WHITE: '#e6e6e6',
    WHITE: '#ffffff',

    // Accent / Special Colors (24-31)
    SKIN_LIGHT: '#ffe0bd',
    SKIN_MEDIUM: '#ffcd94',
    SKIN_TAN: '#d2a679',
    SKIN_DARK: '#8d5524',
    LAVA: '#ff4500',
    ICE: '#a7c7e7',
    TOXIC: '#2ee312',
    DEEP_SEA: '#003366'
  };

  let canvas;
  let ctx;
  let grid = [];
  let currentTool = 'pencil';
  let currentColor = 'WHITE';
  let currentBgColor = 'BLACK';
  let zoom = 1;
  let showGrid = true;
  let isDrawing = false;
  let filename = 'tile.json';

  // Font integration
  let fontCollections = [];
  let selectedCollection = '';
  let fontCharacters = [];
  let selectedChar = '█';
  let showFontPicker = false;

  // Color categories for organized palette display
  const COLOR_CATEGORIES = {
    'Terrain': ['FOREST', 'GRASS', 'DEEP_WATER', 'WATER', 'EARTH', 'SAND', 'MOUNTAIN', 'SNOW'],
    'Markers': ['DANGER', 'ALERT', 'WAYPOINT', 'SAFE', 'OBJECTIVE', 'PURPLE', 'PINK', 'MAGENTA'],
    'Greyscale': ['BLACK', 'DARK_GREY', 'CHARCOAL', 'MEDIUM_GREY', 'STEEL_GREY', 'LIGHT_GREY', 'OFF_WHITE', 'WHITE'],
    'Special': ['SKIN_LIGHT', 'SKIN_MEDIUM', 'SKIN_TAN', 'SKIN_DARK', 'LAVA', 'ICE', 'TOXIC', 'DEEP_SEA']
  };

  function initGrid() {
    grid = [];
    for (let y = 0; y < GRID_SIZE; y++) {
      const row = [];
      for (let x = 0; x < GRID_SIZE; x++) {
        row.push({ char: ' ', fg: 'WHITE', bg: 'BLACK' });
      }
      grid.push(row);
    }
  }

  async function loadFontCollections() {
    try {
      const resp = await fetch('/api/v1/fonts/collections');
      const data = await resp.json();
      console.log('Font collections loaded:', data);
      fontCollections = data.collections || [];
      if (fontCollections.length > 0) {
        selectedCollection = fontCollections[0].name;
        console.log('Auto-selected collection:', selectedCollection);
        await loadFontCharacters(selectedCollection);
      }
    } catch (e) {
      console.error('Failed to load font collections:', e);
    }
  }

  async function loadFontCharacters(collection) {
    try {
      const resp = await fetch(`/api/v1/fonts/characters/${collection}?limit=200`);
      const data = await resp.json();
      console.log(`Characters loaded for ${collection}:`, data);
      fontCharacters = data.items || [];
      if (fontCharacters.length > 0) {
        selectedChar = fontCharacters[0].utf8;
        console.log('Auto-selected character:', selectedChar);
      }
    } catch (e) {
      console.error('Failed to load font characters:', e);
    }
  }

  async function onCollectionChange() {
    await loadFontCharacters(selectedCollection);
  }

  function selectCharacter(char) {
    selectedChar = char.utf8;
    currentTool = 'font';
  }

  function render() {
    if (!ctx) return;
    const size = CELL_SIZE * zoom;

    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y < GRID_SIZE; y++) {
      for (let x = 0; x < GRID_SIZE; x++) {
        const cell = grid[y][x];
        const px = x * size;
        const py = y * size;

        ctx.fillStyle = COLORS[cell.bg] || '#000';
        ctx.fillRect(px, py, size, size);

        if (cell.char && cell.char !== ' ') {
          ctx.font = `${size * 0.8}px 'Noto Sans Symbols 2', 'Segoe UI Symbol', 'Apple Color Emoji', 'Noto Color Emoji', monospace`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = COLORS[cell.fg] || '#FFF';
          ctx.fillText(cell.char, px + size / 2, py + size / 2);
        }
      }
    }

    if (showGrid) {
      ctx.strokeStyle = '#333';
      ctx.lineWidth = 1;
      for (let i = 0; i <= GRID_SIZE; i++) {
        ctx.beginPath();
        ctx.moveTo(i * size, 0);
        ctx.lineTo(i * size, canvas.height);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(0, i * size);
        ctx.lineTo(canvas.width, i * size);
        ctx.stroke();
      }
    }
  }

  function getCellFromEvent(e) {
    const rect = canvas.getBoundingClientRect();
    const size = CELL_SIZE * zoom;
    const x = Math.floor((e.clientX - rect.left) / size);
    const y = Math.floor((e.clientY - rect.top) / size);
    return { x, y };
  }

  function drawCell(x, y) {
    if (x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE) return;
    let char = ' ';
    if (currentTool === 'eraser') {
      char = ' ';
    } else if (currentTool === 'font') {
      char = selectedChar;
    } else {
      char = '█';
    }
    grid[y][x] = {
      char: char,
      fg: currentColor,
      bg: currentBgColor
    };
    render();
  }

  function onMouseDown(e) {
    isDrawing = true;
    const { x, y } = getCellFromEvent(e);
    drawCell(x, y);
  }

  function onMouseMove(e) {
    if (!isDrawing) return;
    const { x, y } = getCellFromEvent(e);
    drawCell(x, y);
  }

  function onMouseUp() {
    isDrawing = false;
  }

  function clear() {
    if (confirm('Clear all pixels?')) {
      initGrid();
      render();
    }
  }

  function zoomIn() {
    if (zoom < 3) zoom += 0.5;
    canvas.width = GRID_SIZE * CELL_SIZE * zoom;
    canvas.height = GRID_SIZE * CELL_SIZE * zoom;
    render();
  }

  function zoomOut() {
    if (zoom > 0.5) zoom -= 0.5;
    canvas.width = GRID_SIZE * CELL_SIZE * zoom;
    canvas.height = GRID_SIZE * CELL_SIZE * zoom;
    render();
  }

  function save() {
    const data = { size: GRID_SIZE, grid };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
  }

  function load() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const text = await file.text();
      const data = JSON.parse(text);
      if (data.size === GRID_SIZE) {
        grid = data.grid;
        filename = file.name;
        render();
      } else {
        alert(`Wrong grid size (expected ${GRID_SIZE})`);
      }
    };
    input.click();
  }

  function exportSVG() {
    const size = 20;
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${GRID_SIZE * size} ${GRID_SIZE * size}">`;

    for (let y = 0; y < GRID_SIZE; y++) {
      for (let x = 0; x < GRID_SIZE; x++) {
        const cell = grid[y][x];
        const px = x * size;
        const py = y * size;
        svg += `<rect x="${px}" y="${py}" width="${size}" height="${size}" fill="${COLORS[cell.bg] || '#000'}"/>`;
        if (cell.char && cell.char !== ' ') {
          svg += `<text x="${px + size / 2}" y="${py + size / 2}" fill="${COLORS[cell.fg] || '#FFF'}" text-anchor="middle" font-family="monospace">${cell.char}</text>`;
        }
      }
    }
    svg += '</svg>';

    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'tile.svg';
    a.click();
  }

  onMount(() => {
    initGrid();
    loadFontCollections();
    canvas.width = GRID_SIZE * CELL_SIZE * zoom;
    canvas.height = GRID_SIZE * CELL_SIZE * zoom;
    ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    render();
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseUp);
  });
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <!-- Header -->
  <header class="bg-gradient-to-r from-orange-600 to-pink-600 text-white p-6 sticky top-0 z-10">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold mb-2">🎨 Pixel Editor</h1>
      <p class="text-orange-100">24×24 tile and character editor</p>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-6xl mx-auto px-4 py-8">
    <!-- Controls -->
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
        <!-- Tools -->
        <div>
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Tool</label>
          <select
            bind:value={currentTool}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="pencil">✏️ Pencil</option>
            <option value="font">🔤 Font Character</option>
            <option value="eraser">🗑️ Eraser</option>
          </select>
        </div>

        <!-- Foreground Color -->
        <div>
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Char Color</label>
          <select
            bind:value={currentColor}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {#each Object.entries(COLOR_CATEGORIES) as [category, colors]}
              <optgroup label={category}>
                {#each colors as color}
                  <option value={color} style="background-color: {COLORS[color]}; color: {['BLACK', 'DARK_GREY', 'CHARCOAL', 'DEEP_WATER', 'DEEP_SEA', 'FOREST'].includes(color) ? '#fff' : '#000'}">
                    {color.replace(/_/g, ' ')}
                  </option>
                {/each}
              </optgroup>
            {/each}
          </select>
        </div>

        <!-- Background Color -->
        <div>
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">BG Color</label>
          <select
            bind:value={currentBgColor}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {#each Object.entries(COLOR_CATEGORIES) as [category, colors]}
              <optgroup label={category}>
                {#each colors as color}
                  <option value={color} style="background-color: {COLORS[color]}; color: {['BLACK', 'DARK_GREY', 'CHARCOAL', 'DEEP_WATER', 'DEEP_SEA', 'FOREST'].includes(color) ? '#fff' : '#000'}">
                    {color.replace(/_/g, ' ')}
                  </option>
                {/each}
              </optgroup>
            {/each}
          </select>
        </div>

        <!-- Zoom -->
        <div class="flex gap-2">
          <button
            on:click={zoomOut}
            class="flex-1 px-3 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg font-medium transition-colors"
          >
            🔍−
          </button>
          <button
            on:click={zoomIn}
            class="flex-1 px-3 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg font-medium transition-colors"
          >
            🔍+
          </button>
        </div>

        <!-- Grid Toggle -->
        <button
          on:click={() => { showGrid = !showGrid; render(); }}
          class={`px-4 py-2 rounded-lg font-medium transition-colors ${
            showGrid
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
          }`}
        >
          📐 Grid
        </button>
      </div>

      <!-- File Operations -->
      <div class="flex flex-wrap gap-2">
        <button
          on:click={clear}
          class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
        >
          🗑️ Clear
        </button>
        <button
          on:click={save}
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
        >
          💾 Save JSON
        </button>
        <button
          on:click={load}
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          📂 Load JSON
        </button>
        <button
          on:click={exportSVG}
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
        >
          ⬇️ Export SVG
        </button>
        <button
          on:click={() => showFontPicker = !showFontPicker}
          class="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium transition-colors"
        >
          🔤 Character Picker
        </button>
      </div>
    </div>

    <!-- Font Character Picker Modal -->
    {#if showFontPicker}
      <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={() => showFontPicker = false}>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto" on:click|stopPropagation>
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">🔤 Select Character</h2>
            <button
              on:click={() => showFontPicker = false}
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
            >
              ×
            </button>
          </div>

          <!-- Collection Selector -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Collection</label>
            <select
              bind:value={selectedCollection}
              on:change={onCollectionChange}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {#each fontCollections as collection}
                <option value={collection.name}>{collection.display_name} ({collection.count} chars)</option>
              {/each}
            </select>
          </div>

          <!-- Selected Character Preview -->
          <div class="mb-4 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <div class="text-center">
              <div class="text-6xl mb-2" style="font-family: 'Noto Sans Symbols 2', 'Segoe UI Symbol', 'Apple Color Emoji', 'Noto Color Emoji', monospace; line-height: 1;">{selectedChar}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Current: {selectedChar} (U+{selectedChar.codePointAt(0)?.toString(16).toUpperCase().padStart(4, '0')})</div>
            </div>
          </div>

          <!-- Character Grid -->
          <div class="grid grid-cols-8 gap-2">
            {#each fontCharacters as char}
              <button
                on:click={() => selectCharacter(char)}
                class="aspect-square p-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors flex items-center justify-center text-3xl {selectedChar === char.utf8 ? 'bg-blue-200 dark:bg-blue-800' : 'bg-white dark:bg-gray-700'}"
                style="font-family: 'Noto Sans Symbols 2', 'Segoe UI Symbol', 'Apple Color Emoji', 'Noto Color Emoji', monospace; line-height: 1;"
                title="{char.name} (U+{char.codepoint.toString(16).toUpperCase().padStart(4, '0')})"
              >
                {char.utf8}
              </button>
            {/each}
          </div>

          {#if fontCharacters.length === 0}
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
              No characters loaded. Select a collection above.
            </div>
          {/if}
        </div>
      </div>
    {/if}

    <!-- Canvas -->
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 flex justify-center">
      <canvas
        bind:this={canvas}
        class="border-2 border-gray-400 dark:border-gray-500 cursor-crosshair"
      />
    </div>
  </main>
</div>

<style lang="postcss">
  @reference "tailwindcss";
</style>
