<script context="module" lang="ts">
  import { getAnchors, getPlaces, getFileTags } from '$lib/services/spatialService';
  import { getThemes, getSiteSummary, getMissions, getContributions } from '$lib/services/rendererService';

  export async function load({ fetch }) {
    const [anchorRes, placeRes, tagRes, themeRes, siteSummary, missionRes, contributionRes] = await Promise.all([
      getAnchors(fetch),
      getPlaces(fetch),
      getFileTags(fetch),
      getThemes(fetch),
      getSiteSummary(fetch),
      getMissions(fetch),
      getContributions(fetch)
    ]);
    const contributions =
      (contributionRes?.contributions ?? []).map((entry: any) => ({
        id: entry.id,
        status: entry.status,
        path: entry.path ?? "",
        manifest: entry.manifest ?? {},
      })) ?? [];

    return {
      anchors: anchorRes?.anchors ?? [],
      places: placeRes?.places ?? [],
      fileTags: tagRes?.file_tags ?? [],
      themes: themeRes?.themes ?? [],
      siteExports: siteSummary?.exports ?? [],
      missions: missionRes?.missions ?? [],
      contributions
    };
  }
 </script>

<script lang="ts">
  import { onMount } from "svelte";
  import { getAdminToken, setAdminToken } from "$lib/services/auth";
  import ThemePicker from '$lib/components/ThemePicker.svelte';
  import MissionQueue from '$lib/components/MissionQueue.svelte';
  import SpatialPanel from '$lib/components/SpatialPanel.svelte';
  import TaskPanel from '$lib/components/TaskPanel.svelte';
  import RendererPreview from '$lib/components/RendererPreview.svelte';
  import ContributionQueue from '$lib/components/ContributionQueue.svelte';
  import '$lib/styles/global.css';
  import type { AnchorRow, PlaceRow, FileTagRow } from '$lib/types/spatial';
  import type { MissionData } from '$lib/lib/types/mission';
  import type { ContributionRow } from '$lib/types/contribution';

  export let data: {
    anchors: AnchorRow[];
    places: PlaceRow[];
    fileTags: FileTagRow[];
    themes: any[];
    siteExports: { theme: string; files: number; lastModified: string | null }[];
    missions: MissionData[];
    contributions: ContributionRow[];
  };

  const { anchors, places, fileTags, themes, siteExports, missions, contributions } = data;

  let adminToken = "";
  let tokenSaved = false;
  let tokenStatus = "Auth disabled";

  onMount(() => {
    adminToken = getAdminToken();
    tokenStatus = adminToken ? "Auth enabled" : "Auth disabled";
  });

  function saveToken() {
    setAdminToken(adminToken);
    tokenSaved = true;
    tokenStatus = adminToken ? "Auth enabled" : "Auth disabled";
    window.location.reload();
  }

  function clearToken() {
    adminToken = "";
    setAdminToken("");
    tokenSaved = true;
    tokenStatus = "Auth disabled";
    window.location.reload();
  }
</script>

<svelte:head>
  <title>uDOS Control Plane</title>
</svelte:head>

<main>
  <header>
    <h1>uDOS v1.3 Control Plane</h1>
    <p>Shared theme metadata, mission queue, and preview helpers.</p>
    <div class="token-status">{tokenStatus}</div>
    <div class="admin-token">
      <label>
        <span>Admin token</span>
        <input
          type="password"
          placeholder="Bearer token for /api/renderer/*"
          bind:value={adminToken}
        />
      </label>
      <div class="token-actions">
        <button on:click={saveToken}>Save</button>
        <button on:click={clearToken}>Clear</button>
      </div>
      {#if tokenSaved}
        <p class="token-note">Token saved. Reloading…</p>
      {:else}
        <p class="token-note">Stored in localStorage as `wizardAdminToken`.</p>
      {/if}
    </div>
  </header>
  <ThemePicker {themes} />
  <section class="two-column">
    <MissionQueue {missions} />
    <TaskPanel {missions} />
  </section>
  <RendererPreview {siteExports} />
  <ContributionQueue {contributions} />
  <SpatialPanel {anchors} {places} {fileTags} />
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .two-column {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }

  .admin-token {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(15, 23, 42, 0.6);
    display: grid;
    gap: 0.5rem;
  }

  .admin-token label {
    display: grid;
    gap: 0.35rem;
    font-size: 0.85rem;
    color: #e2e8f0;
  }

  .admin-token input {
    width: 100%;
    padding: 0.45rem 0.65rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: rgba(2, 6, 23, 0.9);
    color: #e2e8f0;
  }

  .token-actions {
    display: flex;
    gap: 0.5rem;
  }

  .token-actions button {
    padding: 0.45rem 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(59, 130, 246, 0.4);
    background: rgba(59, 130, 246, 0.2);
    color: #e2e8f0;
    cursor: pointer;
  }

  .token-note {
    font-size: 0.75rem;
    color: #94a3b8;
    margin: 0;
  }

  .token-status {
    margin-top: 0.35rem;
    font-size: 0.8rem;
    color: #38bdf8;
  }
</style>
