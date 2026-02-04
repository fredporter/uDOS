<script lang="ts">
  import { onMount } from "svelte";

  type OverlayEntry = {
    id: string;
    enabled: boolean;
    priority: number;
    scope: "renderer" | "dashboard" | "global";
  };

  type OverlayState = {
    enabled: boolean;
    mode: "merge" | "replace";
    overlays: OverlayEntry[];
    lastSaved?: string;
  };

  const STORAGE_KEY = "wizard-round3-mod-overlays";

  let state: OverlayState = {
    enabled: true,
    mode: "merge",
    overlays: [
      { id: "retro-grid", enabled: true, priority: 10, scope: "renderer" },
      { id: "teletext-outline", enabled: false, priority: 20, scope: "dashboard" },
    ],
  };
  let newOverlayId = "";

  onMount(() => {
    if (typeof localStorage === "undefined") return;
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        state = { ...state, ...parsed };
      }
    } catch (err) {
      console.warn("Failed to parse overlay config", err);
    }
  });

  function persist() {
    if (typeof localStorage === "undefined") return;
    const payload = { ...state, lastSaved: new Date().toISOString() };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    state = payload;
  }

  function toggleOverlay(index: number) {
    state.overlays = state.overlays.map((overlay, idx) =>
      idx === index ? { ...overlay, enabled: !overlay.enabled } : overlay,
    );
    persist();
  }

  function updateOverlay(index: number, key: keyof OverlayEntry, value: string | number) {
    state.overlays = state.overlays.map((overlay, idx) => {
      if (idx !== index) return overlay;
      return { ...overlay, [key]: value };
    });
    persist();
  }

  function removeOverlay(index: number) {
    state.overlays = state.overlays.filter((_, idx) => idx !== index);
    persist();
  }

  function addOverlay() {
    const trimmed = newOverlayId.trim();
    if (!trimmed) return;
    state.overlays = [
      ...state.overlays,
      {
        id: trimmed,
        enabled: true,
        priority: 30,
        scope: "renderer",
      },
    ];
    newOverlayId = "";
    persist();
  }
</script>

<section class="overlay-panel">
  <header>
    <div>
      <p class="eyebrow">Round 3 • Mod Overlay Controls</p>
      <h2>Overlay loader knobs</h2>
      <p class="muted">
        Manage overlay packs for the renderer + dashboard preview pipeline. These configs
        are stored locally for now and can be lifted into the plugin registry.
      </p>
    </div>
    <div class="header-actions">
      <label class="switch">
        <input type="checkbox" bind:checked={state.enabled} on:change={persist} />
        <span>{state.enabled ? "Enabled" : "Disabled"}</span>
      </label>
      <select bind:value={state.mode} on:change={persist}>
        <option value="merge">Merge overlays</option>
        <option value="replace">Replace base theme</option>
      </select>
    </div>
  </header>

  <div class="overlay-list">
    {#each state.overlays as overlay, index}
      <article class="overlay-row">
        <div class="title">
          <input
            class="name"
            value={overlay.id}
            on:input={(event) =>
              updateOverlay(index, "id", (event.target as HTMLInputElement).value)}
          />
          <span class={`pill ${overlay.enabled ? "on" : "off"}`}>
            {overlay.enabled ? "ACTIVE" : "OFF"}
          </span>
        </div>
        <div class="controls">
          <label>
            <span>Scope</span>
            <select
              value={overlay.scope}
              on:change={(event) =>
                updateOverlay(index, "scope", (event.target as HTMLSelectElement).value)}
            >
              <option value="renderer">Renderer</option>
              <option value="dashboard">Dashboard</option>
              <option value="global">Global</option>
            </select>
          </label>
          <label>
            <span>Priority</span>
            <input
              type="number"
              min="0"
              value={overlay.priority}
              on:change={(event) =>
                updateOverlay(
                  index,
                  "priority",
                  Number((event.target as HTMLInputElement).value),
                )}
            />
          </label>
          <button class="ghost" on:click={() => toggleOverlay(index)}>
            {overlay.enabled ? "Disable" : "Enable"}
          </button>
          <button class="danger" on:click={() => removeOverlay(index)}>Remove</button>
        </div>
      </article>
    {/each}
  </div>

  <div class="add-row">
    <input
      type="text"
      placeholder="overlay-id (e.g., nes-ui-kit)"
      bind:value={newOverlayId}
    />
    <button class="primary" on:click={addOverlay}>Add overlay</button>
  </div>

  <div class="footer">
    <span>Last saved: {state.lastSaved ? new Date(state.lastSaved).toLocaleString() : "Not yet"}</span>
    <button class="ghost" on:click={persist}>Save now</button>
  </div>
</section>

<style>
  .overlay-panel {
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 1rem;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  header {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }

  .eyebrow {
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 0;
  }

  h2 {
    margin: 0.2rem 0;
    font-size: 1.4rem;
  }

  .muted {
    margin: 0;
    color: #94a3b8;
    font-size: 0.85rem;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    align-items: center;
  }

  .header-actions select,
  .header-actions input[type="checkbox"] + span {
    font-size: 0.85rem;
  }

  .switch {
    display: inline-flex;
    gap: 0.4rem;
    align-items: center;
    background: rgba(148, 163, 184, 0.15);
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    color: #e5e7eb;
    font-weight: 600;
  }

  .overlay-list {
    display: grid;
    gap: 0.8rem;
  }

  .overlay-row {
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 0.75rem;
    padding: 0.85rem;
    background: rgba(15, 23, 42, 0.7);
    display: grid;
    gap: 0.6rem;
  }

  .title {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    align-items: center;
  }

  .name {
    flex: 1;
    background: transparent;
    border: none;
    font-size: 1rem;
    color: #f8fafc;
  }

  .pill {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.2);
    color: #e5e7eb;
  }

  .pill.on {
    background: rgba(52, 211, 153, 0.2);
    color: #bbf7d0;
  }

  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    align-items: flex-end;
  }

  .controls label {
    display: grid;
    gap: 0.25rem;
    font-size: 0.7rem;
    color: #94a3b8;
  }

  .controls select,
  .controls input,
  .add-row input {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: 0.5rem;
    padding: 0.3rem 0.6rem;
    color: #e2e8f0;
    font-size: 0.85rem;
  }

  .ghost,
  .danger,
  .primary {
    border: none;
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
  }

  .ghost {
    background: rgba(148, 163, 184, 0.2);
    color: #e5e7eb;
  }

  .danger {
    background: rgba(248, 113, 113, 0.2);
    color: #fecaca;
  }

  .primary {
    background: #38bdf8;
    color: #0f172a;
  }

  .add-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
  }

  .add-row input {
    flex: 1;
    min-width: 220px;
  }

  .footer {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    flex-wrap: wrap;
    font-size: 0.75rem;
    color: #94a3b8;
  }
</style>
