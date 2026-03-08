<script>
  import { onMount } from "svelte";

  let overview = null;
  let records = [];
  let events = [];
  let tasks = [];
  let error = null;
  const apiBase = import.meta.env.VITE_EMPIRE_API_BASE || "http://127.0.0.1:8991";
  const apiToken = import.meta.env.VITE_EMPIRE_API_TOKEN || "";
  let taskFilter = "all";
  let taskQuery = "";
  let categoryFilter = "all";
  let selectedTask = null;

  const status = [
    { label: "Records", value: "—", tone: "text-empire-300", key: "records" },
    { label: "Sources", value: "—", tone: "text-slate-200", key: "sources" },
    { label: "Events", value: "—", tone: "text-amber-200", key: "events" }
  ];

  const fallbackLines = [
    "[system] Empire overview not loaded yet",
    "[system] Activate Empire in Wizard Extensions, then refresh connectors or load sample data"
  ];

  async function loadData() {
    try {
      const headers = apiToken ? { Authorization: `Bearer ${apiToken}` } : {};
      const tasksUrl =
        taskFilter === "all"
          ? `${apiBase}/tasks?limit=8`
          : `${apiBase}/tasks?limit=8&status=${taskFilter}`;
      const [healthResp, recordsResp, eventsResp, tasksResp] = await Promise.all([
        fetch(`${apiBase}/health`, { cache: "no-store", headers }),
        fetch(`${apiBase}/records?limit=25`, { cache: "no-store", headers }),
        fetch(`${apiBase}/events?limit=8`, { cache: "no-store", headers }),
        fetch(tasksUrl, { cache: "no-store", headers })
      ]);

      if (!healthResp.ok) {
        throw new Error(`API unhealthy: HTTP ${healthResp.status}`);
      }

      records = recordsResp.ok ? await recordsResp.json() : [];
      events = eventsResp.ok ? await eventsResp.json() : [];
      tasks = tasksResp.ok ? await tasksResp.json() : [];

      overview = {
        counts: {
          records: records.length,
          sources: "—",
          events: events.length
        }
      };
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load overview";
    }
  }

  async function setTaskStatus(taskId, status) {
    const headers = apiToken ? { Authorization: `Bearer ${apiToken}` } : {};
    await fetch(`${apiBase}/tasks/${taskId}/status?status=${status}`, {
      method: "POST",
      headers
    });
    await loadData();
  }

  $: categories = Array.from(new Set(tasks.map((task) => task.category).filter(Boolean)));
  $: filteredTasks = tasks.filter((task) => {
    const matchesStatus = taskFilter === "all" || task.status === taskFilter;
    const matchesCategory = categoryFilter === "all" || task.category === categoryFilter;
    const query = taskQuery.trim().toLowerCase();
    const matchesQuery =
      !query ||
      (task.title || "").toLowerCase().includes(query) ||
      (task.notes || "").toLowerCase().includes(query) ||
      (task.source || "").toLowerCase().includes(query) ||
      (task.source_ref || "").toLowerCase().includes(query) ||
      (task.company_name || "").toLowerCase().includes(query);
    return matchesStatus && matchesCategory && matchesQuery;
  });

  onMount(loadData);

  const panels = [
    {
      title: "Sources",
      body: "Secure intake lanes for partner exports, bulk CSV drops, and JSON feeds."
    },
    {
      title: "Normalization",
      body: "Canonicalize names, orgs, lifecycle stages, and HubSpot-aligned fields."
    },
    {
      title: "Enrichment",
      body: "Attach optional data providers and custom scoring without leaving Empire."
    }
  ];
</script>

