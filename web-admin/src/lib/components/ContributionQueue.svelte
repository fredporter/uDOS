<script lang="ts">
  import { updateContributionStatus } from "$lib/services/rendererService";
  import type { ContributionRow } from "$lib/types/contribution";

  export let contributions: ContributionRow[] = [];

  const statusOptions = ["pending", "approved", "rejected"];
  let selectedStatus = "";
  const busy = new Set<string>();

  $: filtered = selectedStatus
    ? contributions.filter((c) => c.status === selectedStatus)
    : contributions;

  async function setStatus(row: ContributionRow, status: string) {
    if (!statusOptions.includes(status)) {
      return;
    }
    busy.add(row.id);
    const payload = await updateContributionStatus(fetch, row.id, status, "web-admin", `set to ${status}`);
    busy.delete(row.id);
    if (payload?.contribution) {
      row.status = payload.contribution.status;
      row.manifest = payload.contribution.manifest ?? row.manifest;
    }
  }
</script>

<section class="contribution-queue">
  <header>
    <div>
      <h3>Contribution queue</h3>
      <p>Patch bundles submitted by Vibe or external contributors.</p>
    </div>
    <label>
      <span>Status</span>
      <select bind:value={selectedStatus}>
        <option value="">All</option>
        {#each statusOptions as option}
          <option value={option}>{option}</option>
        {/each}
      </select>
    </label>
  </header>

  {#if filtered.length}
    <div class="grid">
      {#each filtered as contribution}
        <article>
          <div class="meta">
            <strong>{contribution.id}</strong>
            <span class={contribution.status}>{contribution.status}</span>
          </div>
          <p class="mission">{contribution.manifest.mission_id ?? "mission TBD"}</p>
          {#if contribution.manifest.notes}
            <p class="notes">{contribution.manifest.notes}</p>
          {/if}
          <div class="actions">
            <button on:click={() => setStatus(contribution, "approved")} disabled={busy.has(contribution.id)}>
              Approve
            </button>
            <button on:click={() => setStatus(contribution, "rejected")} disabled={busy.has(contribution.id)}>
              Reject
            </button>
          </div>
        </article>
      {/each}
    </div>
  {:else}
    <p class="empty">No contributions yet.</p>
  {/if}
</section>

<style>
  .contribution-queue {
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 1rem;
    padding: 1.5rem;
    background: rgba(2, 6, 23, 0.9);
  }

  header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: center;
  }

  header select {
    background: rgba(15, 23, 42, 0.8);
    color: #e2e8f0;
    border: 1px solid rgba(148, 163, 184, 0.4);
    padding: 0.35rem 0.75rem;
    border-radius: 0.5rem;
  }

  .grid {
    display: grid;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  article {
    padding: 0.85rem;
    background: rgba(15, 23, 42, 0.85);
    border-radius: 0.65rem;
    border: 1px solid rgba(59, 130, 246, 0.35);
  }

  .meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .meta span {
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    text-transform: uppercase;
  }

  .meta span.pending {
    background: rgba(249, 115, 22, 0.2);
    color: #f97316;
  }

  .meta span.approved {
    background: rgba(16, 185, 129, 0.25);
    color: #10b981;
  }

  .meta span.rejected {
    background: rgba(248, 113, 113, 0.2);
    color: #f87171;
  }

  .mission {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-bottom: 0.35rem;
  }

  .notes {
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  button {
    flex: 1;
    padding: 0.45rem 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(59, 130, 246, 0.2);
    color: #cbd5f5;
    cursor: pointer;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .empty {
    margin-top: 1rem;
    color: #94a3b8;
  }
</style>
