<script lang="ts">
  export let missions: {
    mission_id: string;
    job_id: string;
    status: string;
    ts: string;
    task_counts?: Record<string, number>;
  }[] = [];
</script>

<section class="mission-queue">
  <h2>Mission Queue</h2>
  <div class="grid">
        {#each missions as mission}
          <article>
            <header>
              <p>Mission {mission.mission_id}</p>
              <span class={mission.status}>{mission.status}</span>
            </header>
            <p>Job: {mission.job_id}</p>
            <p>TS: {mission.ts}</p>
            {#if mission.task_counts}
              <p class="task-summary">
                {#each Object.entries(mission.task_counts) as [key, value]}
                  <span>{key}: {value}</span>
                {/each}
              </p>
            {/if}
          </article>
        {/each}
      </div>
</section>

<style>
  .mission-queue {
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 1rem;
    border-radius: 0.75rem;
    background: #020617;
  }

  .mission-queue .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
  }

  .mission-queue article {
    padding: 0.75rem;
    background: rgba(15, 23, 42, 0.85);
    border-radius: 0.5rem;
  }

  .mission-queue header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 0.5rem;
  }

  .mission-queue span {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
  }

  .mission-queue .pending {
    background: rgba(249, 115, 22, 0.2);
    color: #f97316;
  }
</style>
