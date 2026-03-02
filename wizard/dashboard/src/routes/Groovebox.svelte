<script lang="ts">
  import { apiFetch } from "$lib/services/apiBase";
  import { onDestroy, onMount } from "svelte";

  type Playback = {
    now_playing: {
      title: string;
      tempo: string;
      key: string;
      loop: string;
      waveform: string;
    };
    playlists: { name: string; tempo: string; mode: string; duration: string }[];
    sequences: { title: string; type: string; length: number; tracks: string[]; last_updated: string }[];
  };

  type Config = {
    master_volume: number;
    midi_export_enabled: boolean;
    default_format: string;
    monitoring: { latency_ms: number; last_sync: string };
    hotkeys: string[];
  };

  type Preset = {
    name: string;
    colors: string[];
    description: string;
  };

  let playback: Playback | null = null;
  let config: Config | null = null;
  let presets: Preset[] = [];
  let loading = true;
  let error: string | null = null;
  let selectedPresetName: string | null = null;
  let requestedPresetName: string | null = null;
  let selectedPanel: "playback" | "config" = "playback";
  let requestedPanel: "playback" | "config" | null = null;
  let sharedView = false;
  let shareLinkCopied = false;
  let shareResetTimer: number | null = null;
  let cacheInvalidationNotice: string | null = null;
  let cacheNoticeTimer: number | null = null;
  let restoredFromSession = false;

  const grooveboxSessionKey = "wizard:groovebox:view-state";

  function formatTimestamp(value: string | null | undefined) {
    if (!value) return "n/a";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value;
    return parsed.toLocaleString();
  }

  function readRouteState() {
    const hash = typeof window !== "undefined" ? window.location.hash || "" : "";
    const [, rawQuery = ""] = hash.split("?");
    const params = new URLSearchParams(rawQuery);
    const panel = params.get("panel");
    const preset = params.get("preset");
    requestedPanel = panel === "config" ? "config" : panel === "playback" ? "playback" : null;
    requestedPresetName = preset || null;
    sharedView = params.has("panel") || params.has("preset");
  }

  function persistRouteState() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (selectedPanel && selectedPanel !== "playback") params.set("panel", selectedPanel);
    if (selectedPresetName) params.set("preset", selectedPresetName);
    const query = params.toString();
    const nextHash = query ? `groovebox?${query}` : "groovebox";
    if (window.location.hash.slice(1) !== nextHash) {
      window.history.replaceState(null, "", `#${nextHash}`);
    }
  }

  function currentShareLabels() {
    const labels = [];
    if (selectedPanel) labels.push(`panel=${selectedPanel}`);
    if (selectedPresetName) labels.push(`preset=${selectedPresetName}`);
    return labels;
  }

  function clearSharedView() {
    restoredFromSession = false;
    selectedPanel = "playback";
    requestedPanel = null;
    selectedPresetName = presets[0]?.name || null;
    requestedPresetName = null;
    sharedView = false;
    persistRouteState();
    persistViewState();
  }

  function persistViewState() {
    if (typeof window === "undefined") return;
    window.sessionStorage.setItem(
      grooveboxSessionKey,
      JSON.stringify({
        selectedPresetName,
        selectedPanel,
      }),
    );
  }

  function restoreViewState() {
    if (typeof window === "undefined") return;
    const raw = window.sessionStorage.getItem(grooveboxSessionKey);
    if (!raw) return;
    try {
      const payload = JSON.parse(raw);
      if (!payload || typeof payload !== "object") return;
      if (!requestedPresetName && typeof payload.selectedPresetName === "string") {
        selectedPresetName = payload.selectedPresetName;
        requestedPresetName = payload.selectedPresetName;
        restoredFromSession = true;
      }
      if (!requestedPanel && (payload.selectedPanel === "playback" || payload.selectedPanel === "config")) {
        selectedPanel = payload.selectedPanel;
        requestedPanel = payload.selectedPanel;
        restoredFromSession = true;
      }
    } catch {
      window.sessionStorage.removeItem(grooveboxSessionKey);
    }
  }

  function invalidateViewState() {
    if (typeof window === "undefined") return;
    window.sessionStorage.removeItem(grooveboxSessionKey);
  }

  function buildShareUrl() {
    if (typeof window === "undefined") return "";
    const params = new URLSearchParams();
    if (selectedPanel && selectedPanel !== "playback") params.set("panel", selectedPanel);
    if (selectedPresetName) params.set("preset", selectedPresetName);
    const query = params.toString();
    return `${window.location.origin}${window.location.pathname}#${query ? `groovebox?${query}` : "groovebox"}`;
  }

  async function copyShareLink() {
    const url = buildShareUrl();
    if (!url) return;
    try {
      await navigator.clipboard.writeText(url);
      shareLinkCopied = true;
      if (shareResetTimer) window.clearTimeout(shareResetTimer);
      shareResetTimer = window.setTimeout(() => {
        shareLinkCopied = false;
      }, 1500);
    } catch (err: any) {
      error = err?.message || "Failed to copy share link";
    }
  }

  function selectPreset(name: string) {
    restoredFromSession = false;
    selectedPresetName = name;
    requestedPresetName = name;
    sharedView = true;
    persistRouteState();
    persistViewState();
  }

  function selectPanel(panel: "playback" | "config") {
    restoredFromSession = false;
    selectedPanel = panel;
    requestedPanel = panel;
    sharedView = true;
    persistRouteState();
    persistViewState();
  }

  function handlePresetKeydown(event: KeyboardEvent, presetName: string) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      selectPreset(presetName);
    }
  }

  async function loadGroovebox() {
    loading = true;
    error = null;
    try {
      const [playbackResp, configResp, presetsResp] = await Promise.all([
        apiFetch("/api/groovebox/playback"),
        apiFetch("/api/groovebox/config"),
        apiFetch("/api/groovebox/presets"),
      ]);
      if (!playbackResp.ok || !configResp.ok || !presetsResp.ok) {
        throw new Error("Groovebox API unavailable");
      }
      playback = await playbackResp.json();
      config = await configResp.json();
      const presetPayload = await presetsResp.json();
      presets = presetPayload.presets ?? [];

      const knownPreset = requestedPresetName && presets.some((preset) => preset.name === requestedPresetName);
      if (knownPreset) {
        selectedPresetName = requestedPresetName;
      } else {
        const stalePresetName = requestedPresetName;
        selectedPresetName = presets[0]?.name || null;
        if (stalePresetName) {
          invalidateViewState();
          cacheInvalidationNotice = `Cached preset ${stalePresetName} was cleared because it is no longer available.`;
          if (cacheNoticeTimer) window.clearTimeout(cacheNoticeTimer);
          cacheNoticeTimer = window.setTimeout(() => {
            cacheInvalidationNotice = null;
          }, 4000);
        }
      }
      if (requestedPanel) selectedPanel = requestedPanel;
      persistRouteState();
      persistViewState();
    } catch (err: any) {
      console.error(err);
      error = err.message || "Failed to load Groovebox";
    } finally {
      loading = false;
    }
  }

  $: selectedPreset =
    presets.find((preset) => preset.name === selectedPresetName) ||
    presets[0] ||
    null;

  onMount(() => {
    readRouteState();
    restoreViewState();
    loadGroovebox();
  });

  onDestroy(() => {
    if (shareResetTimer) window.clearTimeout(shareResetTimer);
    if (cacheNoticeTimer) window.clearTimeout(cacheNoticeTimer);
  });
