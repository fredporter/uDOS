<script>
  import { onMount } from "svelte";

  let projects = [];
  let tasks = [];
  let selectedProject = null;
  let loading = true;
  let error = null;
  let showNewProject = false;
  let showNewTask = false;
  let newProject = { name: "", description: "" };
  let newTask = { title: "", project_id: null, priority: "medium" };

  async function loadProjects() {
    try {
      const res = await fetch("/api/workflow/projects");
      if (res.ok) {
        projects = await res.json();
      }
    } catch (err) {
      console.error("Failed to load projects:", err);
    }
  }

  async function loadTasks(projectId = null) {
    try {
      const url = projectId
        ? `/api/workflow/tasks?project_id=${projectId}`
        : "/api/workflow/tasks";
      const res = await fetch(url);
      if (res.ok) {
        tasks = await res.json();
      }
      loading = false;
    } catch (err) {
      error = `Failed to load tasks: ${err.message}`;
      loading = false;
    }
  }

  async function createProject() {
    try {
      const res = await fetch("/api/workflow/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newProject),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      showNewProject = false;
      newProject = { name: "", description: "" };
      await loadProjects();
    } catch (err) {
      error = `Failed to create project: ${err.message}`;
    }
  }

  async function createTask() {
    try {
      const res = await fetch("/api/workflow/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTask),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      showNewTask = false;
      newTask = { title: "", project_id: selectedProject, priority: "medium" };
      await loadTasks(selectedProject);
    } catch (err) {
      error = `Failed to create task: ${err.message}`;
    }
  }

  async function updateTaskStatus(taskId, status) {
    try {
      const res = await fetch(`/api/workflow/tasks/${taskId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadTasks(selectedProject);
    } catch (err) {
      error = `Failed to update task: ${err.message}`;
    }
  }

  function selectProject(projectId) {
    selectedProject = projectId;
    loadTasks(projectId);
  }

  onMount(() => {
    loadProjects();
    loadTasks();
  });

  function getPriorityClass(priority) {
    switch (priority) {
      case "high":
        return "text-red-400";
      case "medium":
        return "text-yellow-400";
      case "low":
        return "text-blue-400";
      default:
        return "text-gray-400";
    }
  }

  function getStatusClass(status) {
    switch (status) {
      case "completed":
        return "bg-green-900 text-green-200 border-green-700";
      case "in_progress":
        return "bg-blue-900 text-blue-200 border-blue-700";
      default:
        return "bg-gray-700 text-gray-300 border-gray-600";
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <div class="flex items-center justify-between mb-8">
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Workflow Manager</h1>
      <p class="text-gray-400">Native projects and tasks</p>
    </div>
    <div class="flex gap-3">
      <button
        on:click={() => (showNewProject = !showNewProject)}
        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
      >
        + Project
      </button>
      <button
        on:click={() => (showNewTask = !showNewTask)}
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
      >
        + Task
      </button>
    </div>
  </div>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  {#if showNewProject}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">New Project</h3>
      <div class="space-y-4">
        <input
          type="text"
          bind:value={newProject.name}
          placeholder="Project name"
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        />
        <textarea
          bind:value={newProject.description}
          placeholder="Description (optional)"
          rows="3"
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        ></textarea>
        <button
          on:click={createProject}
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
        >
          Create Project
        </button>
      </div>
    </div>
  {/if}

  {#if showNewTask}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">New Task</h3>
      <div class="space-y-4">
        <input
          type="text"
          bind:value={newTask.title}
          placeholder="Task title"
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        />
        <select
          bind:value={newTask.project_id}
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        >
          <option value={null}>No project</option>
          {#each projects as project}
            <option value={project.id}>{project.name}</option>
          {/each}
        </select>
        <select
          bind:value={newTask.priority}
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        >
          <option value="low">Low Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="high">High Priority</option>
        </select>
        <button
          on:click={createTask}
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
        >
          Create Task
        </button>
      </div>
    </div>
  {/if}

  <div class="grid grid-cols-12 gap-6">
    <!-- Projects Sidebar -->
    <div class="col-span-3">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-semibold text-gray-400 mb-3">PROJECTS</h3>
        <div class="space-y-2">
          <button
            on:click={() => selectProject(null)}
            class="w-full text-left px-3 py-2 rounded {selectedProject === null
              ? 'bg-purple-900 text-purple-200'
              : 'text-gray-300 hover:bg-gray-700'}"
          >
            All Tasks
          </button>
          {#each projects as project}
            <button
              on:click={() => selectProject(project.id)}
              class="w-full text-left px-3 py-2 rounded {selectedProject ===
              project.id
                ? 'bg-purple-900 text-purple-200'
                : 'text-gray-300 hover:bg-gray-700'}"
            >
              {project.name}
            </button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Tasks List -->
    <div class="col-span-9">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-white mb-4">
          Tasks ({tasks.length})
        </h3>
        {#if loading}
          <div class="text-center py-12 text-gray-400">Loading...</div>
        {:else if tasks.length === 0}
          <p class="text-gray-400 text-center py-8">No tasks yet</p>
        {:else}
          <div class="space-y-3">
            {#each tasks as task}
              <div class="bg-gray-900 border border-gray-700 rounded p-4">
                <div class="flex items-start justify-between mb-2">
                  <div class="flex-1">
                    <h4 class="text-white font-medium">{task.title}</h4>
                    <div class="flex items-center gap-3 mt-2 text-xs">
                      <span class={getPriorityClass(task.priority)}>
                        {task.priority} priority
                      </span>
                      {#if task.due_date}
                        <span class="text-gray-400">Due: {task.due_date}</span>
                      {/if}
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span
                      class="px-2 py-1 rounded text-xs border {getStatusClass(
                        task.status,
                      )}"
                    >
                      {task.status}
                    </span>
                    {#if task.status !== "completed"}
                      <button
                        on:click={() => updateTaskStatus(task.id, "completed")}
                        class="text-green-400 hover:text-green-300 text-xs"
                        title="Mark completed"
                      >
                        ✓
                      </button>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>
