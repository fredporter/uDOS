<script>
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";

  let loading = true;
  let busy = false;
  let error = null;
  let platformStatus = null;
  let haStatus = null;
  let discovery = null;
  let playback = null;
  let presentationChoice = "thin-gui";

  const headers = () => buildAuthHeaders(getAdminToken());

  async function loadUHome() {
    loading = true;
    error = null;
    try {
      const [platformRes, haRes, discoverRes, playbackRes] = await Promise.all([
        apiFetch("/api/platform/uhome/status", { headers: headers() }),
        apiFetch("/api/ha/status"),
        apiFetch("/api/ha/discover", { headers: headers() }),
        apiFetch("/api/ha/command", {
          method: "POST",
          headers: { ...headers(), "Content-Type": "application/json" },
          body: JSON.stringify({ command: "uhome.playback.status", params: {} }),
        }),
      ]);

      if (!platformRes.ok) throw new Error(`uHOME status HTTP ${platformRes.status}`);
      platformStatus = await platformRes.json();
      presentationChoice =
        platformStatus?.presentation?.preferred_presentation || "thin-gui";

      haStatus = haRes.ok ? await haRes.json() : null;
      discovery = discoverRes.ok ? await discoverRes.json() : null;
      playback = playbackRes.ok ? (await playbackRes.json())?.result || null : null;
    } catch (err) {
      error = err?.message || String(err);
    } finally {
      loading = false;
    }
  }

  async function startPresentation() {
    busy = true;
    error = null;
    try {
      const res = await apiFetch("/api/platform/uhome/presentation/start", {
        method: "POST",
        headers: { ...headers(), "Content-Type": "application/json" },
        body: JSON.stringify({ presentation: presentationChoice }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadUHome();
    } catch (err) {
      error = `Failed to start presentation: ${err?.message || err}`;
    } finally {
      busy = false;
    }
  }

  async function stopPresentation() {
    busy = true;
    error = null;
    try {
      const res = await apiFetch("/api/platform/uhome/presentation/stop", {
        method: "POST",
        headers: headers(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadUHome();
    } catch (err) {
      error = `Failed to stop presentation: ${err?.message || err}`;
    } finally {
      busy = false;
    }
  }

  onMount(() => {
    loadUHome();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">uHOME</h1>
  <p class="text-gray-400 mb-6">
    Runtime scaffold for presentation, playback status, and Home Assistant bridge alignment.
  </p>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="text-gray-400">Loading uHOME surfaces...</div>
  {:else}
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-4 mb-6">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 xl:col-span-2">
        <div class="flex items-start justify-between gap-3 mb-3">
          <div>
            <div class="text-xs uppercase tracking-[0.2em] text-gray-400">Presentation</div>
            <div class="text-lg font-semibold text-white">Living-room runtime</div>
          </div>
          <div class="text-xs text-gray-400">
            {platformStatus?.template_workspace?.workspace_ref || "@memory/bank/typo-workspace"}
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300 mb-4">
          <div class="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
            <div class="text-gray-400 mb-1">Preferred presentation</div>
            <div class="text-white font-semibold">
              {platformStatus?.presentation?.preferred_presentation || "thin-gui"}
            </div>
            <div class="text-xs text-gray-400 mt-1">
              Source: {platformStatus?.presentation?.preferred_presentation_source || "default"}
            </div>
          </div>
          <div class="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
            <div class="text-gray-400 mb-1">Node role</div>
            <div class="text-white font-semibold">
              {platformStatus?.presentation?.node_role || "server"}
            </div>
            <div class="text-xs text-gray-400 mt-1">
              Source: {platformStatus?.presentation?.node_role_source || "default"}
            </div>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <select
            class="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm text-white"
            bind:value={presentationChoice}
            disabled={busy}
          >
            <option value="thin-gui">thin-gui</option>
            <option value="steam-console">steam-console</option>
          </select>
          <button
            class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded disabled:opacity-50"
            disabled={busy}
            on:click={startPresentation}
          >
            Start
          </button>
          <button
            class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded disabled:opacity-50"
            disabled={busy}
            on:click={stopPresentation}
          >
            Stop
          </button>
          <button
            class="px-3 py-1.5 bg-sky-700 hover:bg-sky-800 text-white text-sm rounded disabled:opacity-50"
            disabled={busy}
            on:click={loadUHome}
          >
            Refresh
          </button>
        </div>
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-xs uppercase tracking-[0.2em] text-gray-400 mb-3">Bridge</div>
        <div class="text-sm text-gray-300 space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-400">HA bridge</span>
            <span class="text-white">{haStatus?.status || "unknown"}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Enabled</span>
            <span class="text-white">{haStatus?.enabled ? "yes" : "no"}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Entities</span>
            <span class="text-white">{discovery?.entity_count ?? 0}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Allowlist</span>
            <span class="text-white">{haStatus?.command_allowlist_size ?? 0}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-xs uppercase tracking-[0.2em] text-gray-400 mb-3">Playback</div>
        <div class="space-y-2 text-sm text-gray-300">
          <div class="flex justify-between">
            <span class="text-gray-400">Jellyfin configured</span>
            <span class="text-white">{playback?.jellyfin_configured ? "yes" : "no"}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Presentation mode</span>
            <span class="text-white">{playback?.presentation_mode || "thin-gui"}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Target client</span>
            <span class="text-white">{playback?.preferred_target_client || "living-room"}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Active sessions</span>
            <span class="text-white">{playback?.active_sessions?.length ?? 0}</span>
          </div>
        </div>
        {#if playback?.note}
          <div class="mt-4 rounded border border-slate-700 bg-slate-900/50 p-3 text-sm text-gray-400">
            {playback.note}
          </div>
        {/if}
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-xs uppercase tracking-[0.2em] text-gray-400 mb-3">Discovered surfaces</div>
        {#if discovery?.entities?.length}
          <div class="space-y-2">
            {#each discovery.entities as entity}
              <div class="rounded border border-slate-700 bg-slate-900/50 p-3">
                <div class="flex items-center justify-between gap-2">
                  <div class="text-white font-semibold">{entity.name}</div>
                  <div class="text-xs text-gray-400">{entity.type}</div>
                </div>
                <div class="text-xs text-gray-400 mt-1">{entity.id}</div>
                <div class="text-xs text-slate-300 mt-2">
                  {entity.capabilities?.join(", ") || "no capabilities"}
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="text-sm text-gray-400">No discoverable uHOME entities reported.</div>
        {/if}
      </div>
    </div>
  {/if}
</div>
