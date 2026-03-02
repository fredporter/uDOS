<script context="module" lang="ts">
  import { getAnchors, getPlaces, getFileTags } from "$lib/services/spatialService";
  import { getThemes, getSiteSummary, getMissions, getContributions } from "$lib/services/rendererService";
  import { getOpsSession, getOpsSummary } from "$lib/services/opsService";

  export async function load({ fetch }) {
    const [
      sessionRes,
      summaryRes,
      anchorRes,
      placeRes,
      tagRes,
      themeRes,
      siteSummary,
      missionRes,
      contributionRes,
    ] = await Promise.all([
      getOpsSession(fetch),
      getOpsSummary(fetch),
      getAnchors(fetch),
      getPlaces(fetch),
      getFileTags(fetch),
      getThemes(fetch),
      getSiteSummary(fetch),
      getMissions(fetch),
      getContributions(fetch),
    ]);

    return {
      session: sessionRes,
      summary: summaryRes,
      anchors: anchorRes?.anchors ?? [],
      places: placeRes?.places ?? [],
      fileTags: tagRes?.file_tags ?? [],
      themes: themeRes?.themes ?? [],
      siteExports: siteSummary?.exports ?? [],
      missions: missionRes?.missions ?? [],
      contributions:
        (contributionRes?.contributions ?? []).map((entry) => ({
          id: entry.id,
          status: entry.status,
          path: entry.path ?? "",
          manifest: entry.manifest ?? {},
        })) ?? [],
    };
  }
</script>

<script lang="ts">
  import ThemePicker from "$lib/components/ThemePicker.svelte";
  import MissionQueue from "$lib/components/MissionQueue.svelte";
  import SpatialPanel from "$lib/components/SpatialPanel.svelte";
  import TaskPanel from "$lib/components/TaskPanel.svelte";
  import RendererPreview from "$lib/components/RendererPreview.svelte";
  import ContributionQueue from "$lib/components/ContributionQueue.svelte";
  import "$lib/styles/global.css";

  export let data;

  const summary = data.summary ?? {};
  const session = data.session ?? { authenticated: false };
  const jobs = summary.jobs ?? {};
  const health = summary.health ?? {};
</script>

<svelte:head>
  <title>uDOS Control Plane</title>
</svelte:head>

<main>
  <header class="hero">
    <div>
      <p class="eyebrow">Managed Wizard Control Plane</p>
      <h1>uDOS operations from workflows, tasks, and prompts</h1>
      <p class="lede">
        The operator surface now assumes session-based access and canonical ops routes. Human-readable
        tasks, workflow templates, schedules, and prompt-driven jobs remain the source of truth.
      </p>
    </div>
    <div class="status-card">
      <div><strong>Deploy mode</strong><span>{data.session?.deploy_mode ?? "local"}</span></div>
      <div><strong>Session</strong><span>{session.authenticated ? "Authenticated" : "Not signed in"}</span></div>
      <div><strong>Role</strong><span>{data.session?.session?.role ?? "guest"}</span></div>
      <div><strong>Health</strong><span>{health.status ?? "unknown"}</span></div>
    </div>
  </header>

  <section class="stats">
    <article>
      <h2>Jobs</h2>
      <p>{jobs.stats?.pending_queue ?? 0} queued</p>
    </article>
    <article>
      <h2>Successful today</h2>
      <p>{jobs.stats?.successful_today ?? 0}</p>
    </article>
    <article>
      <h2>Workflow templates</h2>
      <p>{(summary.workflow_templates ?? []).length}</p>
    </article>
    <article>
      <h2>Workflow runs</h2>
      <p>{(summary.workflow_runs ?? []).length}</p>
    </article>
  </section>

  <ThemePicker themes={data.themes} />
  <section class="two-column">
    <MissionQueue missions={data.missions} />
    <TaskPanel missions={data.missions} />
  </section>
  <RendererPreview siteExports={data.siteExports} />
  <ContributionQueue contributions={data.contributions} />
  <SpatialPanel anchors={data.anchors} places={data.places} fileTags={data.fileTags} />
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .hero {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.8fr);
    gap: 1rem;
    align-items: start;
  }

  .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.75rem;
    color: #38bdf8;
  }

  h1 {
    margin: 0.2rem 0 0.5rem;
  }

  .lede {
    margin: 0;
    max-width: 62ch;
    color: #cbd5e1;
  }

  .status-card,
  .stats article {
    padding: 1rem;
    border-radius: 0.85rem;
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.22);
  }

  .status-card {
    display: grid;
    gap: 0.6rem;
  }

  .status-card div {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    color: #e2e8f0;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
  }

  .stats h2 {
    margin: 0;
    font-size: 0.85rem;
    color: #94a3b8;
  }

  .stats p {
    margin: 0.5rem 0 0;
    font-size: 1.4rem;
    color: #f8fafc;
  }

  .two-column {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }

  @media (max-width: 800px) {
    .hero {
      grid-template-columns: 1fr;
    }
  }
</style>
