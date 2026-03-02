<script>
  import { onDestroy, onMount } from "svelte";
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";

  let loading = true;
  let busy = false;
  let error = null;

  /** @type {Record<string, any> | null} */
  let platformStatus = null;
  /** @type {{name?: string; installed?: boolean; enabled?: boolean} | null} */
  let integration = null;
  /** @type {{status?: string} | null} */
  let sonicHealth = null;
  /** @type {import("$lib/types/sonic").SyncStatus | null} */
  let syncStatus = null;
  /** @type {Array<Record<string, any>>} */
  let builds = [];
  /** @type {Record<string, any> | null} */
  let guiSummary = null;
  /** @type {Record<string, any> | null} */
  let releaseSigningAlert = null;
  /** @type {Record<string, any> | null} */
  let latestReleaseReadiness = null;
  /** @type {Record<string, any> | null} */
  let datasetContract = null;
  /** @type {string | null} */
  let datasetCheckedAt = null;
  let datasetContractStale = false;
  /** @type {string | null} */
  let selectedBuildId = null;
  /** @type {Record<string, any> | null} */
  let selectedBuildReadiness = null;
  /** @type {Record<string, any> | null} */
  let selectedBuildSigningAlert = null;
  let selectedBuildLoading = false;
  let requestedBuildId = null;

  let buildProfile = "alpine-core+sonic";
  let datasetPollTimer = null;

  const headers = () => buildAuthHeaders(getAdminToken());

  function updateDatasetFreshness() {
    if (!datasetCheckedAt) {
      datasetContractStale = true;
      return;
    }
    const checkedAtMs = Date.parse(datasetCheckedAt);
    if (Number.isNaN(checkedAtMs)) {
      datasetContractStale = true;
      return;
    }
    datasetContractStale = Date.now() - checkedAtMs > 5 * 60 * 1000;
  }

  function formatTimestamp(value) {
    if (!value) return "n/a";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value;
    return parsed.toLocaleString();
  }

  function readRouteState() {
    const hash = typeof window !== "undefined" ? window.location.hash || "" : "";
    const [, rawQuery = ""] = hash.split("?");
    const params = new URLSearchParams(rawQuery);
    requestedBuildId = params.get("build") || null;
    const persistedCheckedAt = params.get("datasetCheckedAt");
    if (persistedCheckedAt) {
      datasetCheckedAt = persistedCheckedAt;
      updateDatasetFreshness();
    }
  }

  function persistRouteState() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (selectedBuildId) params.set("build", selectedBuildId);
    if (datasetCheckedAt) params.set("datasetCheckedAt", datasetCheckedAt);
    const query = params.toString();
    const nextHash = query ? `sonic?${query}` : "sonic";
    if (window.location.hash.slice(1) !== nextHash) {
      window.history.replaceState(null, "", `#${nextHash}`);
    }
  }

  async function refreshDatasetContract({ silent = false } = {}) {
    try {
      const res = await apiFetch("/api/platform/sonic/dataset-contract", {
        headers: headers(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const payload = await res.json();
      datasetContract = payload?.dataset_contract || null;
      datasetCheckedAt = payload?.checked_at || null;
      updateDatasetFreshness();
      persistRouteState();
    } catch (err) {
      datasetContractStale = true;
      if (!silent) {
        error = `Failed to load dataset contract: ${err?.message || err}`;
      }
    }
  }

  async function refresh() {
    loading = true;
    error = null;
    try {
      const [statusRes, integrationRes, healthRes, syncRes, buildsRes, summaryRes, datasetRes] =
        await Promise.all([
          apiFetch("/api/platform/sonic/status", { headers: headers() }),
          apiFetch("/api/library/integration/sonic", { headers: headers() }),
          apiFetch("/api/sonic/health", { headers: headers() }),
          apiFetch("/api/sonic/db/status", { headers: headers() }),
          apiFetch("/api/platform/sonic/builds", { headers: headers() }),
          apiFetch("/api/platform/sonic/gui/summary", { headers: headers() }),
          apiFetch("/api/platform/sonic/dataset-contract", { headers: headers() }),
        ]);

      if (statusRes.ok) platformStatus = await statusRes.json();
      if (integrationRes.ok) integration = (await integrationRes.json()).integration;
      if (healthRes.ok) sonicHealth = await healthRes.json();
      if (syncRes.ok) syncStatus = await syncRes.json();
      if (buildsRes.ok) builds = (await buildsRes.json()).builds || [];
      if (summaryRes.ok) {
        guiSummary = await summaryRes.json();
        releaseSigningAlert = guiSummary?.release_signing_alert || null;
        latestReleaseReadiness = guiSummary?.latest_release_readiness || null;
        if (guiSummary?.sync_status) syncStatus = guiSummary.sync_status;
        const latestBuildId = guiSummary?.latest_build?.build_id || null;
        if (latestBuildId) {
          selectedBuildId = latestBuildId;
          selectedBuildReadiness = latestReleaseReadiness;
          selectedBuildSigningAlert = releaseSigningAlert;
        } else {
          selectedBuildId = null;
          selectedBuildReadiness = null;
          selectedBuildSigningAlert = null;
        }
      }
      if (datasetRes.ok) {
        const payload = await datasetRes.json();
        datasetContract = payload?.dataset_contract || null;
        datasetCheckedAt = payload?.checked_at || null;
        updateDatasetFreshness();
      }
      if (requestedBuildId && requestedBuildId !== selectedBuildId) {
        const knownBuild = builds.find((item) => item.build_id === requestedBuildId);
        if (knownBuild) {
          await selectBuild(requestedBuildId);
        }
      }
      persistRouteState();
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

  async function selectBuild(buildId) {
    if (!buildId || selectedBuildLoading) return;
    selectedBuildId = buildId;
    persistRouteState();
    if (buildId === guiSummary?.latest_build?.build_id && latestReleaseReadiness) {
      selectedBuildReadiness = latestReleaseReadiness;
      selectedBuildSigningAlert = releaseSigningAlert;
      return;
    }

    selectedBuildLoading = true;
    error = null;
    try {
      const res = await apiFetch(`/api/platform/sonic/builds/${encodeURIComponent(buildId)}/release-readiness`, {
        headers: headers(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const payload = await res.json();
      selectedBuildReadiness = payload;
      selectedBuildSigningAlert = payload?.release_signing_alert || null;
      persistRouteState();
    } catch (err) {
      selectedBuildReadiness = null;
      selectedBuildSigningAlert = null;
      error = `Failed to load build readiness: ${err?.message || err}`;
    } finally {
      selectedBuildLoading = false;
    }
  }

  onMount(() => {
    readRouteState();
    refresh();
    datasetPollTimer = window.setInterval(() => {
      refreshDatasetContract({ silent: true });
    }, 60000);
  });

  onDestroy(() => {
    if (datasetPollTimer) {
      window.clearInterval(datasetPollTimer);
    }
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

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-6">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-xs uppercase tracking-[0.2em] text-gray-400 mb-3">Release Signing</div>
        {#if selectedBuildSigningAlert || releaseSigningAlert}
          {@const activeAlert = selectedBuildSigningAlert || releaseSigningAlert}
          <div
            class={`rounded-lg border p-4 ${
              activeAlert.severity === "error"
                ? "bg-red-950/60 border-red-700 text-red-100"
                : "bg-amber-950/60 border-amber-700 text-amber-100"
            }`}
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <div class="text-xs uppercase tracking-[0.2em] opacity-80 mb-2">
                  {selectedBuildId ? `Build ${selectedBuildId}` : "Latest Build"}
                </div>
                <div class="text-lg font-semibold mb-1">{activeAlert.title}</div>
                <div class="text-sm opacity-90 mb-2">{activeAlert.detail}</div>
                <div class="text-sm font-medium">{activeAlert.action}</div>
              </div>
              <div class="text-xs uppercase tracking-[0.2em] opacity-80">{activeAlert.severity}</div>
            </div>
          </div>
        {:else}
          <div class="rounded-lg border border-emerald-700 bg-emerald-950/40 p-4 text-emerald-100">
            <div class="text-sm font-semibold mb-1">Release signing is clear</div>
            <div class="text-sm opacity-90">No signing alert is active for the selected Sonic build.</div>
          </div>
        {/if}
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="flex items-center justify-between gap-3 mb-3">
          <div class="text-xs uppercase tracking-[0.2em] text-gray-400">Dataset Contract</div>
          <button
            type="button"
            class="px-3 py-1 text-xs rounded border border-cyan-700 text-cyan-200 hover:bg-cyan-950/40 disabled:opacity-50"
            disabled={busy}
            on:click={() => refreshDatasetContract()}
          >
            Refresh
          </button>
        </div>
        {#if datasetContract}
          <div
            class={`rounded-lg border p-4 ${
              datasetContract.ok
                ? "bg-emerald-950/40 border-emerald-700 text-emerald-100"
                : "bg-amber-950/40 border-amber-700 text-amber-100"
            }`}
          >
            <div class="flex items-start justify-between gap-4 mb-3">
              <div>
              <div class="text-lg font-semibold">
                  {datasetContract.ok ? "Dataset contract verified" : "Dataset contract needs attention"}
                </div>
                <div class="text-sm opacity-90">{datasetContract.detail || "No dataset contract detail available."}</div>
              </div>
              <div class="text-right">
                <div class="text-xs uppercase tracking-[0.2em] opacity-80">{datasetContract.level || "unknown"}</div>
                <div
                  class={`mt-2 text-[11px] uppercase tracking-[0.2em] ${
                    datasetContractStale ? "text-amber-200" : "text-emerald-200"
                  }`}
                >
                  {datasetContractStale ? "stale" : "fresh"}
                </div>
              </div>
            </div>
            <div class="text-sm opacity-90">
              Version: {datasetContract.version || "n/a"} ·
              schema: {datasetContract.schema_version || "n/a"} ·
              updated: {datasetContract.updated || "n/a"}
            </div>
            <div class="text-sm opacity-90 mt-2">
              Checked: {formatTimestamp(datasetCheckedAt)}
            </div>
            <div class="text-sm opacity-90 mt-2">
              Seed rows: {datasetContract.seed_rows?.length ?? 0} ·
              required-field drift: {datasetContract.diff?.required_mismatch_fields?.length ?? 0}
            </div>
            {#if datasetContract.errors?.length}
              <div class="mt-3 text-sm">
                <div class="font-semibold mb-1">Errors</div>
                <ul class="space-y-1">
                  {#each datasetContract.errors.slice(0, 3) as item}
                    <li>{item}</li>
                  {/each}
                </ul>
              </div>
            {/if}
            {#if datasetContract.warnings?.length}
              <div class="mt-3 text-sm">
                <div class="font-semibold mb-1">Warnings</div>
                <ul class="space-y-1">
                  {#each datasetContract.warnings.slice(0, 2) as item}
                    <li>{item}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
        {:else}
          <div class="rounded-lg border border-gray-700 bg-gray-900 p-4 text-gray-400 text-sm">
            Dataset contract summary is not available from the Sonic summary payload.
          </div>
        {/if}
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
      {#if selectedBuildLoading}
        <div class="mt-4 bg-gray-900 border border-gray-700 rounded p-3 text-sm text-gray-400">
          Loading readiness for {selectedBuildId}...
        </div>
      {:else if selectedBuildReadiness}
        <div class="mt-4 bg-gray-900 border border-gray-700 rounded p-3 text-sm">
          <div class="text-gray-200 font-medium mb-1">
            {selectedBuildId ? `Release Readiness: ${selectedBuildId}` : "Latest Release Readiness"}
          </div>
          <div class="text-gray-400">
            Ready: {selectedBuildReadiness.release_ready ? "yes" : "no"} ·
            checksums: {selectedBuildReadiness?.checksums?.verified ? "verified" : "pending"} ·
            signing: {selectedBuildReadiness?.signing?.ready ? "verified" : "attention"}
          </div>
          {#if selectedBuildReadiness?.issues?.length}
            <div class="text-gray-500 mt-2">
              Issues: {selectedBuildReadiness.issues.slice(0, 2).join(" · ")}
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <div class="text-xs text-gray-400 mb-3">Recent Builds</div>
      {#if builds.length === 0}
        <div class="text-gray-400 text-sm">No builds yet.</div>
      {:else}
        <div class="space-y-2">
          {#each builds as build}
            <button
              type="button"
              class={`w-full text-left rounded p-3 text-sm border transition ${
                selectedBuildId === build.build_id
                  ? "bg-cyan-950/40 border-cyan-700 text-cyan-100"
                  : "bg-gray-900 border-gray-700 text-gray-300 hover:border-gray-500"
              }`}
              on:click={() => selectBuild(build.build_id)}
            >
              <div class="flex items-center justify-between gap-4">
                <div>
                  <div class="font-medium">{build.build_id}</div>
                  <div class="text-xs opacity-80 mt-1">
                    {build.profile} · artifacts: {build.artifact_count} · sonic: {build.sonic_sha || "n/a"}
                  </div>
                </div>
                <div class="text-xs uppercase tracking-[0.2em] opacity-70">
                  {selectedBuildId === build.build_id ? "selected" : "inspect"}
                </div>
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
