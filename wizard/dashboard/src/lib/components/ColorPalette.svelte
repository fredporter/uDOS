<script>
  import { UDOS_PALETTE, getAllColors } from "$lib/util/udosPalette";

  let { selectedColor = $bindable(), onChange } = $props();

  // Use the uDOS 32-color palette
  const colorPalette = getAllColors();

  function handleColorClick(color) {
    selectedColor = color.hex;
    onChange(color.hex);
  }

  function getGroupLabel(id) {
    if (id === 0) return "Terrain";
    if (id === 8) return "Markers";
    if (id === 16) return "Greyscale";
    if (id === 24) return "Accents";
    return "";
  }
</script>

<div class="color-palette">
  <div class="palette-title">uDOS 32-Color Palette v{UDOS_PALETTE.version}</div>

  {#each [0, 8, 16, 24] as groupStart}
    {#if getGroupLabel(groupStart)}
      <div class="group-label">{getGroupLabel(groupStart)}</div>
    {/if}
    <div class="color-row">
      {#each colorPalette.slice(groupStart, groupStart + 8) as color}
        <button
          class="color-swatch"
          class:selected={selectedColor === color.hex}
          style="background-color: {color.hex};"
          onclick={() => handleColorClick(color)}
          title="{color.name} ({color.hex})"
          aria-label="Color {color.name}"
        >
          <span class="color-id">{color.id}</span>
        </button>
      {/each}
    </div>
  {/each}

  <!-- Custom color picker -->
  <div class="custom-color-section">
    <label for="custom-color" class="text-sm text-gray-300">Custom:</label>
    <div class="flex gap-2">
      <input
        id="custom-color"
        type="color"
        value={selectedColor}
        oninput={(e) => {
          selectedColor = e.currentTarget.value;
          onChange(selectedColor);
        }}
        class="w-12 h-8 rounded border border-gray-600 cursor-pointer bg-gray-700"
      />
      <input
        type="text"
        value={selectedColor}
        oninput={(e) => {
          selectedColor = e.currentTarget.value;
          onChange(selectedColor);
        }}
        class="flex-1 bg-gray-700 text-gray-100 border border-gray-600 rounded px-2 py-1 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="#000000"
      />
    </div>
  </div>
</div>

<style>
  .color-palette {
    padding: 1rem;
    background-color: rgb(31, 41, 55);
    border-radius: 0.375rem;
    border: 1px solid rgb(55, 65, 81);
  }

  .palette-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: rgb(209, 213, 219);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
  }

  .group-label {
    font-size: 0.625rem;
    color: rgb(156, 163, 175);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0.5rem 0 0.25rem 0;
    font-weight: 600;
  }

  .color-row {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 0.25rem;
    margin-bottom: 0.5rem;
  }

  .color-swatch {
    aspect-ratio: 1;
    border-radius: 0.25rem;
    border: 2px solid rgb(75, 85, 99);
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    padding: 0;
  }

  .color-swatch:hover {
    transform: scale(1.1);
    border-color: rgb(156, 163, 175);
  }

  .color-swatch.selected {
    border-color: white;
    box-shadow: 0 0 0 2px rgb(59, 130, 246);
  }

  .color-id {
    position: absolute;
    bottom: 1px;
    right: 2px;
    color: white;
    text-shadow:
      0 0 2px black,
      0 0 2px black;
    font-weight: bold;
    pointer-events: none;
  }

  .custom-color-section {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgb(55, 65, 81);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
</style>
