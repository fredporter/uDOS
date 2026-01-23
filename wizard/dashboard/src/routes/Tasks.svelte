<script>
  import { onMount } from "svelte";

  let tasks = [];
  let queue = [];
  let loading = true;
  let error = null;
  let showCreateForm = false;
  let newTask = { name: "", schedule: "", command: "" };

  async function loadTasks() {
    try {
      const res = await fetch("/api/v1/tasks/all");
      if (res.ok) {
        tasks = await res.json();
      }
    } catch (err) {
      console.error("Failed to load tasks:", err);
    }
  }

  async function loadQueue() {
    try {
      const res = await fetch("/api/v1/tasks/queue");
      if (res.ok) {
        queue = await res.json();
      }
      loading = false;
    } catch (err) {
      error = `Failed to load queue: ${err.message}`;
      loading = false;
    }
  }

  async function createTask() {
    try {
      const res = await fetch("/api/v1/tasks/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTask),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      showCreateForm = false;
      newTask = { name: "", schedule: "", command: "" };
      await loadTasks();
      await loadQueue();
    } catch (err) {
      error = `Failed to create task: ${err.message}`;
    }
  }

  onMount(() => {
    loadTasks();
    loadQueue();
  });

  function getStateBadgeClass(state) {
    switch (state) {
      case "plant":
        return "bg-blue-900 text-blue-200 border-blue-700";
      case "sprout":
        return "bg-yellow-900 text-yellow-200 border-yellow-700";
      case "harvest":
        return "bg-green-900 text-green-200 border-green-700";
      case "compost":
        return "bg-gray-700 text-gray-300 border-gray-600";
      default:
        return "bg-gray-700 text-gray-300 border-gray-600";
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <div class="flex items-center justify-between mb-8">
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Task Scheduler</h1>
      <p class="text-gray-400">
        Organic cron model: Plant → Sprout → Harvest → Compost
      </p>
    </div>
    <button
      on:click={() => (showCreateForm = !showCreateForm)}
      class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
    >
      {showCreateForm ? "Cancel" : "+ New Task"}
    </button>
  </div>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  {#if showCreateForm}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">Create Task</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-2" for="task-name">
            Task Name
          </label>
          <input
            id="task-name"
            type="text"
            bind:value={newTask.name}
            placeholder="e.g., Daily backup"
            class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2" for="task-schedule">
            Schedule (cron)
          </label>
          <input
            id="task-schedule"
            type="text"
            bind:value={newTask.schedule}
            placeholder="e.g., 0 2 * * * (daily at 2am)"
            class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2" for="task-command">
            Command
          </label>
          <input
            id="task-command"
            type="text"
            bind:value={newTask.command}
            placeholder="e.g., python backup.py"
            class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
          />
        </div>
        <button
          on:click={createTask}
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
        >
          Create Task
        </button>
      </div>
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading tasks...</div>
  {:else}
    <!-- Pending Queue -->
    {#if queue.length > 0}
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold text-white mb-4">
          Pending Queue ({queue.length})
        </h3>
        <div class="space-y-2">
          {#each queue as item}
            <div class="bg-gray-900 border border-gray-700 rounded p-3">
              <div class="flex items-center justify-between">
                <div>
                  <span class="text-white font-medium">{item.task_name}</span>
                  <span class="text-gray-400 text-sm ml-2"
                    >→ {item.scheduled_for}</span
                  >
                </div>
                <span class="text-xs text-yellow-400">Scheduled</span>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- All Tasks -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-white mb-4">
        All Tasks ({tasks.length})
      </h3>
      {#if tasks.length === 0}
        <p class="text-gray-400 text-center py-8">
          No tasks yet. Create one above!
        </p>
      {:else}
        <div class="space-y-3">
          {#each tasks as task}
            <div class="bg-gray-900 border border-gray-700 rounded p-4">
              <div class="flex items-start justify-between mb-2">
                <div>
                  <h4 class="text-white font-medium">{task.name}</h4>
                  <p class="text-gray-400 text-sm mt-1">{task.command}</p>
                </div>
                <span
                  class="px-2 py-1 rounded text-xs border {getStateBadgeClass(
                    task.state,
                  )}"
                >
                  {task.state}
                </span>
              </div>
              <div class="text-xs text-gray-500 mt-2">
                <span>Schedule: {task.schedule || "Manual"}</span>
                {#if task.last_run}
                  <span class="ml-4">Last run: {task.last_run}</span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
