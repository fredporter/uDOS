<script>
  import { onMount, onDestroy } from "svelte";
  import { getAdminToken } from "$lib/services/auth";
  import {
    listAnchors,
    getAnchor,
    bindAnchor,
    listAnchorInstances,
    listAnchorEvents,
    registerAnchor,
    createAnchorInstance,
    destroyAnchorInstance,
  } from "$lib/services/anchorService";

  let adminToken = "";
  let anchors = [];
  let selectedAnchor = "";
  let anchorDetail = null;
  let loading = false;
  let error = "";
  let bindStatus = "";
  let bindError = "";
  let instances = [];
  let events = [];
  let eventLimit = 50;
  let eventInstanceFilter = "";
  let eventTypeFilter = "";
  let livePolling = false;
  let pollTimer = null;

  let bindLocId = "";
  let bindAnchorId = "";
  let bindCoordKind = "tile";
  let bindCoordJson = "{ \"x\": 0, \"y\": 0 }";
  let newAnchorId = "GAME:NETHACK";
  let newAnchorTitle = "NetHack";
  let newAnchorStatus = "";
  let newAnchorError = "";
  let createInstanceStatus = "";
  let createInstanceError = "";

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

  async function refreshInstances() {
    try {
      const payload = await listAnchorInstances(selectedAnchor, adminToken);
      instances = payload.instances || [];
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load instances";
    }
  }

  async function refreshEvents() {
    try {
      const payload = await listAnchorEvents(
        {
          anchorId: selectedAnchor,
          instanceId: eventInstanceFilter || undefined,
          limit: eventLimit,
          type: eventTypeFilter || undefined,
        },
        adminToken,
      );
      events = payload.events || [];
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load events";
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

  async function submitRegister() {
    newAnchorStatus = "";
    newAnchorError = "";
    try {
      await registerAnchor(
        {
          anchor_id: newAnchorId,
          title: newAnchorTitle,
        },
        adminToken,
      );
      newAnchorStatus = `Registered ${newAnchorId}`;
      await refreshAnchors();
    } catch (err) {
      newAnchorError = err instanceof Error ? err.message : "Register failed";
    }
  }

  async function submitCreateInstance() {
    createInstanceStatus = "";
    createInstanceError = "";
    if (!selectedAnchor) {
      createInstanceError = "Select an anchor first.";
      return;
    }
    try {
      const payload = await createAnchorInstance(
        { anchor_id: selectedAnchor },
        adminToken,
      );
      createInstanceStatus = `Instance created: ${payload.instance?.instance_id}`;
      await refreshInstances();
    } catch (err) {
      createInstanceError =
        err instanceof Error ? err.message : "Instance creation failed";
    }
  }

  async function submitDestroyInstance(instanceId) {
    try {
      await destroyAnchorInstance(instanceId, adminToken);
      await refreshInstances();
    } catch (err) {
      error = err instanceof Error ? err.message : "Instance destroy failed";
    }
  }

  onMount(() => {
    adminToken = getAdminToken();
    refreshAnchors();
    pollTimer = setInterval(() => {
      if (!livePolling) return;
      if (!adminToken) return;
      if (!selectedAnchor) return;
      refreshEvents();
    }, 5000);
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
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
      <h3 class="text-sm font-semibold">Register Anchor</h3>
      <label class="text-xs text-gray-400" for="anchor-register-id">Anchor ID</label>
      <input
        id="anchor-register-id"
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        bind:value={newAnchorId}
      />
      <label class="text-xs text-gray-400" for="anchor-register-title">Title</label>
      <input
        id="anchor-register-title"
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        bind:value={newAnchorTitle}
      />
      <button
        class="text-xs px-3 py-1 bg-blue-600 rounded text-white hover:bg-blue-500"
        on:click={submitRegister}
      >
        Register
      </button>
      {#if newAnchorStatus}
        <div class="text-xs text-emerald-300">{newAnchorStatus}</div>
      {/if}
      {#if newAnchorError}
        <div class="text-xs text-red-300">{newAnchorError}</div>
      {/if}
    </div>

    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-3">
      <h3 class="text-sm font-semibold">Instances</h3>
      <button
        class="text-xs text-blue-300 underline"
        on:click={refreshInstances}
      >
        Refresh Instances
      </button>
      <button
        class="text-xs text-blue-300 underline"
        on:click={submitCreateInstance}
      >
        Create Instance
      </button>
      {#if createInstanceStatus}
        <div class="text-xs text-emerald-300">{createInstanceStatus}</div>
      {/if}
      {#if createInstanceError}
        <div class="text-xs text-red-300">{createInstanceError}</div>
      {/if}
      {#if instances.length === 0}
        <div class="text-xs text-gray-500">No instances found.</div>
      {:else}
        <div class="space-y-2 max-h-48 overflow-auto pr-1">
          {#each instances as instance}
            <div class="text-xs text-gray-300 border border-gray-800 rounded p-2">
              <div><strong>ID:</strong> {instance.instance_id}</div>
              <div><strong>Anchor:</strong> {instance.anchor_id}</div>
              <div><strong>Space:</strong> {instance.space_id || "—"}</div>
              <div><strong>Seed:</strong> {instance.seed || "—"}</div>
              <button
                class="text-xs text-red-300 underline mt-1"
                on:click={() => submitDestroyInstance(instance.instance_id)}
              >
                Destroy
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-3">
      <h3 class="text-sm font-semibold">Create Binding</h3>
      <label class="text-xs text-gray-400" for="binding-locid">LocId</label>
      <input
        id="binding-locid"
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        placeholder="EARTH:SUR:L305-DA11"
        bind:value={bindLocId}
      />
      <label class="text-xs text-gray-400" for="binding-anchor-id">Anchor ID</label>
      <input
        id="binding-anchor-id"
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        bind:value={bindAnchorId}
      />
      <label class="text-xs text-gray-400" for="binding-coord-kind">Coord Kind</label>
      <input
        id="binding-coord-kind"
        class="w-full bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
        bind:value={bindCoordKind}
      />
      <label class="text-xs text-gray-400" for="binding-coord-json">Coord JSON</label>
      <textarea
        id="binding-coord-json"
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

    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-3 lg:col-span-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold">Events</h3>
        <div class="flex flex-wrap items-center gap-2">
          <label class="text-xs text-gray-400 flex items-center gap-1">
            <input type="checkbox" bind:checked={livePolling} />
            Live
          </label>
          <input
            class="w-48 bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
            placeholder="Instance filter"
            bind:value={eventInstanceFilter}
          />
          <input
            class="w-32 bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
            placeholder="Type filter"
            bind:value={eventTypeFilter}
          />
          <input
            class="w-20 bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded"
            type="number"
            min="10"
            max="200"
            bind:value={eventLimit}
          />
          <button
            class="text-xs text-blue-300 underline"
            on:click={refreshEvents}
          >
            Refresh Events
          </button>
        </div>
      </div>
      {#if events.length === 0}
        <div class="text-xs text-gray-500">No events found.</div>
      {:else}
        <div class="space-y-2 max-h-56 overflow-auto pr-1">
          {#each events as event}
            <div class="text-xs text-gray-300 border border-gray-800 rounded p-2">
              <div><strong>Type:</strong> {event.type}</div>
              <div><strong>Anchor:</strong> {event.anchor_id}</div>
              <div><strong>Instance:</strong> {event.instance_id}</div>
              <div><strong>LocId:</strong> {event.locid || "—"}</div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </section>
</div>
