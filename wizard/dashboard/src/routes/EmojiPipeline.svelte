<script>
  import { onMount } from "svelte";
  import { extractGlyphsFromFont } from "$lib/util/fontToSvg";
  import {
    EMOJI_COLOR_FULL,
    EMOJI_MONO_FULL,
    EMOJI_FACES,
    EMOJI_SYMBOLS,
  } from "$lib/util/characterDatasets";

  let adminToken = "";
  let fonts = [];
  let selectedFontId = "";
  let glyphs = [];
  let limit = 96;
  let loading = false;
  let error = null;
  let lastLoaded = null;

  const emojiSets = [
    { id: "emoji-color", label: EMOJI_COLOR_FULL.name, set: EMOJI_COLOR_FULL },
    { id: "emoji-mono", label: EMOJI_MONO_FULL.name, set: EMOJI_MONO_FULL },
    { id: "emoji-faces", label: EMOJI_FACES.name, set: EMOJI_FACES },
    { id: "emoji-symbols", label: EMOJI_SYMBOLS.name, set: EMOJI_SYMBOLS },
  ];

  let selectedSetId = emojiSets[0].id;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  function getSelectedSet() {
    return emojiSets.find((item) => item.id === selectedSetId)?.set;
  }

  function buildFontList(manifest) {
    const list = [];
    for (const [collectionName, collection] of Object.entries(
      manifest.collections || {}
    )) {
      for (const [subcategoryName, subcategory] of Object.entries(collection)) {
        for (const [fontKey, fontData] of Object.entries(subcategory)) {
          list.push({
            id: fontKey,
            name: fontData.name,
            file: fontData.file,
            type: fontData.type,
            author: fontData.author,
            license: fontData.license,
            description: fontData.description,
            category: `${collectionName}/${subcategoryName}`,
          });
        }
      }
    }
    return list;
  }

  async function loadManifest() {
    const res = await fetch("/api/v1/fonts/manifest", {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const manifest = await res.json();
    fonts = buildFontList(manifest);
    if (!selectedFontId && fonts.length) {
      const emojiFont =
        fonts.find((font) => font.id === "NotoEmoji") ||
        fonts.find((font) => (font.category || "").includes("emoji/mono")) ||
        fonts.find((font) => font.category.startsWith("emoji/"));
      selectedFontId = (emojiFont || fonts[0]).id;
    }
  }

  function getSelectedFont() {
    return fonts.find((font) => font.id === selectedFontId) || null;
  }

  function isColorEmojiFont(font) {
    if (!font) return false;
    return (font.category || "").includes("emoji/color") || font.id === "NotoColorEmoji";
  }

  function getFontUrl(font) {
    return `/api/v1/fonts/file?path=${encodeURIComponent(font.file)}`;
  }

  async function loadGlyphs() {
    const selectedFont = getSelectedFont();
    if (!selectedFont) return;
    loading = true;
    error = null;
    try {
      const set = getSelectedSet();
      if (!set) throw new Error("No emoji set selected");
      if (isColorEmojiFont(selectedFont)) {
        const fallback =
          fonts.find((font) => font.id === "NotoEmoji") ||
          fonts.find((font) => (font.category || "").includes("emoji/mono"));
        if (fallback) {
          selectedFontId = fallback.id;
        }
        throw new Error(
          "Color emoji fonts (CBDT) are not supported for SVG extraction. Switched to Noto Emoji (outline)."
        );
      }
      const codes = set.codes.slice(0, Math.max(1, limit));
      const fontUrl = getFontUrl(selectedFont);
      const result = await extractGlyphsFromFont(fontUrl, codes);
      glyphs = result;
      lastLoaded = {
        font: selectedFont.name,
        set: set.name,
        count: result.length,
      };
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loading = false;
    }
  }

  function downloadJson() {
    if (!glyphs.length) return;
    const payload = {
      font: getSelectedFont()?.name || "Unknown",
      set: getSelectedSet()?.name || "Unknown",
      generatedAt: new Date().toISOString(),
      glyphs,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `emoji-glyphs-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  onMount(async () => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    try {
      await loadManifest();
    } catch (err) {
      error = err.message || String(err);
    }
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">Emoji Font Pipeline</h1>
    <p class="text-gray-400">
      Extract emoji glyphs to SVG and build dataset exports for the Wizard toolchain
    </p>
  </div>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
      {error}
    </div>
  {/if}

  <div class="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-4">
      <div>
        <label for="emoji-font" class="text-xs uppercase text-gray-400">Font</label>
        <select
          id="emoji-font"
          class="mt-1 w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
          bind:value={selectedFontId}
          on:change={loadGlyphs}
        >
          {#each fonts as font}
            <option value={font.id}>{font.name} — {font.category}</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="emoji-dataset" class="text-xs uppercase text-gray-400"
          >Emoji Dataset</label
        >
        <select
          id="emoji-dataset"
          class="mt-1 w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
          bind:value={selectedSetId}
        >
          {#each emojiSets as option}
            <option value={option.id}>{option.label}</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="emoji-preview-limit" class="text-xs uppercase text-gray-400"
          >Preview Limit</label
        >
        <input
          id="emoji-preview-limit"
          class="mt-1 w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
          type="number"
          min="1"
          max="512"
          bind:value={limit}
        />
      </div>

      <button
        class="w-full px-3 py-2 rounded bg-blue-600 hover:bg-blue-500"
        on:click={loadGlyphs}
        disabled={loading}
      >
        {loading ? "Extracting…" : "Extract Glyphs"}
      </button>

      <button
        class="w-full px-3 py-2 rounded bg-gray-700 hover:bg-gray-600"
        on:click={downloadJson}
        disabled={!glyphs.length}
      >
        Download JSON Export
      </button>

      {#if lastLoaded}
        <div class="text-xs text-gray-400">
          Loaded {lastLoaded.count} glyphs from {lastLoaded.font} ({lastLoaded.set})
        </div>
      {/if}

      <div class="text-xs text-gray-500">
        Tip: color emoji fonts may fail to parse in SVG mode; use the monochrome
        emoji font for extraction.
      </div>
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <h2 class="font-semibold mb-3">Glyph Preview</h2>
      {#if !glyphs.length}
        <div class="text-gray-400 text-sm">No glyphs loaded yet.</div>
      {:else}
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 gap-3">
          {#each glyphs as glyph}
            <div class="bg-gray-900 border border-gray-700 rounded p-3 text-center">
              <div class="text-2xl text-white" aria-hidden="true">
                {@html glyph.svg}
              </div>
              <div class="text-xs text-gray-400 mt-2">
                {glyph.char} • U+{glyph.unicode.toString(16).toUpperCase()}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>
