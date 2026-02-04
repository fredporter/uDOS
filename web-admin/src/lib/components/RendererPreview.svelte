<script lang="ts">
  import { browser } from "$app/environment";
  import { getSiteFiles } from "$lib/services/rendererService";

  export let siteExports: { theme: string; files: number; lastModified: string | null }[] = [];

  let selectedTheme = siteExports[0]?.theme ?? "";
  let files: { path: string; size: number; updatedAt: string | null }[] = [];
  let loading = false;
  let loadedTheme = "";

  $: if (browser && selectedTheme && selectedTheme !== loadedTheme) {
    loadFiles(selectedTheme);
  }

  $: if (siteExports.length && !siteExports.some((entry) => entry.theme === selectedTheme)) {
    selectedTheme = siteExports[0]?.theme ?? "";
  }

  async function loadFiles(theme: string) {
    if (!browser) return;
    loading = true;
    const payload = await getSiteFiles(fetch, theme);
    files = payload?.files ?? [];
    loading = false;
    loadedTheme = theme;
  }
</script>

<section class="renderer-preview">
  <h3>Renderer preview</h3>
  <label for="theme">Theme</label>
  <select id="theme" bind:value={selectedTheme}>
    {#each siteExports as export}
      <option value={export.theme}>{export.theme}</option>
    {/each}
  </select>
  <div class="summary">
    {#if loading}
      <p>Loading...</p>
    {:else if files.length}
      <p>{files.length} files for {selectedTheme}</p>
      <ul>
        {#each files as file}
          <li>{file.path} ({Math.round(file.size / 1024)} KB) {file.updatedAt}</li>
        {/each}
      </ul>
    {:else}
      <p>No files yet.</p>
    {/if}
  </div>
</section>

<style>
  .renderer-preview {
    border: 1px solid rgba(59, 130, 246, 0.4);
    border-radius: 0.75rem;
    padding: 1rem;
    background: rgba(15, 23, 42, 0.85);
  }

  .renderer-preview select {
    width: 100%;
    margin-bottom: 0.75rem;
  }

  .renderer-preview ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .renderer-preview li {
    font-size: 0.85rem;
    color: #cbd5f5;
    margin-bottom: 0.25rem;
  }
</style>
