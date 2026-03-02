<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onDestroy, onMount, tick } from "svelte";

  let binders = [];
  let loading = true;
  let error = null;
  let compiling = false;
  let fileLocations = null;
  let locationsError = null;
  let selectedBinderId = null;
  let requestedBinderId = null;
  let binderSearch = "";
  let binderStatusFilter = "all";
  let sharedView = false;
  let shareLinkCopied = false;
  let shareResetTimer = null;
  let restoredFromSession = false;
  let cacheInvalidationNotice = null;
  let cacheNoticeTimer = null;
  let pendingScrollRestore = false;

  const binderSessionKey = "wizard:binder:view-state";

  function captureScrollPosition() {
    if (typeof window === "undefined") return 0;
    return window.scrollY || window.pageYOffset || 0;
  }

  async function loadBinders() {
    try {
      const res = await apiFetch("/api/binder/all");
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
      const res = await apiFetch(`/api/binder/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ binder_id: binderId, formats: [format] }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = await res.json();
      const output = result.outputs?.[0]?.path || "output";
      alert(`Compiled ${format}: ${output}`);
      await loadBinders();
    } catch (err) {
      error = `Failed to compile: ${err.message}`;
    }
    compiling = false;
  }

  async function loadFileLocations() {
    try {
      const res = await apiFetch("/api/config/wizard");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      fileLocations = data?.content?.file_locations || null;
    } catch (err) {
      locationsError = `Failed to load file locations: ${err.message}`;
    }
  }

  onMount(loadBinders);
  onMount(loadFileLocations);

  function readRouteState() {
    const hash = typeof window !== "undefined" ? window.location.hash || "" : "";
    const [, rawQuery = ""] = hash.split("?");
    const params = new URLSearchParams(rawQuery);
    requestedBinderId = params.get("binder");
    binderSearch = params.get("search") || "";
    binderStatusFilter = params.get("status") || "all";
    sharedView = params.has("binder") || params.has("search") || params.has("status");
  }

  function persistRouteState() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (selectedBinderId) params.set("binder", selectedBinderId);
    if (binderSearch) params.set("search", binderSearch);
    if (binderStatusFilter !== "all") params.set("status", binderStatusFilter);
    const query = params.toString();
    const nextHash = query ? `binder?${query}` : "binder";
    if (window.location.hash.slice(1) !== nextHash) {
      window.history.replaceState(null, "", `#${nextHash}`);
    }
  }

  function currentShareLabels() {
    const labels = [];
    if (selectedBinderId) labels.push(`binder=${selectedBinderId}`);
    if (binderSearch) labels.push(`search=${binderSearch}`);
    if (binderStatusFilter !== "all") labels.push(`status=${binderStatusFilter}`);
    return labels;
  }

  function clearSharedView() {
    restoredFromSession = false;
    selectedBinderId = null;
    requestedBinderId = null;
    binderSearch = "";
    binderStatusFilter = "all";
    sharedView = false;
    persistRouteState();
    persistViewState();
  }

  function clearFilters() {
    clearSharedView();
  }

  function selectBinder(binderId) {
    restoredFromSession = false;
    selectedBinderId = binderId;
    requestedBinderId = binderId;
    sharedView = Boolean(binderId);
    persistRouteState();
    persistViewState();
  }

  async function copyShareLink() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (selectedBinderId) params.set("binder", selectedBinderId);
    if (binderSearch) params.set("search", binderSearch);
    if (binderStatusFilter !== "all") params.set("status", binderStatusFilter);
    const query = params.toString();
    const url = `${window.location.origin}${window.location.pathname}#${query ? `binder?${query}` : "binder"}`;
    try {
      await navigator.clipboard.writeText(url);
      shareLinkCopied = true;
      if (shareResetTimer) window.clearTimeout(shareResetTimer);
      shareResetTimer = window.setTimeout(() => {
        shareLinkCopied = false;
      }, 1500);
    } catch (err) {
      error = `Failed to copy share link: ${err.message || err}`;
    }
  }

  function persistViewState() {
    if (typeof window === "undefined") return;
    window.sessionStorage.setItem(
      binderSessionKey,
      JSON.stringify({
        selectedBinderId,
        binderSearch,
        binderStatusFilter,
        scrollY: captureScrollPosition(),
      }),
    );
  }

  function restoreViewState() {
    if (typeof window === "undefined") return;
    const raw = window.sessionStorage.getItem(binderSessionKey);
    if (!raw) return;
    try {
      const payload = JSON.parse(raw);
      if (!payload || typeof payload !== "object") return;
      if (!requestedBinderId && payload.selectedBinderId) {
        requestedBinderId = payload.selectedBinderId;
        restoredFromSession = true;
        sharedView = true;
      }
      if (!binderSearch && typeof payload.binderSearch === "string") {
        binderSearch = payload.binderSearch;
        restoredFromSession = restoredFromSession || payload.binderSearch.length > 0;
        sharedView = sharedView || payload.binderSearch.length > 0;
      }
      if (binderStatusFilter === "all" && typeof payload.binderStatusFilter === "string" && payload.binderStatusFilter) {
        binderStatusFilter = payload.binderStatusFilter;
        restoredFromSession = restoredFromSession || payload.binderStatusFilter !== "all";
        sharedView = sharedView || payload.binderStatusFilter !== "all";
      }
      if (typeof payload.scrollY === "number") {
        pendingScrollRestore = true;
      }
    } catch {
      window.sessionStorage.removeItem(binderSessionKey);
    }
  }

  function invalidateViewState() {
    if (typeof window === "undefined") return;
    window.sessionStorage.removeItem(binderSessionKey);
  }

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

  onMount(() => {
    readRouteState();
    restoreViewState();
    if (typeof window !== "undefined") {
      window.addEventListener("scroll", persistViewState, { passive: true });
    }
  });

  onDestroy(() => {
    if (typeof window !== "undefined") {
      window.removeEventListener("scroll", persistViewState);
    }
    if (shareResetTimer) clearTimeout(shareResetTimer);
    if (cacheNoticeTimer) clearTimeout(cacheNoticeTimer);
  });

  $: if (binders.length > 0 && requestedBinderId && !selectedBinderId) {
    const knownBinder = binders.find((binder) => String(binder.id) === String(requestedBinderId));
    if (knownBinder) {
      selectedBinderId = knownBinder.id;
      persistRouteState();
      persistViewState();
    } else {
      const staleBinder = requestedBinderId;
      selectedBinderId = null;
      requestedBinderId = null;
      restoredFromSession = false;
      invalidateViewState();
      persistRouteState();
      cacheInvalidationNotice = `Cached binder ${staleBinder} was cleared because it is no longer available.`;
      if (cacheNoticeTimer) clearTimeout(cacheNoticeTimer);
      cacheNoticeTimer = setTimeout(() => {
        cacheInvalidationNotice = null;
      }, 4000);
    }
  }

  $: if (pendingScrollRestore && restoredFromSession && selectedBinderId) {
    pendingScrollRestore = false;
    tick().then(() => {
      const selectedCard =
        typeof document !== "undefined"
          ? document.querySelector(`[data-binder-id="${selectedBinderId}"]`)
          : null;
      if (selectedCard && typeof selectedCard.scrollIntoView === "function") {
        selectedCard.scrollIntoView({ block: "center", behavior: "auto" });
      }
    });
  }

  $: filteredBinders = binders.filter((binder) => {
    const matchesSearch =
      !binderSearch ||
      `${binder.name || ""} ${binder.description || ""}`.toLowerCase().includes(binderSearch.toLowerCase());
    const matchesStatus = binderStatusFilter === "all" || binder.status === binderStatusFilter;
    return matchesSearch && matchesStatus;
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <div class="mb-8 flex items-start justify-between gap-4">
    <div>
      <div class="mb-3 flex flex-wrap items-center gap-2">
        <h1 class="text-3xl font-bold text-white">Binder Compiler</h1>
        {#if restoredFromSession}
          <div class="rounded-full border border-cyan-700 bg-cyan-950/30 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-cyan-200">
            Restored
          </div>
        {/if}
        {#if sharedView}
          <div class="flex flex-wrap items-center gap-2">
            <div class="rounded-full border border-violet-700 bg-violet-950/40 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-violet-200">
              Shared View
            </div>
            {#each currentShareLabels() as label}
              <div class="rounded border border-violet-800 bg-violet-950/20 px-2 py-1 text-[11px] text-violet-100">
                {label}
              </div>
            {/each}
            <button
              type="button"
              class="rounded border border-violet-700 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-violet-200 hover:bg-violet-950/40"
              on:click={clearSharedView}
            >
              Dismiss
            </button>
          </div>
        {/if}
      </div>
      <p class="text-gray-400">
        Multi-format document compilation (Markdown, PDF, JSON, Brief)
      </p>
    </div>
    <button
      type="button"
      class="rounded-lg border border-gray-700 bg-gray-800 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-700"
      on:click={copyShareLink}
    >
      {shareLinkCopied ? "Copied" : "Copy Share Link"}
    </button>
    <button
      type="button"
      class="rounded-lg border border-gray-700 bg-gray-800 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-700"
      on:click={clearFilters}
    >
      Clear Filters
    </button>
  </div>

  <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-[1fr_220px]">
    <div>
      <label class="mb-2 block text-xs uppercase tracking-[0.2em] text-gray-400" for="binder-search">
        Binder Search
      </label>
      <input
        id="binder-search"
        bind:value={binderSearch}
        on:input={() => {
          restoredFromSession = false;
          sharedView = Boolean(selectedBinderId) || binderSearch.length > 0 || binderStatusFilter !== "all";
          persistRouteState();
          persistViewState();
        }}
        class="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white"
        placeholder="Search binders"
      />
    </div>
    <div>
      <label class="mb-2 block text-xs uppercase tracking-[0.2em] text-gray-400" for="binder-status-filter">
        Binder Status
      </label>
      <select
        id="binder-status-filter"
        bind:value={binderStatusFilter}
        on:change={() => {
          restoredFromSession = false;
          sharedView = Boolean(selectedBinderId) || binderSearch.length > 0 || binderStatusFilter !== "all";
          persistRouteState();
          persistViewState();
        }}
        class="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white"
      >
        <option value="all">All statuses</option>
        <option value="compiled">Compiled</option>
        <option value="compiling">Compiling</option>
        <option value="failed">Failed</option>
      </select>
    </div>
  </div>

  {#if locationsError}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6">
      {locationsError}
    </div>
  {/if}

  {#if fileLocations}
    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-6 text-sm">
      <div class="text-gray-400">File Locations</div>
      <div class="text-white">
        <div>Repo Root: {fileLocations.repo_root_actual || "auto"}</div>
        <div>Memory Root: {fileLocations.memory_root_actual || fileLocations.memory_root}</div>
      </div>
    </div>
  {/if}

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  {#if cacheInvalidationNotice}
    <div class="bg-amber-950/60 text-amber-100 p-4 rounded-lg border border-amber-700 mb-6">
      {cacheInvalidationNotice}
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading binders...</div>
  {:else if binders.length === 0}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center">
      <p class="text-gray-400">No binders found. Create one via API or CLI.</p>
    </div>
  {:else if filteredBinders.length === 0}
    <div class="bg-gray-800 border border-dashed border-gray-700 rounded-lg p-8 text-center">
      <p class="mb-2 font-medium text-white">No binders match the current filters.</p>
      <p class="text-sm text-gray-400">Clear the search or status filter to see the full binder set again.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-6">
      {#each filteredBinders as binder}
        <div
          data-binder-id={binder.id}
          class="bg-gray-800 border rounded-lg p-6"
          class:border-cyan-500={selectedBinderId === binder.id}
          class:border-gray-700={selectedBinderId !== binder.id}
        >
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="text-xl font-semibold text-white">{binder.name}</h3>
              {#if binder.description}
                <p class="text-gray-400 text-sm mt-1">{binder.description}</p>
              {/if}
            </div>
            <div class="flex items-center gap-2">
              {#if selectedBinderId === binder.id}
                <span class="rounded-full border border-cyan-700 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-cyan-200">
                  Selected
                </span>
              {/if}
              <span
                class="px-2 py-1 rounded text-xs border {getStatusClass(
                  binder.status,
                )}"
              >
                {binder.status}
              </span>
            </div>
          </div>

          <div class="mb-4">
            <button
              type="button"
              class="rounded border border-cyan-700 px-3 py-1.5 text-sm text-cyan-200 hover:bg-cyan-950/30"
              on:click={() => selectBinder(binder.id)}
            >
              Focus Binder
            </button>
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
          {:else}
            <div class="border-t border-gray-700 mt-4 pt-4">
              <h4 class="text-sm font-semibold text-gray-400 mb-3">
                Recent Outputs:
              </h4>
              <div class="rounded border border-dashed border-gray-700 bg-gray-900/50 px-3 py-4 text-sm text-gray-400">
                No compiled outputs yet for this binder.
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>