<div class="min-h-screen bg-grid bg-gradient-to-br from-slate-950 via-slate-900 to-empire-900/60">
  <div class="mx-auto max-w-6xl px-6 py-12">
    <header class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
      <div>
        <p class="text-xs uppercase tracking-[0.4em] text-empire-200">Empire Suite</p>
        <h1 class="mt-4 font-display text-4xl text-slate-50 md:text-5xl">Business Operations Console</h1>
        <p class="mt-3 max-w-2xl text-base text-slate-300">
          Private extension for business workflows. Ingestion, dedupe, enrichment, and sync run from here.
        </p>
      </div>
      <div class="flex flex-wrap gap-3">
        <button class="rounded-full border border-empire-400/60 bg-empire-500/20 px-5 py-2 text-xs uppercase tracking-[0.25em] text-empire-100">
          Private · Paid
        </button>
        <button class="rounded-full border border-slate-600 px-5 py-2 text-xs uppercase tracking-[0.25em] text-slate-300">
          Version 0.2
        </button>
      </div>
    </header>

    <section class="mt-12 grid gap-4 md:grid-cols-3">
      {#each status as item}
        <div class="glass rounded-2xl border border-slate-700/60 p-5 shadow-glow">
          <p class="text-xs uppercase tracking-[0.3em] text-slate-400">{item.label}</p>
          <p class={`mt-4 font-display text-2xl ${item.tone}`}>
            {overview?.counts?.[item.key] ?? item.value}
          </p>
          <div class="mt-4 h-1 rounded-full bg-slate-700">
            <div class="h-1 w-2/3 rounded-full bg-empire-500/70"></div>
          </div>
        </div>
      {/each}
    </section>

    <section class="mt-10 grid gap-6 lg:grid-cols-3">
      <div class="glass rounded-3xl border border-empire-400/40 p-6 lg:col-span-2">
        <div class="flex items-center justify-between">
          <h2 class="font-display text-xl text-empire-100">Live Console</h2>
          <span class="text-xs uppercase tracking-[0.3em] text-slate-400">stream</span>
        </div>
        <div class="mt-5 rounded-2xl border border-slate-700/70 bg-slate-950/70 p-4 font-mono text-sm text-empire-100">
          {#if error}
            <p class="py-1 text-amber-200">[error] {error}</p>
          {/if}
          {#if events && events.length}
            {#each events as event}
              <p class="py-1">
                [{event.event_type || event.type}] {event.occurred_at} | {event.subject || "Event"}
                {event.notes ? `- ${event.notes}` : ""}
              </p>
            {/each}
          {:else}
            {#each fallbackLines as line}
              <p class="py-1 text-slate-400">{line}</p>
            {/each}
          {/if}
        </div>
        <div class="mt-6 grid gap-3 rounded-2xl border border-slate-700/60 bg-slate-950/60 p-4 text-sm text-slate-200">
          <div class="flex items-center justify-between text-xs uppercase tracking-[0.25em] text-slate-400">
            <span>Recent Records</span>
            <span>{records.length}</span>
          </div>
          {#if records.length}
            {#each records as record}
              <div class="flex flex-col gap-1 border-b border-slate-800/60 pb-3 last:border-none last:pb-0">
                <span class="font-display text-slate-100">
                  {record.firstname || "—"} {record.lastname || ""}
                </span>
                <span class="text-xs text-slate-400">
                  {record.email || "no-email"} · {record.company || "no-org"}
                </span>
              </div>
            {/each}
          {:else}
            <p class="text-xs text-slate-400">No records available.</p>
          {/if}
        </div>
      </div>

      <div class="glass rounded-3xl border border-slate-700/60 p-6">
        <h2 class="font-display text-xl text-slate-100">Control Deck</h2>
        <div class="mt-4 grid gap-3">
          <button class="rounded-2xl border border-empire-400/60 bg-empire-500/15 px-4 py-3 text-left text-sm text-empire-100">
            Start intake run
          </button>
          <button class="rounded-2xl border border-slate-600 px-4 py-3 text-left text-sm text-slate-200">
            Normalize + persist
          </button>
          <button class="rounded-2xl border border-slate-600 px-4 py-3 text-left text-sm text-slate-200">
            Rebuild dashboards
          </button>
        </div>
        <div class="mt-6 rounded-2xl border border-slate-700/60 bg-slate-900/70 p-4 text-xs text-slate-400">
          Auto-sync is currently paused. Enable when HubSpot tokens are present.
        </div>
        <div class="mt-6 rounded-2xl border border-slate-700/60 bg-slate-950/60 p-4 text-sm text-slate-200">
          <div class="flex items-center justify-between text-xs uppercase tracking-[0.25em] text-slate-400">
            <span>Recent Tasks</span>
            <span>{filteredTasks.length}</span>
          </div>
          <div class="mt-3 flex flex-wrap gap-2 text-[11px] uppercase tracking-[0.2em] text-slate-400">
            <button
              class={`rounded-full border px-3 py-1 ${taskFilter === "all" ? "border-empire-400 text-empire-100" : "border-slate-700"}`}
              on:click={() => {
                taskFilter = "all";
                loadData();
              }}
            >
              All
            </button>
            <button
              class={`rounded-full border px-3 py-1 ${taskFilter === "open" ? "border-empire-400 text-empire-100" : "border-slate-700"}`}
              on:click={() => {
                taskFilter = "open";
                loadData();
              }}
            >
              Open
            </button>
            <button
              class={`rounded-full border px-3 py-1 ${taskFilter === "in_progress" ? "border-empire-400 text-empire-100" : "border-slate-700"}`}
              on:click={() => {
                taskFilter = "in_progress";
                loadData();
              }}
            >
              In Progress
            </button>
            <button
              class={`rounded-full border px-3 py-1 ${taskFilter === "done" ? "border-empire-400 text-empire-100" : "border-slate-700"}`}
              on:click={() => {
                taskFilter = "done";
                loadData();
              }}
            >
              Done
            </button>
          </div>
          <div class="mt-4 flex flex-col gap-3 text-xs text-slate-400">
            <input
              class="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-200 outline-none focus:border-empire-400"
              placeholder="Search tasks..."
              bind:value={taskQuery}
            />
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-[11px] uppercase tracking-[0.3em]">Category</span>
              <select
                class="rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-200"
                bind:value={categoryFilter}
              >
                <option value="all">All</option>
                {#each categories as category}
                  <option value={category}>{category}</option>
                {/each}
              </select>
            </div>
          </div>
          {#if filteredTasks.length}
            {#each filteredTasks as task}
              <div class="flex flex-col gap-1 border-b border-slate-800/60 pb-3 last:border-none last:pb-0">
                <button
                  class="text-left font-display text-slate-100 hover:text-empire-200"
                  on:click={() => (selectedTask = task)}
                >
                  {task.title}
                </button>
                <span class="text-xs text-slate-400">
                  {task.category} · {task.status}
                  {task.source_ref ? ` · ${task.source_ref}` : ""}
                </span>
                <div class="mt-2 flex gap-2 text-xs">
                  <button
                    class={`rounded-full border px-3 py-1 ${
                      task.status === "open" ? "border-empire-400 text-empire-100" : "border-slate-700 text-slate-300"
                    }`}
                    on:click={() => setTaskStatus(task.task_id, "open")}
                  >
                    Open
                  </button>
                  <button
                    class={`rounded-full border px-3 py-1 ${
                      task.status === "in_progress"
                        ? "border-empire-400 text-empire-100"
                        : "border-slate-700 text-slate-300"
                    }`}
                    on:click={() => setTaskStatus(task.task_id, "in_progress")}
                  >
                    In Progress
                  </button>
                  <button
                    class={`rounded-full border px-3 py-1 ${
                      task.status === "done" ? "border-empire-400 text-empire-100" : "border-slate-700 text-slate-300"
                    }`}
                    on:click={() => setTaskStatus(task.task_id, "done")}
                  >
                    Done
                  </button>
                </div>
              </div>
            {/each}
          {:else}
            <p class="text-xs text-slate-400">No tasks available.</p>
          {/if}
        </div>
      </div>
    </section>

    <section class="mt-10 grid gap-4 md:grid-cols-3">
      {#each panels as panel}
        <div class="glass rounded-2xl border border-slate-700/60 p-5">
          <h3 class="font-display text-lg text-slate-100">{panel.title}</h3>
          <p class="mt-3 text-sm text-slate-300">{panel.body}</p>
        </div>
      {/each}
    </section>

    {#if selectedTask}
      <section class="mt-10">
        <div class="glass rounded-3xl border border-empire-400/40 p-6">
          <div class="flex items-center justify-between">
            <h2 class="font-display text-2xl text-empire-100">Task Detail</h2>
            <button
              class="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300"
              on:click={() => (selectedTask = null)}
            >
              Close
            </button>
          </div>
          <div class="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Title</p>
              <p class="mt-2 text-lg text-slate-100">{selectedTask.title}</p>
            </div>
            <div>
              <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Status</p>
              <div class="mt-2 flex flex-wrap gap-2 text-sm text-slate-200">
                <button
                  class={`rounded-full border px-3 py-1 ${
                    selectedTask.status === "open"
                      ? "border-empire-400 text-empire-100"
                      : "border-slate-700 text-slate-300"
                  }`}
                  on:click={() => setTaskStatus(selectedTask.task_id, "open")}
                >
                  Open
                </button>
                <button
                  class={`rounded-full border px-3 py-1 ${
                    selectedTask.status === "in_progress"
                      ? "border-empire-400 text-empire-100"
                      : "border-slate-700 text-slate-300"
                  }`}
                  on:click={() => setTaskStatus(selectedTask.task_id, "in_progress")}
                >
                  In Progress
                </button>
                <button
                  class={`rounded-full border px-3 py-1 ${
                    selectedTask.status === "done"
                      ? "border-empire-400 text-empire-100"
                      : "border-slate-700 text-slate-300"
                  }`}
                  on:click={() => setTaskStatus(selectedTask.task_id, "done")}
                >
                  Done
                </button>
              </div>
            </div>
            <div>
              <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Category</p>
              <p class="mt-2 text-slate-200">{selectedTask.category}</p>
            </div>
            <div>
              <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Source</p>
              <p class="mt-2 text-slate-200">{selectedTask.source_ref || selectedTask.source}</p>
            </div>
            <div>
              <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Linked Company</p>
              <p class="mt-2 text-slate-200">{selectedTask.company_name || "—"}</p>
            </div>
          </div>
          <div class="mt-6 rounded-2xl border border-slate-700/60 bg-slate-950/60 p-4 text-sm text-slate-200">
            <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Notes</p>
            <p class="mt-2 whitespace-pre-wrap">{selectedTask.notes || "No notes recorded."}</p>
          </div>
        </div>
      </section>
    {/if}
  </div>
</div>