</script>

<div class="mx-auto max-w-7xl px-4 py-8">
  <div class="mb-8 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
    <div>
      <div class="mb-3 flex flex-wrap items-center gap-2">
        <h1 class="text-3xl font-bold text-white">Groovebox</h1>
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
      <p class="max-w-3xl text-sm text-gray-400">
        Playback, sequencing, and preset surfacing for the Groovebox extension. Share a specific preset or jump
        straight into the playback or config view.
      </p>
    </div>
    <button
      type="button"
      class="rounded border border-violet-700 px-3 py-2 text-xs text-violet-200 hover:bg-violet-950/40"
      on:click={copyShareLink}
    >
      {shareLinkCopied ? "Copied" : "Copy Share Link"}
    </button>
  </div>

  {#if error}
    <div class="mb-6 rounded-lg border border-red-700 bg-red-900 p-4 text-red-200">
      {error}
    </div>
  {/if}

  {#if cacheInvalidationNotice}
    <div class="mb-6 rounded-lg border border-amber-700 bg-amber-950/60 p-4 text-amber-100">
      {cacheInvalidationNotice}
    </div>
  {/if}

  {#if loading}
    <div class="rounded-lg border border-gray-700 bg-gray-800 p-6 text-gray-400">Loading Groovebox data...</div>
  {:else}
    <div class="mb-6 grid grid-cols-1 gap-4 xl:grid-cols-[1.6fr_1fr]">
      <div class="rounded-lg border border-gray-700 bg-gray-800 p-5">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <div class="text-xs uppercase tracking-[0.2em] text-gray-400">Panel Focus</div>
            <div class="mt-1 text-lg font-semibold text-white">
              {selectedPanel === "playback" ? "Playback View" : "Config View"}
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class={`rounded px-3 py-2 text-sm transition-colors ${
                selectedPanel === "playback"
                  ? "bg-cyan-600 text-white"
                  : "border border-gray-600 bg-gray-900 text-gray-200 hover:bg-gray-700"
              }`}
              on:click={() => selectPanel("playback")}
            >
              Playback
            </button>
            <button
              type="button"
              class={`rounded px-3 py-2 text-sm transition-colors ${
                selectedPanel === "config"
                  ? "bg-cyan-600 text-white"
                  : "border border-gray-600 bg-gray-900 text-gray-200 hover:bg-gray-700"
              }`}
              on:click={() => selectPanel("config")}
            >
              Config
            </button>
          </div>
        </div>

        {#if selectedPanel === "playback"}
          <div class="grid grid-cols-1 gap-5 lg:grid-cols-[1.2fr_1fr]">
            <div class="rounded-lg border border-gray-700 bg-gray-900/70 p-4">
              <div class="mb-3 text-xs uppercase tracking-[0.2em] text-gray-400">Now Playing</div>
              {#if playback?.now_playing}
                <img
                  src={playback.now_playing.waveform}
                  alt="Waveform"
                  class="mb-4 h-40 w-full rounded-lg border border-gray-700 object-cover"
                />
                <div class="text-xl font-semibold text-white">{playback.now_playing.title}</div>
                <div class="mt-1 text-sm text-gray-400">{playback.now_playing.loop}</div>
                <div class="mt-2 text-sm text-cyan-200">
                  {playback.now_playing.tempo} · {playback.now_playing.key}
                </div>
              {/if}
            </div>

            <div class="rounded-lg border border-gray-700 bg-gray-900/70 p-4">
              <div class="mb-3 text-xs uppercase tracking-[0.2em] text-gray-400">Playlist Queue</div>
              <div class="space-y-3">
                {#each playback?.playlists ?? [] as item}
                  <div class="rounded border border-gray-700 bg-gray-950/40 p-3">
                    <div class="font-medium text-white">{item.name}</div>
                    <div class="mt-1 text-sm text-gray-400">{item.mode} · {item.tempo} · {item.duration}</div>
                  </div>
                {/each}
              </div>
            </div>
          </div>

          <div class="mt-5">
            <div class="mb-3 text-xs uppercase tracking-[0.2em] text-gray-400">Sequences</div>
            <div class="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
              {#each playback?.sequences ?? [] as seq}
                <div class="rounded-lg border border-gray-700 bg-gray-900/70 p-4">
                  <div class="mb-2 text-[11px] uppercase tracking-[0.2em] text-cyan-300">{seq.type}</div>
                  <div class="font-semibold text-white">{seq.title}</div>
                  <div class="mt-2 text-sm text-gray-400">{seq.length} steps</div>
                  <div class="mt-1 text-xs text-gray-500">Updated {formatTimestamp(seq.last_updated)}</div>
                  <div class="mt-3 flex flex-wrap gap-2">
                    {#each seq.tracks as track}
                      <span class="rounded-full border border-gray-600 px-2 py-1 text-[11px] text-gray-300">{track}</span>
                    {/each}
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {:else}
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div class="rounded-lg border border-gray-700 bg-gray-900/70 p-4">
              <div class="mb-3 text-xs uppercase tracking-[0.2em] text-gray-400">Transport Configuration</div>
              <dl class="space-y-3">
                <div class="flex items-center justify-between gap-3 border-b border-gray-700 pb-3">
                  <dt class="text-sm text-gray-400">Master volume</dt>
                  <dd class="text-sm font-medium text-white">{config?.master_volume?.toFixed(2) ?? "n/a"}</dd>
                </div>
                <div class="flex items-center justify-between gap-3 border-b border-gray-700 pb-3">
                  <dt class="text-sm text-gray-400">MIDI export</dt>
                  <dd class="text-sm font-medium text-white">{config?.midi_export_enabled ? "Enabled" : "Disabled"}</dd>
                </div>
                <div class="flex items-center justify-between gap-3 border-b border-gray-700 pb-3">
                  <dt class="text-sm text-gray-400">Default format</dt>
                  <dd class="text-sm font-medium uppercase text-white">{config?.default_format ?? "n/a"}</dd>
                </div>
                <div class="flex items-center justify-between gap-3 border-b border-gray-700 pb-3">
                  <dt class="text-sm text-gray-400">Latency</dt>
                  <dd class="text-sm font-medium text-white">{config?.monitoring?.latency_ms ?? "n/a"} ms</dd>
                </div>
                <div class="flex items-center justify-between gap-3">
                  <dt class="text-sm text-gray-400">Last sync</dt>
                  <dd class="text-sm font-medium text-white">{formatTimestamp(config?.monitoring?.last_sync)}</dd>
                </div>
              </dl>
            </div>

            <div class="rounded-lg border border-gray-700 bg-gray-900/70 p-4">
              <div class="mb-3 text-xs uppercase tracking-[0.2em] text-gray-400">Transport Hotkeys</div>
              <div class="flex flex-wrap gap-2">
                {#each config?.hotkeys ?? [] as hotkey}
                  <span class="rounded-full border border-cyan-700 bg-cyan-950/30 px-3 py-1 text-xs text-cyan-100">{hotkey}</span>
                {/each}
              </div>
            </div>
          </div>
        {/if}
      </div>

      <div class="rounded-lg border border-gray-700 bg-gray-800 p-5">
        <div class="mb-4">
          <div class="text-xs uppercase tracking-[0.2em] text-gray-400">Preset Focus</div>
          <div class="mt-1 text-lg font-semibold text-white">{selectedPreset?.name || "No preset loaded"}</div>
          <div class="mt-2 text-sm text-gray-400">{selectedPreset?.description || "Select a preset to pin a shared view."}</div>
        </div>

        {#if selectedPreset}
          <div
            class="mb-4 h-3 rounded-full"
            style={`background: linear-gradient(135deg, ${selectedPreset.colors.join(", ")})`}
          ></div>
        {/if}

        <div class="space-y-3">
          {#each presets as preset}
            <div
              class={`cursor-pointer rounded-lg border p-4 transition-all ${
                preset.name === selectedPresetName
                  ? "border-cyan-500 bg-cyan-950/20"
                  : "border-gray-700 bg-gray-900/60 hover:border-cyan-700"
              }`}
              role="button"
              tabindex="0"
              on:click={() => selectPreset(preset.name)}
              on:keydown={(event) => handlePresetKeydown(event, preset.name)}
            >
              <div
                class="mb-3 h-2 rounded-full"
                style={`background: linear-gradient(135deg, ${preset.colors.join(", ")})`}
              ></div>
              <div class="flex items-start justify-between gap-3">
                <div>
                  <div class="font-medium text-white">{preset.name}</div>
                  <div class="mt-1 text-sm text-gray-400">{preset.description}</div>
                </div>
                {#if preset.name === selectedPresetName}
                  <div class="rounded-full border border-cyan-700 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-cyan-200">
                    Selected
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {/if}
</div>
