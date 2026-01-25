<script>
  /**
   * TileGrid - 60×20 tile-based map editor grid
   * Each cell represents a 24×24 pixel tile with an ASCII/block character
   */

  import { createEmptyTile } from "$lib/types/layer";
  let {
    layer,
    selectedChar,
    selectedCode,
    fgColor = "#ffffff",
    bgColor = "#000000",
    tool = "draw",
    showGrid = true,
    showLinks = false,
    zoom = 1,
    onTileChange,
    onTileClick,
  } = $props();

  let isDrawing = $state(false);
  let lastRow = $state(-1);
  let lastCol = $state(-1);

  // Tile size in pixels (24x24 is the standard)
  const baseTileSize = 24;
  const tileSize = $derived(baseTileSize * zoom);

  const handleMouseDown = (row, col, e) => {
    e.preventDefault();
    isDrawing = true;
    lastRow = row;
    lastCol = col;
    applyTool(row, col);
  };

  const handleMouseEnter = (row, col) => {
    if (!isDrawing) return;
    if (row === lastRow && col === lastCol) return;

    lastRow = row;
    lastCol = col;
    applyTool(row, col);
  };

  const handleMouseUp = () => {
    isDrawing = false;
    lastRow = -1;
    lastCol = -1;
  };

  const handleClick = (row, col) => {
    const tile = layer.tiles[row][col];
    onTileClick?.(row, col, tile);
  };

  const applyTool = (row, col) => {
    if (layer.locked) return;

    const currentTile = layer.tiles[row][col];

    switch (tool) {
      case "draw":
        const newTile = {
          char: selectedChar,
          code: selectedCode,
          fg: fgColor,
          bg: bgColor,
          link: currentTile.link, // Preserve existing link
          metadata: currentTile.metadata,
        };
        onTileChange(row, col, newTile);
        break;

      case "erase":
        onTileChange(row, col, createEmptyTile());
        break;

      case "select":
        handleClick(row, col);
        break;

      case "link":
        handleClick(row, col);
        break;
    }
  };

  const getTileStyle = (tile) => {
    let style = `width: ${tileSize}px; height: ${tileSize}px; font-size: ${tileSize * 0.8}px;`;

    if (tile.fg) {
      style += ` color: ${tile.fg};`;
    }
    if (tile.bg) {
      style += ` background-color: ${tile.bg};`;
    }

    return style;
  };

  const hasLink = (tile) => {
    return !!tile.link;
  };
</script>

<svelte:window onmouseup={handleMouseUp} />

<div
  class="tile-grid-container"
  class:show-grid={showGrid}
  style="opacity: {layer.opacity};"
>
  <div
    class="tile-grid"
    style="
      grid-template-columns: repeat({layer.width}, {tileSize}px);
      grid-template-rows: repeat({layer.height}, {tileSize}px);
    "
  >
    {#each layer.tiles as row, rowIndex}
      {#each row as tile, colIndex}
        <button
          class="tile"
          class:has-link={hasLink(tile) && showLinks}
          class:empty={tile.char === " "}
          class:drawing-mode={tool === "draw"}
          class:erasing-mode={tool === "erase"}
          style={getTileStyle(tile)}
          onmousedown={(e) => handleMouseDown(rowIndex, colIndex, e)}
          onmouseenter={() => handleMouseEnter(rowIndex, colIndex)}
          onclick={() => handleClick(rowIndex, colIndex)}
          aria-label="Tile {rowIndex},{colIndex}: {tile.char}"
          tabindex="-1"
        >
          {tile.char}
        </button>
      {/each}
    {/each}
  </div>

  <!-- Grid info -->
  <div class="grid-info">
    {layer.width}×{layer.height} Grid • Tile Size: {baseTileSize}×{baseTileSize}px
    • Zoom: {Math.round(zoom * 100)}%
  </div>
</div>

<style>
  .tile-grid-container {
    display: inline-block;
    border: 2px solid var(--border-color, #4b5563);
    border-radius: 4px;
    background-color: var(--grid-bg, #1f2937);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  }

  .tile-grid {
    display: grid;
    gap: 0;
    padding: 8px;
    font-family: var(--font-mono-variant, "Monaco", monospace);
    line-height: 1;
  }

  .show-grid .tile {
    border: 1px solid rgba(75, 85, 99, 0.3);
  }

  .tile {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #000000;
    color: #ffffff;
    cursor: pointer;
    border: none;
    padding: 0;
    transition:
      opacity 0.1s,
      transform 0.05s;
    user-select: none;
    overflow: hidden;
  }

  .tile:hover {
    opacity: 0.8;
    transform: scale(1.05);
  }

  .tile:active {
    transform: scale(0.95);
  }

  .tile.drawing-mode {
    cursor: crosshair;
  }

  .tile.erasing-mode {
    cursor: cell;
  }

  .tile.empty {
    background-color: #111827;
  }

  .tile.has-link {
    box-shadow: inset 0 0 0 2px rgba(59, 130, 246, 0.5);
    position: relative;
  }

  .tile.has-link::after {
    content: "🔗";
    position: absolute;
    top: 1px;
    right: 1px;
    font-size: 8px;
    opacity: 0.7;
  }

  .grid-info {
    background-color: var(--info-bg, #374151);
    padding: 6px 12px;
    text-align: center;
    font-size: 11px;
    color: var(--info-text, #9ca3af);
    border-top: 1px solid var(--border-color, #4b5563);
    font-family:
      system-ui,
      -apple-system,
      sans-serif;
  }

  /* Dark mode support */
  :global(.dark) .tile-grid-container {
    --border-color: #6b7280;
    --grid-bg: #111827;
    --info-bg: #1f2937;
    --info-text: #d1d5db;
  }
</style>
