<script>
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";

  let loading = true;
  let busy = false;
  let error = null;

  let platformStatus = null;
  let integration = null;
  let sonicHealth = null;
  let syncStatus = null;
  let builds = [];

  let buildProfile = "alpine-core+sonic";

  const headers = () => buildAuthHeaders(getAdminToken());

  async function refresh() {
    loading = true;
    error = null;
    try {
      const [statusRes, integrationRes, healthRes, syncRes, buildsRes] =
        await Promise.all([
          apiFetch("/api/platform/sonic/status", { headers: headers() }),
          apiFetch("/api/library/integration/sonic", { headers: headers() }),
          apiFetch("/api/sonic/health", { headers: headers() }),
          apiFetch("/api/sonic/db/status", { headers: headers() }),
          apiFetch("/api/platform/sonic/builds", { headers: headers() }),
        ]);

      if (statusRes.ok) platformStatus = await statusRes.json();
      if (integrationRes.ok) integration = (await integrationRes.json()).integration;
      if (healthRes.ok) sonicHealth = await healthRes.json();
      if (syncRes.ok) syncStatus = await syncRes.json();
      if (buildsRes.ok) builds = (await buildsRes.json()).builds || [];
    } catch (err) {
      error = err?.message || String(err);
    } finally {
      loading = false;
    }
  }

  async function runLibraryAction(action) {
    busy = true;
    error = null;
    try {
      const method = action === "uninstall" ? "DELETE" : "POST";
      const res = await apiFetch(`/api/library/integration/sonic/${action === "uninstall" ? "" : action}`.replace(/\/$/, ""), {
        method,
        headers: headers(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await refresh();
    } catch (err) {
      error = `Failed to ${action}: ${err?.message || err}`;
    } finally {
      busy = false;
    }
  }

  async function runSync(action) {
    busy = true;
    error = null;
    try {
      const method = action === "export" ? "GET" : "POST";
      const res = await apiFetch(`/api/sonic/${action}`, {
        method,
        headers: headers(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await refresh();
    } catch (err) {
      error = `Failed to ${action}: ${err?.message || err}`;
    } finally {
      busy = false;
    }
  }

  async function buildSonicStick() {
    busy = true;
    error = null;
    try {
      const res = await apiFetch("/api/platform/sonic/build", {
        method: "POST",
        headers: { ...headers(), "Content-Type": "application/json" },
        body: JSON.stringify({ profile: buildProfile }),
        timeoutMs: 120000,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await refresh();
    } catch (err) {
      error = `Build failed: ${err?.message || err}`;
    } finally {
      busy = false;
    }
  }

  onMount(() => {
    refresh();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Sonic</h1>
  <p class="text-gray-400 mb-6">Status, integration lifecycle, sync operations, and Sonic Stick builds.</p>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="text-gray-400">Loading Sonic surfaces...</div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-xs text-gray-400 mb-2">Status</div>
        <div class="text-white">Bridge: {platformStatus?.available ? "available" : "missing"}</div>
        <div class="text-gray-400 text-sm">Version: {platformStatus?.version || "n/a"}</div>
        <div class="text-gray-400 text-sm">Health: {sonicHealth?.status || "unknown"}</div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-xs text-gray-400 mb-2">Sync</div>
        <div class="text-gray-300 text-sm">DB exists: {syncStatus?.db_exists ? "yes" : "no"}</div>
        <div class="text-gray-300 text-sm">Records: {syncStatus?.record_count ?? 0}</div>
        <div class="text-gray-300 text-sm">Last sync: {syncStatus?.last_sync || "n/a"}</div>
      </div>
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6">
      <div class="text-xs text-gray-400 mb-3">Install Surface</div>
      <div class="text-gray-300 text-sm mb-3">
        Integration: {integration?.name || "sonic"} · installed: {integration?.installed ? "yes" : "no"} · enabled: {integration?.enabled ? "yes" : "no"}
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runLibraryAction("install")}>Install</button>
        <button class="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runLibraryAction("enable")}>Enable</button>
        <button class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runLibraryAction("disable")}>Disable</button>
        <button class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runLibraryAction("uninstall")}>Uninstall</button>
      </div>
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6">
      <div class="text-xs text-gray-400 mb-3">Sync Surface</div>
      <div class="flex flex-wrap gap-2">
        <button class="px-3 py-1.5 bg-cyan-700 hover:bg-cyan-800 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runSync("sync")}>Sync</button>
        <button class="px-3 py-1.5 bg-cyan-700 hover:bg-cyan-800 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runSync("rescan")}>Rescan</button>
        <button class="px-3 py-1.5 bg-cyan-700 hover:bg-cyan-800 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runSync("rebuild")}>Rebuild</button>
        <button class="px-3 py-1.5 bg-cyan-700 hover:bg-cyan-800 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={() => runSync("export")}>Export</button>
      </div>
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6">
      <div class="text-xs text-gray-400 mb-3">Build Surface</div>
      <div class="flex flex-wrap items-center gap-2 mb-3">
        <select class="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm text-white" bind:value={buildProfile}>
          <option value="alpine-core">alpine-core</option>
          <option value="alpine-core+sonic">alpine-core+sonic</option>
        </select>
        <button class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded disabled:opacity-50" disabled={busy} on:click={buildSonicStick}>Build Sonic Stick</button>
      </div>
      <div class="text-gray-400 text-xs">Artifacts include image, iso, checksums, and build manifest.</div>
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <div class="text-xs text-gray-400 mb-3">Recent Builds</div>
      {#if builds.length === 0}
        <div class="text-gray-400 text-sm">No builds yet.</div>
      {:else}
        <div class="space-y-2">
          {#each builds as build}
            <div class="bg-gray-900 border border-gray-700 rounded p-2 text-sm text-gray-300">
              {build.build_id} · {build.profile} · artifacts: {build.artifact_count} · sonic: {build.sonic_sha || "n/a"}
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
