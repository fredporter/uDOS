<script>
  import { onMount } from "svelte";
  import { getAdminToken } from "$lib/services/auth";
  import {
    listThemes,
    listSiteExports,
    listSiteFiles,
    listMissions,
    listContributions,
    listPlaces,
    listSpatialAnchors,
    listSpatialPlaces,
    listSpatialFileTags,
    triggerRender,
    getMissionDetail,
    updateContributionStatus,
  } from "$lib/services/rendererService";

  let adminToken = "";
  let loading = false;
  let error = "";
  let themes = [];
  let exports = [];
  let missions = [];
  let contributions = [];
  let contributionsFilter = "all";
  let contributionStatuses = ["all", "pending", "approved", "rejected"];
  let contributionReviewer = "";
  let contributionNote = "";
  let contributionActionError = "";
  let contributionActionBusy = "";
  let places = [];
  let anchors = [];
  let spatialPlaces = [];
  let fileTags = [];
  let selectedTheme = "";
  let missionId = "";
  let renderResult = null;
  let renderError = "";
  let renderInFlight = false;
  let selectedMissionId = "";
  let missionDetail = null;
  let missionDetailError = "";
  let missionDetailLoading = false;
  let missionFiles = [];
  let missionLogs = [];
  let siteFiles = {};
  let siteFilesLoading = {};
  let siteFilesError = {};

  function getMissionId(mission) {
    return mission?.mission_id || mission?.job_id || mission?.id || "";
  }

  function setContributionFilter(status) {
    contributionsFilter = status;
    refreshContributions();
  }

  function themePreviewUrl(themeName) {
    return `/_site/${themeName}/`;
  }

  function statusBadgeClass(status) {
    switch (status) {
      case "approved":
        return "bg-emerald-500/20 text-emerald-200 border-emerald-500/40";
      case "pending":
        return "bg-amber-500/20 text-amber-200 border-amber-500/40";
      case "rejected":
        return "bg-red-500/20 text-red-200 border-red-500/40";
      default:
        return "bg-gray-700/60 text-gray-200 border-gray-600";
    }
  }

  function extractMissionFiles(detail) {
    if (!detail) return [];
    if (Array.isArray(detail.rendered)) return detail.rendered;
    if (Array.isArray(detail.files)) return detail.files;
    if (Array.isArray(detail.outputs)) return detail.outputs;
    if (detail.report && Array.isArray(detail.report.files)) return detail.report.files;
    return [];
  }

  function extractMissionLogs(detail) {
    if (!detail) return [];
    if (Array.isArray(detail.logs)) return detail.logs;
    if (Array.isArray(detail.run_logs)) return detail.run_logs;
    if (typeof detail.log === "string") return detail.log.split("\n");
    if (typeof detail.stdout === "string") return detail.stdout.split("\n");
    if (detail.report && Array.isArray(detail.report.logs)) return detail.report.logs;
    return [];
  }

  async function loadSiteFiles(themeName) {
    if (!themeName) return;
    siteFilesLoading = { ...siteFilesLoading, [themeName]: true };
    siteFilesError = { ...siteFilesError, [themeName]: "" };
    try {
      const payload = await listSiteFiles(themeName, adminToken);
      siteFiles = { ...siteFiles, [themeName]: payload.files || [] };
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load site files";
      siteFilesError = { ...siteFilesError, [themeName]: message };
    } finally {
      siteFilesLoading = { ...siteFilesLoading, [themeName]: false };
    }
  }

  function toggleSiteFiles(themeName) {
    if (!themeName) return;
    if (siteFiles[themeName]) {
      const next = { ...siteFiles };
      delete next[themeName];
      siteFiles = next;
      return;
    }
    loadSiteFiles(themeName);
  }

  async function setContributionStatus(entry, status) {
    if (!entry?.id) return;
    if (!adminToken) {
      contributionActionError = "Admin token required to update contributions.";
      return;
    }
    contributionActionBusy = entry.id;
    contributionActionError = "";
    try {
      await updateContributionStatus(
        entry.id,
        status,
        contributionReviewer || undefined,
        contributionNote || undefined,
        adminToken,
      );
      await refreshContributions();
    } catch (err) {
      contributionActionError =
        err instanceof Error ? err.message : "Failed to update contribution";
    } finally {
      contributionActionBusy = "";
    }
  }

  async function refreshAll() {
    loading = true;
    error = "";
    try {
      const [
        themePayload,
        sitePayload,
        missionPayload,
        contribPayload,
        placePayload,
        anchorPayload,
        spatialPayload,
        tagPayload,
      ] = await Promise.all([
        listThemes(adminToken),
        listSiteExports(adminToken),
        listMissions(adminToken),
        listContributions(adminToken, contributionsFilter !== "all" ? contributionsFilter : undefined),
        listPlaces(adminToken),
        listSpatialAnchors(adminToken),
        listSpatialPlaces(adminToken),
        listSpatialFileTags(adminToken),
      ]);
      themes = themePayload.themes || [];
      exports = sitePayload.exports || [];
      missions = missionPayload.missions || [];
      contributions = contribPayload.contributions || [];
      places = placePayload.places || [];
      anchors = anchorPayload.anchors || [];
      spatialPlaces = spatialPayload.places || [];
      fileTags = tagPayload.file_tags || [];
      if (!selectedTheme && themes.length) {
        selectedTheme = themes[0].name || themes[0].id || "";
      }
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load renderer data";
    } finally {
      loading = false;
    }
  }

  async function refreshContributions() {
    try {
      const payload = await listContributions(
        adminToken,
        contributionsFilter !== "all" ? contributionsFilter : undefined,
      );
      contributions = payload.contributions || [];
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load contributions";
    }
  }

  async function loadMissionDetail(id) {
    if (!id) return;
    selectedMissionId = id;
    missionDetail = null;
    missionDetailError = "";
    missionDetailLoading = true;
    try {
      missionDetail = await getMissionDetail(id, adminToken);
    } catch (err) {
      missionDetailError = err instanceof Error ? err.message : "Failed to load mission detail";
    } finally {
      missionDetailLoading = false;
    }
  }

  async function handleRender() {
    if (!selectedTheme) return;
    renderError = "";
    renderInFlight = true;
    try {
      renderResult = await triggerRender(selectedTheme, missionId, adminToken);
      await refreshAll();
    } catch (err) {
      renderError = err instanceof Error ? err.message : "Render failed";
    } finally {
      renderInFlight = false;
    }
  }

  onMount(() => {
    adminToken = getAdminToken();
    refreshAll();
  });

  $: missionFiles = extractMissionFiles(missionDetail);
  $: missionLogs = extractMissionLogs(missionDetail);
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white space-y-8">
  <header class="space-y-2">
    <h1 class="text-3xl font-bold">Renderer Control Plane</h1>
    <p class="text-gray-400">
      Connected to `/api/renderer/*` for themes, exports, missions, contributions, and spatial metadata.
    </p>
    <button class="px-3 py-1 text-xs bg-gray-700 rounded text-white" on:click={refreshAll} disabled={loading}>
      {loading ? "Refreshing…" : "Refresh"}
    </button>
  </header>

  {#if error}
    <div class="bg-red-900 text-red-200 p-3 rounded border border-red-700">
      {error}
    </div>
  {/if}

  <section class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-4">
    <h2 class="text-lg font-semibold">Trigger Render</h2>
    <div class="grid md:grid-cols-[240px_1fr] gap-4 items-end">
      <label class="text-xs text-gray-400">
        Theme
        <select class="w-full mt-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm" bind:value={selectedTheme}>
          {#each themes as theme}
            <option value={theme.name || theme.id}>{theme.name || theme.id}</option>
          {/each}
        </select>
      </label>
      <label class="text-xs text-gray-400">
        Mission ID (optional)
        <input
          class="w-full mt-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
          placeholder="renderer-nightly"
          bind:value={missionId}
        />
      </label>
    </div>
    <button class="px-3 py-2 text-sm bg-blue-600 rounded text-white" on:click={handleRender} disabled={renderInFlight}>
      {renderInFlight ? "Rendering…" : "Run Render"}
    </button>
    {#if selectedTheme}
      <a
        class="inline-flex items-center text-xs text-blue-300 underline"
        href={themePreviewUrl(selectedTheme)}
        target="_blank"
        rel="noreferrer"
      >
        Preview _site/{selectedTheme}/
      </a>
    {/if}
    {#if renderError}
      <div class="text-sm text-red-300">{renderError}</div>
    {/if}
    {#if renderResult}
      <div class="text-xs text-gray-300 bg-gray-800 border border-gray-700 rounded p-3">
        <div>Job: {renderResult.job_id}</div>
        <div>Theme: {renderResult.theme}</div>
        <div>Status: {renderResult.status}</div>
        <div>Report: {renderResult.report_path || "n/a"}</div>
      </div>
    {/if}
  </section>

  <section class="grid lg:grid-cols-3 gap-4">
    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
      <h3 class="text-sm font-semibold">Themes</h3>
      {#if themes.length === 0}
        <div class="text-xs text-gray-500">No themes available.</div>
      {:else}
        {#each themes as theme}
          <div class="text-xs text-gray-300 border-b border-gray-800 pb-2">
            <div class="font-semibold">{theme.name}</div>
            <div>Slots: {(theme.slots || []).length || "—"}</div>
            <div>Site: {theme.siteExists ? "✅" : "—"}</div>
            {#if theme.siteExists}
              <a class="text-blue-300 underline" href={themePreviewUrl(theme.name)} target="_blank" rel="noreferrer">
                Preview _site/{theme.name}/
              </a>
              <div class="text-gray-400">
                Files: {theme.siteStats?.files ?? "—"} · Updated: {theme.siteStats?.lastModified || "—"}
              </div>
              <button
                class="text-xs text-blue-300 underline"
                on:click={() => toggleSiteFiles(theme.name)}
                disabled={siteFilesLoading[theme.name]}
              >
                {siteFiles[theme.name] ? "Hide files" : "Show files"}
              </button>
              {#if siteFilesLoading[theme.name]}
                <div class="text-xs text-gray-500">Loading files…</div>
              {:else if siteFilesError[theme.name]}
                <div class="text-xs text-red-300">{siteFilesError[theme.name]}</div>
              {:else if siteFiles[theme.name]?.length}
                <div class="mt-2 space-y-1 max-h-32 overflow-auto pr-1">
                  {#each siteFiles[theme.name] as file}
                    <a
                      class="block text-xs text-gray-300 hover:text-white underline"
                      href={`/_site/${theme.name}/${file.path}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {file.path} ({file.size}b)
                    </a>
                  {/each}
                </div>
              {:else if siteFiles[theme.name]}
                <div class="text-xs text-gray-500">No HTML files found.</div>
              {/if}
            {/if}
          </div>
        {/each}
      {/if}
    </div>

    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
      <h3 class="text-sm font-semibold">Exports</h3>
      {#if exports.length === 0}
        <div class="text-xs text-gray-500">No exports found.</div>
      {:else}
        {#each exports as entry}
          <div class="text-xs text-gray-300 border-b border-gray-800 pb-2">
            <div class="font-semibold">{entry.theme}</div>
            <div>Files: {entry.files}</div>
            <div>Updated: {entry.lastModified || "—"}</div>
          </div>
        {/each}
      {/if}
    </div>

    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
      <h3 class="text-sm font-semibold">Missions</h3>
      {#if missions.length === 0}
        <div class="text-xs text-gray-500">No missions recorded.</div>
      {:else}
        <div class="space-y-2 max-h-56 overflow-auto pr-2">
          {#each missions as mission}
            {#if getMissionId(mission)}
              <button
                class={`w-full text-left text-xs border-b border-gray-800 pb-2 hover:text-white ${selectedMissionId === getMissionId(mission) ? "text-white" : "text-gray-300"}`}
                on:click={() => loadMissionDetail(getMissionId(mission))}
              >
                <div class="font-semibold">{getMissionId(mission)}</div>
                <div>Status: {mission.status || "unknown"}</div>
                <div>Theme: {mission.theme || mission.manifest?.theme || "—"}</div>
              </button>
            {/if}
          {/each}
        </div>
      {/if}
    </div>
  </section>

  <section class="grid lg:grid-cols-3 gap-4">
    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="text-sm font-semibold">Contributions Review</h3>
        <div class="flex flex-wrap gap-2">
          {#each contributionStatuses as status}
            <button
              class={`px-2 py-1 text-xs rounded border ${
                contributionsFilter === status
                  ? "bg-blue-600 text-white border-blue-500"
                  : "bg-gray-800 text-gray-300 border-gray-700"
              }`}
              on:click={() => setContributionFilter(status)}
            >
              {status}
            </button>
          {/each}
        </div>
      </div>
      <div class="grid md:grid-cols-2 gap-2">
        <label class="text-xs text-gray-400">
          Reviewer
          <input
            class="w-full mt-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs"
            placeholder="maintainer@udOS"
            bind:value={contributionReviewer}
          />
        </label>
        <label class="text-xs text-gray-400">
          Note
          <input
            class="w-full mt-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs"
            placeholder="Optional review note"
            bind:value={contributionNote}
          />
        </label>
      </div>
      {#if contributionActionError}
        <div class="text-xs text-red-300">{contributionActionError}</div>
      {/if}
      {#if contributions.length === 0}
        <div class="text-xs text-gray-400">No contributions found.</div>
      {:else}
        <div class="grid md:grid-cols-2 xl:grid-cols-3 gap-3 max-h-72 overflow-auto pr-2">
          {#each contributions as entry}
            <div class="text-xs text-gray-300 border border-gray-800 rounded-lg p-3 space-y-2 bg-gray-800/40">
              <div class="flex items-center justify-between gap-2">
                <div class="font-semibold truncate">{entry.id}</div>
                <span class={`px-2 py-0.5 text-[10px] rounded border ${statusBadgeClass(entry.status)}`}>
                  {entry.status || "unknown"}
                </span>
              </div>
              <div class="text-gray-400">
                Mission: {entry.manifest?.mission_id || entry.mission_id || "—"}
              </div>
              <div class="text-gray-400">
                Theme: {entry.manifest?.theme || entry.theme || "—"}
              </div>
              <div class="text-gray-500">
                Updated: {entry.updated_at || entry.modified_at || entry.created_at || "—"}
              </div>
              <div class="flex items-center gap-2 pt-2">
                <button
                  class="px-2 py-1 text-[10px] rounded bg-emerald-600 text-white disabled:opacity-50"
                  on:click={() => setContributionStatus(entry, "approved")}
                  disabled={contributionActionBusy === entry.id}
                >
                  {contributionActionBusy === entry.id ? "Updating…" : "Approve"}
                </button>
                <button
                  class="px-2 py-1 text-[10px] rounded bg-red-600 text-white disabled:opacity-50"
                  on:click={() => setContributionStatus(entry, "rejected")}
                  disabled={contributionActionBusy === entry.id}
                >
                  Reject
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
      <h3 class="text-sm font-semibold">Places (Vault)</h3>
      <div class="text-xs text-gray-400">Tagged files: {places.length}</div>
    </div>
    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
      <h3 class="text-sm font-semibold">Spatial DB</h3>
      <div class="text-xs text-gray-400">Anchors: {anchors.length}</div>
      <div class="text-xs text-gray-400">Places: {spatialPlaces.length}</div>
      <div class="text-xs text-gray-400">File tags: {fileTags.length}</div>
    </div>
  </section>

  <section class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-2">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold">Mission Detail</h3>
      {#if selectedMissionId}
        <button
          class="text-xs text-blue-300 underline"
          on:click={() => loadMissionDetail(selectedMissionId)}
          disabled={missionDetailLoading}
        >
          Refresh detail
        </button>
      {/if}
    </div>
    {#if missionDetailLoading}
      <div class="text-xs text-gray-400">Loading mission detail…</div>
    {:else if missionDetailError}
      <div class="text-xs text-red-300">{missionDetailError}</div>
    {:else if missionDetail}
      <div class="text-xs text-gray-400">Mission: {selectedMissionId}</div>
      <div class="grid lg:grid-cols-3 gap-4">
        <div class="bg-gray-800 border border-gray-700 rounded p-3 space-y-1 text-xs text-gray-300">
          <div class="font-semibold text-gray-200">Summary</div>
          <div>Status: {missionDetail.status || missionDetail.state || "—"}</div>
          <div>Theme: {missionDetail.theme || missionDetail.manifest?.theme || "—"}</div>
          <div>Job: {missionDetail.job_id || "—"}</div>
          <div>Report: {missionDetail.report_path || missionDetail.report?.path || "—"}</div>
          <div>Updated: {missionDetail.updated_at || missionDetail.completed_at || missionDetail.created_at || "—"}</div>
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded p-3 space-y-2 text-xs text-gray-300 lg:col-span-2">
          <div class="font-semibold text-gray-200">Rendered Files</div>
          {#if missionFiles.length === 0}
            <div class="text-gray-400">No render files recorded.</div>
          {:else}
            <div class="grid md:grid-cols-2 gap-2 max-h-40 overflow-auto pr-2">
              {#each missionFiles as file}
                <div class="text-gray-300">
                  {#if typeof file === "string"}
                    {file}
                  {:else}
                    {file.path || file.file || JSON.stringify(file)}
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded p-3 space-y-2 text-xs text-gray-300">
        <div class="font-semibold text-gray-200">Run Logs</div>
        {#if missionLogs.length === 0}
          <div class="text-gray-400">No logs available.</div>
        {:else}
          <pre class="text-xs text-gray-300 bg-black/40 border border-gray-700 rounded p-3 overflow-auto max-h-64">
{missionLogs.join("\n")}
          </pre>
        {/if}
      </div>
      <details class="bg-gray-800 border border-gray-700 rounded p-3">
        <summary class="text-xs text-gray-300 cursor-pointer">Raw mission JSON</summary>
        <pre class="text-xs text-gray-300 mt-2 overflow-auto max-h-64">
{JSON.stringify(missionDetail, null, 2)}
        </pre>
      </details>
    {:else}
      <div class="text-xs text-gray-400">Select a mission to inspect its report.</div>
    {/if}
  </section>
</div>
