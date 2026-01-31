<script>
  import ColorPalette from "$lib/components/ColorPalette.svelte";
  import SVGCanvas from "$lib/components/SVGCanvas.svelte";
  import {
    quantizeToUdosPalette,
    getPaletteColor,
    getPaletteColorName,
    exportPaletteData,
  } from "$lib/util/colorQuantizer";

  let svgContent = "";
  let processedSvg = "";
  let colorMap = [];
  let error = null;
  let selectedColor = "#ffffff";
  let paletteData = exportPaletteData();

  function isValidSvg(text) {
    return text.includes("<svg") && text.includes("</svg>");
  }

  function normalizeHex(hex) {
    if (hex.length === 4) {
      return (
        "#" +
        hex
          .slice(1)
          .split("")
          .map((c) => c + c)
          .join("")
      );
    }
    return hex.toLowerCase();
  }

  function rgbToHex(rgb) {
    const match = rgb
      .replace(/\s+/g, "")
      .match(/rgb\((\d+),(\d+),(\d+)\)/i);
    if (!match) return null;
    const r = Number(match[1]);
    const g = Number(match[2]);
    const b = Number(match[3]);
    const toHex = (value) => value.toString(16).padStart(2, "0");
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  }

  function extractColors(svg) {
    const hexMatches = svg.match(/#[0-9a-fA-F]{3,6}/g) || [];
    const rgbMatches = svg.match(/rgb\([^\)]+\)/gi) || [];
    const colors = new Set();

    hexMatches.forEach((value) => colors.add(normalizeHex(value)));
    rgbMatches.forEach((value) => {
      const hex = rgbToHex(value);
      if (hex) colors.add(hex.toLowerCase());
    });

    return Array.from(colors);
  }

  function buildColorMap(colors) {
    return colors.map((original) => {
      const paletteIndex = quantizeToUdosPalette(original);
      const mapped = getPaletteColor(paletteIndex);
      return {
        original,
        mapped,
        index: paletteIndex,
        name: getPaletteColorName(paletteIndex),
      };
    });
  }

  function applyPalette(svg, map) {
    let output = svg;
    map.forEach((entry) => {
      const escaped = entry.original.replace("#", "\\#");
      const hexRegex = new RegExp(escaped, "gi");
      output = output.replace(hexRegex, entry.mapped);

      const rgb = entry.original
        ? `rgb(${parseInt(entry.original.slice(1, 3), 16)}, ${parseInt(
            entry.original.slice(3, 5),
            16
          )}, ${parseInt(entry.original.slice(5, 7), 16)})`
        : null;
      if (rgb) {
        const rgbRegex = new RegExp(rgb.replace(/[.*+?^${}()|[\\]\\]/g, "\\$&"), "gi");
        output = output.replace(rgbRegex, entry.mapped);
      }
    });
    return output;
  }

  async function handleFileChange(event) {
    const file = event.target.files[0];
    if (!file) return;
    const text = await file.text();
    if (!isValidSvg(text)) {
      error = "Invalid SVG file";
      return;
    }
    svgContent = text;
    processSvg();
  }

  function processSvg() {
    if (!isValidSvg(svgContent)) {
      error = "SVG content is missing or invalid.";
      return;
    }
    error = null;
    const colors = extractColors(svgContent);
    colorMap = buildColorMap(colors);
    processedSvg = applyPalette(svgContent, colorMap);
  }

  function downloadSvg(content, filename) {
    const blob = new Blob([content], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">SVG Palette Tooling</h1>
    <p class="text-gray-400">
      Quantize SVG colors into the uDOS 32-color palette and preview the output
    </p>
  </div>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
      {error}
    </div>
  {/if}

  <div class="grid grid-cols-1 xl:grid-cols-[360px_1fr] gap-6">
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-4">
      <div>
        <label for="svg-input" class="text-xs uppercase text-gray-400"
          >SVG Input</label
        >
        <input id="svg-input" type="file" accept=".svg" on:change={handleFileChange} />
      </div>

      <textarea
        class="w-full h-56 bg-gray-900 border border-gray-700 rounded p-3 text-xs font-mono"
        bind:value={svgContent}
        on:input={processSvg}
      ></textarea>

      <button
        class="w-full px-3 py-2 rounded bg-blue-600 hover:bg-blue-500"
        on:click={processSvg}
      >
        Quantize to Palette
      </button>

      <button
        class="w-full px-3 py-2 rounded bg-gray-700 hover:bg-gray-600"
        on:click={() => downloadSvg(processedSvg || svgContent, "udos-svg.svg")}
        disabled={!svgContent}
      >
        Download SVG
      </button>

      <div class="text-xs text-gray-500">
        Colors found: {colorMap.length}
</div>
</div>

<div class="tool-notes">
  <p>
    SVG Processor outputs diagrams that feed the Font Manager/Pixel/Layer editors via the GUI file picker.
    Use the workspace selector to load seeded SVG prompts from <code>core/framework/seed/bank/graphics/diagrams</code>
    before exporting to Sonic USB payloads or the media player.
  </p>
</div>

<style>
  .tool-notes {
    max-width: 960px;
    margin: 1.5rem auto;
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.4);
    color: #cbd5f5;
    font-size: 0.95rem;
  }
</style>

    <div class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h2 class="font-semibold mb-3">Original Preview</h2>
          {#if svgContent}
            <SVGCanvas svg={svgContent} width={420} height={320} />
          {:else}
            <div class="text-gray-400 text-sm">Load an SVG to preview.</div>
          {/if}
        </div>

        <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h2 class="font-semibold mb-3">Quantized Preview</h2>
          {#if processedSvg}
            <SVGCanvas svg={processedSvg} width={420} height={320} />
          {:else}
            <div class="text-gray-400 text-sm">Quantized output appears here.</div>
          {/if}
        </div>
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h2 class="font-semibold mb-3">Palette Mapping</h2>
        {#if !colorMap.length}
          <div class="text-gray-400 text-sm">No colors detected yet.</div>
        {:else}
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            {#each colorMap as entry}
              <div class="bg-gray-900 border border-gray-700 rounded p-3 flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span class="w-4 h-4 rounded" style="background: {entry.original};"></span>
                  <span class="text-xs text-gray-300">{entry.original}</span>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-xs text-gray-400">→</span>
                  <span class="w-4 h-4 rounded" style="background: {entry.mapped};"></span>
                  <span class="text-xs text-gray-300">{entry.mapped}</span>
                  <span class="text-xs text-gray-500">{entry.name}</span>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h2 class="font-semibold mb-3">uDOS Palette</h2>
        <ColorPalette bind:selectedColor={selectedColor} onChange={() => {}} />
        <div class="text-xs text-gray-400 mt-2">
          Selected color: {selectedColor}
        </div>
      </div>
    </div>
  </div>
</div>
