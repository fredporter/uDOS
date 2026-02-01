<script>
  import { onMount } from "svelte";
  import { teletextFonts } from "../lib/typography.js";

  let adminToken = "";
  let fonts = [];
  let selectedFont = null;
  let fontSize = 16;
  let markdownContent = "";
  let renderedHtml = "";
  let loading = true;
  let error = null;
  let showTeletext = false;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  function renderMarkdown() {
    if (!markdownContent) {
      renderedHtml = "";
      return;
    }
    let html = markdownContent
      .replace(/^#### (.*$)/gim, "<h4>$1</h4>")
      .replace(/^### (.*$)/gim, "<h3>$1</h3>")
      .replace(/^## (.*$)/gim, "<h2>$1</h2>")
      .replace(/^# (.*$)/gim, "<h1>$1</h1>")
      .replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, "<code>$1</code>")
      .replace(/```([^`]+)```/g, "<pre><code>$1</code></pre>")
      .replace(/^> (.*$)/gim, "<blockquote>$1</blockquote>")
      .replace(/^\- (.*$)/gim, "<li>$1</li>")
      .replace(/^\d+\. (.*$)/gim, "<li>$1</li>")
      .replace(/^---$/gim, "<hr>")
      .replace(/\n\n/g, "</p><p>")
      .replace(/\n/g, "<br>");

    html = "<p>" + html + "</p>";
    html = html.replace(/<p><\/p>/g, "");
    html = html.replace(/<p><h/g, "<h").replace(/<\/h(\d)><\/p>/g, "</h$1>");
    html = html.replace(/<p><hr><\/p>/g, "<hr>");
    html = html.replace(/<p><pre>/g, "<pre>").replace(/<\/pre><\/p>/g, "</pre>");
    html = html.replace(
      /<p><blockquote>/g,
      "<blockquote>"
    ).replace(/<\/blockquote><\/p>/g, "</blockquote>");

    renderedHtml = html;
  }

  async function loadManifest() {
    const res = await fetch("/api/fonts/manifest", {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const manifest = await res.json();
    const list = [];
    for (const [collectionName, collection] of Object.entries(
      manifest.collections || {}
    )) {
      // Skip retro fonts - they're in the Teletext section
      if (collectionName === "retro") continue;
      
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
    fonts = list;
    if (fonts.length) {
      selectFont(fonts[0]);
    }
  }

  async function loadSample() {
    const res = await fetch("/api/fonts/sample", {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    markdownContent = await res.text();
    renderMarkdown();
  }

  async function selectFont(font) {
    selectedFont = font;
    try {
      const fontFace = new FontFace(
        font.name,
        `url(/api/fonts/file?path=${encodeURIComponent(font.file)})`
      );
      const loaded = await fontFace.load();
      document.fonts.add(loaded);
      renderMarkdown();
    } catch (err) {
      error = `Failed to load font: ${err.message}`;
    }
  }

  function adjustFontSize(delta) {
    fontSize = Math.max(8, Math.min(72, fontSize + delta));
  }

  onMount(async () => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    loading = true;
    error = null;
    try {
      await loadManifest();
      await loadSample();
    } catch (err) {
      error = `Failed to load fonts: ${err.message}`;
    } finally {
      loading = false;
    }
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">Font Manager</h1>
    <p class="text-gray-400">Manage and preview Wizard font collections</p>
  </div>

  <div class="mb-6 flex gap-2">
    <button
      class={`px-4 py-2 rounded ${showTeletext ? "bg-gray-700 text-gray-300" : "bg-purple-600 text-white"}`}
      on:click={() => (showTeletext = false)}
    >
      Prose & Code Fonts
    </button>
    <button
      class={`px-4 py-2 rounded ${showTeletext ? "bg-purple-600 text-white" : "bg-gray-700 text-gray-300"}`}
      on:click={() => (showTeletext = true)}
    >
      Teletext Fonts
    </button>
  </div>

  {#if showTeletext}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h2 class="text-xl font-semibold mb-4">Teletext & Retro Fonts</h2>
      <p class="text-gray-400 mb-4">
        These fonts are reserved for special rendering modes and will be mapped later.
      </p>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        {#each teletextFonts as font}
          <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
            <div class="font-semibold">{font.label}</div>
            <div class="text-sm text-gray-400 mb-2">{font.description}</div>
            <div
              class="text-xs text-gray-500 mt-2 font-mono"
              style="font-family: {font.stack}"
            >
              ABCDEFGHIJKLMNOPQRSTUVWXYZ<br />
              abcdefghijklmnopqrstuvwxyz<br />
              0123456789 !@#$%^&*()
            </div>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    {#if error}
      <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
        {error}
      </div>
    {/if}

    {#if loading}
      <div class="text-gray-400">Loading fonts...</div>
    {:else}
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
          <div class="p-4 border-b border-gray-700">
            <h2 class="font-semibold">Font Collections</h2>
            <div class="text-xs text-gray-400">{fonts.length} fonts</div>
          </div>
          <div class="max-h-[600px] overflow-y-auto">
            {#each fonts as font}
              <button
                class="w-full text-left p-3 border-b border-gray-700 hover:bg-gray-700 {selectedFont?.id === font.id ? 'bg-gray-700' : ''}"
                on:click={() => selectFont(font)}
              >
                <div class="font-semibold text-sm">{font.name}</div>
                <div class="text-xs text-gray-400">{font.category}</div>
                <div class="text-xs text-gray-500 mt-1">{font.author}</div>
              </button>
            {/each}
          </div>
        </div>

        <div class="lg:col-span-2">
          <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-sm text-gray-400">Selected</div>
                <div class="text-lg font-semibold">{selectedFont?.name || "—"}</div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                  on:click={() => adjustFontSize(-2)}
                >
                  A-
                </button>
                <div class="text-sm">{fontSize}px</div>
                <button
                  class="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                  on:click={() => adjustFontSize(2)}
                >
                  A+
                </button>
              </div>
            </div>
          </div>

          <div
            class="bg-gray-900 border border-gray-700 rounded-lg p-6 prose prose-invert max-w-none"
            style="font-family: '{selectedFont?.name}', monospace; font-size: {fontSize}px;"
          >
            {@html renderedHtml}
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<div class="tool-notes">
  <p>
    Use the workspace selector or the GUI file picker to import font files and seed collections
    from <code>core/framework/seed/bank/graphics</code>. Font Manager renders those assets in the
    workspace while the Pixel/Layer editors use the same file picker hooks for seeded map layers.
  </p>
</div>

<style>
  .tool-notes {
    max-width: 960px;
    margin: 1.5rem auto 0;
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.4);
    color: #cbd5f5;
    font-size: 0.95rem;
  }
</style>
