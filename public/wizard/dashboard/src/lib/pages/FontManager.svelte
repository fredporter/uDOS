<script>
  import { onMount } from 'svelte';

  let collections = [];
  let selectedCollection = '';
  let characters = [];
  let searchQuery = '';
  let loading = false;
  let error = null;

  async function loadCollections() {
    loading = true;
    error = null;
    try {
      const resp = await fetch('/api/v1/fonts/collections');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      collections = data.collections || [];
      if (collections.length > 0 && !selectedCollection) {
        selectedCollection = collections[0].name;
        await loadCharacters(selectedCollection);
      }
    } catch (e) {
      error = `Failed to load collections: ${e.message}`;
      console.error('Font collections error:', e);
    } finally {
      loading = false;
    }
  }

  async function loadCharacters(collectionName) {
    if (!collectionName) return;
    loading = true;
    error = null;
    try {
      const resp = await fetch(`/api/v1/fonts/characters/${collectionName}?limit=200`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      characters = data.items || [];
    } catch (e) {
      error = `Failed to load characters: ${e.message}`;
      console.error('Font characters error:', e);
    } finally {
      loading = false;
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) {
      loadCharacters(selectedCollection);
      return;
    }
    loading = true;
    try {
      const resp = await fetch(`/api/v1/fonts/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await resp.json();
      characters = data.results || [];
    } catch (e) {
      error = `Search failed: ${e}`;
    } finally {
      loading = false;
    }
  }

  function copyToClipboard(char) {
    navigator.clipboard.writeText(char.utf8);
    alert(`Copied: ${char.utf8}`);
  }

  function exportCollection() {
    if (!selectedCollection) return;
    window.open(`/api/v1/fonts/${selectedCollection}/export?format=json`);
  }

  onMount(loadCollections);
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <!-- Header -->
  <header class="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 sticky top-0 z-10">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold mb-2">🔤 Font Manager</h1>
      <p class="text-purple-100">Browse, search, and manage character fonts</p>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-6xl mx-auto px-4 py-8">
    {#if error}
      <div class="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
        <p class="text-red-800 dark:text-red-200">{error}</p>
      </div>
    {/if}

    <!-- Controls -->
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Collection Select -->
        <div>
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            Font Collection
          </label>
          <select
            bind:value={selectedCollection}
            on:change={() => loadCharacters(selectedCollection)}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {#each collections as coll}
              <option value={coll.name}>
                {coll.family} ({coll.character_count} chars)
              </option>
            {/each}
          </select>
        </div>

        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            Search Characters
          </label>
          <input
            type="text"
            placeholder="Search by name..."
            bind:value={searchQuery}
            on:keyup={handleSearch}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
        </div>

        <!-- Actions -->
        <div class="flex items-end gap-2">
          <button
            on:click={exportCollection}
            class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            ⬇️ Export JSON
          </button>
        </div>
      </div>

      <p class="text-sm text-gray-600 dark:text-gray-400">
        {characters.length} characters found
      </p>
    </div>

    <!-- Character Grid -->
    {#if loading}
      <div class="flex justify-center py-12">
        <p class="text-gray-500 dark:text-gray-400">Loading characters...</p>
      </div>
    {:else if characters.length === 0}
      <div class="bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 text-center">
        <p class="text-yellow-800 dark:text-yellow-200">No characters found</p>
      </div>
    {:else}
      <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
        {#each characters as char}
          <button
            on:click={() => copyToClipboard(char)}
            class="aspect-square flex items-center justify-center bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-lg transition-all"
            title={char.name ? char.name : `U+${char.codepoint.toString(16).toUpperCase()}`}
          >
            <span class="text-3xl">{char.utf8}</span>
          </button>
        {/each}
      </div>
    {/if}
  </main>
</div>

<style lang="postcss">
  @reference "tailwindcss";
</style>
