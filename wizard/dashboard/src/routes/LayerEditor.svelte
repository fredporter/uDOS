<script>
  import { onMount } from "svelte";
  import LayerPanel from "$lib/components/LayerPanel.svelte";
  import TileGrid from "$lib/components/TileGrid.svelte";
  import TileLinker from "$lib/components/TileLinker.svelte";
  import CharacterPalette from "$lib/components/CharacterPalette.svelte";
  import ColorPalette from "$lib/components/ColorPalette.svelte";
  import MapLayerBrowser from "$lib/components/MapLayerBrowser.svelte";
  import {
    createMapDocument,
    createLayer,
    createEmptyTile,
  } from "$lib/types/layer";

  let adminToken = "";
  let document = createMapDocument("Untitled Map");
  let tool = "draw";
  let selectedChar = "█";
  let selectedCode = 0x2588;
  let fgColor = "#ffffff";
  let bgColor = "#000000";
  let showGrid = true;
  let showLinks = true;
  let zoom = 1;
  let sidebarTab = "layers";
  let error = null;

  let roots = {};
  let scope = "sandbox";
  let files = [];
  let filename = "";

  let linkTarget = null;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  function activeLayer() {
    return (
      document.layers.find((layer) => layer.id === document.activeLayerId) ||
      document.layers[0]
    );
  }

  function commitDocument() {
    document = { ...document, layers: [...document.layers] };
  }

  function handleTileChange(row, col, tile) {
    const layer = activeLayer();
    if (!layer || layer.locked) return;
    layer.tiles[row][col] = tile;
    layer.metadata = { ...layer.metadata, modified: new Date().toISOString() };
    commitDocument();
  }

  function handleTileClick(row, col, tile) {
    if (tool === "link") {
      linkTarget = { row, col, tile };
    }
  }

  function updateSelectedChar(char, code) {
    selectedChar = char;
    selectedCode = code;
  }

  function addLayer() {
    const name = prompt("Layer name", `Layer ${document.layers.length + 1}`);
    if (!name) return;
    const layer = createLayer(`layer-${Date.now()}`, name, document.defaultWidth, document.defaultHeight);
    layer.zIndex = document.layers.length;
    document.layers = [...document.layers, layer];
    document.activeLayerId = layer.id;
    commitDocument();
  }

  function removeLayer(layerId) {
    if (document.layers.length === 1) return;
    if (!confirm("Delete this layer?")) return;
    document.layers = document.layers.filter((layer) => layer.id !== layerId);
    if (document.activeLayerId === layerId) {
      document.activeLayerId = document.layers[0]?.id || null;
    }
    commitDocument();
  }

  function duplicateLayer(layerId) {
    const layer = document.layers.find((item) => item.id === layerId);
    if (!layer) return;
    const clone = JSON.parse(JSON.stringify(layer));
    clone.id = `layer-${Date.now()}`;
    clone.name = `${layer.name} Copy`;
    clone.zIndex = document.layers.length;
    document.layers = [...document.layers, clone];
    document.activeLayerId = clone.id;
    commitDocument();
  }

  function selectLayer(layerId) {
    document.activeLayerId = layerId;
    commitDocument();
  }

  function moveLayer(layerId, direction) {
    const index = document.layers.findIndex((layer) => layer.id === layerId);
    if (index === -1) return;
    const targetIndex = direction === "up" ? index + 1 : index - 1;
    if (targetIndex < 0 || targetIndex >= document.layers.length) return;
    const layers = [...document.layers];
    const [removed] = layers.splice(index, 1);
    layers.splice(targetIndex, 0, removed);
    layers.forEach((layer, i) => (layer.zIndex = i));
    document.layers = layers;
    commitDocument();
  }

  function toggleVisibility(layerId) {
    document.layers = document.layers.map((layer) =>
      layer.id === layerId ? { ...layer, visible: !layer.visible } : layer
    );
    commitDocument();
  }

  function toggleLock(layerId) {
    document.layers = document.layers.map((layer) =>
      layer.id === layerId ? { ...layer, locked: !layer.locked } : layer
    );
    commitDocument();
  }

  function renameLayer(layerId, newName) {
    document.layers = document.layers.map((layer) =>
      layer.id === layerId ? { ...layer, name: newName } : layer
    );
    commitDocument();
  }

  function updateOpacity(layerId, opacity) {
    document.layers = document.layers.map((layer) =>
      layer.id === layerId ? { ...layer, opacity } : layer
    );
    commitDocument();
  }

  function saveLink(link) {
    const layer = activeLayer();
    if (!layer || !linkTarget) return;
    const tile = layer.tiles[linkTarget.row][linkTarget.col];
    layer.tiles[linkTarget.row][linkTarget.col] = {
      ...tile,
      link,
    };
    linkTarget = null;
    commitDocument();
  }

  function closeLinker() {
    linkTarget = null;
  }

  async function loadRoots() {
    const res = await fetch("/api/v1/layers/roots", {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    roots = data.roots || {};
  }

  async function loadFiles() {
    const res = await fetch(`/api/v1/layers/list?scope=${scope}`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    files = data.files || [];
  }

  async function loadDocument(file) {
    const path = `${roots[scope]}/${file}`;
    const res = await fetch(`/api/v1/layers/load?path=${encodeURIComponent(path)}`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    document = data.document || createMapDocument("Untitled Map");
  }

  async function saveDocument() {
    if (!filename) {
      alert("Enter a filename");
      return;
    }
    const path = `${roots[scope]}/${filename}`;
    const res = await fetch("/api/v1/layers/save", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ path, document }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await loadFiles();
  }

  function newDocument() {
    document = createMapDocument("Untitled Map");
  }

  function importCoreLayer(filename, metadata) {
    const layer = createLayer(
      `core-${Date.now()}`,
      metadata?.layer_name || filename,
      document.defaultWidth,
      document.defaultHeight
    );
    layer.metadata = {
      ...layer.metadata,
      custom: {
        source: "core",
        filename,
        metadata,
      },
    };
    document.layers = [...document.layers, layer];
    document.activeLayerId = layer.id;
    commitDocument();
  }

  onMount(async () => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    try {
      await loadRoots();
      await loadFiles();
    } catch (err) {
      error = err.message || String(err);
    }
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">Layer Editor</h1>
    <p class="text-gray-400">Multi-layer tile editor with links and core map imports</p>
  </div>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
      {error}
    </div>
  {/if}

  <div class="grid grid-cols-1 xl:grid-cols-[320px_1fr] gap-6">
    <aside class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-4">
      <div class="space-y-2">
        <label for="layer-doc-name" class="text-xs uppercase text-gray-400"
          >Document</label
        >
        <input
          id="layer-doc-name"
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
          bind:value={document.name}
          on:input={commitDocument}
        />
        <div class="flex gap-2">
          <button class="flex-1 px-3 py-2 rounded bg-gray-700" on:click={newDocument}>
            New
          </button>
          <button class="flex-1 px-3 py-2 rounded bg-blue-600" on:click={saveDocument}>
            Save
          </button>
        </div>
      </div>

      <div class="space-y-2">
        <label for="layer-storage" class="text-xs uppercase text-gray-400"
          >Storage</label
        >
        <div class="flex gap-2">
          <select
            id="layer-storage"
            class="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
            bind:value={scope}
            on:change={loadFiles}
          >
            {#each Object.keys(roots) as key}
              <option value={key}>{key}</option>
            {/each}
          </select>
          <button class="px-3 py-2 rounded bg-gray-700" on:click={loadFiles}>
            Refresh
          </button>
        </div>
        <input
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
          placeholder="filename.json"
          bind:value={filename}
        />
        <div class="max-h-36 overflow-y-auto border border-gray-700 rounded">
          {#each files as file}
            <button
              class="w-full text-left px-3 py-2 text-xs border-b border-gray-700 hover:bg-gray-700"
              on:click={() => loadDocument(file)}
            >
              {file}
            </button>
          {/each}
        </div>
      </div>

      <div class="space-y-2">
        <div class="text-xs uppercase text-gray-400">Tools</div>
        <div class="grid grid-cols-2 gap-2">
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={tool === "draw"}
            class:bg-gray-700={tool !== "draw"}
            on:click={() => (tool = "draw")}
          >Draw</button>
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={tool === "erase"}
            class:bg-gray-700={tool !== "erase"}
            on:click={() => (tool = "erase")}
          >Erase</button>
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={tool === "link"}
            class:bg-gray-700={tool !== "link"}
            on:click={() => (tool = "link")}
          >Link</button>
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={tool === "select"}
            class:bg-gray-700={tool !== "select"}
            on:click={() => (tool = "select")}
          >Select</button>
        </div>
        <div class="flex items-center gap-3 text-xs text-gray-400">
          <label class="flex items-center gap-2">
            <input type="checkbox" bind:checked={showGrid} /> Grid
          </label>
          <label class="flex items-center gap-2">
            <input type="checkbox" bind:checked={showLinks} /> Links
          </label>
        </div>
        <label for="layer-zoom" class="text-xs uppercase text-gray-400">Zoom</label>
        <input id="layer-zoom" type="range" min="0.5" max="2" step="0.1" bind:value={zoom} />
      </div>

      <div class="space-y-2">
        <div class="text-xs uppercase text-gray-400">Sidebar Tabs</div>
        <div class="grid grid-cols-2 gap-2">
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={sidebarTab === "layers"}
            class:bg-gray-700={sidebarTab !== "layers"}
            on:click={() => (sidebarTab = "layers")}
          >Layers</button>
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={sidebarTab === "palette"}
            class:bg-gray-700={sidebarTab !== "palette"}
            on:click={() => (sidebarTab = "palette")}
          >Palette</button>
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={sidebarTab === "links"}
            class:bg-gray-700={sidebarTab !== "links"}
            on:click={() => (sidebarTab = "links")}
          >Links</button>
          <button
            class="px-3 py-2 rounded"
            class:bg-blue-600={sidebarTab === "browser"}
            class:bg-gray-700={sidebarTab !== "browser"}
            on:click={() => (sidebarTab = "browser")}
          >Core Maps</button>
        </div>
      </div>

      {#if sidebarTab === "layers"}
        <div class="h-[420px] border border-gray-700 rounded overflow-hidden">
          <LayerPanel
            {document}
            onAddLayer={addLayer}
            onRemoveLayer={removeLayer}
            onDuplicateLayer={duplicateLayer}
            onSelectLayer={selectLayer}
            onMoveLayer={moveLayer}
            onToggleVisibility={toggleVisibility}
            onToggleLock={toggleLock}
            onRenameLayer={renameLayer}
            onUpdateOpacity={updateOpacity}
          />
        </div>
      {:else if sidebarTab === "palette"}
        <div class="space-y-4">
          <CharacterPalette
            bind:selectedCode={selectedCode}
            onSelect={updateSelectedChar}
          />
          <ColorPalette bind:selectedColor={fgColor} onChange={(color) => (fgColor = color)} />
          <ColorPalette bind:selectedColor={bgColor} onChange={(color) => (bgColor = color)} />
        </div>
      {:else if sidebarTab === "links"}
        <div class="text-xs text-gray-400">
          Use the Link tool and click a tile to attach a resource.
        </div>
      {:else if sidebarTab === "browser"}
        <div class="h-[420px] border border-gray-700 rounded overflow-hidden">
          <MapLayerBrowser onLoadLayer={importCoreLayer} />
        </div>
      {/if}
    </aside>

    <section class="bg-gray-900 border border-gray-700 rounded-lg p-4 overflow-auto">
      {#if activeLayer()}
        <TileGrid
          layer={activeLayer()}
          selectedChar={selectedChar}
          selectedCode={selectedCode}
          fgColor={fgColor}
          bgColor={bgColor}
          tool={tool}
          showGrid={showGrid}
          showLinks={showLinks}
          zoom={zoom}
          onTileChange={handleTileChange}
          onTileClick={handleTileClick}
        />
      {:else}
        <div class="text-gray-400">No active layer.</div>
      {/if}
    </section>
  </div>
</div>

{#if linkTarget}
  <TileLinker
    tile={linkTarget.tile}
    row={linkTarget.row}
    col={linkTarget.col}
    onSaveLink={saveLink}
    onClose={closeLinker}
  />
{/if}
