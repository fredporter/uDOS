<script>
  import { onMount } from "svelte";
  import { TileEditor, tileEditorStyles } from "../lib/tile-editor.js";

  let editor = null;

  function ensureStyles() {
    const existing = document.getElementById("wizard-tile-editor-styles");
    if (existing) return;
    const style = document.createElement("style");
    style.id = "wizard-tile-editor-styles";
    style.textContent = tileEditorStyles;
    document.head.appendChild(style);
  }

  onMount(() => {
    ensureStyles();
    editor = new TileEditor("wizard-pixel-editor", { gridSize: 24, cellSize: 20 });
    return () => {
      editor = null;
    };
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">Pixel Editor</h1>
    <p class="text-gray-400">24×24 tile editor with SVG/ASCII export</p>
  </div>

<div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
  <div id="wizard-pixel-editor"></div>
</div>
</div>

<div class="tool-notes">
  Seeded map layers live under <code>core/framework/seed/bank/graphics</code> and the workspace selector
  lets you pick a layer or font bundle before opening this editor. Every export can be pushed to the
  GUI file picker so Sonic/Font tooling stays in sync.
</div>

<style>
  .tool-notes {
    max-width: 960px;
    margin: 1.25rem auto 0;
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.4);
    color: #cbd5f5;
  }
</style>
