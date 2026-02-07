<script>
  import { onMount } from "svelte";
  import { getAdminToken } from "$lib/services/auth";
  import {
    listAnchors,
    getAnchor,
    bindAnchor,
  } from "$lib/services/anchorService";

  let adminToken = "";
  let anchors = [];
  let selectedAnchor = "";
  let anchorDetail = null;
  let loading = false;
  let error = "";
  let bindStatus = "";
  let bindError = "";

  let bindLocId = "";
  let bindAnchorId = "";
  let bindCoordKind = "tile";
  let bindCoordJson = "{ \"x\": 0, \"y\": 0 }";

  async function refreshAnchors() {
    loading = true;
    error = "";
    try {
      const payload = await listAnchors(adminToken);
      anchors = payload.anchors || [];
      if (!selectedAnchor && anchors.length) {
        selectedAnchor = anchors[0].anchor_id;
      }
      if (selectedAnchor) {
        await loadAnchor(selectedAnchor);
      }
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load anchors";
    } finally {
      loading = false;
    }
  }

  async function loadAnchor(anchorId) {
    if (!anchorId) return;
    anchorDetail = null;
    try {
      const payload = await getAnchor(anchorId, adminToken);
      anchorDetail = payload.anchor || null;
      bindAnchorId = anchorDetail?.anchor_id || anchorId;
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load anchor";
    }
  }

  async function submitBind() {
    bindStatus = "";
    bindError = "";
    try {
      const coord = JSON.parse(bindCoordJson);
      const payload = await bindAnchor(
        {
          locid: bindLocId,
          anchor_id: bindAnchorId,
          coord_kind: bindCoordKind,
          coord_json: coord,
        },
        adminToken,
      );
      bindStatus = `Binding created: ${payload.binding_id}`;
    } catch (err) {
      bindError = err instanceof Error ? err.message : "Binding failed";
    }
  }

  onMount(() => {
    adminToken = getAdminToken();
    refreshAnchors();
  });
</script>

<div class="max-w-6xl mx-auto px-4 py-8 text-white space-y-6">
  <header class="space-y-2">
    <h2 class="text-2xl font-semibold">Anchors</h2>
    <p class="text-sm text-gray-400">
      Gameplay anchor registry + LocId bindings for Sonic UI.
    </p>
  </header>

  {#if loading}
    <div class="text-gray-400">Loading anchors...</div>
  {:else if error}
    <div class="text-red-300">{error}</div>
  {/if}

  <section class="grid lg:grid-cols-3 gap-4">
    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold">Registry</h3>
        <button
          class="text-xs text-blue-300 underline"
          on:click={refreshAnchors}
        >
          Refresh
        </button>
      </div>
      {#if anchors.length === 0}
        <div class="text-xs text-gray-500">No anchors registered.</div>
      {:else}
        {#each anchors as anchor}
          <button
            class="w-full text-left text-xs text-gray-300 border-b border-gray-800 py-2 hover:text-white"
            on:click={() => {
              selectedAnchor = anchor.anchor_id;
              loadAnchor(anchor.anchor_id);
            }}
          >
            <div class="font-semibold">{anchor.anchor_id}</div>
            <div class="text-gray-500">{anchor.title}</div>
          </button>
        {/each}
      {/if}
    </div>

    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
      <h3 class="text-sm font-semibold">Anchor Detail</h3>
      {#if !anchorDetail}
        <div class="text-xs text-gray-500">Select an anchor to view details.</div>
      {:else}
        <div class="text-xs text-gray-300">
          <div><strong>ID:</strong> {anchorDetail.anchor_id}</div>
          <div><strong>Title:</strong> {anchorDetail.title}</div>
          <div><strong>Version:</strong> {anchorDetail.version || "—"}</div>
          <div><strong>Description:</strong> {anchorDetail.description || "—"}</div>
          <div class="mt-2">
            <div class="text-gray-400">Capabilities:</div>
            <pre class="text-xs bg-gray-800 p-2 rounded">{JSON.stringify(anchorDetail.capabilities || {}, null, 2)}</pre>
          </div>
        </div>
      {/if}
    </div>

    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-3">
      <h3 class="text-sm font-semibold">Create Binding</h3>
      <label class="text-xs text-gray-400">LocId</label>
      <input
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        placeholder="EARTH:SUR:L305-DA11"
        bind:value={bindLocId}
      />
      <label class="text-xs text-gray-400">Anchor ID</label>
      <input
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        bind:value={bindAnchorId}
      />
      <label class="text-xs text-gray-400">Coord Kind</label>
      <input
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        bind:value={bindCoordKind}
      />
      <label class="text-xs text-gray-400">Coord JSON</label>
      <textarea
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded min-h-[120px]"
        bind:value={bindCoordJson}
      ></textarea>
      <button
        class="text-xs px-3 py-1 bg-blue-600 rounded text-white hover:bg-blue-500"
        on:click={submitBind}
      >
        Bind
      </button>
      {#if bindStatus}
        <div class="text-xs text-emerald-300">{bindStatus}</div>
      {/if}
      {#if bindError}
        <div class="text-xs text-red-300">{bindError}</div>
      {/if}
    </div>
  </section>
</div>
