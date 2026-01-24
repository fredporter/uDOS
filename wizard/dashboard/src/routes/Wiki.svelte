<script>
  import { onMount } from "svelte";

  let wikiData = null;
  let loading = true;
  let error = null;
  let selectedCategory = null;

  const osEmojis = {
    alpine: "🐧",
    macos: "🍎",
    ubuntu: "🐧",
    windows: "🪟",
  };

  async function loadWiki() {
    loading = true;
    error = null;
    try {
      const res = await fetch("/api/v1/wiki/structure");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      wikiData = await res.json();
      if (wikiData.categories && wikiData.categories.length > 0) {
        selectedCategory = wikiData.categories[0].slug;
      }
    } catch (err) {
      error = `Failed to load wiki: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  async function provisionWiki() {
    try {
      const res = await fetch("/api/v1/wiki/provision", { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = await res.json();
      alert(`Wiki provisioned: ${result.message}`);
      loadWiki();
    } catch (err) {
      alert(`Wiki provisioning failed: ${err.message}`);
    }
  }

  function getSelectedPages() {
    if (!wikiData || !selectedCategory) return [];
    return wikiData.pages.filter((p) => p.category === selectedCategory);
  }

  function getCategory(slug) {
    if (!wikiData) return null;
    return wikiData.categories.find((c) => c.slug === slug);
  }

  onMount(loadWiki);
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between gap-3">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Wiki</h1>
      <p class="text-gray-400">Public documentation and guides</p>
    </div>
    <button
      class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
      on:click={provisionWiki}
    >
      Provision Wiki
    </button>
  </div>

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading wiki...</div>
  {:else if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700">
      {error}
    </div>
  {:else if wikiData}
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Categories sidebar -->
      <div class="lg:col-span-1">
        <div
          class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2"
        >
          <h3 class="font-semibold text-white mb-4">Categories</h3>
          {#each wikiData.categories as category (category.slug)}
            <button
              class={`w-full text-left px-3 py-2 rounded-lg transition ${
                selectedCategory === category.slug
                  ? "bg-indigo-600 text-white"
                  : "hover:bg-gray-700 text-gray-300"
              }`}
              on:click={() => (selectedCategory = category.slug)}
            >
              <span class="mr-2">{category.icon}</span>
              {category.title}
            </button>
          {/each}
        </div>
      </div>

      <!-- Pages content -->
      <div class="lg:col-span-3 space-y-6">
        {#if getCategory(selectedCategory)}
          <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div>
              <h2
                class="text-2xl font-bold text-white mb-2 flex items-center gap-2"
              >
                <span>{getCategory(selectedCategory).icon}</span>
                {getCategory(selectedCategory).title}
              </h2>
              <p class="text-gray-400">
                {getCategory(selectedCategory).description}
              </p>
            </div>
          </div>
        {/if}

        <!-- Pages list -->
        <div class="space-y-3">
          {#each getSelectedPages() as page (page.slug)}
            <div
              class="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h3 class="text-lg font-semibold text-white">
                      {page.title}
                    </h3>
                    <span
                      class={`px-2 py-0.5 rounded text-xs font-semibold ${
                        page.status === "published"
                          ? "bg-green-900 text-green-100"
                          : page.status === "draft"
                            ? "bg-amber-900 text-amber-100"
                            : "bg-slate-700 text-slate-200"
                      }`}
                    >
                      {page.status}
                    </span>
                  </div>
                  <p class="text-gray-400 text-sm">{page.description}</p>
                </div>
              </div>
            </div>
          {/each}
        </div>

        {#if getSelectedPages().length === 0}
          <div class="text-center py-12 text-gray-400">
            No pages in this category yet
          </div>
        {/if}
      </div>
    </div>

    <!-- Wiki stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Total Pages</div>
        <div class="text-2xl font-bold text-white">
          {wikiData.pages?.length || 0}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Categories</div>
        <div class="text-2xl font-bold text-white">
          {wikiData.categories?.length || 0}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Published</div>
        <div class="text-2xl font-bold text-white">
          {wikiData.pages?.filter((p) => p.status === "published").length || 0}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Drafts</div>
        <div class="text-2xl font-bold text-white">
          {wikiData.pages?.filter((p) => p.status === "draft").length || 0}
        </div>
      </div>
    </div>
  {/if}
</div>
