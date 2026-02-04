<script lang="ts">
  export let missions: { task_counts?: Record<string, number> }[] = [];

  $: totals = missions.reduce(
    (acc, mission) => {
      const counts = mission.task_counts || {};
      Object.entries(counts).forEach(([key, val]) => {
        acc[key] = (acc[key] || 0) + (val ?? 0);
      });
      return acc;
    },
    {} as Record<string, number>
  );
</script>

<section class="task-panel">
  <h3>Task snapshot</h3>
  <ul>
    {#each Object.entries(totals) as [key, value]}
      <li><strong>{key}</strong>: {value}</li>
    {/each}
    {#if !Object.keys(totals).length}
      <li>No task data yet.</li>
    {/if}
  </ul>
</section>

<style>
  .task-panel {
    border: 1px solid rgba(16, 185, 129, 0.5);
    border-radius: 0.75rem;
    padding: 1rem;
    background: rgba(15, 23, 42, 0.85);
  }

  .task-panel ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .task-panel li {
    font-size: 0.9rem;
    color: #cbd5f5;
    display: flex;
    justify-content: space-between;
  }
</style>
