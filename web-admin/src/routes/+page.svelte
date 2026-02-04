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
</script>

<svelte:head>
  <title>uDOS Control Plane</title>
</svelte:head>

<main>
  <header>
    <h1>uDOS v1.3 Control Plane</h1>
    <p>Shared theme metadata, mission queue, and preview helpers.</p>
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
</style>
