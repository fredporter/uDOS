<script>
  import { onMount } from "svelte";

  let binders = [];
  let loading = true;
  let error = null;
  let compiling = false;

  async function loadBinders() {
    try {
      const res = await fetch("/api/v1/binder/all");
      if (res.ok) {
        binders = await res.json();
      }
      loading = false;
    } catch (err) {
      error = `Failed to load binders: ${err.message}`;
      loading = false;
    }
  }

  async function compileBinder(binderId, format) {
    compiling = true;
    try {
      const res = await fetch(`/api/v1/binder/${binderId}/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ format }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = await res.json();
      alert(`Compiled ${format}: ${result.output_path}`);
      await loadBinders();
    } catch (err) {
      error = `Failed to compile: ${err.message}`;
    }
    compiling = false;
  }

  onMount(loadBinders);

  function getFormatIcon(format) {
    switch (format) {
      case "markdown":
        return "📝";
      case "pdf":
        return "📄";
      case "json":
        return "📊";
      case "brief":
        return "📋";
      default:
        return "📦";
    }
  }

  function getStatusClass(status) {
    switch (status) {
      case "compiled":
        return "bg-green-900 text-green-200 border-green-700";
      case "compiling":
        return "bg-blue-900 text-blue-200 border-blue-700";
      case "failed":
        return "bg-red-900 text-red-200 border-red-700";
      default:
        return "bg-gray-700 text-gray-300 border-gray-600";
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Binder Compiler</h1>
  <p class="text-gray-400 mb-8">
    Multi-format document compilation (Markdown, PDF, JSON, Brief)
  </p>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading binders...</div>
  {:else if binders.length === 0}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center">
      <p class="text-gray-400">No binders found. Create one via API or CLI.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-6">
      {#each binders as binder}
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="text-xl font-semibold text-white">{binder.name}</h3>
              {#if binder.description}
                <p class="text-gray-400 text-sm mt-1">{binder.description}</p>
              {/if}
            </div>
            <span
              class="px-2 py-1 rounded text-xs border {getStatusClass(
                binder.status,
              )}"
            >
              {binder.status}
            </span>
          </div>

          <div class="grid grid-cols-3 gap-4 text-sm mb-4">
            <div>
              <span class="text-gray-400">Chapters:</span>
              <span class="text-white ml-2">{binder.chapter_count || 0}</span>
            </div>
            <div>
              <span class="text-gray-400">Word Count:</span>
              <span class="text-white ml-2">{binder.word_count || 0}</span>
            </div>
            <div>
              <span class="text-gray-400">Last Updated:</span>
              <span class="text-white ml-2">
                {new Date(binder.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          <!-- Compile Actions -->
          <div class="border-t border-gray-700 pt-4">
            <h4 class="text-sm font-semibold text-gray-400 mb-3">
              Compile To:
            </h4>
            <div class="flex gap-2">
              {#each ["markdown", "pdf", "json", "brief"] as format}
                <button
                  on:click={() => compileBinder(binder.id, format)}
                  disabled={compiling}
                  class="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition flex items-center gap-2"
                >
                  <span>{getFormatIcon(format)}</span>
                  <span class="capitalize">{format}</span>
                </button>
              {/each}
            </div>
          </div>

          <!-- Recent Outputs -->
          {#if binder.outputs && binder.outputs.length > 0}
            <div class="border-t border-gray-700 mt-4 pt-4">
              <h4 class="text-sm font-semibold text-gray-400 mb-3">
                Recent Outputs:
              </h4>
              <div class="space-y-2">
                {#each binder.outputs as output}
                  <div
                    class="flex items-center justify-between bg-gray-900 border border-gray-700 rounded p-2"
                  >
                    <div class="flex items-center gap-2">
                      <span class="text-lg">{getFormatIcon(output.format)}</span
                      >
                      <span class="text-white text-sm">{output.format}</span>
                    </div>
                    <div class="text-xs text-gray-400">
                      {new Date(output.created_at).toLocaleString()}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
